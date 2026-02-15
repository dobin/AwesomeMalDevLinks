# https://aff-wg.org/2025/12/01/tradecraft-orchestration-in-the-garden/

[Skip to content](https://aff-wg.org/2025/12/01/tradecraft-orchestration-in-the-garden/#content)

What’s more relaxing than a beautiful fall day, a crisp breeze, a glass of Sangria, and music from the local orchestra? Of course, I expect you answered: writing position-independent code projects that separate capability from tradecraft. If you didn’t answer that way, you’re wrong.

In the last six months, [Tradecraft Garden](https://tradecraftgarden.org/) has covered a lot of ground. This project started as a linker to make it easier to write position-independent code DLL loaders and it has rapidly evolved into an Aspect Oriented Programming tool to weave tradecraft into PIC and PICO capabilities. It can still write position-independent code DLL loaders too (modular and self-incepting DLL loaders, at that)—but there’s a lot more potential here.

One of the needs in the current model, is that while we can separate tradecraft from capability in C—the linker script forces us to define our architecture and tradecraft as one monolithic thing. Separating base architecture and tradecraft, within the specification files themselves, is the theme of this release.

### Build Templates with %variables

This release introduces %variables into the Crystal Palace specification language. These are user-defined strings passed in at the beginning of the program. %variables are usable anywhere you would use a “string” argument in Crystal Palace’s specification language.

For example:

`load %foo`

This command will resolve %foo and load its contents. Easy enough, right?

We also have string concatenation with the <> operator too. So:

`load %foo <> “.x64.o”`

This will resolve %foo and append .x64.o to it.

With %variables comes the need to better understand what a script is doing. The new echo command prints its arguments to STDOUT (CLI) or to a SpecLogger object (API):

`echo “I am looking at: “ %hooks`

%variables evolve the Crystal Palace specification file language from a collection of commands into a build templating language. That is, a specification file may now define the architecture of a loader or capability with the information about specific tradecraft getting added later.

[Simple Loader – Execution Guardrails](https://tradecraftgarden.org/simpleguard.html) uses these new features. The loader is now agnostic to the follow-on specification file it encrypts and packs. The `%STAGE2` variable is a stand-in for that file. You can pair this stage with one of the other examples from the Tradecraft Garden (including a COFF loader or just straight PIC).

### Populating %variables (“The Glue”)

For this base architecture and specific tradecraft separation to work, we need a glue. That is a means to specify %variables.

Specifying %variables via the Java API is easy. Put a “%variable” key into the environment map with a “string” value.

You may also specify %var=”value” arguments via the ./link and ./piclink CLI tools too.

If you want to keep a variable configuration in a file, add @file.spec to your program’s CLI. This will read file.spec and use its commands to populate variables before the main linker script is run. And yes, we have new commands to set %variables from a Crystal Palace .spec file.

setg sets a variable within the global scope for this build session:

`setg “%bar” “0xAABBCCDD”`

Crystal Palace has a concept of scope for variables too. You will almost always want global variables in these configuration files. But, local scope exists for variables that are visible only within the current label’s execution context. Use set to set a local variable:

`set “%foo” “file.spec”`

With any commands that set or update %variables, quote the variable name to prevent Crystal Palace from evaluating the variable to its contents before command execution.

And, pack is a way to marshal %variables (and other strings) into a $VARIABLE byte array.

`pack $VAR “template” “arg1” %arg2 …`

The Perl programmer in me can’t resist a good pack command. [pack](https://tradecraftgarden.org/docs.html#pack) accepts a variable, template string, and list of arguments that correspond to the characters in the template string. Think of the template as a condensed C struct definition. Each character specifies how pack will interpret the argument string and what type it will marshal the value to.

While I see these commands as configuration tools, they are generic Crystal Palace commands. You can use them anywhere.

### Layering and Chaining

While straight variable substitution is handy, sometimes, we want to mix and match modules of an unknown quantity. That’s where the next feature helps.

Crystal Palace’s foreach command expects a comma-separated list of items as its argument.

`foreach %libs: mergelib %_`

The foreach command walks the provided list and calls another Crystal Palace command with %\_ set to the current element of the list. %libs needs to exist, but an empty value is OK. The goal of foreach is to act as a placeholder for layered tradecraft that’s dynamically brought into a base architecture.

The next command is a list shift and execute tool. next expects a “%variable” name argument and it expects %variable is a comma-separated list of values. If the list is empty, next does nothing. If the list is not empty, next removes %variable’s first item and runs the specified command with %\_ set to that element.

`next “%NEXT”: run %_`

The goal of next is to support chaining tradecraft together, giving cooperating modules a mean to pass execution through each other.

### Modular Specification File Contracts

Crystal Palace’s main modularity tool is to create separate .spec files and use run to execute their commands in another file. This release gives us more modularity options.

The run command now accepts positional arguments. And, it passes them on to the child script as %1, %2, %3, etc.

`run “file.spec” “arg1” %arg2`

The positional arguments of “file.spec” are local to that run of that file. If file.spec runs another .spec file, the positional arguments are local to that specification file’s runs. The local scope is necessary to prevent our .spec files from stepping on each other’s arguments.

This release also adds callable labels to specification files too. Think of them as local runnable files, user-defined commands, or Crystal Palace functions. To create a callable label use:

`name.x64:`

Then, list your commands like normal. That’s it. These labels are callable with a dot name syntax and accept positional arguments too:

`.name “arg1” “arg2”`

The nice thing about this feature is we now have a choice or whether to split a function into its own .spec file or let it co-exist inside of the current .spec file. And, while this is nice, that’s not why I chose to build this feature. The real payoff is the call command.

call runs a callable label from another specification file:

`call “file.spec” "name" “arg1” “arg2”`

call is an encapsulation tool. That is, our base specification defines the architecture of our capability or loader. %variables become the placeholder for our tradecraft implementation. And, callable labels and call let us present the pieces of a tradecraft in a single file, with a common interface (callable labels), that our base architecture expects to act on.

[Simple Loader – Hooking](https://tradecraftgarden.org/simplehook.html) demonstrates this idea. It defines a base architecture for hooking a DLL and a modular contract for hooking tradecraft modules. [XORhooks](https://tradecraftgarden.org/xorhooks.html) demonstrates this contract. [Stack Cutting](https://tradecraftgarden.org/stackcutting.html) is now a module that composes on top of this base loader. What’s really cool? You can layer them together.. See the [Simple Loader – Hooking](https://tradecraftgarden.org/simplehook.html) notes for more on this.

### File Paths

One of the mundane, but important details in this scheme is file path resolution. Crystal Palace commands treat file paths as relative to the current .spec file. With %variables, things get messy, because we might specify a file path in one place (e.g., the CLI, @config.spec, an argument to run/call) and it gets used elsewhere. The resolve command brings some predictability to this.

`resolve “%files”`

resolve will walk through %files (assuming it’s a comma-separated list of files), canonicalize each entry to a filename \[relative to the current .spec\], and set %files to these full paths. This gives you control over when this path resolution happens and which .spec context its relative to.

The` -r` CLI option will resolve file paths in a %key=”value” argument provided that way.

### Migration Notes

1. The link and piclink shell scripts changed in this version. You’ll want to update to the latest from the Crystal Palace distribution or source archive.

2. I’ve updated the CLI syntax for piclink and link to accept % and $ sigils for %VAR and $DATAKEY values specified on the command-line. The old behavior of KEY=\[bytes\] to set $KEY still works, but going forward, the documentation and other materials will use explicit sigils. You may want to update your scripts to use explicit sigils too.

3. Several of the methods in crystalpalace.spec.LinkerSpec were deprecated. I cleaned up the API to make it easier to share arguments between a configuration LinkSpec and the main LinkSpec. [https://tradecraftgarden.org/docs.html#javaapi](https://tradecraftgarden.org/docs.html#javaapi)

### Closing Thoughts

This release introduced several commands and features to change how Crystal Palace specification files work together.

The combination of %variables and the ability to set those via the [Java API](https://tradecraftgarden.org/api/crystalpalace/spec/LinkSpec.html#run(crystalpalace.spec.Capability,java.util.Map)) or CLI allow our users to combine a base specification with specific tradecraft choices later on. This turns a base PIC into a re-usable component.

Callable labels and call allow us to encapsulate tradecraft modules into a single file with different touch points (e.g., initialization, apply hooks) available via a common convention. Pair this with foreach and we have a means to specify tradecraft modules in one %variable and use them at the right-spots within the base project.

The goal of this release is to move Tradecraft Garden projects from singular monolithic examples, that each redefine everything, into reusable components to compose tradecraft cocktails with.

To see the full list of what’s new, check out the [release notes](https://tradecraftgarden.org/releasenotes.txt).

- [Subscribe](https://aff-wg.org/2025/12/01/tradecraft-orchestration-in-the-garden/) [Subscribed](https://aff-wg.org/2025/12/01/tradecraft-orchestration-in-the-garden/)








  - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)

Join 97 other subscribers

Sign me up

  - Already have a WordPress.com account? [Log in now.](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F12%252F01%252Ftradecraft-orchestration-in-the-garden%252F)


- - [![](https://aff-wg.org/wp-content/uploads/2024/08/cropped-affwgsiteimage_nowreath.png?w=50) Adversary Fan Fiction Writers Guild](https://aff-wg.org/)
  - [Subscribe](https://aff-wg.org/2025/12/01/tradecraft-orchestration-in-the-garden/) [Subscribed](https://aff-wg.org/2025/12/01/tradecraft-orchestration-in-the-garden/)
  - [Sign up](https://wordpress.com/start/)
  - [Log in](https://wordpress.com/log-in?redirect_to=https%3A%2F%2Fr-login.wordpress.com%2Fremote-login.php%3Faction%3Dlink%26back%3Dhttps%253A%252F%252Faff-wg.org%252F2025%252F12%252F01%252Ftradecraft-orchestration-in-the-garden%252F)
  - [Copy shortlink](https://wp.me/pfXSCG-k1)
  - [Report this content](https://wordpress.com/abuse/?report_url=https://aff-wg.org/2025/12/01/tradecraft-orchestration-in-the-garden/)
  - [View post in Reader](https://wordpress.com/reader/blogs/235916366/posts/1241)
  - [Manage subscriptions](https://subscribe.wordpress.com/)
  - [Collapse this bar](https://aff-wg.org/2025/12/01/tradecraft-orchestration-in-the-garden/)