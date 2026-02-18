# https://www.cobaltstrike.com/blog/in-memory-evasion

This website uses cookies. You may change your settings at any time.

AcceptReject AllManage Cookies

Cookie Preferences

[Home](https://www.cobaltstrike.com/) » [Blog](https://www.cobaltstrike.com/blog/) » In-Memory Evasion

# In-Memory Evasion

Thursday 08 February, 2018

Many analysts and automated solutions take advantage of various memory detections to find injected DLLs in memory. Memory detections look at the properties (and content) of processes, threads, and memory to find indicators of malicious activity in the current process.

In-memory Evasion is a four-part mini course on the cat and mouse game related to memory detections. This course is for red teams that want to update their tradecraft in this area. It’s also for blue teams that want to understand the red perspective on these techniques. Why do they work in some situations? How is it possible to work around these heuristics in other cases?

Part 1 of In-memory Evasion introduces Memory Detections. This lecture walks through the observable properties of Processes, Threads, and Memory with Process Hacker. Common heuristics, the in-memory indicators we want to evade, are covered too.

In-memory Evasion (1 of 4) - Detections - YouTube

[Photo image of Cobalt Strike Archive](https://www.youtube.com/channel/UCJU2r634VNPeCRug7Y7qdcw?embeds_referring_euri=https%3A%2F%2Fwww.cobaltstrike.com%2F)

Cobalt Strike Archive

21.2K subscribers

[In-memory Evasion (1 of 4) - Detections](https://www.youtube.com/watch?v=lz2ARbZ_5tE)

Cobalt Strike Archive

Search

Watch later

Share

Copy link

Info

Shopping

Tap to unmute

If playback doesn't begin shortly, try restarting your device.

Full screen is unavailable. [Learn More](https://support.google.com/youtube/answer/6276924)

More videos

## More videos

You're signed out

Videos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.

CancelConfirm

Share

Include playlist

An error occurred while retrieving sharing information. Please try again later.

[Watch on](https://www.youtube.com/watch?v=lz2ARbZ_5tE&embeds_referring_euri=https%3A%2F%2Fwww.cobaltstrike.com%2F)

0:00

0:00 / 35:10

•Live

•

Part 2 of In-memory Evasion goes through A Payload’s Life. This lecture discusses the heuristics in Part 1 and where they interact with actions taken by a representative offense platform (in this case, Cobalt Strike). This lecture makes the case that offense toolsets do strange things, but in some cases, these deviations from normal program behavior are optional.

In-memory Evasion (2 of 4) - A Payload's Life - YouTube

[Photo image of Cobalt Strike Archive](https://www.youtube.com/channel/UCJU2r634VNPeCRug7Y7qdcw?embeds_referring_euri=https%3A%2F%2Fwww.cobaltstrike.com%2F)

Cobalt Strike Archive

21.2K subscribers

[In-memory Evasion (2 of 4) - A Payload's Life](https://www.youtube.com/watch?v=TC2pyS_V-IA)

Cobalt Strike Archive

Search

Watch later

Share

Copy link

Info

Shopping

Tap to unmute

If playback doesn't begin shortly, try restarting your device.

Full screen is unavailable. [Learn More](https://support.google.com/youtube/answer/6276924)

More videos

## More videos

You're signed out

Videos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.

CancelConfirm

Share

Include playlist

An error occurred while retrieving sharing information. Please try again later.

[Watch on](https://www.youtube.com/watch?v=TC2pyS_V-IA&embeds_referring_euri=https%3A%2F%2Fwww.cobaltstrike.com%2F)

0:00

0:00 / 35:37

•Live

•

Part 3 of this course discusses Evasion. General tips to avoid the strange behavior these detections find are discussed. This lecture then gets into the meat: options to configure how Cobalt Strike’s Beacon payload lives in memory are explained and demonstrated. This lecture also shows how to conduct an OPSEC review of your configuration prior to action on a target. Finally, this lecture concludes with a discussion on process context and how it influences the amount of suspect actions/indicators an automated solution will allow.

In-memory Evasion (3 of 4) - Evasion - YouTube

[Photo image of Cobalt Strike Archive](https://www.youtube.com/channel/UCJU2r634VNPeCRug7Y7qdcw?embeds_referring_euri=https%3A%2F%2Fwww.cobaltstrike.com%2F)

Cobalt Strike Archive

21.2K subscribers

[In-memory Evasion (3 of 4) - Evasion](https://www.youtube.com/watch?v=tzSkblL1fkI)

Cobalt Strike Archive

Search

Watch later

Share

Copy link

Info

Shopping

Tap to unmute

If playback doesn't begin shortly, try restarting your device.

Full screen is unavailable. [Learn More](https://support.google.com/youtube/answer/6276924)

More videos

## More videos

You're signed out

Videos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.

CancelConfirm

Share

Include playlist

An error occurred while retrieving sharing information. Please try again later.

[Watch on](https://www.youtube.com/watch?v=tzSkblL1fkI&embeds_referring_euri=https%3A%2F%2Fwww.cobaltstrike.com%2F)

0:00

0:00 / 34:01

•Live

•

Part 4 concludes the course with a brief discussion of Threat Emulation. Cobalt Strike’s flexibility in this area is demonstrated to steer an analyst to believe they’re dealing with a specific real-world actor in a simulated incident.

In-memory Evasion (4 of 4) - Threat Emulation - YouTube

[Photo image of Cobalt Strike Archive](https://www.youtube.com/channel/UCJU2r634VNPeCRug7Y7qdcw?embeds_referring_euri=https%3A%2F%2Fwww.cobaltstrike.com%2F)

Cobalt Strike Archive

21.2K subscribers

[In-memory Evasion (4 of 4) - Threat Emulation](https://www.youtube.com/watch?v=1-0bUFwUiWk)

Cobalt Strike Archive

Search

Watch later

Share

Copy link

Info

Shopping

Tap to unmute

If playback doesn't begin shortly, try restarting your device.

Full screen is unavailable. [Learn More](https://support.google.com/youtube/answer/6276924)

More videos

## More videos

You're signed out

Videos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.

CancelConfirm

Share

Include playlist

An error occurred while retrieving sharing information. Please try again later.

[Watch on](https://www.youtube.com/watch?v=1-0bUFwUiWk&embeds_referring_euri=https%3A%2F%2Fwww.cobaltstrike.com%2F)

0:00

0:00 / 9:21

•Live

•

Part 5 is an April 2018 addendum to this course. This video covers the memory-related threat emulation and evasion features in Cobalt Strike 3.11.

In-memory Evasion (5 of 4) - Cobalt Strike 3.11 Addendum - YouTube

[Photo image of Cobalt Strike Archive](https://www.youtube.com/channel/UCJU2r634VNPeCRug7Y7qdcw?embeds_referring_euri=https%3A%2F%2Fwww.cobaltstrike.com%2F)

Cobalt Strike Archive

21.2K subscribers

[In-memory Evasion (5 of 4) - Cobalt Strike 3.11 Addendum](https://www.youtube.com/watch?v=uWVH9l2GMw4)

Cobalt Strike Archive

Search

Watch later

Share

Copy link

Info

Shopping

Tap to unmute

If playback doesn't begin shortly, try restarting your device.

Full screen is unavailable. [Learn More](https://support.google.com/youtube/answer/6276924)

More videos

## More videos

You're signed out

Videos you watch may be added to the TV's watch history and influence TV recommendations. To avoid this, cancel and sign in to YouTube on your computer.

CancelConfirm

Share

Include playlist

An error occurred while retrieving sharing information. Please try again later.

[Watch on](https://www.youtube.com/watch?v=uWVH9l2GMw4&embeds_referring_euri=https%3A%2F%2Fwww.cobaltstrike.com%2F)

0:00

0:00 / 30:37

•Live

•

I’m a big believer that red teams should know the defenses they work with and know how their tools interact with these defenses. The area of memory detections has developed considerably over the past several years. Whether you’re on the red or blue side, I hope you find this perspective helpful.

#### [Raphael Mudge](https://www.cobaltstrike.com/profile/raphael-mudge)

Founder

[View Profile](https://www.cobaltstrike.com/profile/raphael-mudge)

TOPICS


- [Red Team](https://www.cobaltstrike.com/blog?_sft_cornerstone=red-team "Red Team")