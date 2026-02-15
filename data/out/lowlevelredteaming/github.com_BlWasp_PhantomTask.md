# https://github.com/BlWasp/PhantomTask

[Skip to content](https://github.com/BlWasp/PhantomTask#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/BlWasp/PhantomTask) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/BlWasp/PhantomTask) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/BlWasp/PhantomTask) to refresh your session.Dismiss alert

{{ message }}

[BlWasp](https://github.com/BlWasp)/ **[PhantomTask](https://github.com/BlWasp/PhantomTask)** Public

- [Notifications](https://github.com/login?return_to=%2FBlWasp%2FPhantomTask) You must be signed in to change notification settings
- [Fork\\
12](https://github.com/login?return_to=%2FBlWasp%2FPhantomTask)
- [Star\\
121](https://github.com/login?return_to=%2FBlWasp%2FPhantomTask)


A tool to play with scheduled tasks on Windows, in Rust


### License

[GPL-3.0 license](https://github.com/BlWasp/PhantomTask/blob/master/LICENSE)

[121\\
stars](https://github.com/BlWasp/PhantomTask/stargazers) [12\\
forks](https://github.com/BlWasp/PhantomTask/forks) [Branches](https://github.com/BlWasp/PhantomTask/branches) [Tags](https://github.com/BlWasp/PhantomTask/tags) [Activity](https://github.com/BlWasp/PhantomTask/activity)

[Star](https://github.com/login?return_to=%2FBlWasp%2FPhantomTask)

[Notifications](https://github.com/login?return_to=%2FBlWasp%2FPhantomTask) You must be signed in to change notification settings

# BlWasp/PhantomTask

master

[**1** Branch](https://github.com/BlWasp/PhantomTask/branches) [**0** Tags](https://github.com/BlWasp/PhantomTask/tags)

[Go to Branches page](https://github.com/BlWasp/PhantomTask/branches)[Go to Tags page](https://github.com/BlWasp/PhantomTask/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![BlWasp](https://avatars.githubusercontent.com/u/35003340?v=4&size=40)](https://github.com/BlWasp)[BlWasp](https://github.com/BlWasp/PhantomTask/commits?author=BlWasp)<br>[Help in README and rustfmt](https://github.com/BlWasp/PhantomTask/commit/f6ef85bd25fcc2001b4e41d64f9d17742122e1b9)<br>4 months agoNov 1, 2025<br>[f6ef85b](https://github.com/BlWasp/PhantomTask/commit/f6ef85bd25fcc2001b4e41d64f9d17742122e1b9) · 4 months agoNov 1, 2025<br>## History<br>[3 Commits](https://github.com/BlWasp/PhantomTask/commits/master/) <br>Open commit details<br>[View commit history for this file.](https://github.com/BlWasp/PhantomTask/commits/master/) 3 Commits |
| [src](https://github.com/BlWasp/PhantomTask/tree/master/src "src") | [src](https://github.com/BlWasp/PhantomTask/tree/master/src "src") | [Help in README and rustfmt](https://github.com/BlWasp/PhantomTask/commit/f6ef85bd25fcc2001b4e41d64f9d17742122e1b9 "Help in README and rustfmt") | 4 months agoNov 1, 2025 |
| [.gitignore](https://github.com/BlWasp/PhantomTask/blob/master/.gitignore ".gitignore") | [.gitignore](https://github.com/BlWasp/PhantomTask/blob/master/.gitignore ".gitignore") | [Initial commit](https://github.com/BlWasp/PhantomTask/commit/1010baf37d5eaf0543a95c534329f94681f10b40 "Initial commit") | 4 months agoOct 31, 2025 |
| [Cargo.lock](https://github.com/BlWasp/PhantomTask/blob/master/Cargo.lock "Cargo.lock") | [Cargo.lock](https://github.com/BlWasp/PhantomTask/blob/master/Cargo.lock "Cargo.lock") | [Initial commit](https://github.com/BlWasp/PhantomTask/commit/1010baf37d5eaf0543a95c534329f94681f10b40 "Initial commit") | 4 months agoOct 31, 2025 |
| [Cargo.toml](https://github.com/BlWasp/PhantomTask/blob/master/Cargo.toml "Cargo.toml") | [Cargo.toml](https://github.com/BlWasp/PhantomTask/blob/master/Cargo.toml "Cargo.toml") | [Initial commit](https://github.com/BlWasp/PhantomTask/commit/1010baf37d5eaf0543a95c534329f94681f10b40 "Initial commit") | 4 months agoOct 31, 2025 |
| [LICENSE](https://github.com/BlWasp/PhantomTask/blob/master/LICENSE "LICENSE") | [LICENSE](https://github.com/BlWasp/PhantomTask/blob/master/LICENSE "LICENSE") | [Add GNU GPL v3 license to the project](https://github.com/BlWasp/PhantomTask/commit/5616b53a8fb722fb40dded045ebfa716f901df87 "Add GNU GPL v3 license to the project  Added the GNU General Public License version 3 to the project.") | 4 months agoOct 31, 2025 |
| [README.md](https://github.com/BlWasp/PhantomTask/blob/master/README.md "README.md") | [README.md](https://github.com/BlWasp/PhantomTask/blob/master/README.md "README.md") | [Help in README and rustfmt](https://github.com/BlWasp/PhantomTask/commit/f6ef85bd25fcc2001b4e41d64f9d17742122e1b9 "Help in README and rustfmt") | 4 months agoNov 1, 2025 |
| View all files |

## Repository files navigation

# PhantomTask

[Permalink: PhantomTask](https://github.com/BlWasp/PhantomTask#phantomtask)

A Windows command-line utility for creating and executing scheduled tasks with session-specific control. PhantomTask leverages the Windows Task Scheduler API to create tasks that run in specific user sessions with elevated privileges.

## Features

[Permalink: Features](https://github.com/BlWasp/PhantomTask#features)

- **Session Management**: Create tasks targeting specific Windows Terminal Services sessions
- **Session Enumeration**: List all active sessions on the local machine with detailed information
- **Flexible Authentication**: Support for both interactive token and password-based authentication
- **Elevated Privileges**: Tasks can be configured to run with highest privileges
- **Immediate Execution**: Automatically triggers tasks after creation with configurable session targeting
- **Hidden Tasks**: Tasks are created as hidden by default

## Requirements

[Permalink: Requirements](https://github.com/BlWasp/PhantomTask#requirements)

- Windows operating system
- Rust toolchain (2024 edition)
- Administrator privileges (recommended for full functionality)

## Installation

[Permalink: Installation](https://github.com/BlWasp/PhantomTask#installation)

Clone the repository and build using Cargo:

```
git clone <repository-url>
cd phantomtask
cargo build --release
```

The compiled binary will be available at `target/release/phantomtask.exe`

## Usage

[Permalink: Usage](https://github.com/BlWasp/PhantomTask#usage)

### Help

[Permalink: Help](https://github.com/BlWasp/PhantomTask#help)

```
Usage: phantomtask.exe [OPTIONS]

Options:
  -l, --list                   List active sessions on the local machine
  -n, --name <taskname>        The name of the task to create
  -f, --program <program>      The program to execute
  -a, --arguments <arguments>  The arguments to pass to the program
  -u, --username <username>    The username to run the task as
  -p, --password <password>    The password for the specified username
  -s, --sessionid <sessionid>  The session ID to run the task in
  -h, --help                   Print help
  -V, --version                Print version
```

### List Active Sessions

[Permalink: List Active Sessions](https://github.com/BlWasp/PhantomTask#list-active-sessions)

Display all active Windows Terminal Services sessions with their details:

```
phantomtask.exe --list
# or
phantomtask.exe -l
```

Output example:

```
===== Active Sessions =====

SessionID  User                 State           Station              Domain
=====================================================================================
0          <None>               Active          Services             <Local>
1          Administrator        Active          Console              WORKSTATION
```

### Create and Execute a Task

[Permalink: Create and Execute a Task](https://github.com/BlWasp/PhantomTask#create-and-execute-a-task)

**If you want to execute a task as `SYSTEM` (session 0), change the username in `get_user_from_session()`!** It is localisation dependent (Système, System, ...), and there is no automatic resolution on this account.

Create a scheduled task that runs in a specific session:

```
phantomtask.exe --name "MyTask" --program "C:\path\to\program.exe" --sessionid 1
```

#### Required Arguments

[Permalink: Required Arguments](https://github.com/BlWasp/PhantomTask#required-arguments)

- `-n, --name <TASKNAME>`: Name of the task to create
- `-f, --program <PROGRAM>`: The program to execute
- `-s, --sessionid <SESSIONID>`: Session ID where the task should run

#### Optional Arguments

[Permalink: Optional Arguments](https://github.com/BlWasp/PhantomTask#optional-arguments)

- `-a, --arguments <ARGUMENTS>`: Arguments to pass to the program
- `-u, --username <USERNAME>`: Username to run the task as
- `-p, --password <PASSWORD>`: Password for the specified username

### Examples

[Permalink: Examples](https://github.com/BlWasp/PhantomTask#examples)

#### Basic Task Creation

[Permalink: Basic Task Creation](https://github.com/BlWasp/PhantomTask#basic-task-creation)

```
phantomtask.exe -n "NotepadTask" -f "notepad.exe" -s 1
```

#### Task with Arguments

[Permalink: Task with Arguments](https://github.com/BlWasp/PhantomTask#task-with-arguments)

```
phantomtask.exe -n "CmdTask" -f "cmd.exe" -a "/c dir" -s 1
```

#### Task with Specific User Credentials

[Permalink: Task with Specific User Credentials](https://github.com/BlWasp/PhantomTask#task-with-specific-user-credentials)

```
phantomtask.exe -n "UserTask" -f "C:\Tools\app.exe" -u "DOMAIN\User" -p "Password123" -s 1
```

## How It Works

[Permalink: How It Works](https://github.com/BlWasp/PhantomTask#how-it-works)

1. **COM Initialization**: Initializes the Component Object Model (COM) library with multithreaded apartment
2. **Task Scheduler Connection**: Connects to the Windows Task Scheduler service
3. **Task Definition**: Creates a new task definition with:

   - Time trigger (scheduled to run 1 minute after creation)
   - Execution action with specified program and arguments
   - Principal configuration (user and logon type)
   - Security settings (run with highest privileges)
4. **Session Resolution**: Resolves the username associated with the target session ID
5. **Task Registration**: Registers the task in the root folder of Task Scheduler
6. **Immediate Execution**: Triggers the task immediately using the resolved session context

## Project Structure

[Permalink: Project Structure](https://github.com/BlWasp/PhantomTask#project-structure)

```
phantomtask/
├── Cargo.toml          # Project dependencies and configuration
├── src/
│   ├── main.rs         # Entry point and CLI argument parsing
│   ├── tasks.rs        # Task creation and registration logic
│   ├── sessions.rs     # Session enumeration and user resolution
│   └── utils.rs        # Utility functions (wide string conversion)
└── README.md
```

## Dependencies

[Permalink: Dependencies](https://github.com/BlWasp/PhantomTask#dependencies)

- **windows**: Windows API bindings for Rust (v0.62.2)

  - Task Scheduler COM interfaces
  - Remote Desktop Services API
  - COM and OLE support
- **windows-core**: Core Windows types (v0.62.2)
- **clap**: Command-line argument parser (v4.5.51)

## Limitations

[Permalink: Limitations](https://github.com/BlWasp/PhantomTask#limitations)

- Windows-only (uses Windows-specific APIs)
- Requires administrator rights for most operations
- Session ID 0 defaults to "Système" user (in french, localization-dependent)

## Error Handling

[Permalink: Error Handling](https://github.com/BlWasp/PhantomTask#error-handling)

The application provides detailed console output for:

- COM initialization status
- Task creation progress
- Session user resolution
- Task execution confirmation
- Error messages with context

## Disclaimers

[Permalink: Disclaimers](https://github.com/BlWasp/PhantomTask#disclaimers)

This is an obvious disclaimer because I don't want to be held responsible if someone uses this tool against anyone who hasn't asked for anything.

Usage of anything presented in this repo to attack targets without prior mutual consent is illegal. It's the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program. Only use for educational purposes.

## About

A tool to play with scheduled tasks on Windows, in Rust


### Resources

[Readme](https://github.com/BlWasp/PhantomTask#readme-ov-file)

### License

[GPL-3.0 license](https://github.com/BlWasp/PhantomTask#GPL-3.0-1-ov-file)

### Uh oh!

There was an error while loading. [Please reload this page](https://github.com/BlWasp/PhantomTask).

[Activity](https://github.com/BlWasp/PhantomTask/activity)

### Stars

[**121**\\
stars](https://github.com/BlWasp/PhantomTask/stargazers)

### Watchers

[**0**\\
watching](https://github.com/BlWasp/PhantomTask/watchers)

### Forks

[**12**\\
forks](https://github.com/BlWasp/PhantomTask/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2FBlWasp%2FPhantomTask&report=BlWasp+%28user%29)

## [Releases](https://github.com/BlWasp/PhantomTask/releases)

No releases published

## [Packages\  0](https://github.com/users/BlWasp/packages?repo_name=PhantomTask)

No packages published

## Languages

- [Rust100.0%](https://github.com/BlWasp/PhantomTask/search?l=rust)

You can’t perform that action at this time.