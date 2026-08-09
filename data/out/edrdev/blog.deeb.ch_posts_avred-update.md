# https://blog.deeb.ch/posts/avred-update/

# Avred background: Advances in Reversing Defender Signature Format

New findings from Windows Defender signature database reverse
engineering shed some light on the results of avred.

The blog article from retooling.io
[An unexpected journey into Microsoft Defender’s signature World](https://retooling.io/blog/an-unexpected-journey-into-microsoft-defenders-signature-world)
from 2024.06.28 has some interesting analysis of Defender’s
signature format.

`WdFilter.sys` is the main kernel space component, which registers
itself as minifilter driver, and therefore is responsible for
scanning files.

## Sub-Rules & Score Threshold

Signatures contain several sub-rules. Each sub-rule contains
bytes that need to be matched and a weight. The signature
has a required threshold that needs to be exceeded by the accumulated
weight of the applied sub-rules.

So if a signature has a threshold of 10, and 8 sub-rules each
with a weight of 4, then at least 3 of the 8 sub-rules need to apply
for the signature to trigger.

This explains much of the non-dominant match detection of Avred.
Dominant matches can be explained by sub-rules with a weight
equal or larger than the signature threshold.

### Sub-Rules example

An example from the retooling.io blog article:
![retooling.io sub rules](https://blog.deeb.ch/avredupdate/subrules.png)

## Wildcards

Signatures are byte-exact. But there are wildcards.

This explains why some of my signature-breaker technique attempts
did not yield good results: NOP’s or register’s of
ASM instructions may be wildcarded by good rules.

### Wildcard Types

Again
examples from the retooling.io blog article, translated into
equivalent yara rules:

`90 01 XX`: match a sequence of bytes of a specific length, defined by the quantity XX.

```
$sub_rule_3_hex = { 45 78 69 74 C7 85 ?? FF FF FF 54 68 72 65 66 C7 85 ?? 04 FF FF FF 61 64 }
```

`90 02 XX`: a placeholder to match up to XX bytes in a specific position.

```
$sub_rule_2_hex = { 75 61 6C 41 C7 [0-16] 6C 6C 6F 63 }
```

`90 03 XX YY`:
two consecutive sequences of bytes whose lengths are defined by XX and YY. The expected bytes to be found must match one of the two sequences.

```
$sub_rule_1_hex = { 50 6f 6c 69 63 69 65 73 5c 45 78 70 6c 6f 72 65 72 5c 52 75 6e 22 20 2f 76 20 22 (43 49 50 41|56 49 50 41) 22 20 2f 64 20 43 3a 5c 55 6e 6e 69 73 74 74 61 6c 6c 2e 65 78 65 20 2f 74 20 22 52 45 47 5f 53 5a 22 20 2f 66 00 90 00 }
```

`90 04 XX YY`:
a placeholder for a regex-like expression, where XX represents the exact number of bytes that must be found, and YY represents the length of the regex-like pattern

```
$example_90_04_first_rule = { 68 74 74 70 3a 2f 2f 61 72 70 2e 31 38 31 38 [30-39] [30-39] 2e 63 6e 2f 61 72 70 2e 68 74 6d 90 00 }
```

`90 05 XX YY`:
placeholder for a regex-like expression, where XX represents the upper bound on the number of bytes that must be found, and YY represents the length of the regex-like pattern.
case insensitive of previous

```
$example_90_05 = "http://[a-zA-Z]{0,64}\\.com/dfrg32\\.exe"
```