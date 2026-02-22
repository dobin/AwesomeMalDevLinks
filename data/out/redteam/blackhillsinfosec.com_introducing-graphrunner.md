# https://www.blackhillsinfosec.com/introducing-graphrunner/

[Join us at Wild West Hackin' Fest @ Mile High in Denver for Training, Community, and Fun!](https://wildwesthackinfest.com/wild-west-hackin-fest-mile-high-2026/)

19Oct2023

[Beau Bullock](https://www.blackhillsinfosec.com/category/author/beau-bullock/), [How-To](https://www.blackhillsinfosec.com/category/how-to/), [Red Team](https://www.blackhillsinfosec.com/category/red-team/), [Red Team Tools](https://www.blackhillsinfosec.com/category/red-team/tool-red-team/), [Steve Borosh](https://www.blackhillsinfosec.com/category/author/steve-borosh/)[Azure](https://www.blackhillsinfosec.com/tag/azure/), [cloud](https://www.blackhillsinfosec.com/tag/cloud/), [microsoft365](https://www.blackhillsinfosec.com/tag/microsoft365-2/)

# [Introducing GraphRunner: A Post-Exploitation Toolset for Microsoft 365](https://www.blackhillsinfosec.com/introducing-graphrunner/)

By [Beau Bullock](https://www.blackhillsinfosec.com/team/beau-bullock/) & [Steve Borosh](https://www.blackhillsinfosec.com/team/stephan-borosh/)

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled.jpeg)

## TL;DR

We built a post-compromise toolset called [GraphRunner](https://github.com/dafthack/GraphRunner/) for interacting with the Microsoft Graph API. It provides various tools for performing reconnaissance, persistence, and pillaging of data from a Microsoft Entra ID (Azure AD) account. Below are some of the main features. At the end of the blog post, make sure to take a peek at the potential attack path scenarios we have laid out. There are a few in there we think may be quite interesting to both offensive and defensive security team members.

### **Main Features:**

- Search and export email
- Search and export SharePoint and OneDrive files accessible to a user
- Search all Teams chats and channels visible to the user and export full conversations
- Deploy malicious apps
- Discover misconfigured mailboxes that are exposed
- Clone security groups to carry out watering hole attacks
- Find groups that can be modified directly by your user or where membership rules can be abused to gain access
- Search all user attributes for specific terms
- Leverage a GUI built on the Graph API to pillage a user’s account
- Dump conditional access policies
- Dump app registrations and external apps including consent and scope to identify potentially malicious apps
- Tools to complete OAuth flow during consent grant attacks
- Continuously refresh your token package
- GraphRunner doesn’t rely on any third-party libraries or modules
- Works with Windows and Linux

You can find GraphRunner here: [https://github.com/dafthack/GraphRunner/](https://github.com/dafthack/GraphRunner/)

## The Graph API

The Microsoft Graph API is undeniably one of the most important pieces of infrastructure to enable Microsoft cloud services to function. Everything from Outlook to SharePoint to Teams to Entra ID rely on this API. Most of the time when you are interacting with Microsoft services, you never visually see the Graph API but, under the hood, it is constantly being utilized. There are PowerShell modules that use it, such as the MSOnline or AzureAD modules. The AZ command line tool (az cli) also uses it. As an administrator, the Graph API is a very powerful tool for carrying out tasks in Azure.

But what about as a normal user?

During penetration tests, red team engagements, cloud assessments, and other offensive security assessments, there are often times where we obtain access to an M365 user’s account. This could be due to various attacks such as password spraying or phishing being successful. Through a web browser, we may be able to access certain resources like email and file sharing services. But there are many other data points that can be collected from a Microsoft tenant besides email and files. The Azure (Entra) Portal is a good place to start, but it can easily be locked down so that only administrative users can utilize it.

Luckily, access to the Graph API is necessary for much of Microsoft 365 to function. Even when access to the Azure Portal is blocked, most of the same data can be accessed via the API and, in some cases, interacted with. Through performing offensive engagements, we have found ourselves in this situation many times. In exploring what the API has to offer, through real-world engagements as well as R&D sessions, a toolset began to be developed internally at BHIS.

In this blog post, you will find a thorough description of each piece of the toolset we are releasing. Additionally, we present several attack path scenarios to demonstrate situations where you may find this toolset useful. Some of these attack paths may be familiar while others may not. Our goal in releasing this toolset is primarily to provide offensive operators the tools they need to quickly identify security issues in Microsoft cloud environments. But this tool can also be leveraged by defenders to preemptively identify security issues and mitigate them.

Now, let’s dive into what **GraphRunner** is all about.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Picture1.jpg)

There are three main pieces to GraphRunner:

- **GraphRunner.ps1 –** A PowerShell script containing a number of modules for post-compromise recon, persistence, and pillaging of an account.
- **GraphRunnerGUI.html** – An HTML graphic user interface to be used with an access token. Provides various modules around enumeration and pillaging data from services such as Outlook, SharePoint, OneDrive, and Teams.
- **PHPRedirector**-A basic PHP script that can be used to capture OAuth authorization codes during an OAuth consent flow and a Python script to automatically complete the flow to obtain access tokens.

## GraphRunner PowerShell

GraphRunner includes a PowerShell set of tools to assist with carrying out various attacks during post-exploitation of a Microsoft Entra ID (Azure AD) tenant. Most of the modules rely on having authenticated access tokens. To assist with this, there are multiple modules for obtaining and working with both user and application (service principal) tokens. The majority of modules don’t require a privileged account.

To get started, import GraphRunner into a new PowerShell session.

```
Import-Module .\GraphRunner.ps1
```

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-21.png)

Here’s a high-level summary of each module included in the PowerShell script:

**Authentication**

- **Get-GraphTokens**– Authenticate as a user to Microsoft Graph
- **Invoke-RefreshGraphTokens** – Use a refresh token to obtain new access tokens
- **Get-AzureAppTokens** – Complete OAuth flow as an app to obtain access tokens
- **Invoke-RefreshAzureAppTokens** – Use a refresh token and app credentials to refresh a token
- I **nvoke-AutoTokenRefresh** – Refresh tokens at an interval

**Recon & Enumeration Modules**

- **Invoke-GraphRecon** – Performs general recon for org info, user settings, directory sync settings, etc.
- **Invoke-DumpCAPS** – Gets conditional access policies
- **Invoke-DumpApps** – Gets app registrations and external enterprise apps, along with consent and scope info
- **Get-AzureADUsers** – Gets user directory
- **Get-SecurityGroups** – Gets security groups and members
- **Get-UpdatableGroups** – Gets groups that may be able to be modified by the current user
- **Get-DynamicGroups** – Finds dynamic groups and displays membership rules
- **Get-SharePointSiteURLs**– Gets a list of SharePoint site URLs visible to the current user
- **Invoke-GraphOpenInboxFinder** – Checks each user’s inbox in a list to see if they are readable
- **Get-TenantID** – Retrieves the tenant GUID from the domain name

**Persistence Modules**

- **Invoke-InjectOAuthApp** – Injects an app registration into the tenant
- **Invoke-SecurityGroupCloner** – Clones a security group while using an identical name and member list but can inject another user as well
- **Invoke-InviteGuest** – Invites a guest user to the tenant
- **Invoke-AddGroupMember** – Adds a member to a group

**Pillage Modules**

- **Invoke-SearchSharePointAndOneDrive** – Search across all SharePoint sites and OneDrive drives visible to the user
- **Invoke-ImmersiveFileReader**– Open restricted files with the immersive reader
- **Invoke-SearchMailbox** – Has the ability to do deep searches across a user’s mailbox and can export messages
- **Invoke-SearchTeams** – Can search all Teams messages in all channels that are readable by the current user
- **Invoke-SearchUserAttributes** – Search for terms across all user attributes in a directory
- **Get-Inbox** – Gets the latest inbox items from a mailbox and can be used to read other user mailboxes (shared)
- **Get-TeamsChat** – Downloads full Teams chat conversations

**Invoke-GraphRunner Module**

- **Invoke-GraphRunner** – Runs Invoke-GraphRecon, Get-AzureADUsers, Get-SecurityGroups, Invoke-DumpCAPS, Invoke-DumpApps, and then uses the default\_detectors.json file to search with Invoke-SearchMailbox, Invoke-SearchSharePointAndOneDrive, and Invoke-SearchTeams.

**Supplemental Modules**

- **Invoke-AutoOAuthFlow**– Automates the OAuth flow completion to obtain access and refresh keys when a user grants consent to an app registration
- **Invoke-DeleteOAuthApp** – Delete an OAuth App
- **Invoke-DeleteGroup** – Delete a group
- **Invoke-RemoveGroupMember** – Module for removing users/members from groups
- **Invoke-DriveFileDownload** – Has the ability to download single files from SharePoint and OneDrive as the current user
- **Invoke-CheckAccess** – Check if tokens are valid
- **Invoke-HTTPServer** – A basic web server to use for accessing the emailviewer that is output from Invoke-SearchMailbox
- **Invoke-BruteClientIDAccess**– Test different client\_id’s against MSGraph to determine permissions
- **Invoke-ImportTokens** – Import tokens from other tools for use in GraphRunner
- **Get-UserObjectID** – Retrieves an Object ID for a user

### Authentication

A good place to start is to authenticate with the **Get-GraphTokens** module. This module will launch a device-code login, allowing you to authenticate the PowerShell session from a browser session. Access and refresh tokens will be written to the global $tokens variable and your tenant ID will be written to the $tenantid variable. To use them with other GraphRunner modules use the Tokens flag (Example: Invoke-DumpApps -Tokens $tokens).

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-1.png)

Enter the code at [microsoft.com/devicelogin](http://microsoft.com/devicelogin) to authenticate your session.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-2.png)

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-3.png)

Access tokens typically have an expiration time of one hour so it will be necessary to refresh them occasionally. If you have already run the Get-GraphTokens command, your refresh tokens will be utilized from the $tokens variable automatically when you run **Invoke-RefreshGraphTokens** to obtain a new set of tokens.

GraphRunner also includes modules for authenticating as a service principal. This can be useful for leveraging an app registration (as detailed later in the Persistence section in this blog post). The **Get-AzureAppTokens** module can assist with completing an OAuth flow to obtain access tokens for an Azure App Registration. After obtaining an authorization code, it can be utilized with a set of app registration credentials (client id and secret) to complete the flow.

### Recon & Enumeration

GraphRunner includes a number of reconnaissance modules to determine configuration settings, list objects, and identify attack paths in a tenant. The **Invoke-GraphRecon** module gathers general information about the tenant including the primary contact info, directory sync settings, and user settings such as if users have the ability to create apps, create groups, or consent to apps. The primary contact information for the tenant is displayed along with directory sync settings, and user settings.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-4.png)![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-5.png)

