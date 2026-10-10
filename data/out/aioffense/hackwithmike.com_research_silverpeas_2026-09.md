# https://hackwithmike.com/research/silverpeas/2026-09

> ## Documentation Index
>
> Fetch the complete documentation index at: [/llms.txt](https://hackwithmike.com/llms.txt)
>
> Use this file to discover all available pages before exploring further.

[Skip to main content](https://hackwithmike.com/research/silverpeas/2026-09#content-area)

In March 2026, shortly after completing the OSWE exam, I was really excited to put what I had just learned to real world use. I was also curious about how far the coding agents available at the time could be pushed in security. Naturally, I turned to open-source security research as a way to test both my skills and the capabilities of AI-assisted code review.

## [​](https://hackwithmike.com/research/silverpeas/2026-09\#why-silverpeas)  Why Silverpeas

I chose Silverpeas after watching Tyler Ramsbey’s video, [I Found 8 CVEs in 2 Weeks (And You Can Too!)](https://www.youtube.com/watch?v=2VB4Zd5C8N8). Silverpeas seemed like a good place to start because its maintainers had a history of responding quickly to researchers and an established disclosure process. The source code was public, and the official Docker image made it easy to run the application locally for testing.

## [​](https://hackwithmike.com/research/silverpeas/2026-09\#review-setup)  Review setup

I cloned the official Silverpeas Core repository and ran the official Docker image for dynamic testing and validation. Gemini CLI was my primary agent, using both the Flash and Pro models, while Claude served as a secondary agent. In practice, the split was roughly 80% Gemini and 20% Claude. The agents at the time were definitely way less capable than what the frontier cyber models can do now, but it was already possible to achieve meaningful results.At the time, I did not have a purpose-built security research harness (now I do!). I simply gave the agents access to the repository and local deployment, stated the authorized scope, and pointed them toward an attack surface such as authentication, access control, file upload, or file access. They were allowed to search the codebase and trace relevant data flows.The agents produced a lot of leads and candidates that **can’t be simply treated as valid vulnerabilities**. Therefore, I reviewed each of the leads, sent uncertain cases back for a deeper trace, and manually reproduced the complete exploit paths. For the final validation, I used a fresh instance so that leftover files, changed state, or incorrect privileges from earlier testing could not affect the result.

## [​](https://hackwithmike.com/research/silverpeas/2026-09\#findings)  Findings

| CVE | Result | CVSS 3.1 | Severity |
| --- | --- | --- | --- |
| [CVE-2026-53695](https://hackwithmike.com/research/advisories/silverpeas/cve-2026-53695) | Unauthenticated reflected XSS and API token theft | 8.2 | High |
| [CVE-2026-53696](https://hackwithmike.com/research/advisories/silverpeas/cve-2026-53696) | Path traversal, arbitrary file write, and RCE | 9.9 | Critical |
| [CVE-2026-53697](https://hackwithmike.com/research/advisories/silverpeas/cve-2026-53697) | Attacker-selected upload path and RCE | 9.9 | Critical |
| [CVE-2026-53698](https://hackwithmike.com/research/advisories/silverpeas/cve-2026-53698) | Authenticated arbitrary file read | 7.7 | High |
| [CVE-2026-53699](https://hackwithmike.com/research/advisories/silverpeas/cve-2026-53699) | Unauthenticated account takeover | 9.8 | Critical |
| [CVE-2026-53700](https://hackwithmike.com/research/advisories/silverpeas/cve-2026-53700) | Authenticated reflected XSS | 4.6 | Medium |

### [​](https://hackwithmike.com/research/silverpeas/2026-09\#cross-site-scripting)  Cross-site scripting

I started with XSS because it was familiar and relatively easy to check manually. I mainly searched JSP files for request data reaching HTML or JavaScript output without encoding for the correct context.

#### [​](https://hackwithmike.com/research/silverpeas/2026-09\#html-attribute-injection-cve-2026-53695)  HTML attribute injection: CVE-2026-53695

The initial sink analysis led to `defaultChangePassword.jsp`. The page wrote `Login` and `DomainId` directly into hidden input values:

```
<input type="hidden" name="login" value="${param.Login}"/>
<input type="hidden" name="domainId" value="${param.DomainId}"/>
```

Silverpeas had an XSS filter in front of the page, but it relied on a blocklist that only matched `<script>` and `<iframe>` patterns. Event-handler payloads using elements such as `<svg>` or `<img>` passed through it (classic!).

![Silverpeas password-change page displaying an alert injected through the Login parameter](https://mintcdn.com/hackwithmike/p7ac3gH7YlwQqU4v/assets/images/research/silverpeas/cve-2026-53695-xss-login.png?fit=max&auto=format&n=p7ac3gH7YlwQqU4v&q=85&s=51852f08486cbfa65d194ef98825d418)

JavaScript executing through the Login parameter on the unauthenticated password-change page

Usually, XSS has a lower impact when session cookies have appropriate security attributes and restrictive browser security policies are in place. In this case, however, **the current user’s API token was displayed directly on the profile page**. The vulnerable page did not require authentication, so an attacker could send a crafted link to a logged-in administrator. JavaScript running in the administrator’s session could request the profile page, extract the token, and send it to the attacker. That token could then be used to perform administrative actions through the API, including creating another administrator account, **turning the reflected XSS into account takeover**.

Your browser does not support embedded WebM video.

Using the unauthenticated password-change XSS to extract an administrator's API token

#### [​](https://hackwithmike.com/research/silverpeas/2026-09\#javascript-string-injection-cve-2026-53700)  JavaScript string injection: CVE-2026-53700

During the hunt for XSS, Gemini identified a vulnerable `ReturnUrl` sink in `htmlEditor.jsp`. The page read `ReturnUrl` from the request, stored it, and later concatenated it into a JavaScript string used by the editor’s Back button.This sink needed JavaScript-string encoding rather than HTML encoding. A value such as `');alert(document.domain);sp.navRequest('` closed the original string and inserted JavaScript. The victim had to be authenticated, open the crafted editor URL, and click on the Back button.I could not push the impact much further because exploitation required that specific sequence of user actions. I did not consider it a particularly practical vulnerability, but I reported it anyway.

Your browser does not support embedded WebM video.

Triggering the ReturnUrl payload through the editor's Back button

### [​](https://hackwithmike.com/research/silverpeas/2026-09\#password-reset-and-account-takeover)  Password reset and account takeover

The account takeover vulnerability was the most interesting find. During the review, the main authentication and password-reset flows did not appear vulnerable, but I found a **legacy password-change path that was no longer exposed through the front end**. The maintainers later confirmed that the vulnerable handler was a deprecated function left behind after an earlier password-reset fix - another reason why legacy code should be carefully reviewed and removed when possible.A password reset normally requires proof that the requester controls the account, often through a one-time token sent to a trusted email address. The legacy Silverpeas handler had no equivalent identity check. It accepted the target account name and domain ID from the request, with a `checkId` as the only gate before changing the password.Despite its name, **the `checkId` did not prove ownership of the account**. It only confirmed that the proposed password had passed the password policy, and anyone could obtain one from the unauthenticated `/services/password/policy/checking` endpoint. It was not bound to a user, a reset session, or a trusted recovery channel.This made [CVE-2026-53699](https://hackwithmike.com/research/advisories/silverpeas/cve-2026-53699) exploitable in two unauthenticated requests. The first submitted a proposed password to the policy-checking endpoint and received a `checkId`. The second sent that value, an attacker-chosen `Login` and `DomainId`, and the new password to `CredentialsServlet/ChangePassword`:

```
assertPasswordHasBeenCorrectlyChecked(checkId, password);
AuthenticationCredential credential = AuthenticationCredential
    .newWithAsLogin(login)
    .withAsDomainId(domainId);
getAuthenticator().resetPassword(credential, password);
```

Setting `Login` to `SilverAdmin` and `DomainId` to `0` reset the built-in administrator password. The response also redirected the attacker into an authenticated session.

![Unauthenticated password-policy request returning a checkId](https://mintcdn.com/hackwithmike/p7ac3gH7YlwQqU4v/assets/images/research/silverpeas/cve-2026-53699-check-id.png?fit=max&auto=format&n=p7ac3gH7YlwQqU4v&q=85&s=6d6480c85d922f8ce71e5314689090f9)

Obtaining a checkId from the public password-policy endpoint

![Password-reset request for SilverAdmin returning an authenticated session cookie](https://mintcdn.com/hackwithmike/p7ac3gH7YlwQqU4v/assets/images/research/silverpeas/cve-2026-53699-password-reset.png?fit=max&auto=format&n=p7ac3gH7YlwQqU4v&q=85&s=9e56efba8fb159eaa8f05358e5d8b860)

Resetting the SilverAdmin password and receiving an authenticated session

Your browser does not support embedded WebM video.

Complete unauthenticated password-reset and account-takeover demonstration

### [​](https://hackwithmike.com/research/silverpeas/2026-09\#file-uploads-and-remote-code-execution)  File uploads and remote code execution

File upload was one of the areas I deliberately asked the agents to inspect because path and file-type validation failures are common entry points to code execution.

| CVE | Attacker-controlled value | What it controlled |
| --- | --- | --- |
| [CVE-2026-53697](https://hackwithmike.com/research/advisories/silverpeas/cve-2026-53697) | `Path` request parameter | The destination directory used by `uploadWebsiteFile.jsp` |
| [CVE-2026-53696](https://hackwithmike.com/research/advisories/silverpeas/cve-2026-53696) | `X-UPLOAD-SESSION` form value | The base directory used by the REST upload session |

The agents initially identified and established findings on path traversal and arbitrary file write, but did not find a reliable route to code execution on their own. From there, I took over the impact analysis and tried to identify files that the running application would load or execute. I first looked at configuration files and existing JSP locations, but many of the promising files were generated during deployment. Overwriting them did not cause the application to reload or execute the new content.I eventually turned to WildFly’s deployment mechanism. The server monitored `/opt/wildfly/standalone/deployments/` and automatically loaded deployable applications placed there. **Writing a malicious WAR into that directory turned the arbitrary file write into RCE** without requiring another user to trigger the deployment.

#### [​](https://hackwithmike.com/research/silverpeas/2026-09\#direct-upload-path-cve-2026-53697)  Direct upload path: CVE-2026-53697

`uploadWebsiteFile.jsp` trusted the `Path` request parameter when constructing the destination file. The file-extension check ran only in client-side JavaScript, so it did not protect a direct request to the JSP.I validated the issue by building an exploded WAR in the deployment directory: upload the JSP, add a minimal `WEB-INF/web.xml`, and write the `.dodeploy` marker. A pre-built WAR as a single upload also worked.

![Upload request using the Path parameter to write a file into the container filesystem](https://mintcdn.com/hackwithmike/p7ac3gH7YlwQqU4v/assets/images/research/silverpeas/cve-2026-53697-arbitrary-write.png?fit=max&auto=format&n=p7ac3gH7YlwQqU4v&q=85&s=a52c2685dd54dfdb112f2efabd30cace)

Writing a file to an attacker-selected path through uploadWebsiteFile.jsp

Your browser does not support embedded WebM video.

Building and deploying a malicious WAR through uploadWebsiteFile.jsp

#### [​](https://hackwithmike.com/research/silverpeas/2026-09\#upload-session-traversal-cve-2026-53696)  Upload-session traversal: CVE-2026-53696

The REST upload endpoint checked `fullPath` for `..` but did not apply the same check to `X-UPLOAD-SESSION`. `UploadSession` used the session value to construct the base directory before it joined the clean filename:

```
uploadSessionFolder =
    new File(FileRepositoryManager.getTemporaryPath(), uploadSessionId);
```

A traversal value in `X-UPLOAD-SESSION` escaped the temporary directory. A low-privilege user could therefore upload a pre-built WAR directly into WildFly’s deployment directory.

Your browser does not support embedded WebM video.

Using X-UPLOAD-SESSION traversal for an arbitrary file write

Your browser does not support embedded WebM video.

Uploading a WAR through X-UPLOAD-SESSION traversal and executing commands as root

### [​](https://hackwithmike.com/research/silverpeas/2026-09\#fileserver-arbitrary-file-read)  FileServer arbitrary file read

For file read, I asked the agents to enumerate functions that opened files and look for paths with weaker access checks. That search led to [CVE-2026-53698](https://hackwithmike.com/research/advisories/silverpeas/cve-2026-53698) in the `FileServer` servlet.Three behaviors combined:

1. Omitting `ComponentId` selected the personal-space path, where `isUserAllowed()` returned true.
2. Supplying `TypeUpload` caused `SourceFile` to be treated as an absolute filesystem path.
3. The relative-path check rejected `../` but did not reject an absolute path such as `/etc/passwd`.

An authenticated request for `SourceFile=/etc/passwd&TypeUpload=` returned the file as a download. The same path could expose configuration, credentials, keys, or any other file readable by the application server process.

![Authenticated FileServer request returning the contents of /etc/passwd](https://mintcdn.com/hackwithmike/p7ac3gH7YlwQqU4v/assets/images/research/silverpeas/cve-2026-53698-file-read.png?fit=max&auto=format&n=p7ac3gH7YlwQqU4v&q=85&s=466c6f870116828b76a7f9f8a6211af6)

Reading /etc/passwd through the FileServer servlet

## [​](https://hackwithmike.com/research/silverpeas/2026-09\#some-final-thoughts)  Some final thoughts

AI-assisted vulnerability research will (or has) become an essential part of source-code review. Even the models available in March 2026 gave me more coverage than I could have achieved on my own.To their credits, the agents found most of the candidate functions behind these vulnerabilities. Their strongest contribution was coverage: they could move through a large repository, trace values across files, and return code paths that deserved manual testing. They also helped produce requests and payloads after I had a concrete exploitation plan.However, **they were less reliable at judging whether a candidate was exploitable and how far its impact could be pushed**. Some findings were false positives because the agent missed a protection elsewhere in the call path. In other cases, it stopped at a lower severity result and did not push for a higher impact.Does that mean that AI is bad at security research? Definitely no. All they need are simply a better harness, or an experienced human operator to stir them into the right directions and enforce scopes & goals. Most of my role throughout the research was to choose useful attack surfaces, redirect the agents when they entered a dead end, filter the output, plan the exploitation path, and validate the final impact.I expect the human role to move away from boring and repetitive tasks like reviewing and eyeballing every line, and toward managing the engagement. Building a good harness is part of that job. It gives the model a constrained environment where it can inspect code, interact with the target, record evidence, and repeat tests without losing track of scope. I am currently actively exploring and building in that area, and I hope to share more on my learnings very soon!

## [​](https://hackwithmike.com/research/silverpeas/2026-09\#disclosure-timeline)  Disclosure timeline

| Date | Event |
| --- | --- |
| March 2026 | The vulnerabilities were disclosed to Silverpeas. |
| March 2026 | Silverpeas acknowledged the reports and committed fixes to the maintained branches. |
| June 2026 | MITRE CNA-LR assigned CVE-2026-53695 through CVE-2026-53700. |
| July 2026 | Silverpeas released version 6.4.7 with the fixes. |
| September 2026 | This research was published. |

## [​](https://hackwithmike.com/research/silverpeas/2026-09\#references)  References

- [I Found 8 CVEs in 2 Weeks (And You Can Too!)](https://www.youtube.com/watch?v=2VB4Zd5C8N8)
- [Silverpeas-Core source repository](https://github.com/Silverpeas/Silverpeas-Core)
- [CVE-2026-53698 record](https://www.cve.org/CVERecord?id=CVE-2026-53698)

## [​](https://hackwithmike.com/research/silverpeas/2026-09\#acknowledgements)  Acknowledgements

Thank you to Tyler Ramsbey for publishing the video that inspired this research, and to the Silverpeas maintainers for promptly reviewing the reports and fixing the vulnerabilities.

Last modified onSeptember 8, 2026

Was this page helpful?

YesNo