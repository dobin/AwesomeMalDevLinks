# https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/

[Skip to content](https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/#wp--skip-link--target)

## What No One Tells You About Non-Interactive Logs

Me and non-interactive sign-in logs had a rough start.

I used to think these logs were only relevant in one scenario:

When a refresh token is used to get a new access token.

And it made sense – after all, that’s something that happens without user interaction. No need to re-enter a username, password, or MFA.

**BUT**

Apparently, there are many other cases _hiding_ in these logs.

And if you’re not aware of them, you might miss real attacks.

Don’t worry – I’m here to save you all the confusion! 😊

* * *

Let’s start with how to actually **get** these logs, because even that part can be a bit confusing.

Do you remember this field in the sign-in logs?

![](https://sapirxfed.com/wp-content/uploads/2025/06/image.png?w=810)

Well, I thought if we filter for `false`, we’d get the non-interactive logs.

Guess what? That’s not how it works.

![](https://sapirxfed.com/wp-content/uploads/2025/06/image-1.png?w=940)

So, what **is** the correct way to read the non-interactive logs?

![](https://sapirxfed.com/wp-content/uploads/2025/06/image-2.png?w=398)

Here’s the query you need:

```
https://graph.microsoft.com/beta/auditLogs/signIns?$filter=signInEventTypes/any(t:+t+eq+'nonInteractiveUser')
```

![](https://sapirxfed.com/wp-content/uploads/2025/06/image-3.png?w=744)

By the way, I tried checking the UI to understand how it reads these logs, and saw this:

![](https://sapirxfed.com/wp-content/uploads/2025/06/image-4.png?w=940)

Turns out, the UI is using the **AADGraph** endpoint to read non-interactive logs.

* * *

Anyway—now that we know how to **read** them, let’s talk about what’s actually **in** them.

According to Microsoft, these are the scenarios that generate non-interactive logs:

- A client app uses an OAuth 2.0 refresh token to get an access token.
- A client uses an OAuth 2.0 authorization code to get an access token and refresh token.
- A user performs single sign-on (SSO) to a web or Windows app on a Microsoft Entra joined PC (without providing an auth factor or interacting with a prompt).
- A user signs in to a second Microsoft Office app on a mobile device using FOCI (Family of Client IDs).

Now here’s the interesting part – some of these are cases where the user is **actually doing something**.

Not everything here is fully “behind the scenes”.

That means…

An attacker’s behavior might **only show up** in the non-interactive logs.

And here’s another thing:

These aren’t even **all** the scenarios that lead to non-interactive logs!

* * *

My journey started with this:

![](https://sapirxfed.com/wp-content/uploads/2025/06/image-5.png?w=824)

How weird is it to see a **non-interactive** log with a **wrong password**?

If it’s not interactive, how did the user even enter the wrong password?

What kind of scenario can cause that?

If you’ve ever seen [this post](https://www.speartip.com/fasthttp-used-in-new-bruteforce-campaign/) about brute force attacks with a “`fasthttp`” user agent – this is _that_ case.

So what do we have here?

- Non-interactive sign-in log
- “Other clients” client
- Error code 50126 (wrong password)
- `authenticationRequirement: singleFactorAuthentication`

My first assumption?

This must be some kind of legacy authentication.

According to Microsoft’s documentation:

![](https://sapirxfed.com/wp-content/uploads/2025/06/image-6.png?w=940)

We now know we can detect this kind of brute-force behavior by simply searching for non-interactive logs using “Other clients”.

But to understand _exactly_ which flow the attacker used… keep reading 😉

* * *

The key thing to understand about this attack is:

It’s not just hidden in the logs – it also **bypasses MFA**.

Why? Because basic authentication doesn’t support MFA.

While researching this case, I tried a bunch of legacy/basic auth flows.

But all of them showed up as **interactive**.

This is where I say **thank you** to [@4ndyGit](https://x.com/4ndyGit), who talked to Microsoft and helped us find the right direction!

The method used here was:

**The RST2 flow.**

Who’s familiar with this? I knew _nothing_ about it!

RST2 is a super old authentication method.

It’s not part of OAuth flows. It uses SOAP, and it allows basic auth – username and password **in every request**.

It’s considered deprecated, but it can still be used by some apps (like SharePoint).

you can see how the SOAP request looks like in AADInternals:

![](https://sapirxfed.com/wp-content/uploads/2025/06/image-9.png?w=1024)

It’s kinda funny that I couldn’t find much about it in Microsoft’s docs—

but of course, I _did_ find something about it in **AADInternals**!

![](https://sapirxfed.com/wp-content/uploads/2025/06/image-7.png?w=940)

Apparently, the `Invoke-AADIntUserEnumerationAsOutsider` function in AADInternals supports four auth flows—

and one of them uses the RST2 endpoint.

![](https://sapirxfed.com/wp-content/uploads/2025/06/image-8.png?w=940)

So to perform the attack, you can run:

```
Invoke-AADIntUserEnumerationAsOutsider -UserName <User>
```

And that’s it!

* * *

**Conclusion**

It can be _really_ frustrating to see behavior in the logs that you can’t explain.

This post shows the answer right away – but trust me, it took me a lot of time to get here.

Still, all the testing I did along the way taught me a _ton_. (:

### Share this:

- [Share on X (Opens in new window)X](https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/?share=twitter&nb=1)
- [Share on Facebook (Opens in new window)Facebook](https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/?share=facebook&nb=1)

LikeLoading…

### Leave a comment [Cancel reply](https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/\#respond)

Δ

[Toggle photo metadata visibility](https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/#)[Toggle photo comments visibility](https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/#)

Loading Comments...

Write a Comment...

Email (Required)Name (Required)Website

- [Comment](https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/#respond)
- [Reblog](https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/)
- [Subscribe](https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/) [Subscribed](https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/)








  - [![](https://sapirxfed.com/wp-content/uploads/2024/07/downloadfile4731434878068414586.jpg?w=50) Sapir's failed research blog](https://sapirxfed.com/)

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Fsapirxfed.com%252F2025%252F06%252F20%252Fwhat-no-one-tells-you-about-non-interactive-logs%252F)


- - [![](https://sapirxfed.com/wp-content/uploads/2024/07/downloadfile4731434878068414586.jpg?w=50) Sapir's failed research blog](https://sapirxfed.com/)
  - [Subscribe](https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/) [Subscribed](https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Fsapirxfed.com%252F2025%252F06%252F20%252Fwhat-no-one-tells-you-about-non-interactive-logs%252F)
  - [Copy shortlink](https://wp.me/pfTADh-5H)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/)
  - [View post in Reader](https://wordpress.com/reader/blogs/234893899/posts/353)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://sapirxfed.com/2025/06/20/what-no-one-tells-you-about-non-interactive-logs/)

%d