The authorization policy section includes configuration settings such as if users can read their own Bitlocker keys, who can invite external users, if MSOL PowerShell is blocked, and more.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-6.png)

The Invoke-GraphRecon module also has a switch called “PermissionEnum”. If this switch is set, it will use an undocumented “Estimate Access” API to brute force a list of almost 400 actions (permissions reference: [https://learn.microsoft.com/en-us/azure/active-directory/roles/permissions-reference](https://learn.microsoft.com/en-us/azure/active-directory/roles/permissions-reference)) to determine what actions the current user is allowed to do. This is useful for discovering what unique actions your user is able to perform in the tenant. Additionally, when we get into the group editing section later in the blog post, this method is useful for helping determine what access may have changed.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-7.png)

The **Invoke-DumpCAPS** module dumps conditional access policies from a tenant. This module uses the legacy Azure Active Directory Graph API (graph.windows.net) to pull the policies.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-8.png)

A module detailed later in this blog post around injecting app registrations (Invoke-InjectOAuthApp) spurred the creation of the **Invoke-DumpApps** module. This module can assist in identifying malicious app registrations. It will dump a list of Azure app registrations from the tenant, including permission scopes and users that have consented to the apps. Additionally, it will list external apps that are not owned by the current tenant or by Microsoft’s main app tenant. This is a way to find third-party external apps that users may have consented to.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-9.png)![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-10.png)

