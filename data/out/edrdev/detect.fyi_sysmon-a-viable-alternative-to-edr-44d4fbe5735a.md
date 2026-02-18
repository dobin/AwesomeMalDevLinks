# https://detect.fyi/sysmon-a-viable-alternative-to-edr-44d4fbe5735a

[Sitemap](https://detect.fyi/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fdetect.fyi%2Fsysmon-a-viable-alternative-to-edr-44d4fbe5735a&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fdetect.fyi%2Fsysmon-a-viable-alternative-to-edr-44d4fbe5735a&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:64:64/1*dmbNkD5D-u45r44go_cf0g.png)

[**Detect FYI**](https://detect.fyi/?source=post_page---publication_nav-d5fd8f494f6a-44d4fbe5735a---------------------------------------)

·

Follow publication

[![Detect FYI](https://miro.medium.com/v2/resize:fill:76:76/1*ayMhoNccbO0IxQ1UPFv0SA.png)](https://detect.fyi/?source=post_page---post_publication_sidebar-d5fd8f494f6a-44d4fbe5735a---------------------------------------)

Threat Detection Engineering and DFIR Insights

Follow publication

# Sysmon: a viable alternative to EDR?

[![Alex Teixeira](https://miro.medium.com/v2/resize:fill:64:64/1*awwcCrqzd_wPjZDuJKGtOQ.jpeg)](https://ateixei.medium.com/?source=post_page---byline--44d4fbe5735a---------------------------------------)

[Alex Teixeira](https://ateixei.medium.com/?source=post_page---byline--44d4fbe5735a---------------------------------------)

Follow

7 min read

·

Jul 4, 2024

165

12

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3D44d4fbe5735a&operation=register&redirect=https%3A%2F%2Fdetect.fyi%2Fsysmon-a-viable-alternative-to-edr-44d4fbe5735a&source=---header_actions--44d4fbe5735a---------------------post_audio_button------------------)

Share

I've been recently engaged in workshops with distinct clients from completely different industries/verticals and this is a recurring topic.

**Sysmon + SIEM Detection Rules.** Is that idea worth pursuing?

If you want to save your time from reading, the answer is a clear **NO**. Stick around if you want to know why based on very practical arguments.

## Why NOT Sysmon?

First of all, pretty much everything I write here is focused or applies to **enterprise** environment. Big deployments. Big budgets.

The opinion here doesn't apply to home or student lab environments.

It also doesn't apply to organizations restricted from using commercial products, mainly relying on free or open source software.

Also, it doesn't apply to research labs or environments used by practitioners to play around with the **rich** [Sysmon](https://learn.microsoft.com/en-us/sysinternals/downloads/sysmon) log telemetry.

![](https://miro.medium.com/v2/resize:fit:490/1*VBfZhlvjMk9Br7KKjmkRcQ.png)

Lastly, I'm not speaking about forensics or any post-incident use case, I'm talking about leveraging Sysmon's log telemetry for **building detection**.

### Goals & Perspectives

If you put yourself in a position to lead a security monitoring practice for a big enterprise, with a relatively _deep_ pocket and limited human resources, I believe it's easier to understand my point here.

That's completely different from someone with limited budget and contract restrictions — besides the human resource limitation everyone is subject to.

Is it all about money in enterprise environment then? Pretty much, yes, especially if you consider _time_ as a monetary investment too.

Deploying Sysmon is one task, maintaining that deployment is another, and using Sysmon’s log telemetry to **build detection** mechanisms is yet another complete, distinct challenge.

> Storing even the richest log data has little to no detection value until it is actively consumed (Detection).

So assume the goal here is **to leverage endpoint signals to detect threats**.

As a leader, here's what you need to account for:

- **Detection Surface:** your team needs to cover as much attack surface as possible given what the org is exposed to. In this case, we are speaking about endpoint security and mainly commodity malware, a very common attack vector with new variants emerging in a daily basis.
- **Deployment Maintenance:** besides being able to deploy the agent to as many endpoints as possible, that needs to happen fast. Troubleshooting or updating those agents should also be painless.

The Out-of-the-Box value one can get from Sysmon is not comparable to what a modern EDR is able to bring to the table which sounds unfair since we are speaking about a free product versus a commercial one.

Still, this comparison is valid today, hence this article. Next, we deep dive into the pros/cons about using an EDR.

## Sysmon x EDR

Here's perhaps harder to realize if you haven't used a decent EDR before.

The first one I was exposed to was [Carbon Black](https://www.vmware.com/products/endpoint-detection-and-response.html), almost 10 years ago!

The first thing to highlight here is most EDR products will provide multiple capabilities, from rich log telemetry, to alert signals, to response features.

If you are all into raw telemetry, please do check out [this cool project](https://github.com/tsale/EDR-Telemetry) I had the pleasure to bring to life with [Kostas](https://kostas-ts.medium.com/) which highlights the log telemetry capabilities from a number of EDRs.

Given all those features, the focus here is on **detection capabilities** only.

### Telemetry differs from Detection

It sounds obvious (to you and me), but many people need to read this: an _alert_ event differs from a regular log event.

An _alert_ event carries a clear _alert_ signal such as "Suspicious MS Office child process". A regular event simply reads "Here's a new process created".

I've already written about [the importance of endpoint telemetry and EDRs](https://detect.fyi/detection-surface-the-role-of-endpoint-telemetry-861f58cf3b79) here, but simply put, having only the _raw_ telemetry is like having crude oil instead of a byproduct such as fuel for a car.

Until you are able to refine it, there are very few use cases for it. That means no value until you are able to consume it.

Now, how hard is it to craft good detection out of raw endpoint telemetry?

It is extremely challenging!

I have enabled a team to maintain and further develop an alert framework with over 400 custom detections/indicators based on EDR _raw_ telemetry.

It's challenging, trust me.

Here's an example of what can be done with _raw_ endpoint telemetry:

![](https://miro.medium.com/v2/resize:fit:700/0*wvEbHLEZfSR2gxEp.png)

From [https://detect.fyi/rats-race-detecting-remote-access-tools-beyond-pattern-based-indicators-5c864b171892](https://detect.fyi/rats-race-detecting-remote-access-tools-beyond-pattern-based-indicators-5c864b171892)

Nevertheless, most organizations do not have the engineering power or skills to pursue such route. Besides, maintaining that is not an easy task if you don't design a framework considering scalability since the beginning.

## Get Alex Teixeira’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

Perhaps another great topic for an upcoming article: what's the difference between building _detections_ and building _analytics_?

SIEM-wise, most times we are focused on the latter while the actual _detection_ is done somewhere else (in an EDR?).

That’s a major decision in your strategy, and here I start defending why you should _outsource_ those detections to an EDR.

### Throughput: Product Team x Your Team

This is the strongest argument I can give you.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*vtUlRuiinyp_asknam_vYw.png)

When it comes to delivering _new_ detections, your team is simply not able to compete against a research team part of a specific product such as an EDR.

Vendors are employing multiple researchers and engineers into the development of new detection code. It's their _core_ business sometimes.

Your (small) internal team needs to keep Sysmon alive while also having to design, test and deploy SIEM detections that leverage Sysmon logs.

That's a no-brainer to me. Stop doing that.

The EDR product detections (and features) will easily outpace what your team is able to accomplish with raw telemetry + SIEM rules. Period.

As a leader, I'd better allocate those resources since most teams are also performing other tasks outside detection engineering such as threat intel/modeling, incident response, etc.

As a practitioner, if you really enjoy doing that, consider joining a vendor or even building your own product. Many [successful stories](https://www.reddit.com/r/cybersecurity/comments/y86ei3/i_am_excanadian_national_defense_and_created_a/) out there!

I keep saying this:

> Today, the single most effective step to significantly increase detection coverage in an enterprise environment is installing a new EDR agent.

From the instant it's active, there are hundreds of scenarios monitored, no SIEM ruleset can be compared to this.

Most times, from a data collection perspective, simply ingesting the EDR alerts in your SIEM should suffice instead of also bringing raw telemetry in.

However, a SIEM is still the king when it comes to making sure no alert signal is missed and agents are installed in as many endpoints (servers and laptops) as possible. And those are just a few examples for use cases.

## The usual counter arguments

Here's what I have read or heard when it comes to Sysmon usage in the enterprise environment despite having an EDR at disposal.

### Sysmon is complementary

It's easy to agree with this one but I've seen with my own eyes how hard it is to keep a healthy and large Sysmon deployment running. That requires time which could have been spent on other Ops cycles.

On top of that, I'm not sure about:

1. What's the use case NOT covered by EDR. Sooner or later, vendors will be able to cover that given the development pace they employ today.
2. The value of such use case to justify the investment in maintaining multiple agents in an endpoint + Sysmon maintenance.

### EDR detections = Blackbox

That's true for most products. You won't be able to see a clear list of detections, let alone the code or logic behind them.

However, a modern EDR will cover a good bunch of detections so that the actual challenge becomes prioritizing which alert signals to engage your teams on. And here's where **SIEM Analytics** come into play!

Whenever a clear gap is identified your team should be able to build on top of EDR out-of-the-box capabilities — using the EDR itself.

For instance, most EDRs won't flag [TeamViewer](https://www.teamviewer.com/) and other legit Remote Assistance software as suspicious.

In that case, your EDR should provide a way to create **custom detection** that can be deployed to multiple endpoints without a hustle.

**Pro Tip:** what if you could craft EDR detection just like you do in a SIEM?

I mean, using the same [development workflows](https://ateixei.medium.com/jira-workflow-for-detection-engineering-teams-a7433f4c2a9f) and perhaps even the same query language?

Yes, **Microsoft** and **CrowdStrike** have a clear leverage here!

That's done by _selectively_ enabling the right EDR raw telemetry for later capturing it via a detection rule in your SIEM.

Or even better, by having a custom detection rule built on top of the EDR, and later aggregating this alert signal at the SIEM.

## Did I miss anything?

If you have a chance to get an EDR as part of technology stack **do it!**

Otherwise you are missing out and that's going to impact sooner or later in your security monitoring or detection strategy.

Feel free to reach out via [LinkedIn](https://www.linkedin.com/in/inode/) in case you want to exchange ideas around those topics or to provide any feedback.

_Written by_ [_Alex Teixeira_](https://opstune.com/alex/)

_Don’t forget_ [_subscribe_](https://ateixei.medium.com/subscribe) _to my stories to get notified when new articles come out! New stories don’t require membership for_ **_the first 24h_** _after publication._

[Siem](https://medium.com/tag/siem?source=post_page-----44d4fbe5735a---------------------------------------)

[Detection Engineering](https://medium.com/tag/detection-engineering?source=post_page-----44d4fbe5735a---------------------------------------)

[Security Analytics](https://medium.com/tag/security-analytics?source=post_page-----44d4fbe5735a---------------------------------------)

[Edr](https://medium.com/tag/edr?source=post_page-----44d4fbe5735a---------------------------------------)

[Incident Response](https://medium.com/tag/incident-response?source=post_page-----44d4fbe5735a---------------------------------------)

[![Detect FYI](https://miro.medium.com/v2/resize:fill:96:96/1*ayMhoNccbO0IxQ1UPFv0SA.png)](https://detect.fyi/?source=post_page---post_publication_info--44d4fbe5735a---------------------------------------)

[![Detect FYI](https://miro.medium.com/v2/resize:fill:128:128/1*ayMhoNccbO0IxQ1UPFv0SA.png)](https://detect.fyi/?source=post_page---post_publication_info--44d4fbe5735a---------------------------------------)

Follow

[**Published in Detect FYI**](https://detect.fyi/?source=post_page---post_publication_info--44d4fbe5735a---------------------------------------)

[2.5K followers](https://detect.fyi/followers?source=post_page---post_publication_info--44d4fbe5735a---------------------------------------)

· [Last published 4 days ago](https://detect.fyi/detection-satelital-dll-sideloading-via-mfc-turla-s-kazuar-v3-3de2fbd2d6af?source=post_page---post_publication_info--44d4fbe5735a---------------------------------------)

Threat Detection Engineering and DFIR Insights

Follow

[![Alex Teixeira](https://miro.medium.com/v2/resize:fill:96:96/1*awwcCrqzd_wPjZDuJKGtOQ.jpeg)](https://ateixei.medium.com/?source=post_page---post_author_info--44d4fbe5735a---------------------------------------)

[![Alex Teixeira](https://miro.medium.com/v2/resize:fill:128:128/1*awwcCrqzd_wPjZDuJKGtOQ.jpeg)](https://ateixei.medium.com/?source=post_page---post_author_info--44d4fbe5735a---------------------------------------)

Follow

[**Written by Alex Teixeira**](https://ateixei.medium.com/?source=post_page---post_author_info--44d4fbe5735a---------------------------------------)

[2.3K followers](https://ateixei.medium.com/followers?source=post_page---post_author_info--44d4fbe5735a---------------------------------------)

· [558 following](https://medium.com/@ateixei/following?source=post_page---post_author_info--44d4fbe5735a---------------------------------------)

I design and build detection and SIEM/EDR/XDR content for Enterprise #SecOps teams #DetectionEngineering [http://opstune.com](http://opstune.com/)

Follow

## Responses (12)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fdetect.fyi%2Fsysmon-a-viable-alternative-to-edr-44d4fbe5735a&source=---post_responses--44d4fbe5735a---------------------respond_sidebar------------------)

Cancel

Respond

See all responses

[Help](https://help.medium.com/hc/en-us?source=post_page-----44d4fbe5735a---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----44d4fbe5735a---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----44d4fbe5735a---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----44d4fbe5735a---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----44d4fbe5735a---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----44d4fbe5735a---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----44d4fbe5735a---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----44d4fbe5735a---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----44d4fbe5735a---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)