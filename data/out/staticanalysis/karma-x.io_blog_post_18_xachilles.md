# https://karma-x.io/blog/post/18/?=xachilles

![The Problem With YARA: Evading Elastic Security EDR with a NOP instruction](https://www.karma-x.io/static/img/havoc_achilles.png)

## The Problem With YARA: Evading Elastic Security EDR with a NOP instruction

Feb. 10, 2024 \| Categories:

[Research](https://karma-x.io/blog/category/Research/)

YARA's strength, is also its Achilles' heel

🔍 STATIC SIGNATURE VULNERABILITY

# The Problem With YARA

How One NOP Instruction Evades Elastic Security EDR

**YARA rules stand as powerful sentinels against static cyber threats.** Their strength, however, is also their Achilles' heel. The static nature of YARA rules means they can be effortlessly circumvented, especially when they are made public.

Elastic Security, for instance, publishes their YARA rules on [Github: Elastic Security - Protection Artifacts](https://github.com/elastic/protections-artifacts), potentially offering adversaries a blueprint to dodge detection simply by trivially altering their malicious code.

### 🎯 The Core Problem

**Public signatures = Public evasion roadmap**

In a recent [Karma-X blog](https://karma-x.io/blog/post/15/?=elasticblog), we took a look at Havoc C2 Framework, which describes itself as a **"modern and malleable post-exploitation command and control framework."** In revisiting that post, we would be remiss if we didn't point out that other EDR vendors already had published some detection mechanisms for this Framework.

**That said**, by publishing their YARA rules, an adversary can trivially make changes to generated Havoc agents to bypass their YARA. Let's take a closer look.

## 📋 Elastic's Three YARA Rules for Havoc C2

Elastic publishes 3 YARA rules for Havoc C2:

#### Rule \#1: Windows\_Trojan\_Havoc\_77f3d40e (Created: 2022-10-20)

```
rule Windows_Trojan_Havoc_77f3d40e {
    meta:
        author = "Elastic Security"
        id = "77f3d40e-9365-4e76-a1a3-36d128e775a9"
        fingerprint = "95d35d167df7f77f23b1afb1b7655cc47830c9986c54791b562c33db8f2773ae"
        creation_date = "2022-10-20"
        last_modified = "2022-11-24"
        threat_name = "Windows.Trojan.Havoc"
        reference_sample = "3427dac129b760a03f2c40590c01065c9bf2340d2dfa4a4a7cf4830a02e95879"
        severity = 100
        arch_context = "x86"
        scan_context = "file, memory"
        license = "Elastic License v2"
        os = "windows"
    strings:
        $core = { 48 ?? ?? 2C 06 00 00 00 ?? ?? 48 ?? ?? 5C 06 00 00 00 ... }
        $commands_table = { 0B 00 00 00 ?? ?? ?? ?? ?? ?? ?? ?? 64 00 00 00 ... }
        $hashes_0 = { F6 99 5A 2E }
        $hashes_1 = { DA 81 B3 C0 }
        ... [multiple hash patterns]
    condition:
        $core or ($commands_table and all of ($hashes*))
}
```

#### Rule \#2: Windows\_Trojan\_Havoc\_9c7bb863 (Created: 2023-04-28)

```
rule Windows_Trojan_Havoc_9c7bb863 {
    meta:
        author = "Elastic Security"
        id = "9c7bb863-b6c2-4d5f-ae50-0fd900f1d4eb"
        creation_date = "2023-04-28"
        last_modified = "2023-06-13"
        threat_name = "Windows.Trojan.Havoc"
        severity = 100
    strings:
        $a1 = { 56 48 89 E6 48 83 E4 F0 48 83 EC 20 E8 0F 00 00 00 48 89 F4 5E C3 }
        $a2 = { 65 48 8B 04 25 60 00 00 00 }
    condition:
        all of them
}
```

#### Rule \#3: Windows\_Trojan\_Havoc\_88053562 (Created: 2024-01-04)

```
rule Windows_Trojan_Havoc_88053562 {
    meta:
        author = "Elastic Security"
        id = "88053562-ae19-44fe-8aaf-d6b9687d6b80"
        creation_date = "2024-01-04"
        last_modified = "2024-01-12"
        threat_name = "Windows.Trojan.Havoc"
        severity = 100
    strings:
        $a = { 48 81 EC F8 04 00 00 48 8D 7C 24 78 44 89 8C 24 58 05 00 00 ... }
    condition:
        all of them
}
```

## 🧪 The Evasion Experiment

1

### Test Initial Detection

We tested the original Havoc demon.x64.bin using yara64.exe:

![Initial YARA Detection](https://www.karma-x.io/static/img/yara_latest_detection_havoc.png)

**Interesting Finding:** The Demon agent we compiled from the previous blog already evades Elastic's first YARA rule written in 2022. That tests our theory—maybe the authors of HAVOC C2 specifically rewrote something to evade Elastic's YARA rule. Either way, it looks like Elastic has two more rules that do detect the latest version.

2

### Analyze with Ghidra

Let's take a look at Ghidra to see what they are detecting:

![Ghidra Analysis 1](https://www.karma-x.io/static/img/ghidra_havoc_1.png)![Ghidra Analysis 2](https://www.karma-x.io/static/img/ghidra_havoc_2.png)

**Discovery:** There are two unique patterns of bytes that Elastic thinks are inherently attributable to the Havoc framework. We didn't dig too deeply, but the second one seems to be **DemonConfig function** where source is provided. The first signature focuses on the very beginning of the Demon assembly shellcode which is provided as source and compiles each time an agent is configured.

![Havoc Payload Config](https://www.karma-x.io/static/img/havoc_payload.png)

3

### Evade Rule \#2: Add a NOP Instruction

#### 🔧 The Trivial Modification

Ok, let's just modify the assembly and include a **NOP instruction** to evade the first YARA rule:

![NOP Instruction Added](https://www.karma-x.io/static/img/havoc_nop_instruction.png)

Follow the same steps as previous blog on recompiling Havoc, and voilà:

![After NOP - Rule 2 Evaded](https://www.karma-x.io/static/img/yara_latest_detection_havoc_2.png)

#### ✅ Rule \#2 Evaded

One simple NOP instruction bypassed the second YARA rule

4

### Evade Rule \#3: Modify Stack Size

The third YARA rule is in the Demon source. That's a little harder to compile, and rather than spend the time necessary to rebuild that (despite author warnings), let's just modify something inconsequential with HxD. **As long as we don't add any bytes, we shouldn't have to worry about any offset issues.**

![HxD Hex Editor](https://www.karma-x.io/static/img/havoc_hxd.png)

#### 🔧 The Stack Modification

All we should have to modify is the instructions which reserve stack space and decommit stack space. We could easily add a stack variable in source, but let's knock this out.

![Stack Size Location](https://www.karma-x.io/static/img/ghidra_havoc_2.png)

We change the stack size to **0x5f8** instead of **0x4f8** and save. Let's rerun with Elastic's YARA rule:

![All Rules Evaded](https://www.karma-x.io/static/img/havoc_yara_evade_full.png)

#### ✅ All 3 Rules Evaded

Simple modifications bypassed all Elastic YARA signatures

#### ❌ Before Modifications

Detected by 2 out of 3 Elastic YARA rules

#### ✅ After Modifications

Evades all 3 Elastic YARA rules

## ⏱️ Time to Evade All Rules

**Less than 10 minutes**

One NOP instruction. One hex edit. Complete evasion.

## 🛡️ But What About Karma-X?

Anyways, let's see what happens if we inject that directly into Karma-X **(without any YARA rules to target this binary)**:

![Karma-X Detection](https://www.karma-x.io/static/img/havoc_detection.png)

## 🎯 Protection Without Signatures

Even with all YARA rules evaded, Karma-X stopped the attack through **structural protection**. No signatures needed. No trivial bypasses possible.

This is the difference between detection and protection.

**📦 Contributing Back to the Community**

We updated the Elastic YARA rule here:

[View on Karma-X Github →](https://github.com/Karma-X-Inc/protections-artifacts/blob/main/yara/rules/Windows_Trojan_Havoc.yar)

## 🚀 Beyond Static Signatures

For more information about how Karma-X protects you in a more sophisticated way than static signatures:

[Start Free with Vitamin-K](https://karma-x.io/account/)

(after signing up and logging in)

document

##### Easy Install

From small business to enterprise, Karma-X installs simply and immediately adds peace of mind

shop

##### Integration Ready

Karma-X doesn't interfere with other software, only malware and exploits, due to its unique design.

time-alarm

##### Reduce Risk

Whether adversary nation or criminal actors, Karma-X significantly reduces exploitation risk of any organization

office

##### Updated Regularly

Update to deploy new defensive techniques to suit your organization's needs as they are offered

box-3d-50

## Deploy    Karma-X

[Get Karma-X!](https://karma-x.io/contact-us/)

💬 Ask our AI Assistant Kali

Kali - Karma-X AI Assistant×

Send