The **Get-AzureADUsers** and **Get-SecurityGroups** modules can be used to dump users and groups from the tenant.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-11.png)

Group-based attacks are one of the more interesting areas to highlight when it comes to GraphRunner’s capabilities. Our first use-case for attacking M365 groups involves changing group membership of certain groups, even as a non-administrative user. For example, GraphRunner has modules that help in exploiting the fact that **the default behavior for Microsoft 365 groups is that anyone in the organization can join them**. Whenever a team is created, so is a Microsoft 365 group. With that comes the automatic creation of a SharePoint site, a mailbox, Teams channel, and more.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-12.png)[https://learn.microsoft.com/en-us/azure/active-directory/enterprise-users/groups-self-service-management](https://learn.microsoft.com/en-us/azure/active-directory/enterprise-users/groups-self-service-management)

As detailed in Microsoft’s documentation (screenshot below), the default behavior for Microsoft 365 groups makes them open for all to join. Also, note that in some scenarios, security groups can be configured to be joinable as well.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-13.png)[https://learn.microsoft.com/en-us/microsoftteams/office-365-groups](https://learn.microsoft.com/en-us/microsoftteams/office-365-groups)

This is where the **Get-UpdatableGroups** module comes in. This module also leverages the “Estimate Access” API to determine if your current user has the ability to update groups in the tenant. It will gather all groups from the tenant and check them one by one to determine if they are modifiable.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-14.png)

If you find modifiable groups, that means that your current user has the ability to add members to that group, including yourself, other tenant members, and even guests. This can lead to privilege escalation scenarios as we demonstrate in the attack paths section later in the post.

On a similar topic, “dynamic groups” are another interesting attack path in Microsoft 365. Dynamic groups are groups that are created with dynamic group membership rules. When created, dynamic groups are configured with a set of rules that automatically process objects into groups with certain attributes. These groups can include various parameters such as the user’s email, location, job title, device, and more. They can help to automatically add users to groups but when misconfigured can be abused by attackers.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-15.png)

In the example above, this dynamic group is configured to add any users whose user principal name contains the word “admin”. This scenario can be exploited by simply inviting a guest user to the tenant with an email address that contains “admin” in it. Upon being added as a guest to the tenant, the account with “admin” in the name would automatically get added to the dynamic group.

GraphRunner helps in finding dynamic groups with the **Get-DynamicGroups** module. After listing out dynamic groups in a tenant, it would be necessary to analyze the membership rules to determine the potential for exploitability.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-16.png)

The **Get-SharePointSiteURLs** module goes hand-in-hand with the groups modules mentioned previously. It uses the Graph Search API to try to locate all unique sites the user has access to. It can be useful to run both prior to and after performing any group-based abuse to determine what new sites you have gained access to.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-17.png)

In 2017, I (Beau) [wrote a post](https://www.blackhillsinfosec.com/abusing-exchange-mailbox-permissions-mailsniper/) about abusing Exchange mailbox permissions. Back then, I wrote a module called Invoke-OpenInboxFinder for [MailSniper](https://github.com/dafthack/MailSniper) that assisted in finding mailboxes that were configured so that other users in the organization could access them. That module leveraged Exchange Web Services and Outlook Web Access. It turns out that the same type of mailbox enumeration can be performed via the Microsoft Graph API. GraphRunner has the **Invoke-GraphOpenInboxFinder** module to carry out this task.

In order for this to work, you will need a token that is scoped to the Mail.Read.Shared permission or the Mail.ReadWrite.Shared permission. This can be accomplished by consenting to an application with this scoped permission. One quick and easy way to do this is to leverage the Graph Explorer. It is a well-known application for testing out Graph API calls and you can consent to specific permissions here: [https://developer.microsoft.com/en-us/graph/graph-explorer](https://developer.microsoft.com/en-us/graph/graph-explorer). After consenting, you can click the “Access token” tab to view your token and then set it to the $tokens.access\_token variable in your GraphRunner session.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-18-1024x478.png)

Now running the Invoke-GraphOpenInboxFinder module against a userlist will attempt to access each inbox from the provided list. If a user has set their inbox permissions too widely, it’s possible your current user may be able to read messages from their inbox.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-19.png)

## Persistence

When it comes to maintaining access, GraphRunner has a few modules that can help to establish various levels of persistence in a tenant. Deploying an application to a tenant is interesting in multiple scenarios. By default, users can create applications. But, by default, they cannot add administrative privileges such as Directory.ReadWrite.All. They can, however, add a number of delegated privileges that do not require admin consent by default. Most of these privileges that do not require admin consent are for performing common tasks such as reading email (Mail.Read), listing users in the directory (User.ReadBasic.All), navigating SharePoint and OneDrive (Files.ReadWrite.All and Sites.ReadWrite.All), and many more.

By deploying an app with these permissions and then consenting to it as a user we have compromised, we can then leverage the service principal credentials tied to the application to access the user’s account. If the compromised user changes their password, the app still retains access to their account. If all sessions are killed for the compromised user, we still have access until the access token expires (default is 1 hour) to operate as the user.

The **Invoke-InjectOAuthApp** module is a tool for automating the deployment of an app registration to a Microsoft tenant. In the event that the Azure portal is locked down, this may provide an additional mechanism for app deployment, provided that users are allowed to register apps in the tenant.

This module has a few hardcoded scope settings for quick deployment of certain types of apps, but custom values can be entered as well. For example, when setting the -scope parameter to “op backdoor”, the tool will create an app and add a large number of common permissions to it, including access to Mail, Files, Teams, and more. None of these permissions require admin consent.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-20.png)

