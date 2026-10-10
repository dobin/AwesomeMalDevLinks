# https://cicada-8.medium.com/im-watching-you-how-to-spy-windows-users-via-ms-uia-c9acd30f94c4

[Sitemap](https://cicada-8.medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=---top_nav_layout_nav-------------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fcicada-8.medium.com%2Fim-watching-you-how-to-spy-windows-users-via-ms-uia-c9acd30f94c4&source=post_page---top_nav_layout_nav-----------------------global_nav--------------------)

[Medium Logo](https://medium.com/?source=---top_nav_layout_nav-------------------------------------------)

Get app

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav--------------------)

[Search](https://medium.com/search?source=---top_nav_layout_nav-------------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fcicada-8.medium.com%2Fim-watching-you-how-to-spy-windows-users-via-ms-uia-c9acd30f94c4&source=post_page---top_nav_layout_nav-----------------------global_nav--------------------)

![Unknown user](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

[![CICADA8](https://miro.medium.com/v2/resize:fill:40:40/1*ytXKSKqguQZ3MH1iZ0G7qQ.png)](https://cicada-8.medium.com/?source=post_page---post_author_sidebar--c9acd30f94c4-----------------1d7232a03767------------------------)

## CICADA8

CICADA8 is a vulnerability management service with real-time cyber threat tracking capabilities. [https://cicada8.ru/](https://cicada8.ru/)

Follow writer

[Red Team](https://medium.com/tag/red-team?source=post_page---header_tags--c9acd30f94c4-----------------------------------------)

[Windows](https://medium.com/tag/windows?source=post_page---header_tags--c9acd30f94c4-----------------------------------------)

[Hacking](https://medium.com/tag/hacking?source=post_page---header_tags--c9acd30f94c4-----------------------------------------)

[Pentesting](https://medium.com/tag/pentesting?source=post_page---header_tags--c9acd30f94c4-----------------------------------------)

# I’m watching you! How to spy Windows users via MS UIA

[![CICADA8](https://miro.medium.com/v2/resize:fill:32:32/1*ytXKSKqguQZ3MH1iZ0G7qQ.png)](https://cicada-8.medium.com/?source=post_page---byline--c9acd30f94c4-----------------------------------------)

[CICADA8](https://cicada-8.medium.com/?source=post_page---byline--c9acd30f94c4-----------------------------------------)

Follow

9 min read

·

Jan 5, 2025

60

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dc9acd30f94c4&operation=register&redirect=https%3A%2F%2Fcicada-8.medium.com%2Fim-watching-you-how-to-spy-windows-users-via-ms-uia-c9acd30f94c4&source=---header_actions--c9acd30f94c4---------------------post_audio_button--------------------)

Share

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*v30i8prL1TCwExyWlfTlXA.png)

Hello everybody, my name is [Michael Zhmailo](https://www.linkedin.com/in/mzhmo/) and I am a penetration testing expert in the [CICADA8](https://cicada8.ru/) team.

We’re sure you’ll agree that keeping track of users has always been an interesting challenge. It’s like exploring their secrets, finding passwords, and discovering attack scenarios that depend only on the human factor.

We’re excited to share our new research about using a User Interface Automation framework for user spying. In this article, we’ll take you on a journey through the Windows Component Object Model, create our own event handlers, and learn about the Windows graphical representation tree, among other things.

We have also developed a POC called [Spyndicapped](https://github.com/CICADA8-Research/Spyndicapped).

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*Iybg_DwQOBtqIDJkjpiThA.png)

Tool help

## What’s MS UIA?

[MS UIA](https://learn.microsoft.com/en-us/windows/win32/winauto/uiauto-uiautomationoverview) ( _Microsoft User Interface Automation_) is a special framework designed to automate the use of the Windows GUI. With its help you can read any text values on the screen, open menus, close windows.

In general, you can do everything a user does in front of a monitor, just as if a hacker were sitting at a desktop.

The framework was originally designed for handicapped people, hence the name of the tool — **Spy** ndicapped.

MSAA ( _Microsoft Active Accessibility_) was heavily used in Windows prior to MS UIA, but it has been completely replaced by MS UIA. I should note that MS UIA is supported by almost all modern systems, starting with Windows XP, so I don’t see any point in diving into MSAA.

![](https://miro.medium.com/v2/resize:fit:640/1*xvlb7VbOJeLN0EZGgV7Hbg.jpeg)

U can read more information about MSAA and UIA comparsion [here](https://learn.microsoft.com/en-us/windows/win32/winauto/microsoft-active-accessibility-and-ui-automation-compared).

## Basic Structure

### Elements, Properties and so on

So, let’s take a look at the basic structure.

The framework itself is made up of several main components: elements, properties, events, and patterns.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*xegcMKFZIOlTctVN708I2g.png)

Highlighting all elements

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*SJoikuABcjVsnhpTAXLZIg.png)

Highliting all properties

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*N1aL2bc__rn3CKsf313F8g.png)

Pattern calling

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*_I-EygRpPY0aMfHskbzfpg.png)

Appearance of UIA\_Window\_WindowOpenedEventId event

**Elements** are everything you see on the screen, like text, buttons, menus, and anything else there. **Properties** are what make each element special. For example, the Name property of an element contains the NAME of the element, and the Value property is the value. Flags are various additional flags. Hopefully, you get the idea.

It’s a bit like the built-in graphics engine in Windows, but for UIA. You can handle any **events** related to the GUI, like entering data, changing a property, or opening a window.

And finally, **patterns** provide the opportunity for live interaction with elements, which is really cool. For example, the _Scroll_ pattern allows you to scroll Scroll Bars using program code, and the _Invoke_ pattern simulates a function call that occurs when a button is clicked.

### Graphical representation of elements in Windows

(aka Automation Tree or Control Tree)

All graphical elements in Windows have a strict hierarchical structure. The root of the hierarchy is the current desktop. The descendants of the desktop are the displayed windows. Descendants of windows are controls inside the window. In turn, inside the controls there may be other buttons, menus and other mechanisms with which the user interacts.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*d966upkMQoODryUwYCgDvw.png)

Windows automation tree view in inspect.exe (we’ll explore this tool later)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*PV_3BTbqaNdy_5il77oJGw.png)

Button in the control tree

This tree structure is incredibly convenient for searching for items, traversing the tree, or handling structure changes. In Spyndicapped there are quite a few methods related to working with a tree, you can find them in a special class [MyTreeWalker](https://github.com/CICADA8-Research/Spyndicapped/blob/main/Spyndicapped/MyTreeWalker.cpp).

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*DAtTefIrT3j75wATqcPscg.png)

Example methods to work with tree

### Let’s dive into COM!

Work with UIA is available only on top of the corresponding COM classes. You can develop a program also in CSharp, but I did it in C++, because I like them and I like to make a lot of mistakes in memory management :).

Globally, we need to use multiple interfaces:

\- [IUIAutomation](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nn-uiautomationclient-iuiautomation) — allows us to get started with COM. It can be obtained through the call of CoCreateInstance() function;

\- [IUIAutomationElement](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nn-uiautomationclient-iuiautomationelement) — points to a specific graphical element. It can be obtained by processing UIA events or through tree traversal (more on this later);

\- [IUIAutomationCondition](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nn-uiautomationclient-iuiautomationcondition) — allows you to create conditions used when searching for the desired element. For example, you can create a condition to find an element with the name **_Misha123_** or the value **_Cicada8_**;

\- [IUIAutomationTreeWalker](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nn-uiautomationclient-iuiautomationtreewalker) — is needed for traversing the tree of the graphical representation.

It is worth noting that the user only sees the _IUIAutomatomatioElement_ on the screen. Everything else is auxiliary interfaces.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*XgujWB6E0xWQCBtfJaqC8Q.png)

This is all an IUIAutomationElement that we can interact with

Almost all of our code will be based on processing events, getting the necessary _IUIAutomationElement_ and outputting their values.

The methods of these interfaces will help us with this, but let’s first familiarize ourselves with event handlers.

### Event handling

Globally on top of all those entities I described earlier, there are two more roles: the UIA client and the UIA provider. The UIA client subscribes to and processes events that are received from UIA providers. You can generate your own UIA events if you write a provider. But we will write a client, since it is sufficient for POC to handle events that are provided by the built-in Windows UIA providers.

There are quite a large number of different events that can be handled. And the processing must be done with the help of a suitable provider.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*lTgO6ooT5_0v9L4XeV7YIw.png)

Events example (accevent.exe. we’ll explore this tool later)

The [IUIAutomationEventHandler](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nn-uiautomationclient-iuiautomationeventhandler) is used to handle basic UIA events. These events include, for example, opening windows, calling functions. In general, all constants that start with _UIA\__ and end with _EventId_.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*xJTNW0EzTQtPxs3qP5yqIA.png)

UIA Events example

When registering a handler, you must explicitly specify which events you want to track. If you do not specify any events, you will not be able to receive notifications. Handler registration is done using the [AddAutomationEventHandler()](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nf-uiautomationclient-iuiautomation-addautomationeventhandler) function from the _IUIAutomationEventHandler_ interface, to which you pass the address of the handler function and the events you want to handle.

Here’s registration example.

```
 std::vector<EVENTID> eventIds = {
   UIA_AutomationPropertyChangedEventId,
   UIA_Text_TextSelectionChangedEventId,
   UIA_Text_TextChangedEventId,
   UIA_Invoke_InvokedEventId,
   UIA_Window_WindowOpenedEventId,
 };

 for (size_t i = 0; i < eventIds.size(); i++)
 {
  HRESULT hr = pAutomation->AddAutomationEventHandler(eventIds[i], pAutomationElement, TreeScope_Subtree, NULL, (IUIAutomationEventHandler*)pMyAutomationEventHandler);
  if (FAILED(hr)) {
   Log(L"Failed to add event handler for event ID: " + std::to_wstring(eventIds[i]), WARNING);
   PrintErrorFromHRESULT(hr);
   return E_ABORT;
  }
 }
```

After that the handler function will be called. Here’s handler example.

```
HRESULT STDMETHODCALLTYPE MyAutomationEventHandler::HandleAutomationEvent(IUIAutomationElement* pAutomationElement, EVENTID eventID)
{
  ...
}
```

- _pAutomationElement_ — the element that generated the event. For example, it will be an input field if it started receiving data;
- _eventID_ — triggered event.

The Spyndicapped tool also registers a property handler ( [IUIAutomationPropertyChangedEventHandler](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nf-uiautomationclient-iuiautomationpropertychangedeventhandler-handlepropertychangedevent)). It allows you to track property changes that are registered with specific programs, such as chrome.exe or keepass.exe.

Adding such a handler is possible via [AddPropertyChangedEventHandler()](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nf-uiautomationclient-iuiautomationeventhandlergroup-addpropertychangedeventhandler) or [AddPropertyChangedHandlerNativeArray()](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nf-uiautomationclient-iuiautomation-addpropertychangedeventhandlernativearray).

## Get CICADA8’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Remember me for faster sign in

Here’s registration example.

```
std::vector<int> propertyIds = {
 UIA_NamePropertyId,
 UIA_ValueValuePropertyId,
 UIA_SelectionItemIsSelectedPropertyId,
};

SAFEARRAY* propertyArray = SafeArrayCreateVector(VT_I4, 0, propertyIds.size());
if (!propertyArray)
{
 Log(L"Can't create property arrray", WARNING);
 return E_ABORT;
}

for (size_t i = 0; i < propertyIds.size(); i++)
{
 long index = static_cast<long>(i);
 SafeArrayPutElement(propertyArray, &index, &propertyIds[i]);
}

hr = pAutomation->AddPropertyChangedEventHandler(pAutomationElement, TreeScope_Subtree, NULL, pMyPropertyChangedEventHandler, propertyArray);

if (FAILED(hr)) {
 Log(L"Failed to add property changed event handler" , WARNING);
 PrintErrorFromHRESULT(hr);
 return E_ABORT;
}
```

And handler’s function.

```
HRESULT STDMETHODCALLTYPE MyPropertyChangedEventHandler::HandlePropertyChangedEvent(IUIAutomationElement* pAutomationElement, PROPERTYID propId, VARIANT vVar)
{
  ...
}
```

- _pAutomationElement_ — the element that generated the event. For example, it will be an input field if it started receiving data;
- _propId_— id of the modified property;
- _vVar_— new value in VARIANT format.

These are by no means all handlers. You can create handlers for notifications, changing focus, changing text position and much more. Here is the full list:

- [IUIAutomationChangesEventHandler](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nn-uiautomationclient-iuiautomationchangeseventhandler) — any changes;
- [IUIAutomationActiveTextPositionChangedEventHandler](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nn-uiautomationclient-iuiautomationactivetextpositionchangedeventhandler) — text position changes;
- [IUIAutomationTextEditTextChangedEventHandler](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nn-uiautomationclient-iuiautomationtextedittextchangedeventhandler) — text modification through autocomplete and other mechanisms for the visually impaired;
- [IUIAutomationFocusChangedEventHandler](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nn-uiautomationclient-iuiautomationfocuschangedeventhandler) — focus changed;
- [IUIAutomationStructureChangedEventHandler](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nn-uiautomationclient-iuiautomationstructurechangedeventhandler) — changes in the control tree (adding a element for example);
- [IUIAutomationNotificationEventHandler](https://learn.microsoft.com/en-us/windows/win32/api/uiautomationclient/nf-uiautomationclient-iuiautomationnotificationeventhandler-handlenotificationevent) — notification handling.

## Development assistance using UIA

How to understand which event occurs when a key is pressed? Or which graphic element should be accessed to solve our problem? Several tools (including the aforementioned _inspect.exe_ and _accevent.exe_) can help us here.

### WinSpy

[Link](https://github.com/zodiacon/WinSpy)

This is an extended version of the well-known Spy++ for debugging graphical elements. To view the UIA tree, click on the _View Automation Tree_ button:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*fqu6wvQlqTpgRu7dTDDU_A.png)

Usage example

### Inspect.exe

[Link](https://learn.microsoft.com/en-us/windows/win32/winauto/inspect-objects)

I like Inspect.exe better than WinSpy. This tool comes bundled with the Windows SDK. It displays all the necessary data about the Windows graphical tree.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*i_L99n3YsA5Wat8ZNGuvZQ.png)

inspect.exe demo

You can click on these buttons and make the item light up, which is very handy for locating the right button!

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*tcd6yXy8BVY6Q9Dv1OO_4g.png)

Help buttons

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*bjtqG6IMsgJZOs2ZovFGqg.png)

Yellow highlighting example

U can learn more about inspect.exe usage [here](https://youtu.be/6b0K2883rXA?si=lIBnRDSsHL3xJgqB).

### accevent.exe

[Link](https://learn.microsoft.com/en-us/windows/win32/winauto/accessible-event-watcher)

With this application, you can keep track of all UIA events in Windows. In fact, it is a universal UIA Client! Usage is so simple. Firstly, click on the mode and select «UIA Events».

![](https://miro.medium.com/v2/resize:fit:451/1*tPo1bz48HgWRu90JClry9Q.png)

Then click on button «Settings» and select the desired events and the properties you want to receive about the event.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*NtqYqPt9X2rChf41Sz_RdQ.png)

Settings example

Then go to «Events» -> «Start Listening»

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*RY-DULvuqb7I4zvPycZLeQ.png)

And u’ll start receiving events.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*KICSR-3XiXVHuOzEo7oDyw.png)

Events capture

Then click on the «Stop Listening» button and start analyzing events.

## How to make your own stealth logger

During my research I identified the main events that occur when typing or working with text data, after which I created two handlers:

\- [MyAutomationEventHandler.cpp](https://github.com/CICADA8-Research/Spyndicapped/blob/main/Spyndicapped/MyAutomationEventHandler.cpp);

\- [MyPropertyChangedEventHandler.cpp](https://github.com/CICADA8-Research/Spyndicapped/blob/main/Spyndicapped/MyPropertyChangedEventHandler.cpp).

The first one allows to handle general UIA events, and the second one — property changed events.

Then i learned to identify from an event which process it came from. I did this with the help of functions:

\- [Finder::GetPIDByUIAutomationElement](https://github.com/CICADA8-Research/Spyndicapped/blob/main/Spyndicapped/MyAutomationEventHandler.cpp#L86)();

\- [Finder::GetModuleNameFromPid](https://github.com/CICADA8-Research/Spyndicapped/blob/main/Spyndicapped/MyAutomationEventHandler.cpp#L94)();

After that I implemented a simple routing mechanism on lambda functions. Depending on the process name, the corresponding function is called from the file named _<HandlerName>Apps.cpp_

```

 if (g_IgnoreHandlers)
 {
  HandleOther(pAutomationElement, wsProcName, wsEventString, wsDate, eventID);
 }
 else {
  std::unordered_map<std::wstring, std::function<void()>> handlers = {
   { L"firefox.exe", [this, pAutomationElement, wsProcName, wsEventString, wsDate, eventID]() { HandleFirefox(pAutomationElement, wsProcName, wsEventString, wsDate, eventID); } },
   { L"explorer.exe", [this, pAutomationElement, wsProcName, wsEventString, wsDate, eventID]() { HandleExplorer(pAutomationElement, wsProcName, wsEventString, wsDate, eventID); } }
  };

  auto it = handlers.find(Helpers::ConvertToLower(wsProcName));

  if (it != handlers.end()) {
   it->second();
  }
  else {
   HandleOther(pAutomationElement, wsProcName, wsEventString, wsDate, eventID);
  }
 }
```

For example, if the event was received in the _MyAutomationEventHandler.cpp_ handler, the function from _MyAutomationEventHandlerApps.cpp_ will be called.

Then inside each-function handler I created unique logic for each process.

For example, if there were changes in the firefox.exe process, the domain name of the current tab is checked. If it is _web.whatsapp.com_ or _app.slack.com_, then it processes that site to find the contents of the message and the name of the recipient.

```
std::unordered_map<std::wstring, std::function<void()>> handlers = {
   { L"web.whatsapp.com", [this, pAutomationElement, wsProcName, wsDate]() { HandleWhatsAppFF(pAutomationElement, wsProcName, wsDate); } },
   { L"app.slack.com", [this, pAutomationElement, wsProcName, wsDate]() { HandleSlackFF(pAutomationElement, wsProcName, wsDate); } }
 };

 auto it = handlers.find(Helpers::ConvertToLower(wsDomain));

 if (it != handlers.end()) {
  it->second();
 }
 else {
  HandleOther(pAutomationElement, wsProcName, wsEventString, wsDate, eventID);
 }
```

As a result, you have the ability to intercept almost any potentially interesting text content.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*WWrtzZI8tM3clZqNldC0lA.png)

Slack looting example

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*qkHy3zuIl0XOSS-l9wuetQ.png)

Whatsapp web looting example

Among other things, I added a separate handler for the _KeePass.exe_ process. If Spyndicapped detects an open KeePass window, it automatically retrieves all passwords from the current tab by quickly emulating the “Copy Password” button. All this is done only by MS UIA tools, which potentially makes the tool quite stealthy from EDR.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*BeSu5ygF30IA0ElVLofWuA.png)

Keepass looting example

My tool utilizes almost all of the concepts necessary for successful development with MS UIA. You can easily check the [source code](https://github.com/CICADA8-Research/Spyndicapped) and modify Spyndicapped to automate tracking of almost **ANY application on Windows**!

## Conclusion

Thank you for reading this article. Feedback is very important to me. If you liked the article, you can give it a star on Github or retwit it on the X!

Merry Christmas.

[Red Team](https://medium.com/tag/red-team?source=post_page---footer_tags--c9acd30f94c4-----------------------------------------)

[Windows](https://medium.com/tag/windows?source=post_page---footer_tags--c9acd30f94c4-----------------------------------------)

[Hacking](https://medium.com/tag/hacking?source=post_page---footer_tags--c9acd30f94c4-----------------------------------------)

[Pentesting](https://medium.com/tag/pentesting?source=post_page---footer_tags--c9acd30f94c4-----------------------------------------)

[![CICADA8](https://miro.medium.com/v2/resize:fill:48:48/1*ytXKSKqguQZ3MH1iZ0G7qQ.png)](https://cicada-8.medium.com/?source=post_page---post_author_info--c9acd30f94c4-----------------------------------------)

[![CICADA8](https://miro.medium.com/v2/resize:fill:64:64/1*ytXKSKqguQZ3MH1iZ0G7qQ.png)](https://cicada-8.medium.com/?source=post_page---post_author_info--c9acd30f94c4-----------------------------------------)

Follow

[**Written by CICADA8**](https://cicada-8.medium.com/?source=post_page---post_author_info--c9acd30f94c4-----------------------------------------)

[354 followers](https://cicada-8.medium.com/followers?source=post_page---post_author_info--c9acd30f94c4-----------------------------------------)

· [0 following](https://cicada-8.medium.com/following?source=post_page---post_author_info--c9acd30f94c4-----------------------------------------)

CICADA8 is a vulnerability management service with real-time cyber threat tracking capabilities. [https://cicada8.ru/](https://cicada8.ru/)

Follow

[Help](https://help.medium.com/hc/en-us?source=post_page-----c9acd30f94c4-----------------------------------------)

[Status](https://status.medium.com/?source=post_page-----c9acd30f94c4-----------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----c9acd30f94c4-----------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----c9acd30f94c4-----------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----c9acd30f94c4-----------------------------------------)

[Store](https://medium.com/store)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----c9acd30f94c4-----------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----c9acd30f94c4-----------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----c9acd30f94c4-----------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----c9acd30f94c4-----------------------------------------)

reCAPTCHA

Recaptcha requires verification.

protected by **reCAPTCHA**