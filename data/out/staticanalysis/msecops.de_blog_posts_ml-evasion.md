# https://msecops.de/blog/posts/ml-evasion/

In my x33fcon talk [The Art of Evasion](https://www.youtube.com/watch?v=QV0C-NQSjsg), I presented general Packer/Loader explanations as well as what machine-learning-based detections are about and how to bypass them. This blog post is the companion to that talk and also introduces the RustPack version 1.7 features that cover ML evasion by default.

## The Packer/Loader Architecture and Minimum Needed Features

When we talk about the architecture of a Packer in the malware development field, it usually consists of two main components:

1. The Packer code
2. The Loader code

The Packer can be used by an operator with various input arguments to enable optional features. It typically encrypts or encodes an input payload, generates the “Loader code” and then compiles it to produce an executable, DLL or other output payload. That output payload executes the original input from memory in an OPSEC-safe way after decrypting or decoding it.

From my perspective, any Packer needs at minimum the following features so that you can use it long-term without getting signatured or flagged at runtime:

![](https://msecops.de/blog/posts/ml-evasion/Minimum.png)

Polymorphism means that every output payload differs heavily from the next, so that creating signatures or YARA rules for that output is as hard as possible. This can be implemented in a simple or a more complex way. A very simple example would be to place `RANDVALUE` placeholders throughout the “Loader code” templates; for every single payload, the Packer then replaces these stubs with custom, always different-looking code before compiling it. This ensures that new random instructions are inserted every few instructions, so every output looks different. A very simple implementation is used in my public [NimSyscallPacker](https://github.com/S3cur3Th1sSh1t/NimSyscallPacker), in which random, always different-looking strings are inserted:

![](https://msecops.de/blog/posts/ml-evasion/RAND.png)

RustPack uses a far more complex implementation: various code snippets from a pool are inserted, and those snippets are heavily randomised as well, so that the inserted junk code never looks the same. In a bad implementation, the inserted junk code itself might get signatured and become an IoC of its own.

Suspicious strings in your payload can get it caught directly, which is why string obfuscation is a must, at least for obvious IoCs. Something simple such as `XOR` with a custom seed, for example the compile time, can be sufficient:

![](https://msecops.de/blog/posts/ml-evasion/StringEncryption.png)

However, at the latest when an analyst or an LLM takes a look at the payload, this kind of encryption can simply be reversed to recover the original plaintext strings. So, to complicate analysis further, a random key for every single string as well as multiple different encryption/decryption functions are recommended, which is again implemented in RustPack.

Any payload that is dropped to disk is analysed by an emulation engine at some AV/EDR vendors (not all). Emulation is different from a sandbox: payloads are not executed on a real, virtualized operating system. Instead, the vendor emulates the payload’s ASM instructions and, for any real Win32 API, provides the software with `fake return values` so that the malware thinks execution succeeded even though it never really happened. So, for example, when the malware calls `LoadLibraryA` to load `amsi.dll`, the emulation engine returns a fake success value and some fake handle to the malware, but the DLL was never really loaded. Different approaches can be used to bypass such emulation engines, for example:

1. Resource Exhaustion
2. Breaking the Implementation

Emeric Nasi published a [good talk](https://github.com/sevagas/conf/blob/main/2024/MCTTP/BypassAVDynamics_10YearsLater_extended.pdf) on this topic at MCTTP 2024 - if you are interested, it is a recommended read!

Some implementations might break one emulation engine but not another. The recommendation here is to be creative and to find your own custom bypasses.

Encryption or encoding of the input payload is generally recommended, though not strictly necessary. If the input payload is not known-malicious, or is retrieved from a file on disk or some other channel at runtime, it is optional.

Various optional features can be implemented in a Packer, such as `userland hook evasion` via different techniques, `DLL sideloading` output and so on. However, these are only needed against certain vendors or in specific situations. Bypassing `AMSI` or `ETW` data collection, for example, is only needed when executing known-malicious scripts or .NET assemblies from memory.

## Machine Learning Based Detections

Even if you have implemented all of the minimum required features in your Packer/Loader, you might still face a detection like the following:

![](https://msecops.de/blog/posts/ml-evasion/MLDetection.png)

And this is where machine-learning-based detections come into play. Talking about machine learning in 2026, most people think of ChatGPT, Claude, Grok and so on. But this is not what AV/EDR vendors use for detection in their products. What most vendors use is “passive metadata analysis”.

![](https://msecops.de/blog/posts/ml-evasion/ML.png)

But how does “passive metadata analysis” work? For me, this was a real question until Brandon (mez0) published the following blog post:

- [https://mez0.cc/posts/evaluating-implants-with-ember/](https://mez0.cc/posts/evaluating-implants-with-ember/)

Before that point, I was not aware of the publication of [EMBER2024](https://github.com/futurecomputing4ai/ember2024), EMBER2018 or EMBER2017. In a nutshell, EMBER2024 was trained on millions of files collected from VirusTotal during 2024. For every sample, both benign and malicious, various metadata was analysed. This way, a small, offline-running machine learning model of just a few MB was created that anyone can download and use for scanning or analysis on [HuggingFace](https://huggingface.co/joyce8/EMBER2024-benchmark-models).

What does this mean for us? We can use EMBER2024 ourselves to go for:

1. Offline testing of ML detections
2. Automated testing of ML detections

For this purpose, I vibe-coded a simple Python wrapper around EMBER2024 to scan `NimSyscallPacker` payloads. And although all of the minimum required features from above are implemented there, all payloads are classified as malicious with a high score:

![](https://msecops.de/blog/posts/ml-evasion/NSP1.png)

And even when we use payload encoding to lower the entropy of the payload, the machine learning score doesn’t decrease at all:

![](https://msecops.de/blog/posts/ml-evasion/NSP2.png)

When analysing the EMBER2024 model, you will find that it uses various input metadata for the final classification:

![](https://msecops.de/blog/posts/ml-evasion/EMBER.png)

One or two years ago, I would have adjusted my payload in each of these sections manually, one after another, to find out which change decreases the score the most. But we are in 2026, and such tasks can easily be fully automated with an LLM such as Claude. So instead, I gave Claude the following prompt, asking it to find out what exactly decreases the score of an exemplary small loader written in `.c` the most:

![](https://msecops.de/blog/posts/ml-evasion/Prompt.png)

The base score for this small `.c` loader file was 99% malicious. After just a few minutes, Claude found that using benign-looking fake imports in the loader code reduces the score, and that adding imports which occur in typical malware increases the score accordingly:

![](https://msecops.de/blog/posts/ml-evasion/IAT.png)

After a few more minutes, it combined various benign-looking fake IAT entries in the payload and achieved a BENIGN score for EMBER2024:

![](https://msecops.de/blog/posts/ml-evasion/Benign.png)

It was still the same code - just benign imports added, nothing else. And this logic holds, at least for EMBER2024: the more benign IAT entries are added, the more the score decreases. So with 141 benign imports added to the payload, the score already decreased by 93%:

![](https://msecops.de/blog/posts/ml-evasion/Final.png)

But the analysis also found that the following adjustments decrease the ML score of the payload:

1. Valid code Signing certificates
2. Export Table entries
3. `.pdata` section entries

And this makes total sense. When analysing VirusTotal data, statistically only a rare few malicious payloads are signed with a valid code-signing certificate. Most binaries considered malicious are not signed, so signing malware with a valid certificate drastically reduces the ML score. Signing the malware with an invalid certificate, on the other hand, doesn’t really influence the score.

Typical malware on VirusTotal does not use any Export Address Table (EAT) entries. So adding EAT entries to an executable also decreases the score, because this is rarely done by malware.

The `.pdata` section in a binary contains the function table entries. So if your malware has just one main function, you will have only one or very few `.pdata` entries. Most shellcode loaders don’t use many different functions either, but benign software does. So adding more functions to the loader code enlarges the `.pdata` section and also decreases the score. For EMBER2024, however, this accounted for only a few percent of the overall change.

Before this analysis, RustPack already had some features implemented, such as `--pumpml`, which imports huge Rust libraries into the loader code and calls functions from them. This decreased the machine learning score, because these huge libraries came with their own imports and various new functions - benign IAT entries and a lot more benign code were added.

After this analysis, and since RustPack version 1.7.5, the core payloads were adjusted. Now every single payload uses many different imports from a pool of several hundred Win32 APIs that are considered benign. So a random number of benign functions is added to every payload, and different functions for every payload, so that the imports themselves cannot become an IoC. IAT camouflage was previously implemented quite simply, by just calling various Win32 APIs from a single function. Now the fake Win32 API calls are spread across the whole code base in ever-changing places. As a result, the ML score is now decreased by default for every single payload.

## Active LLM Analysis

LLMs have gotten really good at reverse engineering by now. You can have an LLM search for vulnerabilities in closed-source projects by pointing it at the executables and DLLs, and it will find the relevant parts of the code in no time. I did this a lot in 2026, and the results are astonishing.

We cannot really tell what AV/EDR vendors do when a payload is submitted to the cloud for analysis. For sure there will be some sandbox behaviour checks, emulation engines and maybe even some static analysis. With the drastic changes in the field of LLMs since the end of 2025, I believe that at some point vendors might also implement some simple - and in some cases maybe even more complex - active LLM analysis of payloads. Who knows, maybe this is already being done partially. Elastic published a blog post in April 2026 about [LLM-driven reverse engineering vs. iterative LLM obfuscation](https://www.elastic.co/security-labs/llm-reversing-vs-llm-obfuscation), which made me curious about how to make an LLM think my payloads are benign.

I started letting Claude Opus analyse my `NimSyscallPacker` payloads, having it use Python and the Capstone library for reversing. It should rate the input binary from 0 to 100, where a score of 70 or above would get the process killed in production, which could lead to disruptions. This was added to make sure the LLM would only score above 70 when it was really sure about the maliciousness of a payload.

![](https://msecops.de/blog/posts/ml-evasion/Prompt2.png)

After just a few minutes, Claude knew that this payload makes heavy use of string obfuscation and dynamically invokes Win32 APIs at runtime:

![](https://msecops.de/blog/posts/ml-evasion/Claude.png)

![](https://msecops.de/blog/posts/ml-evasion/Claude2.png)

The analysis was finished after 10-15 minutes: it decrypted the encrypted strings, found the anti-debugging functionality and various other things - final score of 92 - KILL IN PRODUCTION:

![](https://msecops.de/blog/posts/ml-evasion/Claude3.png)

In this case, it did not find out how and what is being executed. It could have found, for example, that indirect syscalls are used for execution, and decrypting the original shellcode would also have been my expectation here, which did not happen yet. But the harness with Python and Capstone is of course very simple, and a better harness would make the LLM much more effective. Still, the classification and results in that timeframe were impressive to me.

My question now was how to make the LLM score my loader payloads as benign, even though they are not. I started with a simple analysis like the one above, but also let the LLM generate a full report of IoCs as a Markdown file. It should explain in depth what was considered malicious and why.

I forwarded the IoC report from that first analysis to a fresh-context LLM and told it to make a plan for getting rid of all the IoCs mentioned in that initial Markdown file. I always reviewed that plan manually myself and adjusted it, because the LLM often wanted to remove IoCs with techniques that would have introduced even more new ones. Especially for a commercial product like RustPack, used by many companies, it is important not to introduce generic IoCs across all payloads just to avoid others. So this manual review was strictly necessary. The adjusted report was then forwarded for implementation, and afterwards the new payload was pointed to the very first LLM again for IoC analysis and rating with a report.

So in the end this became a loop, and I had to go through it many times over the course of weeks until, for the first time, Claude rated my binary as BENIGN:

![](https://msecops.de/blog/posts/ml-evasion/FinalBenign.png)

And in this analysis it was of course also looking for dynamic API resolution, direct syscalls, various well-known API hashing functions and so on, but could no longer find such IoCs:

![](https://msecops.de/blog/posts/ml-evasion/Scorings.png)

Getting to that point is, on the one hand, about removing well-known IoCs such as the ones mentioned above. On the other hand, it is about adding legitimate-looking code - and, in the case of RustPack, always different-looking code - so that at some point the LLM concludes it is too complex for a full analysis, and, since no direct IoCs are visible, also finishes the analysis early with a low score.

Of course, when you tell the LLM to dig deeper across several sessions, at some point it will change its rating and score. But the result up to this point already made me happy. If vendors start analysing payloads in the cloud with an LLM, they cannot spend endless tokens and context on that analysis. There has to be a cap, because it would very quickly become very expensive and resource-intensive to run such an analysis on all payloads that are dropped to disk. So for now I’m confident the chosen approach is safe enough, even if these detections start being used soon.

In RustPack 1.7.0 we also introduced a file-backdooring feature. It lets operators backdoor benign executables or DLLs so that the input payload is executed in a stealthy way at runtime while preserving the original executable’s or DLL’s functionality. To see how an LLM rates such a backdoored binary, I backdoored `7z.exe` with shellcode and pointed Claude at this backdoored executable for analysis:

![](https://msecops.de/blog/posts/ml-evasion/7z.png)

In the very first backdoor implementation, Claude’s analysis was still able to find the custom shellcode and identify the potentially malicious code. However, after some iterations of the loop, the result was even better than with the unsigned executable. Because RustPack does not backdoor the entrypoint of an executable, but instead actively debugs the target to find suitable alternative locations for injection, an entrypoint analysis did not find suspicious results. And later in the code, no obvious execution primitives were found either. The main IoC for Claude was that the file was no longer signed. But it also finished the analysis early, after 3 minutes, because of that legitimate first impression.

![](https://msecops.de/blog/posts/ml-evasion/7zfinal.png)

In general, if you want a loader not to look suspicious to an active LLM analysis, the following things should be avoided:

![](https://msecops.de/blog/posts/ml-evasion/avoid.png)

If your code is not complex enough, the LLM can easily decompile and analyse everything in a short amount of time. If it’s one single string-obfuscation function used across the whole code base, that’s easy and fast to spot as well as to decrypt. PEB-walk patterns in general are an IoC that LLMs check for - here you need to get creative. Typical, well-known API-hashing patterns are a no-go, as those are found very fast. Low entropy is needed, so don’t just encrypt. If you don’t have any imports at all anymore, that’s also obviously suspicious - but how and where to place which IAT entries is, again, where you need to get creative.

## Conclusion

Creating a Packer or Loader is not a new topic. There are plenty of public tools on GitHub and from various other sources that provide the minimum required features for OPSEC-safe execution of payloads from memory.

However, there is still very little information about how machine-learning-based detections work and how to bypass them. Over the last few years, the offensive security community switched to new programming languages several times because of lower detection rates - for example the [Nim programming language](https://github.com/byt3bl33d3r/OffensiveNim) or [Zig](https://github.com/darkr4y/OffensiveZig). The secret behind it: these were detected less often because ML engines were not yet trained on samples written in these languages. But within 1-2 years of their growing use for malware development, the ML engines were adjusted and started flagging not just malicious samples in these languages, but even simple “Hello World” programs. Why? Because every Nim binary, for example, contains the exact same “benign-looking” imports in its IAT, since it uses a custom API resolution via dynlib. Using a new language is therefore not a long-term solution for a bypass.

Active LLM analysis is, to our knowledge, not yet used by vendors to identify malicious payloads. But with the recent changes in the LLM space, it is conceivable that LLMs will also start playing an active part in malware analysis in the near future.

With this blog post, we share some more information with the wider community and provide all of these features ready to use for our RustPack customers. If you don’t want to - or cannot - do this research or tool development on your own, feel free to reach out to us!

Home

Imprint

#### Angaben gemäß § 5 TMG:

MSec Operations UG (haftungsbeschränkt)

Hainstraße 153

42109 Wuppertal

Handelsregister: HRB 34849

Registergericht: Amtsgericht Wuppertal

#### Vertreten durch:

Fabian Mosch

#### Kontakt:

info\[at\]msecops\[dot\]de

#### Haftung für Inhalte

Als Diensteanbieter sind wir gemäß § 7 Abs.1 TMG für eigene Inhalte auf diesen Seiten nach den allgemeinen Gesetzen verantwortlich. Nach §§ 8 bis 10 TMG sind wir als Diensteanbieter jedoch nicht verpflichtet, übermittelte oder gespeicherte fremde Informationen zu überwachen oder nach Umständen zu forschen, die auf eine rechtswidrige Tätigkeit hinweisen.

Verpflichtungen zur Entfernung oder Sperrung der Nutzung von Informationen nach den allgemeinen Gesetzen bleiben hiervon unberührt. Eine diesbezügliche Haftung ist jedoch erst ab dem Zeitpunkt der Kenntnis einer konkreten Rechtsverletzung möglich. Bei Bekanntwerden von entsprechenden Rechtsverletzungen werden wir diese Inhalte umgehend entfernen.

#### Haftung für Links

Diese Webseite enthält Links zu externen Webseiten Dritter, auf deren Inhalte wir keinen Einfluss haben. Daher können wir für diese Inhalte auch keine Haftung übernehmen. Für die Inhalte der verlinkten Seiten ist stets der Anbieter oder Betreiber selbst verantwortlich. Die verlinkten Seiten wurden zum Zeitpunkt der Verlinkung auf potentielle Rechtsverstöße überprüft. Rechtswidrige Inhalte waren zum Zeitpunkt der Verlinkung nicht erkennbar.

Eine ständige inhaltliche Kontrolle der verlinkten Seiten ist jedoch ohne konkrete Anhaltspunkte einer Rechtsverletzung nicht zumutbar. Bei Bekanntwerden von Rechtsverletzungen werden wir derartige Links umgehend entfernen.

#### Urheberrecht

Die Inhalte und Werke, die von den Betreibern dieser Seiten erstellt wurden, unterliegen dem deutschen Urheberrecht. Die Vervielfältigung, Bearbeitung, Verbreitung und jede Art der Nutzung außerhalb der Grenzen des Urheberrechts bedürfen der schriftlichen Zustimmung des jeweiligen Autors oder Erstellers. Downloads und Kopien dieser Seite sind nur für den privaten, nicht kommerziellen Gebrauch erlaubt.

Sofern die Inhalte auf dieser Seite nicht vom Betreiber erstellt wurden, werden die Urheberrechte Dritter respektiert. Insbesondere werden Inhalte Dritter als solche gekennzeichnet. Sollten Sie dennoch auf eine Urheberrechtsverletzung aufmerksam werden, bitten wir um einen entsprechenden Hinweis. Bei Bekanntwerden von Rechtsverletzungen werden wir solche Inhalte umgehend entfernen.

Privacy

#### Datenschutzerklärung

### Allgemeine Informationen

Die folgend aufgeführten Informationen geben einen Überblick, was mit personenbezogenen Daten beim Besuch dieser Webseite passiert. Personenbezogene Daten sind all jede, mit denen Sie persönlich identifiziert werden können. Detail-Informationen zum Thema Datenschutz entnehmen Sie dieser Datenschutzerklärung.

### Verantwortlichkeit / Datenschutzbeauftragter

MSec Operations UG (haftungsbeschränkt)

Hainstraße 153

42109 Wuppertal

E-Mail Addresse:

info\[at\]msecops\[dot\]de

Vertretungsberechtigt: Herr Fabian Mosch

### Welche Daten werden auf der Webseite erfasst

Daten auf dieser Webseite werden sowohl dadurch erfasst, dass Sie uns diese mitteilen, als auch automatisch nach Einwilligung beim Besuch der Webseite. Dies können entweder Daten sein, welche im Kontaktformular hinterlegt werden, oder aber Daten, welche vom IT-System selbst erfasst werden (z.B. Internetbrowser, Betriebssystem oder Uhrzeit des Seitenaufrufs). Die Erfassung der Daten vom IT-System erfolgt, sobalt die Webseite betreten wird.

#### Wofür werden Daten genutzt

Teilweise werden Daten zur fehlerfreien Bereitstellung der Webseite erhoben. Andere Daten können zur Analyse des Nutzerverhaltens verwendet werden.

#### Auskunft über die Daten

Herkunft, Empfänger und Zweck der gespeicherten personenbezogenen Daten können jederzeit unentgeldlich angefragt werden. Zudem kann eine Löschung der Daten verlangt werden. Die Einwilligung zur Datenverarbeitung kann jederzeit widerrufen werden. Unter bestimmten Umständen kann die Einschränkung der Verarbeitung Ihrer personenbezogenen Daten verlangt werden. Zudem steht ein Beschwerderecht bei der zuständigen Aufsichtsbehörde zu.

Bei Fragen können Sie sich jederzeit an die Impressum genannten Kontakt-Daten wenden.

#### Rechtsgrundlage

Die Verarbeitung der Personenbezogenen Daten erfolgt regelmäßig nach Einwilligung der jeweiligen Benutzer. In manchen Fällen ist eine Einwilligung technisch nicht möglich. In diesen Fällen ist die Verarbeitung der Daten jedoch durch gesetzliche Vorschriften gestattet, siehe Art. 6 Abs. 1 lit. f DSGVO.

#### Cookies

Diese Webseite verwendet an mehreren Stellen Cookies. Beim Aufruf der Webseite kann ein Cookie im Browser des Besuchers der Webseite gespeichert werden. Ein Cookie enthält eine eindeutige Zeichenfolge, welche die Identifizierung dieses Browsers bzw. Benutzers beim erneuten Aufrufen der Webseite ermöglicht.

Benutzer der Webseite können durch Änderung der Einstellungen des Internetbrowsers die Übertragung und Speicherung von Cookies deaktivieren oder einschränken. Sollten Cookies abgespeichert worden sein, können diese jederzeit in den Browser-Einstellungen gelöscht werden.

#### Google Analytics

Diese Webseite nutzt Google Analytics des Anbieters "Google". Über Google Analytics werden statistische Auswertungen von Benutzerzugriffen auf die Webseite analysiert. Durch die Erfassung dieser Daten ist eine Optimierung der Qualität sowie der Inhalte dieser Webseite möglich. Die Erfassung dieser Daten erfolgt ebenfalls im Zusammenhang mit dem Artikel 6 Abs. 1 lit. der DSGVO. Die Analyse der Daten kann technisch unterbunden werden, indem JavaScript und Cookies im Webbrowser deaktiviert werden. Details hierzu können den jeweiligen Produktbeschreibungen der Browser-Anbieter entnommen werden. Weitere Informationen sowie ein Browser-Addon zur Deaktivierung der Daten-Sammlung finden Sie hier: https://tools.google.com/dlpage/gaoptout?hl=de

Die Nutzungsbedingungen sowie Datenschutz-Erklärung von Google können folgenden Links entnommen werden:

\- https://marketingplatform.google.com/about/analytics/terms/de/

\- https://policies.google.com/?hl=de&gl=de

#### Kontaktformular

Auf dieser Webseite befindet sich ein Kontaktformular. Bei Benutzung dieses Kontaktformulars werden folgende Daten an uns übermittelt und gespeichert:

\- Vorname

\- Nachname

\- E-Mail

\- Telefonnummer

\- Individueller Text im Freifeld

\- IP-Adresse des Benutzers

\- Datum und Uhrzeit der Absendung

Als Rechtsgrundlage für die Verarbeitung dieser Daten ist Art. 6 Abs. 1 lit. f DSGVO gegeben. Die Daten werden zur Bearbeitung der Anfrage sowie zur Kommunikation mit dem jeweiligen Benutzer verwendet.

#### Sicherheit

MSec Operations UG (haftungsbeschränkt) setzt verschiedene technische und organisatorische Sicherheitsmaßnahmen ein, um die personenbezogenen Daten gegen zufällige oder vorsätzliche Manipulationen sowie den Verlust/Zugriff oder die Zerstörung dieser zu schützen. Die hierbei verwendeten Sicherheitsmaßnahmen werden fortlaufend verbessert und weiterentwickelt.

#### Anfragen per E-Mail

Sollten Sie uns per E-Mail kontaktieren, wird diese Anfrage inklusive der daraus hervorgehenden personenbezogenen Daten (Name, Anfrage, Datum, Uhrzeit), zum Zwecke der Bearbeitung des Anliegens bei uns gespeichert und verarbeitet. Diese Daten werden nicht ohne Ihre Einwilligung weitergegeben. Die übersandten Daten verbleiben bei uns, bis Sie uns zur Löschung dieser auffordern, oder die Einwilligung zur Speicherung widerrufen. Wenn der Zweck für die Datenspeicherung entfällt (nach abgeschlossener Bearbeitung) werden diese ebenfalls gelöscht.

Die Verarbeitung dieser Daten erfolgt auf Grundlage von Art. 6 ASbs. 1 lit b DSGVO.

#### Soziale Netzwerke

MSec Operations UG (haftungsbeschränkt) unterhält verschiedene öffentlich zugängliche Profile in sozialen Netzwerken. Die genutzten sozialen Netzwerke finden Sie unten.

Über soziale Netzwerke wie LinkedIn etc. können Nutzerverhalten umfassend analysiert werden, sobald die Webseite des Anbieters besuchen oder mit integrierten Inhalten (wie z.B. Like-Buttons oder Kommentaren) interagieren. Beim Besuch einer solchen Webseite werden diverse personenbezogene Daten erhoben, wie beispielsweise:

\- Zuordnung Ihres Benutzer-Kontos zum jeweiligen Social Media Portal. DIes kann auch erfolgen, wenn Sie nicht eingeloggt sind oder keinen Account auf der jeweiligen Webseite besitzen. Die Datenerfassung erfolgt hier über Cookies.

\- Über diese Zuordnung können Benutzer-Profile erstellt werden, in denen Präferenzen sowie Interessen hinterlegt sind. Auf diese weise kann zugeschnittene Werbung in- und außerhalb der jeweiligen Social Media Präsenz angezeigt werden. Bei Benutzung eines Accounts kann diese Werbung auf allen verwendeten Geräten (wie beispielsweise auch Smartphones) angezeigt werden.

Bei der Erfassung von Daten über Soziale Netzwerke ist die Grundlage ebenfalls Art. 6 Abs. 1 lit. f DSGVO. Die Analyseprozesse selbst beruhen ggf. auf abweichenden Grundlagen, wie der Einwilligung im Sinne des Art. 6 Abs. 1 lit. a DSGVO.

Die Geltendmachung von Rechten zur Auskunft, zur Berichtigung, zur Löschung sowie Einschränkung dieser Daten können beim jeweiligen Sozialen Netzwerk Anbieter geltend gemacht werden.

Auf die Speicherdauer der Daten auf Sozialen Netzwerken der jeweiligen Anbieter haben wir keinen Einfluss. Informieren Sie sich daher bitte bei den jeweiligen Betreibern der sozialen Netzwerke.

##### Genutzte Soziale Netzwerke

Twitter:

MSec Operations UG nutzt den Kurznachrichtendienst Twitter. Anbieter ist die Twitter International Company, One Cumberland Place, Fenian Street, Dublin 2, D02 AX07, Irland.

Die Datenschutz-Einstellungen für Twitter können im jeweiligen Benutzer-Profil selbstständig bearbeitet bzw. angepasst werden: https://twitter.com/personalization

Die Datenübertragung in die USA wird auf die Standardvertragsklauseln der EU-Kommission gestützt. Details finden Sie hier: https://gdpr.twitter.com/en/controller-to-controller-transfers.html.

Details entnehmen Sie der Datenschutzerklärung von Twitter: https://twitter.com/de/privacy.

LinkedIn:

Des Weiteren wird ein Profil auf LinkedIn verwendet. Anbieter ist die LinkedIn Ireland Unlimited Company, Wilton Plaza, Wilton Place, Dublin 2, Irland.

Die Einstellungen zur Verarveitung von Datenschutz-relevanten Inhalten können hier bearbeitet werden: https://www.linkedin.com/psettings/guest-controls/retargeting-opt-out.

Die Datenübertragung in die USA wird auf die Standardvertragsklauseln der EU-Kommission gestützt. Details finden Sie hier: https://www.linkedin.com/legal/l/dpa und https://www.linkedin.com/legal/l/eu-sccs.

Details zu deren Umgang mit Ihren personenbezogenen Daten entnehmen Sie der Datenschutzerklärung von LinkedIn: https://www.linkedin.com/legal/privacy-policy.