After the app is deployed, the consent URL is automatically generated and displayed in the terminal (in green above). This URL is custom and tied to the specific app registration, including all of the requested scope items. When a user visits this URL, they will be asked to consent to the permissions set for the app.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-22-396x1024.png)

A few years ago, this was leveraged heavily by attackers carrying out illicit consent grant phishing attacks. Microsoft made some changes that effectively limited what an external, unverified app could request access to for users not in the same tenant. When an app is deployed in the same tenant as the victim being phished, this is not the case. Later in the attack paths section, an internal app-based phishing scenario is laid out. But in terms of persistence, we would be visiting this link as our compromised user and consenting to it ourselves.

When an application with delegated permissions is consented to, we need to catch the OAuth code that is sent to the specified redirect URI in order to complete the flow and obtain access tokens. GraphRunner has multiple ways built-in to catch and complete the OAuth flow once consent has been granted. In situations where the user is remote, you would most likely want to stand up a web server and use something like the basic PHP redirector included in the GraphRunner repo to capture the code and complete the flow.

If we are creating persistence within an account we control, it’s possible to complete this flow by directing the browser to localhost. The **Invoke-AutoOAuthFlow** module stands up a minimal web server to listen for this request and completes the OAuth flow with the provided app registration credentials. When a “localhost” URL such as “http://localhost:8000” is set as the ReplyURL with Invoke-InjectOAuthApp, it will automatically detect it and ouput the exact command needed to run in another terminal to catch and complete the flow.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-1-1.png)

Prior to navigating to the consent URL and clicking consent, run the command that was output in another terminal. It will listen for requests to it containing the OAuth code and automatically complete the flow using the service principal’s credentials. Upon successfully completing the flow, it will output a new set of access tokens, as well as write them to the global $apptokens variable in the terminal. Now when you run GraphRunner modules, you can specify the app tokens (-Tokens $apptokens) and it will run in the context of the application leveraging the delegated permissions consented to in the user account.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-2-1.png)

Another potentially interesting attack vector via groups would be to create groups in an attempt to exploit watering hole-style attacks. In this scenario, an attacker would create a group to resemble another group that already exists but include their own user within it. When applying permissions to a group via the Azure Portal, the Microsoft Admin portal, SharePoint sites, and other locations, it’s not always clear exactly what group a policy is being applied to. For example, when applying a role to a resource in the Azure Portal — such as when a user is granted permissions to read, contribute, or own a resource — only the name of the group or user is displayed. No other identifiable information about the group is provided here.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-3-1.png)

GraphRunner has a module called **Invoke-SecurityGroupCloner** that automates the ability to clone a group while adding your user or another of your choosing.

Running this module will list out all the groups in the tenant along with their members.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-4-1.png)

The Invoke-SecurityGroupCloner module will then ask what group you want to clone, if you want to add your current user to the group, if you want to add a different user, and if you want to name it something else.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-5-1.png)

Upon cloning a group, it will create an identically named group, adding the current members of that group while including your own user. Now when someone goes to add the “Administrators” group to a role, they will be presented with two options. Which one will they select? Maybe both?

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-6-1.png)

GraphRunner also includes modules for inviting guest users ( **Invoke-InviteGuest**) as well as adding members to groups ( **Invoke-AddGroupMember**).

In order to use the Invoke-AddGroupMember module, you will need both the group ID and the member ID of the user you want to add to the group. The group ID is output with each group via the Get-SecurityGroups module and the Get-UpdatableGroups module. The user ID for your current user can be found by running Invoke-CheckAccess or using the Get-UserObjectID module.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-7-1.png)

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-8-1.png)

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-9-1.png)

### Pillage

GraphRunner includes a number of pillage modules that assist in identifying interesting data post-compromise of a Microsoft 365 account. It contains modules for searching through and collecting data from email, SharePoint, OneDrive, and Teams. The **Invoke-SearchMailbox** module allows for the searching of terms through the current user’s mailbox. It allows for downloading messages including their attachments and even has a minimal HTML email viewer included for opening the downloaded messages in a web browser.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-10-1.png)

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-11-1-1024x764.png)

The Invoke-SearchMailbox module uses the Graph Search API, so it doesn’t allow for searching of other user’s mailbox. Also, due to the use of the Search API, only items that match the search term will be returned. If you want to get the latest messages from an inbox of either the current user or a shared mailbox, then the **Get-Inbox** module is the one you will want to use. This module will pull the latest 25 messages from an inbox by default; more can be specified with the -TotalMessages parameter.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-12-1.png)

