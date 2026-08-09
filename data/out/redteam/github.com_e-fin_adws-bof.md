# https://github.com/e-fin/ADWS-BOF

[Skip to content](https://github.com/e-fin/ADWS-BOF#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/e-fin/ADWS-BOF) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/e-fin/ADWS-BOF) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/e-fin/ADWS-BOF) to refresh your session.Dismiss alert

{{ message }}

[e-fin](https://github.com/e-fin)/ **[ADWS-BOF](https://github.com/e-fin/ADWS-BOF)** Public

- [Notifications](https://github.com/login?return_to=%2Fe-fin%2FADWS-BOF) You must be signed in to change notification settings
- [Fork\\
3](https://github.com/login?return_to=%2Fe-fin%2FADWS-BOF)
- [Star\\
36](https://github.com/login?return_to=%2Fe-fin%2FADWS-BOF)


main

[**1** Branch](https://github.com/e-fin/ADWS-BOF/branches) [**0** Tags](https://github.com/e-fin/ADWS-BOF/tags)

[Go to Branches page](https://github.com/e-fin/ADWS-BOF/branches)[Go to Tags page](https://github.com/e-fin/ADWS-BOF/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>![author](https://github.githubassets.com/images/gravatars/gravatar-user-420.png?size=40)<br>Your Name<br>[removing unused code](https://github.com/e-fin/ADWS-BOF/commit/e6871acccb25f125ec55a233ae0012ba5be212b0)<br>2 months agoJun 12, 2026<br>[e6871ac](https://github.com/e-fin/ADWS-BOF/commit/e6871acccb25f125ec55a233ae0012ba5be212b0) · 2 months agoJun 12, 2026<br>## History<br>[13 Commits](https://github.com/e-fin/ADWS-BOF/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/e-fin/ADWS-BOF/commits/main/) 13 Commits |
| [ADWS-BOF](https://github.com/e-fin/ADWS-BOF/tree/main/ADWS-BOF "ADWS-BOF") | [ADWS-BOF](https://github.com/e-fin/ADWS-BOF/tree/main/ADWS-BOF "ADWS-BOF") | [removing unused code](https://github.com/e-fin/ADWS-BOF/commit/e6871acccb25f125ec55a233ae0012ba5be212b0 "removing unused code") | 2 months agoJun 12, 2026 |
| [.gitignore](https://github.com/e-fin/ADWS-BOF/blob/main/.gitignore ".gitignore") | [.gitignore](https://github.com/e-fin/ADWS-BOF/blob/main/.gitignore ".gitignore") | [remove unused code, update CNA, update .gitignore](https://github.com/e-fin/ADWS-BOF/commit/8abbff130ca674ccc0483bf989f46d103f11b8a2 "remove unused code, update CNA, update .gitignore") | 2 months agoJun 11, 2026 |
| [ADWS-BOF.sln](https://github.com/e-fin/ADWS-BOF/blob/main/ADWS-BOF.sln "ADWS-BOF.sln") | [ADWS-BOF.sln](https://github.com/e-fin/ADWS-BOF/blob/main/ADWS-BOF.sln "ADWS-BOF.sln") | [initialcommit](https://github.com/e-fin/ADWS-BOF/commit/1512e6b4564313b84bc4405f54d942a5f4e78e3d "initialcommit") | 2 months agoJun 5, 2026 |
| [LICENSE](https://github.com/e-fin/ADWS-BOF/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/e-fin/ADWS-BOF/blob/main/LICENSE "LICENSE") | [initialcommit](https://github.com/e-fin/ADWS-BOF/commit/1512e6b4564313b84bc4405f54d942a5f4e78e3d "initialcommit") | 2 months agoJun 5, 2026 |
| [README.md](https://github.com/e-fin/ADWS-BOF/blob/main/README.md "README.md") | [README.md](https://github.com/e-fin/ADWS-BOF/blob/main/README.md "README.md") | [update readme and cna](https://github.com/e-fin/ADWS-BOF/commit/d0de730481752190c36e7efe5b2b473db212e127 "update readme and cna") | 2 months agoJun 12, 2026 |
| [adws.cna](https://github.com/e-fin/ADWS-BOF/blob/main/adws.cna "adws.cna") | [adws.cna](https://github.com/e-fin/ADWS-BOF/blob/main/adws.cna "adws.cna") | [update readme and cna](https://github.com/e-fin/ADWS-BOF/commit/d0de730481752190c36e7efe5b2b473db212e127 "update readme and cna") | 2 months agoJun 12, 2026 |
| View all files |

## Repository files navigation

# ADWS LDAP Beacon Object File

[Permalink: ADWS LDAP Beacon Object File](https://github.com/e-fin/ADWS-BOF#adws-ldap-beacon-object-file)

This repository is for a beacon object file that allos operators to query LDAP using Active Directory Web Services (ADWS).

Currently it supports using the existing access token, in addition to accepting user supplied credentials.

Domain Controller IP is determined automatically, if it cant be found or can be reached, specify with `--ip`

Big shoutout to [https://github.com/ZakiPedio/BridgeHead/](https://github.com/ZakiPedio/BridgeHead/). Was working on my own C implementation for ADWS, but ZakiPedio released a C++ library which I used heavily when creating this C implementation that was compatible with BOFs.

This is still very much a work in progress, i have a list of things at the bottom im looking to add. PRs welcome.

## Usage

[Permalink: Usage](https://github.com/e-fin/ADWS-BOF#usage)

```
beacon> adwsldapsearch
[-] Usage:
	adwsldapsearch --ip 10.0.0.1 --domain example.com --username user --password password --query (objectClass=user) --attrs sAMAccountName,description --dn DC=lab,DC=local

	Arguments:
		--ip			IP address of server running ADWS, typically domain controller.
		--domain		Domain Name of the Domain you are querying.
		--username		(OPTIONAL)Username to use for authentication, use --domain to specify user domain.
		--password		(OPTIONAL) Password to use for authentication. (OPTIONAL)
		--query			LDAP Query, CNA handles spaces in arguments, dont need to use quotes.
		--attrs			(OPTIONAL)Attributes for LDAP query, provide none to choose *
		--dn            Search Base for the LDAP Query

	Notes:
		- Do not wrap any arguments in quotes.
		- Arguments can be placed in any order.
		- Providing no username or password will use current access token.
```

## Example Usage

[Permalink: Example Usage](https://github.com/e-fin/ADWS-BOF#example-usage)

#### Provided Credentials, attributes set to \*

[Permalink: Provided Credentials, attributes set to *](https://github.com/e-fin/ADWS-BOF#provided-credentials-attributes-set-to-)

```
[06/05 17:10:53] beacon> adwsldapsearch --ip 192.168.1.100 --domain lab.local --username administrator --password nicetry --query (&(objectClass=user)(memberOf:1.2.840.113556.1.4.1941:=CN=Domain Admins,CN=Users,DC=lab,DC=local)) --dn DC=lab,DC=local
[06/05 17:10:53] [+] host called home, sent: 105470 bytes
[06/05 17:10:53] [+] received output:
[*] Object 1
  logonCount                    : 50
  codePage                      : 0
  objectCategory                : CN=Person,CN=Schema,CN=Configuration,DC=lab,DC=local
  description                   : Built-in account for administering the computer/domain
  uSNChanged                    : 69677
  instanceType                  : 4
  name                          : Administrator
  badPasswordTime               : 134243686929634297
  pwdLastSet                    : 134176712944191294
  objectClass                   : top
  objectClass                   : person
  objectClass                   : organizationalPerson
  objectClass                   : user
  badPwdCount                   : 0
  sAMAccountType                : 805306368
  lastLogonTimestamp            : 134249737202264337
  uSNCreated                    : 8196
  objectGUID                    : {4B2E7F70-8614-4EB5-88ED-BDA213DEFA50}
  memberOf                      : CN=Group Policy Creator Owners,CN=Users,DC=lab,DC=local
  memberOf                      : CN=Domain Admins,CN=Users,DC=lab,DC=local
  memberOf                      : CN=Enterprise Admins,CN=Users,DC=lab,DC=local
  memberOf                      : CN=Schema Admins,CN=Users,DC=lab,DC=local
  memberOf                      : CN=Administrators,CN=Builtin,DC=lab,DC=local
  whenCreated                   : 20260311141845.0Z
  userAccountControl            : 66048
  cn                            : Administrator
  countryCode                   : 0
  primaryGroupID                : 513
  whenChanged                   : 20260603152200.0Z
  dSCorePropagationData         : 20260311143504.0Z
  dSCorePropagationData         : 20260311143504.0Z
  dSCorePropagationData         : 20260311141954.0Z
  dSCorePropagationData         : 16010101181216.0Z
  lastLogon                     : 134249766192554339
  distinguishedName             : CN=Administrator,CN=Users,DC=lab,DC=local
  adminCount                    : 1
  isCriticalSystemObject        : TRUE
  sAMAccountName                : Administrator
  objectSid                     : S-1-5-21-1063646002-3733688200-3763894859-500
  lastLogoff                    : 0
  accountExpires                : 9223372036854775807
  container-hierarchy-parent    : 32b63b29-6ec4-4d64-9c73-da0cc9e026a6
  relativeDistinguishedName     : CN=Administrator
  distinguishedName             : CN=Administrator,CN=Users,DC=lab,DC=local

[06/05 17:10:53] [+] received output:
[*] Object 2
  logonCount                    : 44
  codePage                      : 0
  objectCategory                : CN=Person,CN=Schema,CN=Configuration,DC=lab,DC=local
  dSCorePropagationData         : 20260423165034.0Z
  dSCorePropagationData         : 16010101000000.0Z
  uSNChanged                    : 66772
  instanceType                  : 4
  name                          : domainuser1
  badPasswordTime               : 134237718550978880
  pwdLastSet                    : 134177141599763086
  objectClass                   : top
  objectClass                   : person
  objectClass                   : organizationalPerson
  objectClass                   : user
  badPwdCount                   : 0
  sAMAccountType                : 805306368
  lastLogonTimestamp            : 134246849608723280
  uSNCreated                    : 16429
  objectGUID                    : {6DEB9A5E-3ADA-4E21-93FA-5F7DB6EFAA7B}
  memberOf                      : CN=Domain Admins,CN=Users,DC=lab,DC=local
  whenCreated                   : 20260311144919.0Z
  userAccountControl            : 66048
  cn                            : domainuser1
  countryCode                   : 0
  primaryGroupID                : 513
  whenChanged                   : 20260531070920.0Z
  lastLogon                     : 134248849202713069
  distinguishedName             : CN=domainuser1,CN=Users,DC=lab,DC=local
  adminCount                    : 1
  sAMAccountName                : domainuser1
  objectSid                     : S-1-5-21-1063646002-3733688200-3763894859-1106
  lastLogoff                    : 0
  displayName                   : domainuser1
  accountExpires                : 9223372036854775807
  userPrincipalName             : domainuser1@lab.local
  container-hierarchy-parent    : 32b63b29-6ec4-4d64-9c73-da0cc9e026a6
  relativeDistinguishedName     : CN=domainuser1
  distinguishedName             : CN=domainuser1,CN=Users,DC=lab,DC=local

[06/05 17:10:53] [+] received output:
[*] Object 3
  logonCount                    : 0
  codePage                      : 0
  objectCategory                : CN=Person,CN=Schema,CN=Configuration,DC=lab,DC=local
  dSCorePropagationData         : 20260603152410.0Z
  dSCorePropagationData         : 16010101000000.0Z
  uSNChanged                    : 69679
  instanceType                  : 4
  name                          : labadmin
  badPasswordTime               : 0
  pwdLastSet                    : 134249731714679835
  objectClass                   : top
  objectClass                   : person
  objectClass                   : organizationalPerson
  objectClass                   : user
  badPwdCount                   : 0
  sAMAccountType                : 805306368
  lastLogonTimestamp            : 134249732251991876
  uSNCreated                    : 69659
  objectGUID                    : {95A0188B-C2DC-4C73-8628-EA786216A967}
  memberOf                      : CN=Domain Admins,CN=Users,DC=lab,DC=local
  whenCreated                   : 20260603151251.0Z
  userAccountControl            : 66048
  cn                            : labadmin
  countryCode                   : 0
  primaryGroupID                : 513
  whenChanged                   : 20260603152410.0Z
  lastLogon                     : 0
  distinguishedName             : CN=labadmin,CN=Users,DC=lab,DC=local
  adminCount                    : 1
  sAMAccountName                : labadmin
  objectSid                     : S-1-5-21-1063646002-3733688200-3763894859-1111
  lastLogoff                    : 0
  displayName                   : labadmin
  accountExpires                : 9223372036854775807
  userPrincipalName             : labadmin@lab.local
  container-hierarchy-parent    : 32b63b29-6ec4-4d64-9c73-da0cc9e026a6
  relativeDistinguishedName     : CN=labadmin
  distinguishedName             : CN=labadmin,CN=Users,DC=lab,DC=local
```

#### No credentials (use current access token), specify attributes

[Permalink: No credentials (use current access token), specify attributes](https://github.com/e-fin/ADWS-BOF#no-credentials-use-current-access-token-specify-attributes)

```
[06/11 09:29:03] beacon> adwsldapsearch --ip 192.168.1.100 --domain lab.local --query (&(objectClass=user)(memberOf:1.2.840.113556.1.4.1941:=CN=Domain Admins,CN=Users,DC=lab,DC=local)) --dn DC=lab,DC=local --attrs samaccountname,objectsid
[06/11 09:29:03] [+] host called home, sent: 105814 bytes
[06/11 09:29:04] [+] received output:
[*] Object 1
  objectSid                     : S-1-5-21-1063646002-3733688200-3763894859-500
  sAMAccountName                : Administrator

[06/11 09:29:04] [+] received output:
[*] Object 2
  objectSid                     : S-1-5-21-1063646002-3733688200-3763894859-1106
  sAMAccountName                : domainuser1

[06/11 09:29:04] [+] received output:
[*] Object 3
  objectSid                     : S-1-5-21-1063646002-3733688200-3763894859-1111
  sAMAccountName                : labadmin
```

#### No credentials (use current access token), specify attributes, automatically resolve DC IP

[Permalink: No credentials (use current access token), specify attributes, automatically resolve DC IP](https://github.com/e-fin/ADWS-BOF#no-credentials-use-current-access-token-specify-attributes-automatically-resolve-dc-ip)

```
[06/12 12:34:21] beacon> adwsldapsearch  --domain lab.local --query (&(objectClass=user)(memberOf:1.2.840.113556.1.4.1941:=CN=Domain Admins,CN=Users,DC=lab,DC=local)) --dn DC=lab,DC=local --attrs samaccountname,objectsid
[06/12 12:34:21] [+] host called home, sent: 93472 bytes
[06/12 12:34:22] [+] received output:
[*] Object 1
  objectSid                     : S-1-5-21-1063646002-3733688200-3763894859-500
  sAMAccountName                : Administrator

[06/12 12:34:22] [+] received output:
[*] Object 2
  objectSid                     : S-1-5-21-1063646002-3733688200-3763894859-1106
  sAMAccountName                : domainuser1

[06/12 12:34:22] [+] received output:
[*] Object 3
  objectSid                     : S-1-5-21-1063646002-3733688200-3763894859-1111
  sAMAccountName                : labadmin
```

## TODO

[Permalink: TODO](https://github.com/e-fin/ADWS-BOF#todo)

- [x]  user specify dn
- [x]  Authenticate with current access token
- [x]  Auto resolve DC
- [ ]  Add feature to allow operator to specify \* in attributes with other attributes (example: \*,ntsecuritydescriptor)
- [ ]  Look into making output better
- [ ]  Create complimentary Python script to convert output into BH JSON for ingestion
- [ ]  Test and implement features like configuring RBCD, etc
- [ ]  Cleanup code

## About

Beacon Object File for LDAP Queries Through ADWS

### Resources

[Readme](https://github.com/e-fin/ADWS-BOF#readme-ov-file)

[Apache-2.0 license](https://github.com/e-fin/ADWS-BOF#Apache-2.0-1-ov-file)

[Activity](https://github.com/e-fin/ADWS-BOF/activity)

### Stars

**36** stars

### Watchers

**1** watching

### Forks

[**3** forks](https://github.com/e-fin/ADWS-BOF/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fe-fin%2FADWS-BOF&report=e-fin+%28user%29)

## Releases

## Packages

## Contributors

## Languages

You can’t perform that action at this time.