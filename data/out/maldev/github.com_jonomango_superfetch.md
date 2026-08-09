# https://github.com/jonomango/superfetch

[Skip to content](https://github.com/jonomango/superfetch#start-of-content)

You signed in with another tab or window. [Reload](https://github.com/jonomango/superfetch) to refresh your session.You signed out in another tab or window. [Reload](https://github.com/jonomango/superfetch) to refresh your session.You switched accounts on another tab or window. [Reload](https://github.com/jonomango/superfetch) to refresh your session.Dismiss alert

{{ message }}

[jonomango](https://github.com/jonomango)/ **[superfetch](https://github.com/jonomango/superfetch)** Public

- [Notifications](https://github.com/login?return_to=%2Fjonomango%2Fsuperfetch) You must be signed in to change notification settings
- [Fork\\
22](https://github.com/login?return_to=%2Fjonomango%2Fsuperfetch)
- [Star\\
142](https://github.com/login?return_to=%2Fjonomango%2Fsuperfetch)


main

[**1** Branch](https://github.com/jonomango/superfetch/branches) [**0** Tags](https://github.com/jonomango/superfetch/tags)

[Go to Branches page](https://github.com/jonomango/superfetch/branches)[Go to Tags page](https://github.com/jonomango/superfetch/tags)

Go to file

Code

Open more actions menu

## Folders and files

| Name | Name | Last commit message | Last commit date |
| --- | --- | --- | --- |
| ## Latest commit<br>[![jonomango](https://avatars.githubusercontent.com/u/26609800?v=4&size=40)](https://github.com/jonomango)[jonomango](https://github.com/jonomango/superfetch/commits?author=jonomango)<br>[Consistency.](https://github.com/jonomango/superfetch/commit/bfdf15cd5dde8650b758792e225e77bb26ff0f69)<br>2 years agoJun 6, 2024<br>[bfdf15c](https://github.com/jonomango/superfetch/commit/bfdf15cd5dde8650b758792e225e77bb26ff0f69) · 2 years agoJun 6, 2024<br>## History<br>[6 Commits](https://github.com/jonomango/superfetch/commits/main/) <br>Open commit details<br>[View commit history for this file.](https://github.com/jonomango/superfetch/commits/main/) 6 Commits |
| [include/superfetch](https://github.com/jonomango/superfetch/tree/main/include/superfetch "This path skips through empty directories") | [include/superfetch](https://github.com/jonomango/superfetch/tree/main/include/superfetch "This path skips through empty directories") | [Consistency.](https://github.com/jonomango/superfetch/commit/bfdf15cd5dde8650b758792e225e77bb26ff0f69 "Consistency.") | 2 years agoJun 6, 2024 |
| [CMakeLists.txt](https://github.com/jonomango/superfetch/blob/main/CMakeLists.txt "CMakeLists.txt") | [CMakeLists.txt](https://github.com/jonomango/superfetch/blob/main/CMakeLists.txt "CMakeLists.txt") | [Added code.](https://github.com/jonomango/superfetch/commit/84c67c547a4ff05f7a3fe272d80c4e08ce514eeb "Added code.") | 2 years agoJun 4, 2024 |
| [LICENSE](https://github.com/jonomango/superfetch/blob/main/LICENSE "LICENSE") | [LICENSE](https://github.com/jonomango/superfetch/blob/main/LICENSE "LICENSE") | [Initial commit](https://github.com/jonomango/superfetch/commit/d7137283626198211298b211314e08cc043f3616 "Initial commit") | 2 years agoJun 4, 2024 |
| [README.md](https://github.com/jonomango/superfetch/blob/main/README.md "README.md") | [README.md](https://github.com/jonomango/superfetch/blob/main/README.md "README.md") | [Consistency.](https://github.com/jonomango/superfetch/commit/bfdf15cd5dde8650b758792e225e77bb26ff0f69 "Consistency.") | 2 years agoJun 6, 2024 |
| View all files |

## Repository files navigation

# superfetch

[Permalink: superfetch](https://github.com/jonomango/superfetch#superfetch)

Simple library for translating virtual addresses to physical addresses from usermode.

## Example usage

[Permalink: Example usage](https://github.com/jonomango/superfetch#example-usage)

```
#include <superfetch/superfetch.h>

int main() {
  auto const mm = spf::memory_map::current();
  if (!mm) {
    // Do something with mm.error()
  }

  // Any kernel virtual address.
  void const* const virt = ...;

  std::uint64_t const phys = mm->translate(virt);
  if (!phys) {
    // Do something...
  }

  std::printf("%p -> %zX\n", virt, phys);
}
```

## Installation

[Permalink: Installation](https://github.com/jonomango/superfetch#installation)

To use `superfetch`, simply add the `include` directory to your project and include
`superfetch/superfetch.h`.

### CMake

[Permalink: CMake](https://github.com/jonomango/superfetch#cmake)

If you are using [CMake](https://cmake.org/), add this repository as a
subdirectory and link to the `superfetch` target library.

```
add_subdirectory(path/to/superfetch/repo/dir)
target_link_libraries(my_project_target superfetch)
```

## About

Translate virtual addresses to physical addresses from usermode.

### Resources

[Readme](https://github.com/jonomango/superfetch#readme-ov-file)

[MIT license](https://github.com/jonomango/superfetch#MIT-1-ov-file)

[Activity](https://github.com/jonomango/superfetch/activity)

### Stars

**142** stars

### Watchers

**3** watching

### Forks

[**22** forks](https://github.com/jonomango/superfetch/forks)

[Report repository](https://github.com/contact/report-content?content_url=https%3A%2F%2Fgithub.com%2Fjonomango%2Fsuperfetch&report=jonomango+%28user%29)

## Contributors

## Languages

You can’t perform that action at this time.