Microsoft Teams has become the primary chat app for many organizations. Occasionally, sensitive data tends to get sent through this medium. It may be of benefit to search through Teams chat messages the user is a part of. **The Invoke-SearchTeams** module provides search capabilities for messages sent via Teams Chat (Direct Messages).

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-13-1.png)

Similarly, the **Get-TeamsChat** module downloads full Teams chat conversations. It will prompt to either download all conversations for a particular user or to download individual conversations using a chat ID. This module requires that you have a token scoped to Chat.ReadBasic, Chat.Read, or Chat.ReadWrite.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-14-1.png)

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-15-1.png)

Occasionally, sensitive data ends up in attributes tied to user accounts. Maybe the help desk set a password for an account and didn’t want to forget it, so they set the password as a comment in an attribute. We have seen similar cases to this on many pentests, and it can lead to gaining access to other accounts not previously accessible. GraphRunner has a module to search through every attribute field for every Entra ID user called **Invoke-SearchUserAttributes**. Using this module, you can pass it a search term to look for in Entra ID user attributes.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-16-1.png)

SharePoint is one of the largest services for file sharing and collaboration. Many organizations are using it in a similar manner to the way that internal network file shares are used to store files, some of them including sensitive data such as credentials. Historically, we have used tools such as ShareFinder and FileFinder from [PowerView](https://github.com/SnaffCon/Snaffler), or [Snaffler](https://github.com/SnaffCon/Snaffler) to help us look for interesting files on internal networks. There is [SnaffPoint](https://github.com/nheiniger/SnaffPoint/tree/main) for searching SharePoint sites but it doesn’t appear to use the Graph API. The advantage of using the [Graph Search API](https://learn.microsoft.com/en-us/graph/api/resources/search-api-overview?view=graph-rest-1.0) for searching for files is that it will automatically search all SharePoint sites AND OneDrive locations accessible to your user without needing to specify a certain site.

The Graph Search API uses [Keyword Query Language](https://learn.microsoft.com/en-us/sharepoint/dev/general-development/keyword-query-language-kql-syntax-reference) (KQL), which lets users filter searches with terms like “filetype”, “filename”, and “author”. For example, if you wanted to find all Word document files that contain the term “password” in them, you can search for “filetype:docx password”. GraphRunner has a module called **Invoke-SearchSharePointAndOneDrive** that leverages this search functionality and allows you to also download any files that were discovered.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-17-1.png)

If you want to simulate a similar type of assessment that Snaffler and Snaffpoint do, you can leverage the provided “default\_detectors.json” file in the GraphRunner repo. This file contains much of the same search syntax the other tools use, with some modifications to make them work with KQL. The following script will use Invoke-SearchSharePointAndOneDrive while looping through all of the detectors and output a CSV file called interesting-files.csv into a folder that is titled with the current date and time. The output contains the detector name that triggered, the name of the file, the Drive ID and Item ID (needed for downloading files), the last modified date, a file preview, the size of the file, and the web location (URL) where the file can be found.

```
$folderName = "SharePointSearch-" + (Get-Date -Format 'yyyyMMddHHmmss')
New-Item -Path $folderName -ItemType Directory | Out-Null
$spout = "$folderName\interesting-files.csv"$DetectorFile = ".\default_detectors.json"$detectors = Get-Content $DetectorFile
$detector = $detectors |ConvertFrom-Json
foreach($detect in $detector.Detectors){Invoke-SearchSharePointAndOneDrive  -Tokens $tokens -SearchTerm $detect.SearchQuery -DetectorName $detect.DetectorName -PageResults -ResultCount 500 -ReportOnly -OutFile $spout -GraphRun}
```

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-18-1.png)

If you want to download one of the files from the CSV output, you can use the supplemental module called Invoke-DriveFileDownload and specify the combined Drive ID and Item ID from the spreadsheet.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-19-1.png)

### Using Immersive File Reader to Bypass SharePoint File Block

Microsoft’s SharePoint Online [service](https://support.microsoft.com/en-us/office/get-started-with-sharepoint-909ec2f0-05c8-4e92-8ad3-3f8b0b6cf261) allows authenticated users to manage files in a cloud storage environment. Accessing SharePoint Online may be done via a web browser to https://companyname.sharepoint.com or with the SharePoint/OneDrive app.

From a security perspective, controlling who has access to what in SharePoint is critical to prevent data loss. Microsoft recommends enforcing a least-privilege administrative model described here: [https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/implementing-least-privilege-administrative-models](https://learn.microsoft.com/en-us/windows-server/identity/ad-ds/plan/security-best-practices/implementing-least-privilege-administrative-models). Meaning users should only have permissions to access what _they_ need. I would add that users should only be able to authenticate to a company’s SharePoint instance from a company compliant device.

To help prevent data loss, Microsoft provides the option to restrict access to users accessing SharePoint from unmanaged devices that are not controlled by the organization operating the SharePoint instance. [https://learn.microsoft.com/en-us/sharepoint/control-access-from-unmanaged-devices](https://learn.microsoft.com/en-us/sharepoint/control-access-from-unmanaged-devices).

With the policy enabled, a user browses to SharePoint Online and attempts to open a file named death\_star\_plans.txt.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-23.png)

Note the warning that security policy doesn’t allow you to download or view the file since the user is browsing from an unmanaged device.

When a user on an unmanaged device clicks “Open”, the security policy will block the user from opening the file.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-1-2.png)

However, the option to open the file in Immersive Reader may appear under the “Open” drop-down.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-2-2.png)

