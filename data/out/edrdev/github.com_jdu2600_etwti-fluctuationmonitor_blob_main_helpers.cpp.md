# https://github.com/jdu2600/EtwTi-FluctuationMonitor/blob/main/helpers.cpp

[Skip to content](https://github.com/jdu2600/EtwTi-FluctuationMonitor/blob/main/helpers.cpp#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/jdu2600/EtwTi-FluctuationMonitor/blob/main/helpers.cpp) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/jdu2600/EtwTi-FluctuationMonitor/blob/main/helpers.cpp) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/jdu2600/EtwTi-FluctuationMonitor/blob/main/helpers.cpp) to refresh your session.Dismiss alert

{{ message }}

[jdu2600](https://github.com/jdu2600)/ **[EtwTi-FluctuationMonitor](https://github.com/jdu2600/EtwTi-FluctuationMonitor)** Public

- [Notifications](https://github.com/login?return_to=%2Fjdu2600%2FEtwTi-FluctuationMonitor) You must be signed in to change notification settings
- [Fork\\
16](https://github.com/login?return_to=%2Fjdu2600%2FEtwTi-FluctuationMonitor)
- [Star\\
169](https://github.com/login?return_to=%2Fjdu2600%2FEtwTi-FluctuationMonitor)


## Collapse file tree

## Files

main

Search this repository

/

# helpers.cpp

Copy path

BlameMore file actions

BlameMore file actions

## Latest commit

![author](https://github.githubassets.com/images/gravatars/gravatar-user-420.png?size=40)

John Uhlmann

[BHASIA23](https://github.com/jdu2600/EtwTi-FluctuationMonitor/commit/695a39058ed1b3f35998400d0922920fdb16901f)

3 years agoMay 15, 2023

[695a390](https://github.com/jdu2600/EtwTi-FluctuationMonitor/commit/695a39058ed1b3f35998400d0922920fdb16901f) · 3 years agoMay 15, 2023

## History

[History](https://github.com/jdu2600/EtwTi-FluctuationMonitor/commits/main/helpers.cpp)

Open commit details

[View commit history for this file.](https://github.com/jdu2600/EtwTi-FluctuationMonitor/commits/main/helpers.cpp) History

45 lines (39 loc) · 1.04 KB

/

# helpers.cpp

Top

## File metadata and controls

- Code

- Blame


45 lines (39 loc) · 1.04 KB

[Raw](https://github.com/jdu2600/EtwTi-FluctuationMonitor/raw/refs/heads/main/helpers.cpp)

Copy raw file

Download raw file

Open symbols panel

Edit and raw actions

1

2

3

4

5

6

7

8

9

10

11

12

13

14

15

16

17

18

19

20

21

22

23

24

25

26

27

28

29

30

31

32

33

34

35

36

37

38

39

40

41

42

43

44

45

#include"stdafx.h"

constchar\\* ProtectionString(DWORD Protection) {

switch (Protection) {

case PAGE\_NOACCESS:

return"\-\-\-";

case PAGE\_READONLY:

return"R--";

case PAGE\_READWRITE:

return"RW-";

case PAGE\_WRITECOPY:

return"RC-";

case PAGE\_EXECUTE:

return"--X";

case PAGE\_EXECUTE\_READ:

return"R-X";

case PAGE\_EXECUTE\_READWRITE:

return"RWX";

case PAGE\_EXECUTE\_WRITECOPY:

return"RCX";

}

return"???";

}

std::wstring ProcessName(DWORD processId) {

std::wstring buffer;

buffer.resize(32768);

HANDLE hProcess = OpenProcess(PROCESS\_QUERY\_LIMITED\_INFORMATION, FALSE, processId);

if (hProcess) {

DWORD dwSize = (DWORD)buffer.size();

if (QueryFullProcessImageNameW(hProcess, 0, &buffer\[0\], &dwSize))

{

buffer = std::filesystem::path(buffer).filename();

}

CloseHandle(hProcess);

}

if (buffer.empty()) {

wsprintf(&buffer\[0\], L"pid:%d", processId);

}

return buffer;

}

You can’t perform that action at this time.