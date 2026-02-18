# https://www.linkedin.com/pulse/unseen-magic-com-steven-dejean-o7ipf

Agree & Join LinkedIn


By clicking Continue to join or sign in, you agree to LinkedIn’s [User Agreement](https://www.linkedin.com/legal/user-agreement?trk=linkedin-tc_auth-button_user-agreement), [Privacy Policy](https://www.linkedin.com/legal/privacy-policy?trk=linkedin-tc_auth-button_privacy-policy), and [Cookie Policy](https://www.linkedin.com/legal/cookie-policy?trk=linkedin-tc_auth-button_cookie-policy).


``````````````

``````````````[Skip to main content](https://www.linkedin.com/pulse/unseen-magic-com-steven-dejean-o7ipf#main-content)

````````

![The Unseen Magic of COM](https://media.licdn.com/dms/image/v2/D4D12AQGOjC09Ojb5Nw/article-cover_image-shrink_600_2000/B4DZg0Zys2G8AQ-/0/1753225835824?e=2147483647&v=beta&t=E8W_lE1lA_6tclaotJmWhpLj12xWeeQ67ITA4olZBtE)

rot169, Attack Detect Defend

Most Windows users interact with COM every day, whether they know it or not. Actions like embedding Excel into Word documents, using right-click options like “Add to archive” or “Scan with Bitdefender,” and even copying and pasting content across applications, all rely on the Component Object Model behind the scenes.

In this article, I’ll break down the unseen mechanics of COM at a high level and share with you all the information I gathered during my quest of understanding COM.

### What is Component Object Model?

Per Windows definition, COM is a platform-independent, distributed, object-oriented system for creating binary software components that can interact. COM is the foundation technology for Microsoft's OLE (compound documents) and ActiveX (Internet-enabled components) technologies.

The purpose of COM is to enable software components to interact across different programming languages, execution environments, and processes within Windows. It provides a standardized way for objects to expose functionality without needing to know their internal implementation.

Adding an Excel sheet into a Word document is possible thanks to OLE (Object Linking and Embedding) which is an application of COM.

### How does COM work?

Now that we have defined what COM is and how it could be useful, we will now dive into its inner working and how it operates under the hood.

The image below is from one of "Andy" videos. Andy aka rot169 creates a lot of amazing videos on several topics of SecOps. You should check his youtube channel: [https://www.youtube.com/@rot169/videos](https://www.youtube.com/@rot169/videos?trk=article-ssr-frontend-pulse_little-text-block)

rot169, Attack Detect Defend

When a COM client wants to use functionality from a COM component, it first initializes the COM library for the calling thread using CoInitialize or CoInitializeEx, and then calls CoCreateInstance() and provides two things: the CLSID (Class ID) and the IID (Interface ID). The CLSID tells COM which class or component to create, for example a calculator object, while the IID specifies which interface the client wants to use, such as basic calculator functions versus extended math features. Essentially, the CLSID identifies "what" to create and the IID defines "how" the client wants to interact with it.

When a COM-based DLL is used, the COM system follows a precise process. First, using the CLSID, COM consults the Windows Registry to find the DLL path registered for that CLSID. It then loads the DLL into memory using LoadLibrary(). Once loaded, COM calls the exported function DllGetClassObject(), which every COM DLL must implement. This function returns a class factory, an object that implements the IClassFactory interface and that is responsible for creating instances of a specific COM class on behalf of clients. The COM system or client then calls the factory's CreateInstance() method to create the actual COM object in memory. The returned object exposes only the interface(s) the client asked for, and all interaction occurs via these interfaces.

For COM EXEs (out-of-process servers), the flow is similar to DLL-based COM servers but involves launching a separate process. When a COM EXE is registered, the Windows Registry maps the CLSID to the path of the executable. When a client calls CoCreateInstance() with a CLSID that corresponds to a COM EXE, the COM runtime checks whether the EXE is already running. If it isn’t, COM launches the EXE. Once running, the EXE must call CoRegisterClassObject() to register its class factory, an object that knows how to create instances of the requested class. COM then communicates with the EXE using RPC (Remote Procedure Call) to obtain the class factory. As with DLLs, it calls CreateInstance() to create the COM object, but in this case, the object lives in the EXE’s process. The client interacts with it via inter-process COM, using a mechanism called Marshaling.

When the COM object is created, the COM runtime doesn't give the client direct access to the entire object. Instead, it provides an interface pointer, which exposes only the specific functionality defined by the requested interface. This ensures strict encapsulation and separation between interface and implementation.

Internally, the interface pointer doesn't point directly to the object's data, but rather to a vtable (virtual method table). This vtable is a structure that holds function pointers, with each slot corresponding to a method in the interface. When the client calls a method like Add() or Open() through the interface pointer, that call is routed through the vtable to the actual function implementation inside the COM object's class. This level of indirection allows COM to be language-independent, efficient and flexible, because the calling code doesn't need to know how the method works, only that it exists.

Imagine calling room service in a hotel. The phone you use is like the interface pointer. When you dial a service number, you're connected to the front desk (the vtable), which then contacts the kitchen (the class that implements the logic). You never interact directly with the kitchen staff, you simply request a service, and the system handles the rest. Similarly, the COM client never sees the internal implementation, it just calls methods through the interface.

A COM object can implement multiple interfaces. For example, a single object might support both ICalculator and IExtendedCalculator. When a client obtains one interface, it can request access to another using the QueryInterface() method. This allows the client to ask the object: "Do you also support this other interface?". If the object does, COM returns a new interface pointer that provides access to the additional functionality.

All COM interfaces ultimately inherit from the base interface IUnknown, which defines three critical methods:

- QueryInterface(): Used to discover and obtain pointers to other interfaces implemented by the same object.
- AddRef(): Increases the reference count, indicating that a client is using the object.
- Release(): Decreases the reference count. When it reaches zero, the object deallocates itself.

COM uses reference counting to manage the lifetime of objects. Each time a client obtains an interface pointer, AddRef() is called. When the client is finished with the object, it must call Release() to decrement the count. When no clients are using the object (reference count hits zero), the object automatically cleans itself up.

Finally, when a COM client application is done using COM services entirely, it must call CoUninitialize() to release any remaining system resources associated with COM initialization.

Bonus: I asked my friend ChatGPT to draw this beautiful diagram to summarize the flow ^^

ChatGPT

References:

\[1\] [https://learn.microsoft.com/en-us/windows/win32/com/component-object-model--com--portal](https://www.linkedin.com/redir/redirect?url=https%3A%2F%2Flearn%2Emicrosoft%2Ecom%2Fen-us%2Fwindows%2Fwin32%2Fcom%2Fcomponent-object-model--com--portal&urlhash=Nirv&trk=article-ssr-frontend-pulse_little-text-block)

\[2\] [https://www.youtube.com/watch?v=svFundrBIiQ](https://www.youtube.com/watch?v=svFundrBIiQ&trk=article-ssr-frontend-pulse_little-text-block)

\[3\] [https://www.221bluestreet.com/offensive-security/windows-components-object-model/demystifying-windows-component-object-model-com#out-of-process-server](https://www.linkedin.com/redir/redirect?url=https%3A%2F%2Fwww%2E221bluestreet%2Ecom%2Foffensive-security%2Fwindows-components-object-model%2Fdemystifying-windows-component-object-model-com%23out-of-process-server&urlhash=MKt0&trk=article-ssr-frontend-pulse_little-text-block)

``````````

``

[Like](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_like-toggle_like-cta)

[Comment](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_comment-cta)

````

- Copy
- LinkedIn
- Facebook
- X

Share


````

[198](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_likes-count_social-actions-reactions)`````````````` [9 Comments](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_likes-count_social-actions-comments)

[Yash Kanzariya](https://in.linkedin.com/in/yash-kanzariya-7686bb237?trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_actor-name)


































6mo



- [Report this comment](https://www.linkedin.com/uas/login?session_redirect=https%3A%2F%2Fwww.linkedin.com%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_ellipsis-menu-semaphore-sign-in-redirect&guestReportContentType=COMMENT&_f=guest-reporting)

Thanks for sharing, Steven

[Like](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_like) [Reply](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_reply) [1 Reaction](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_reactions)
2 Reactions


[Nelson Cacuango](https://ec.linkedin.com/in/nelsoncgo?trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_actor-name)


































6mo



- [Report this comment](https://www.linkedin.com/uas/login?session_redirect=https%3A%2F%2Fwww.linkedin.com%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_ellipsis-menu-semaphore-sign-in-redirect&guestReportContentType=COMMENT&_f=guest-reporting)

Great article, thanks by sharing! 🧑🏻💻

[Like](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_like) [Reply](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_reply) [1 Reaction](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_reactions)
2 Reactions


[Belynda Latre E. LAWSON BETUM](https://tg.linkedin.com/in/b%C3%A9lynda-latr%C3%A9-e-lawson-betum/en?trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_actor-name)


































6mo



- [Report this comment](https://www.linkedin.com/uas/login?session_redirect=https%3A%2F%2Fwww.linkedin.com%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_ellipsis-menu-semaphore-sign-in-redirect&guestReportContentType=COMMENT&_f=guest-reporting)

Loved the honesty, [Steven Dejean](https://tg.linkedin.com/in/steven-dejean?trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment-text).
Arguing with ChatGPT and Copilot? That’s peak modern learning 😄
The way you demystified COM while embracing the struggle is exactly what makes technical content relatable.

Thanks for doing the hard part so we can all benefit from the magic (unseen or not)!

[Like](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_like) [Reply](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_reply) [1 Reaction](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_reactions)
2 Reactions


[Isidore Badéra ALI](https://tg.linkedin.com/in/isid0r3?trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_actor-name)


































7mo



- [Report this comment](https://www.linkedin.com/uas/login?session_redirect=https%3A%2F%2Fwww.linkedin.com%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_ellipsis-menu-semaphore-sign-in-redirect&guestReportContentType=COMMENT&_f=guest-reporting)

😂 (If you can ^^), visiblement tu as bien fait de préciser 🤣 [Steven](https://tg.linkedin.com/in/steven-dejean?trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment-text)

[Like](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_like) [Reply](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_reply) [1 Reaction](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_reactions)
2 Reactions


[Aakash Raman](https://www.linkedin.com/in/aakash-raman-66676b38?trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_actor-name)


































7mo



- [Report this comment](https://www.linkedin.com/uas/login?session_redirect=https%3A%2F%2Fwww.linkedin.com%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_ellipsis-menu-semaphore-sign-in-redirect&guestReportContentType=COMMENT&_f=guest-reporting)

Really interesting read [Steven Dejean](https://tg.linkedin.com/in/steven-dejean?trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment-text)!

[Like](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_like) [Reply](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_reply) [1 Reaction](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments-action_comment_reactions)
2 Reactions


[See more comments](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_comments_comment-see-more)

To view or add a comment, [sign in](https://www.linkedin.com/signup/cold-join?session_redirect=%2Fpulse%2Funseen-magic-com-steven-dejean-o7ipf&trk=article-ssr-frontend-pulse_x-social-details_feed-cta-banner-cta)

## More articles by Steven Dejean

- [Hunting and Detecting Cobalt Strike’s In-Memory PowerShell Toolsets](https://www.linkedin.com/pulse/hunting-detecting-cobalt-strikes-in-memory-powershell-steven-dejean-3fucf)







Nov 25, 2025



### Hunting and Detecting Cobalt Strike’s In-Memory PowerShell Toolsets





Cobalt Strike is one of the most widely used C2 frameworks in both red-team operations and real-word intrusions. One of…



````




220


``````````````



5 Comments



- [Kerberos Authentication](https://www.linkedin.com/pulse/kerberos-authentication-steven-dejean-gc1vf)







Mar 28, 2024



### Kerberos Authentication





In this article, I will talk about Kerberos protocol, how it works and the mechanism behind it. I hope you enjoy the…



````




31


``````````````



5 Comments



- [Something about Access Tokens](https://www.linkedin.com/pulse/something-access-tokens-steven-dejean-2dbwf)







Feb 23, 2024



### Something about Access Tokens





Hello everyone. In this article, we will talk about Access Tokens and how it influences the experience of end users in…



````




23


``````````````



7 Comments



- [File deletion in a NTFS Filesystem](https://www.linkedin.com/pulse/file-deletion-ntfs-filesystem-steven-dejean-2t6pf)







Jan 19, 2024



### File deletion in a NTFS Filesystem





Hello, in this article, we will be looking, on a high-level at the processes that occur when we delete a file in a NTFS…



````




49


``````````````



15 Comments




## Explore content categories

- [Career](https://www.linkedin.com/top-content/career/)
- [Productivity](https://www.linkedin.com/top-content/productivity/)
- [Finance](https://www.linkedin.com/top-content/finance/)
- [Soft Skills & Emotional Intelligence](https://www.linkedin.com/top-content/soft-skills-emotional-intelligence/)
- [Project Management](https://www.linkedin.com/top-content/project-management/)
- [Education](https://www.linkedin.com/top-content/education/)
- [Technology](https://www.linkedin.com/top-content/technology/)
- [Leadership](https://www.linkedin.com/top-content/leadership/)
- [Ecommerce](https://www.linkedin.com/top-content/ecommerce/)
- [User Experience](https://www.linkedin.com/top-content/user-experience/)
- [Recruitment & HR](https://www.linkedin.com/top-content/recruitment-hr/)
- [Customer Experience](https://www.linkedin.com/top-content/customer-experience/)
- [Real Estate](https://www.linkedin.com/top-content/real-estate/)
- [Marketing](https://www.linkedin.com/top-content/marketing/)
- [Sales](https://www.linkedin.com/top-content/sales/)
- [Retail & Merchandising](https://www.linkedin.com/top-content/retail-merchandising/)
- [Science](https://www.linkedin.com/top-content/science/)
- [Supply Chain Management](https://www.linkedin.com/top-content/supply-chain-management/)
- [Future Of Work](https://www.linkedin.com/top-content/future-of-work/)
- [Consulting](https://www.linkedin.com/top-content/consulting/)
- [Writing](https://www.linkedin.com/top-content/writing/)
- [Economics](https://www.linkedin.com/top-content/economics/)
- [Artificial Intelligence](https://www.linkedin.com/top-content/artificial-intelligence/)
- [Employee Experience](https://www.linkedin.com/top-content/employee-experience/)
- [Workplace Trends](https://www.linkedin.com/top-content/workplace-trends/)
- [Fundraising](https://www.linkedin.com/top-content/fundraising/)
- [Networking](https://www.linkedin.com/top-content/networking/)
- [Corporate Social Responsibility](https://www.linkedin.com/top-content/corporate-social-responsibility/)
- [Negotiation](https://www.linkedin.com/top-content/negotiation/)
- [Communication](https://www.linkedin.com/top-content/communication/)
- [Engineering](https://www.linkedin.com/top-content/engineering/)
- [Hospitality & Tourism](https://www.linkedin.com/top-content/hospitality-tourism/)
- [Business Strategy](https://www.linkedin.com/top-content/business-strategy/)
- [Change Management](https://www.linkedin.com/top-content/change-management/)
- [Organizational Culture](https://www.linkedin.com/top-content/organizational-culture/)
- [Design](https://www.linkedin.com/top-content/design/)
- [Innovation](https://www.linkedin.com/top-content/innovation/)
- [Event Planning](https://www.linkedin.com/top-content/event-planning/)
- [Training & Development](https://www.linkedin.com/top-content/training-development/)

Show more

Show less