Clicking on “Open in Immersive Reader” results in the file opening for us!

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-3-2-1024x253.png)

Immersive Reader will even speak the text to you.

**What is Immersive Reader?**

At its core, Immersive Reader is an application that performs text-to-speech within certain Microsoft applications. For Microsoft SharePoint Online, that means we can visibly and audibly “read” text files from accessible SharePoint drives.

More info here: [https://techcommunity.microsoft.com/t5/education-blog/immersive-reader-comes-to-powerpoint-for-the-web-onedrive/ba-p/2242568](https://techcommunity.microsoft.com/t5/education-blog/immersive-reader-comes-to-powerpoint-for-the-web-onedrive/ba-p/2242568)

Back to the previous request for “death\_star\_plans.txt”, we take a look at the request which opens the file with Immersive Reader.

```
GET /transform/imreader?provider=spo&inputFormat=txt&cs=fFNQTw&docid=https%3A%2F%2Ftestbeau.sharepoint.com%3A443%2F_api%2Fv2.0%2Fdrives%2Fb!UZKcPDJOak6rlVu_8sqLHrL37OSkA7tNiIu6hH3cVmYli4rws4usRomUi9sy-cG4%2Fitems%2F01F276Q3X3SAZEE3ZISRBZ7UJRBMQRKWEB%3Fversion%3DPublished&access_token=<eyJ0>&nocache=true&cTag=%22c%3A%7B423290FB-286F-4394-9FD1-310B21155881%7D%2C1%22 HTTP/1.1
Host: southcentralus1-mediap.svc.ms
User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0
Accept: /
Accept-Language: en-US,en;q=0.5
Accept-Encoding: gzip, deflate
Referer: https://testbeau.sharepoint.com/
Origin: https://testbeau.sharepoint.com
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: cross-site
Te: trailers
Connection: close
```

We can see that the access\_token is in the GET request. Checking the JWT in jwt.io, we see that it is scoped to SharePoint Online’s principle ID.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-4-2.png)

It’s also interesting to note that the request isn’t being directed to \*.sharepoint.com. Rather, it’s directed at southcentralus1-mediap.svc.ms.

#### **GraphRunner Weaponization**

Implementing Invoke-ImmersiveFileRead into GraphRunner was rather easy with the captured GET request. The cmdlet takes the target SharePoint domain, DriveID, and FileID as parameters.

We might find the DriveID and FileID by searching SharePoint for the filename\* and the filetype with extension.

```
Invoke-SearchSharePointAndOneDrive -Tokens $tokens -SearchTerm "death_star_plans* AND Filetype:txt"
```

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-5-2-1024x377.png)

The file was found in two places as our user shared it in Teams as well.

GraphRunner will prompt you with the option to download any files that were found.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-7-2-1024x319.png)

Attempting to download both files, we see that the Teams file successfully downloaded, because it is on the user’s personal OneDrive/SharePoint. Unfortunately, the default block policy only applies to SharePoint, which doesn’t seem to include the “tenant-my.sharepoint” sites by default.

Further restrictions are needed to restrict downloads from unmanaged devices on other applications. [https://learn.microsoft.com/en-us/microsoftteams/block-access-sharepoint](https://learn.microsoft.com/en-us/microsoftteams/block-access-sharepoint)

Next, we’ll use Invoke-ImmersiveFileReader to attempt to open the file we couldn’t access.

```
Invoke-ImmersiveFileReader -SharePointDomain testbeau.sharepoint.com -DriveID "b!U.." -FileID ")1.." -Tokens $Tokens
```

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-8-2.png)

Success! We’ve successfully opened the file just like the Immersive Reader feature in the browser.

Some txt files may not show the Immersive Reader as an option. These may still be viewed by Immersive Reader in some cases.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-9-2.png)

Now, what about reading other types of files? Here is pyauth.py on the testbeau.sharepoint.com SharePoint site.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-10-2-1024x381.png)

We see that the file is restricted from being open or downloaded, and, most importantly, there is no immersive file reader option. We’ll try with the Invoke-ImmersiveFileReader cmdlet.

```
Invoke-SearchSharePointAndOneDrive -Tokens $tokens -SearchTerm "pyauth* AND filetype:py”
```

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-11-2-1024x325.png)

We found the file and attempted to download it without success.

Even though there’s no Immersive Reader option from the browser for this Python file, we’ll try Invoke-ImmersiveFileReader anyway.

```
Invoke-ImmersiveFileReader -SharePointDomain testbeau.sharepoint.com -DriveID "b!UZKcPDJOak6rlVu_8sqLHrL37OSkA7tNiIu6hH3cVmYli4rws4usRomUi9sy-cG4\" -FileID "01F276Q3TIC57IYFZK3BBIDB2JE4VHVWSY" -Tokens $Tokens
```

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-12-2.png)

Success! We have accessed the data in a Python file with Immersive Reader, where there was no option from the web portal. The file should not be readable with the Unrestricted Device policy in-place as well. What other files can we read using Immersive Reader?

### **Defenses Against Immersive Reader Access**

To enforce basic protections on SharePoint Online, Microsoft requires an “ [Enterprise Mobility + Security](https://www.microsoft.com/en-US/security/business/solutions/identity-access)” license.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-13-2.png)

Next, enforce Unmanaged Device blocking policy.

From the SharePoint Admin Center, SharePoint administrators may enforce the Unmanaged Devices policy to block unauthorized access to files from non-compliant devices.

📢

Access is allowed on apps that don’t use modern authentication. Users who use these apps will have full access to content in SharePoint and OneDrive, even on unmanaged devices.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-14-2-1024x487.png)

