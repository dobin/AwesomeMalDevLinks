# https://ferib.dev/blog/EV-code-signing-with-pfx-in-2024/

[![A 'not so good lookin' pumpkin](https://ferib.dev/logo.png)](https://ferib.dev/)

For one to sign his own Microsoft Windows Drivers, he will need an EV Code Sign certificate. As AFAIK all these Extended Validation (EV) ones will require some sort of vetting and will only be handed out to actual organizations, and not persons.

## Setting up a shell company

Sure enough, setting up a small company isn't that big of a deal. It only costs a few thousand for initial investment capital, which can be immediatly used for notary and legal fees.

Once such a company is set up, it is time to shop for an EV Code Sign cert.

## Signing up for an EV Code Sign cert

As I was reading some of the documentation on the Microsoft Developer Network (MSDN) website, I saw a [list of recommended vendors](https://learn.microsoft.com/en-us/windows-hardware/drivers/dashboard/code-signing-reqs#where-to-get-code-signing-certificates) to get an EV Code Sign cert from.

I have no experience with code signing certs in general, but to me, it looked like they were all selling the same type of baloney. By just looking at the Google search results, I can see how crowded the results are with corporate blog posts and articles, all trying to sell you the same product.

Anyway, I am looking for _just_ the EV Code Sign cert, I have no interest in any special features or whatever. So I decided to go with the cheapest possible [recommendation from the list](https://learn.microsoft.com/en-us/windows-hardware/drivers/dashboard/code-signing-reqs#where-to-get-code-signing-certificates), GlobalSign. Just looking at their website, I can see they cut a lot of corners as I navigate the 2010-style web panels and make my way to the checkout.

![](https://ferib.dev/img/blog/pricing.webp)

I heard from other people there are cheaper options which are in the 100 ~ 150 price range. The more expansive ones are somewhere 500+ a year.

Looking back at this, I wish I took the cheapest option possible, regardless of what's on [the Microsoft recommendation list](https://learn.microsoft.com/en-us/windows-hardware/drivers/dashboard/code-signing-reqs#where-to-get-code-signing-certificates). I highly doubt I got any value for paying so much extra.

## The vetting process

Okay, I had to do this weird sales thing where I cannot buy the product directly, but instead, a special account is created for me as I wait for a 'salesperson' to reach out to me over email.

At this point, I just forgot \_(or couldn't be bothered)\_ to complete my purchase. About 4 months later I wanted to finish what I had started, but obviously, I forgot my password. Thanks to this 2010-styled website, automated password recovery doesn't seem to be a thing. A few days later everything worked out, and I finally paid the 339 EURO to complete the process.

![](https://ferib.dev/img/blog/certpickup_another_vetting.webp)

Next, I receive a new email from another company regarding my order. They requested some documents as part of the ID verification, I supplied those and was told to wait for further instructions. They then informed me they would call me in the next couple of days. So about a week or so later, I got a call from some non-native-speaking guy from, a crowded call center -- judging by the background noise -- asking the same question like five times as I had such a hard time making sense of what he was asking. I think they tried to pronounce my full name, to which I said "yes yes" and the call ended shortly after.

Cheers, 2 days later, a GlobalSign email arrives informing me that my certificate download is ready!

## Obtaining the certificate

Okay good, now all that's left to do is download a `.pfx` file and start signing?

![](https://ferib.dev/img/blog/certpickup_IE_compat_mode.webp)

Sure, let me google how to enable Internet Explorer Compatibility Mode in 2024, this shouldn't be hard.

![](https://ferib.dev/img/blog/globalsign_usb_token_disclaimer.webp)

USB Token? Eh, no?

This reminds me... after I completed the vetting, this Indian call center guy sent me an email requesting the following information:

![](https://ferib.dev/img/blog/email_usb_token_request.webp)

At this point in time, I assumed it was some malicious sales practice where they happily send you an eToken if you didn't have one already, just to send you an absurd invoice afterwards. So I refused to get a stupid enterprise eToken from a shady Indian guy...

Spoiler alert, I was wrong... the eToken was included in the price. I reached out to my 'salesperson' guy over email, and he confirmed this eToken was included, even the shipping was included!

## Obtainig my eToken

Okay, let me reply to that one email with the requested information so I can get my eToken. Just a few more weeks of waiting, and it arrived at my door.

Along with the eTokens comes of course the bloatware. I installed this SafeNet Authentication Client aka SACTools as I set up the eToken, but I could immediatly see my system being bloated with whatever corporate crap that is.

A new process named 'SACMonitor.exe' is running in the background, new tray icons are showing up, and new startup processes `SACMonitor.exe` was added so it runs whenever I reboot my device...

Shame! Closed-source crapware bloating my device is a no-go. I quickly uninstalled the tools and started looking for an alternative.

## Buying a better USB Token

Looking back at the certificate pickup website, I was prompted with 2 options. I either use the Fortify app or Internet Explorer (compatible) browser. I decided that I already had enough bloatware on my Windows machine, so installing enterprise apps like this was a no-go.

Anyway, what I wanted to show was this little checkbox on the bottom. It forced me to check it, which meant I was forced to use a FIPS140-2 compatible device.

!\[fortify\](Fortify\_browser\_pickup.webp"/>


### Shopping for a FIPS-compatible Yubikey

Browsing the Yubcio I noticed the following product matching what I need. It even has NFC support, how neat, can sign my drivers without even plugging it in? 🤣

![](https://ferib.dev/img/blog/yubikey_FIPS_compatible.webp)

I also found this other product, which looks pretty interesting, but the price point is a bit far away from my budget.

![](https://ferib.dev/img/blog/yubikey_FIPS_compatible_HSM.webp)

Anyway, before I buy the 85 EURO YubiKey I better make sure that these devices can be used for code signing as I have only seen people use them for 2FA and such.

I was also informed that RSA 4096-bit keys must be used for the EV Code Sign certs, so I also made sure this was a thing by checking the specifications of the device.

![](https://ferib.dev/img/blog/yubikey_FIPS_standards.png)

As well as looking at the community to see if this was a valid solution.

![](https://ferib.dev/img/blog/yubico_2048_max_key.webp)

## Setting up the YubiKey

After confidently completing the purchase, I waited about a week for it to arrive. Once it arrived, I couldn't wait to set it up and install the fancy GUI it came with

![](https://ferib.dev/img/blog/yubico_sig_options.webp)

It took me a couple of minutes, just to get disapointed as I tried to generate my first 'Digital Signature' keys.

![](https://ferib.dev/img/blog/yubico_sig_algo_options.webp)

The limited selection of the algorithms doesn't include `RSA4096`, it seems that `RSA2048` is the highest option available.

So I ended up doing some research and found the CLI tool for YubiKeys. I set up this `ykman` tool and used the CLI to generate a key with algorithm `RSA4096`, but I am once again greeted with that same list from the GUI, which is missing the option I want.

![](https://ferib.dev/img/blog/ykman_try_gen_RSA4096.webp)

In my last attempt, I generated a 4096-bit RSA key myself and figured I might be able to import it into Yubikey using the CLI. But no, I once again faced disappointment.

![](https://ferib.dev/img/blog/ykman_try_import_RSA4096.webp)

## Back to the eToken

Okay, it's been a few weeks now... what was the password again for my eToken? Ah yes, I wrote it down, did I?

_\*Enters PIN wrong 3 times\*_

Shit, did I fatfinger the pin like 3 times in a row? Oh well, let me grab that admin password.

_\*Enters Admin Password wrong 4 times\*_

![](https://ferib.dev/img/blog/eToken_attempts_remaining.webp)

Oh shit, that pin and password I wrote down? Yeah, that was for my Yubikey, NOT my crappy eToken... But wait, come to think of it, I never set a password for the eToken!

Okay, then it must still be using the default password? Sure, let me look up the manual for that eToken.

![](https://ferib.dev/img/blog/eToken_docs_default_pin.webp)

Lovely, the default _"administrator password must be entered using 48 hexadecimal zeros (24 binary zeros)."_. Wait what? I have exactly 1 attempt left, how do I enter 48 hexadecimal zeros?

Do I format 48 zeros with a whitespace, like this `00 00 00 ...`? or maybe `0 0 0 ...`? or should I prefix em `0x00 0x00 0x00 ...`? or do I drop whitespaces like so `000...` or do I need to enter a double 00's for every 0 like `000000...`?

I am baffled, so I asked ChatGPT's opinion.

![](https://ferib.dev/img/blog/eToken_ask_chatGPT_opinion.webp)

Okay, let me just blatantly copy-paste the zeros from the 'Hexadecimal Format', paste them at the login prompt, and hope for the best?

![](https://ferib.dev/img/blog/eToken_admin_password.webp)

Well... it didn't work and my eToken is now locked 😅

## Unlocking my eToken

Okay... time to email support and ask how I can reset the eToken?

After a few days, I get a phone call -- in the middle of the day during actual work -- and I'm asked to join another call on MS Teams as I'm asked to share my screen. I tell the woman on the phone I have no headphones or mic available on my device, and ask her to keep talking over the phone. I then join the MS Teams calls, and she ends the phone call...

After a good 10 minutes of looking for headphones and an external microphone around the house, I managed to talk to the support woman using my desktop device.

### The Support Call

Long story short, I was told to navigate the bloatware and do "Initialize Token...", but this option was disabled in the GUI as my eToken was already initialized. She told me to downgrade my SACTools, restart the device, and try again.

![](https://ferib.dev/img/blog/SACTools_downgraded.webp)

Oh look, the "Initialize Token..." became visible after removing 10.8 and installing version 10.7. But once I click this, the application just closes and nothing happened...

After like half an hour of support with screen share, she suggested that I should buy a new eToken as she concluded there was no way possible to recover this.

Sure, I said I'll talk this over with my financial department -- trying not to laugh out loud as I tell her -- and exit the Teams call. Out of curiosity I opened x64dbg and attached the debugger to the SACTools.exe to see why it is closing. After clicking the "Initialize Token..." I see x64dbg caught an exception.

![](https://ferib.dev/img/blog/SACTools_stackoverflow_old_version.webp)

And no surprise, that the application is having some sort of unrecoverable bug happening. Most likely it was never intended to click this option when the device is in this specific state, which is most likely why this action is disabled on the later version of 10.8.

## The Reverse Engineering lifestyle

Okay, at this point, I am already poking at binaries and reversing them, so I might as well go down the rabbit hole and figure out exactly how this eToken was supposed to work.

With the loss of my eToken, I won't waste any more time on reversing the SAC tools/drivers/binaries and instead will focus on the certification pickup website. There must be some way to spoof or emulate the presence of the eToken, and send off my own DIY CSR to the remote server. I even doubt the eToken is performing cryptographic computations related to the key generation, and I assume most of it happens in either an Internet Explorer-compatible browser or whatever this 'Fortify app' is.

### Reversing the Legacy IE JavaScript

Okay, I am running the Edge browser -- you know, that thing no one uses yet Microsoft is forcing it onto their users -- which, no surprise, is the only way to have Internet Explorer Legacy Compatibility mode.

To make things worse, this thing doesn't have devtools like Element Inspection, Network Inspection, or a JS Console. To see the network traffic I would use `mitmproxy` and intercept HTML and JS files, as well as take note of requests being made.

![](https://ferib.dev/img/blog/mitm_pickup_software.webp)

I don't see too much going on here, this is most likely because of the old 2010-style website. The website is a good old html using `<form>` tags and `<input>` fields. They only seem to use JavaScript for very specific things like eToken and cryptographic (legacy) APIs.

To learn a bit more about the expected workflow of the website, I use my 'broken' eToken. The website still picks it up -- that is, after installing some bloatware drivers -- and can be used to send valid requests to the server. None of these requests will complete -- and therefore won't consume my pickup cert -- as my 'broken' eToken is causing the below error:

![](https://ferib.dev/img/blog/eToken_pickup_error_spoof_results.webp)

### Extract source code

I look at the `mitmproxy` requests and dump all `.js` files to disk so I can properly look at them. The code below -- which has Chinese comments, lol -- seems to be invoking cryptographic operations to generate things.

![](https://ferib.dev/img/blog/certpickup_js_KeySpec.webp)![](https://ferib.dev/img/blog/certpickup_js_RE_CreateRequest.webp)

I decided to also dump the `.html` files to disk and then found this gem.

![](https://ferib.dev/img/blog/certpickup_js_hidden_forum_fields.webp)

It seems to contain a series of `type="hidden"` fields which were pre-defined by the attestation/pickup server. The `keyLength` is already set to `4096`. The `commonName` aka `CN` is set to something that appears to be my account identifier. The last important one is the `token` field, which seems to be some sort of temporary password for the certificate pickup.

### Generating my own CSR

Okay, I think I have enough knowledge to create my own keys and CSR to fool the attestation server!

I rush to my trashcan and take out the Yubikey from months ago as I need it back to follow all the steps in this [CSR attestation with yubikey manager guide](https://virot.eu/csr-attestation-with-yubikey-manager/). I learned that the Yubikey cannot have 4096-bit RSA, but now that I am in control of these hidden input fields, I might be able to change the bit size.

These are the commands used on `ykman` to set up an RSA 2048-bit key.

```
& 'C:\Program Files\Yubico\YubiKey Manager\ykman.exe' piv reset -f
& 'C:\Program Files\Yubico\YubiKey Manager\ykman.exe' piv keys generate --pin-policy ONCE --touch-policy CACHED --algorithm RSA2048 --management-key 010203040506070801020304050607080102030405060708 9a "$($env:TEMP)\junkfile"
& 'C:\Program Files\Yubico\YubiKey Manager\ykman.exe' piv certificates generate -s "CN=Selfsigned" --pin 123456 --management-key 010203040506070801020304050607080102030405060708 9a "$($env:TEMP)\junkfile"
& 'C:\Program Files\Yubico\YubiKey Manager\ykman.exe' piv objects generate --management-key 010203040506070801020304050607080102030405060708 chuid
& 'C:\Program Files\Yubico\YubiKey Manager\ykman.exe' piv certificates  export f9  "$($env:TEMP)\yubico_intermediate.cer"
& 'C:\Program Files\Yubico\YubiKey Manager\ykman.exe' piv keys attest 9a "$($env:TEMP)\yubico_attestation.cer"
```

The only thing I have changed here is the `"CN=Selfsigned"` to match the `CN` value from the `"commonName"` hidden input field. I then proceed to build the Certificate Signing Request (CSR) and export it as base64.

### Injecting my DIY CSR

Now, weaponized with a self-made CSR, I can start thinking of a way to inject this into the form post. I will be using `mitmdump -s proxy.py` with the below `proxy.py`.

```
class FeribProxy(object):
	def __init__(self):
		pass
	def response(self, flow):
		url = flow.request.url
		if "enroll_on_vista2.js" in url:
			flow.response.text = open("enroll_on_vista2.js", 'r').read()

addons = [\
	FeribProxy()\
]
```

The above Python script will look for a file named `enroll_on_vista2.js` and replace it with our malicious `enroll_on_vista2.js` file as seen below.

```
<script style="display:block">
$(document).ready(function() {
	let v = document.getElementById("pkcs10");
	v.type='test'

	let b = document.getElementById("nextButton");
	b.onclick = '';

	alert('ok')
})
</script>
add enroll_on_vista2.js
```

This file will inject this `<script style="display: block">` tag. Notice how we inject a `<script>` tag which has this `"display:block"` style property set. This means that the element is actually made visible on the website itself.

![](https://ferib.dev/img/blog/mitmdump_certpickup_injected_web_code.webp)

It's rather annoying to not have any sort of devtools on this IE Compatible browser, so having this visual feedback of the script being injected helps so much.

Now that we have working inputs on the website, I will do a quick test and simply set the hidden `pkcs10` field to `"test"` and press the submit button.

![](https://ferib.dev/img/blog/certpickup_spoof_CSR_error.webp)

Yay, I am under the assumption that this generic obscure error message indicates some completely unexpected error has happened. Most likely as it was unable to parse the expected pkcs10.

Okay, now I just force 2048 bit like so

```
let v = document.getElementById("keyLength");
v.type='2048'

```

I make the change, I see my `<script>` content changed on the webpage, and with full confidence I click submit!

![](https://ferib.dev/img/blog/certpickup_4096_bit_required.webp)

Sad...

### Generating a CSR on disk

Okay.. threw my Yubikey across the room and finally gave up on Yubikeys. I will be using `openssl` cli commands like a normal person. Nothing new here, I follow the steps from some random article and make sure to set my `CN` correctly.

Okay, exported it to pkcs10 and pasted it into my script, hit submit, and this happened.

![](https://ferib.dev/img/blog/certpickup_installcert_mitm_post.webp)

Yay? my Certificate has been generated? But I still have an error message?

### Recovering the pkcs7 response

Okay, still surprised that it got accepted, but I have bigger things to worry about now. My pickup token is consumed and the response key is most likely in my Edge.exe process, somewhere in the RAM memory? I would also assume it to be some sort of base64 encoded string?

Did my `mitmproxy` log anything? Of course not, I'm running `mitmdump` with this custom script.

Okay, no panic, let's revisit my collection of `.js` files and figure out what error code that is.

![](https://ferib.dev/img/blog/certpickup_js_errorcode_re.webp)

There is our error code, so who is calling this `_AcceptP7` function? And what's the meaning of this Chinese comment?

![](https://ferib.dev/img/blog/IECM_pickup_pkcs.webp)

Chinese comments seem useless, so I Ctrl+F and find something calling `AcceptP7`?

![](https://ferib.dev/img/blog/certpickup_js_input_pkcs7.webp)

I look around and see `installPkcs7IEWithUntrustedRoot()` which calls `document.getElementByName("pkcs7")`. This `"pkcs7"` must be one of the _(hidden?)_ response fields given by the webserver?

I am desperate here, so I attach CheatEngine to Edge.exe, I scan the process memory for string `"pkcs7"` to hope and find some sort of JS/HTML code.

![](https://ferib.dev/img/blog/certpickup_ce_search_string_pkcs7.png)

As I looked for bronze, I found gold! Thanks to the oldschool response of the webserver, I found this hidden input containing the pkcs7.

![](https://ferib.dev/img/blog/certpickup_completed.webp)

Finally, I use `openssl` once more and convert my pkcs7 file into a `.pfx` file 🤩

## Let's Sign Something!

![](https://ferib.dev/img/blog/binsig_test_ok.png)

Tada! Countless hours of frustration, support, emailing, vetting, reversing, debugging, and a whole lot of other bullshit, along with the cost of a useless eToken and Yubikey devices.

Finally, I can move on to the next step: requesting vetting for Microsoft Driver Signing 🙃