Additionally, SharePoint administrators may further modify the conditional access policy created when enabling the unmanaged device block. Further restrict authenticated users from accessing SharePoint Online files from unmanaged devices by ensuring the device is compliant and/or Hybrid joined.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-15-2.png)

Microsoft SharePoint Online provides administrators with the ability to restrict file downloads for authenticated users accessing the service from an unmanaged device. Using the Immersive Reader feature, we’re able to bypass unmanaged device restrictions that aren’t backed by additional conditional policy.

## Invoke-GraphRunner

GraphRunner includes a function that automates the running of multiple recon and pillage modules called Invoke-GraphRunner. This module will run the Invoke-GraphRecon, Get-AzureADUsers, Get-SecurityGroups, Invoke-DumpCAPS, Invoke-DumpApps recon modules. It then uses the default\_detectors.json file to search with Invoke-SearchMailbox, Invoke-SearchSharePointAndOneDrive, and Invoke-SearchTeams. This may be of benefit when trying to quickly automate data collection from an account.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-16-2.png)

## GraphRunner GUI

While not as fully featured as the GraphRunner PowerShell script, the HTML GUI can be useful in times when you want to visually click through items such as email, Teams messages, SharePoint/OneDrive drives, and more. All it requires is that you have an authenticated access token to the Microsoft Graph API. Each of the functionalities require different permissions, so unless your token has been scoped correctly, some functions may not work.

Once the GraphRunnerGUI.html file has been opened in a web browser, input your authenticated access token into the “Access Token” field. After doing so, all functionality in the page will utilize this token during requests to the Microsoft Graph API. It’s important to understand that every action against the Microsoft Graph API relies on specific permissions being scoped to the token you have. When in doubt refer to this permissions reference guide: [https://learn.microsoft.com/en-us/graph/permissions-reference](https://learn.microsoft.com/en-us/graph/permissions-reference)

The GUI has a “Parse Token” function that will parse your token and display the permissions that are scoped to your token.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-24.png)

There is a Custom API Request section that gives you a place to make custom requests to the API if you wish. You can use the drop down to select other HTTP methods and can use the text box to insert POST data.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-1-3-1024x469.png)

The directory sections provide the ability to gather users and groups from the directory. The “Export” button will create a text file of the results. Clicking on a group name will display the members of that group below.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-2-3.png)

The “Email Viewer (Current User)” section is where you can load recent messages from the current account as well as search for specific terms. Clicking on a message will load it in an HTML email viewer below the list of emails.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-3-3.png)

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-4-3-1024x261.png)

The “Email Viewer (Other Users)” section is where you can read mailboxes that have been shared by other users. Use this in collaboration with the Invoke-GraphOpenInboxFinder module from the GraphRunner.ps1 script to discover mailboxes that have been misconfigured in the tenant to allow other users to access them.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-5-3.png)

The “Send Email” section allows you to send emails from the current account, including the ability to add attachments.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-6-3.png)

The “Teams Chat Viewer (Direct Messages and Group Chat)” loads Teams chat conversations where the user is either DM’ing with someone or part of a group chat. Clicking on the conversation date box will load the recent messages from that chat. While a conversation is selected messages can be sent to that particular conversation through the “Send Message to Teams Chat” text box.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-7-3.png)

The “OneDrive My Files” button will load files from the current user’s OneDrive file share. Folders can be navigated through and files can be downloaded here.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-8-3.png)

The “OneDrive Shared Files” button will load files that have been shared with the user. This is commonly where files sent through Teams messages are located.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-9-3.png)

Last but not least, the SharePoint section will load the user’s SharePoint documents and allow you to download them.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-10-3-1024x965.png)

## OAuth Flow Automation

Whenever a user consents to an OAuth app, their browser sends a request to a specified redirect URI to provide an authorization code. The PHPRedirector folder contains code that can be hosted on a web server to capture an OAuth authorization code as well as complete the OAuth flow. In situations where the user that is consenting to an app is remote, you may want to automatically complete the OAuth flow and obtain access and refresh tokens. The AutoOAuthFlow.py script facilitates this ability while writing any access tokens to a file on disk called access\_tokens.txt.

When you are ready to capture codes, you can run AutoOAuthFlow.py to watch for new OAuth codes and complete the flow using your App credentials. Whenever a web request is sent to the web server that contains an OAuth code, it will be written to codes-bak.txt and will be used to attempt OAuth flow completion to obtain access tokens. If successful, the access tokens will be written to access\_tokens.txt in the same directory as the Python script.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-11-3.png)

## Potential Attack Paths

GraphRunner has a lot of different modules that do specific tasks, but combining them can lead to interesting attack paths in certain scenarios. Below are a few examples where GraphRunner may benefit you in identifying potential situations where it can be used for persistence, privilege escalation, data harvesting, and more within an M365 account.

### Group-Based PrivEsc (Adding user)

1. Identify groups that can be modified by current user (Get-UpdatableGroups)
2. Determine current access level (Get-SharePointSites, Invoke-DumpCAPS, Check for subscription access, Invoke-GraphRecon -PermissionEnum, etc.)
3. Inject your user into the group (Invoke-AddGroupMember)
4. Re-run enumeration modules to see if there is new access to sites/policies.

**Bonus**

Guest users can be injected into groups too, but your current user (Entra ID user in the target tenant) needs to be injected first.

### Dynamic Group PrivEsc (Abusing membership rule)

1. Identify dynamic groups (Get-DynamicGroups) that have rules that can be abused, such as a rule that adds a user to a group if their email contains “admin”.
2. Analyze membership rules to determine if they can be abused.
   - Example: Invite guest user to tenant with an email that has “admin” in the email address to get added as a member of a group where UPN’s that contain “admin” get automatically added to it.

### Watering Hole Attack via Cloned Group

1. Identify an interesting group (SharePoint Admins, Dev groups, other IT groups, etc.)
2. Clone it and add your own user (Invoke-SecurityGroupCloner)
3. Wait for an admin to mistakenly add your cloned group to a policy somewhere OR come up with a ruse to get it added
4. Monitor access to various M365 pieces like SharePoint, Teams, CAPS policies, subscriptions, etc.

### Persistence via OAuth App

1. Inject an OAuth App registration (Invoke-InjectOAuthApp) into the same tenant as the compromised user.
2. Set up a listener to complete the OAuth flow with either Invoke-AutoOAuthFlow to catch the redirect on your localhost, or the AutoOAuthFlow.py script to catch it on another server.
3. After consenting to the app, it will generate tokens associated with the app registration that can be leveraged for accessing M365 as the user.
4. If the user changes their password, you still have access as the app.
5. If all sessions get killed, the refresh token of the app is still valid until it expires (default is 1 hour from creation time)

### Persistence to SharePoint/OneDrive Files via Guest User access

If external sharing for a site is set to allow “Anyone” or “New and existing guests” access via external sharing, then it may be possible to leverage a guest account for long term access to specific files.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/Untitled-12-3.png)

1. Invite guest user to tenant (Invoke-InviteGuest).
2. Gather SharePoint share links and maintain long term access to files until guest user is removed.

## Internal Phishing via OAuth App

1. Inject an OAuth app (Invoke-InjectOAuthApp) that has limited permissions (Mail.Read) into the same tenant as the compromised user.
2. Use it to perform illicit consent grant phishing attacks internally for more access.

### Find Other Mailboxes You Can Read

1. Deploy an app with the “Mail.Read.Shared” scope into the victim tenant and consent to it with your user, or consent to this permission on the Graph Explorer and leverage the app token with GraphRunner.
2. Use Invoke-GraphOpenInboxFinder to find other mailboxes that have been shared with you.
3. Use Get-Inbox to pull the latest messages from other inboxes you can read.

### Pillage SharePoint, Teams, and Email

1. Leverage the pillage modules to identify sensitive data sent in email (Invoke-SearchMailbox, Get-Inbox), Teams chat (Invoke-SearchTeams, Get-TeamsChat), or SharePoint (Invoke-SearchSharePointAndOneDrive).
2. Use the following command to perform “Snaffler-like” scanning of a SharePoint site:
   - Invoke-GraphRunner -Tokens $tokens -DisableRecon -DisableUsers -DisableGroups -DisableCAPS -DisableApps -DisableEmail -DisableTeams

### Search User Attributes

1. Leverage the Invoke-SearchUserAttributes module to identify potentially sensitive information in Entra ID user attributes.

### Immersive File Reader

1. Use Invoke-SearchSharePointAndOneDrive to identify interesting files
2. Use Invoke-ImmersiveFileReader to download them in some environments that block file downloads from SharePoint and OneDrive.

### Find CAP Bypasses and Enumerate Permission Scopes Using Different Client IDs

1. Gather a refresh token from an authenticated session (Ex. intercept browser).
2. Use it with the Invoke-BruteClientIDAccess module to find applications that can authenticate or be refreshed to, along with their associated permission scopes.
3. In this instance, conditional access blocked access to MSGraph from FireFox.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/A911pn54y_dh5ttw_9r8.jpg)

5\. As seen below, there are some clientID’s that have rights where some do not.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/A9btqa3l_dh5ttz_9r8-1024x254.jpg)

6\. It may be possible to abuse this for initial access via Device Code phishing by changing the ClientID for the initial code request to something like Microsoft Edge.

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/A9m3df0z_dh5tu2_9r8.jpg)

![](https://www.blackhillsinfosec.com/wp-content/uploads/2023/10/A91xs9c45_dh5tu5_9r8.jpg)

7\. Successful Device Code flow bypassing a Conditional Access Policy.

## Conclusion

GraphRunner was created to help identify and exploit common security issues in Microsoft 365. It’s a tool that was made for the red team, but we think blue teamers will be able to leverage it as well to proactively identify security issues. The attack surface for cloud environments continues to grow, and with that, so will GraphRunner. For the user guide and information about individual modules, check out the wiki here: [https://github.com/dafthack/GraphRunner/wiki](https://github.com/dafthack/GraphRunner/wiki)

Download GraphRunner: [https://github.com/dafthack/GraphRunner/](https://github.com/dafthack/GraphRunner/)

* * *

* * *

\*Psst\* If you liked this blog, we think you’d enjoy Beau’s class:

[Breaching the Cloud](https://www.antisyphontraining.com/on-demand-courses/breaching-the-cloud-w-beau-bullock/)

Available live/virtual and on-demand!

![](https://www.blackhillsinfosec.com/wp-content/uploads/2022/11/AntiSyphon_3-1-150x150.png)

* * *

* * *

[Abusing Active Directory Certificate Services (Part 2)](https://www.blackhillsinfosec.com/abusing-active-directory-certificate-services-part-2/)[Opt for TOTP to Deal With MFA App Sprawl](https://www.blackhillsinfosec.com/opt-for-totp/)