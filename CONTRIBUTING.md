# Summary

So you like our open-sourceness-ish stuff and want to contribute with this
project? Great, let us help you help us!

## Environment Setup

### Cloning a Repository

Cloning a project is easy as pie. Provided that you have [git][1] installed on
your favourite platform, just open the command line and clone it, either via
[https][2] or [ssh][3] and you are good to go.

```
$ git clone https://github.com/stone-payments/<repository_name>
```

## Coding Guidelines

Implement code that is...

* **Beautiful**. Everyone must enjoy working with it, so keep it well
formatted, avoid long scrollable lines with lots of responsibility and unusual
formatting.
* **Clean**. Everyone must have the power to maintain it, so keep it simple and
clean, use good naming and avoid abbreviations that can prejudice readability.
* **Documented**. Everyone should be able to understand it, even when
businesses logic rules makes it hard, so keep it well documented.
* **Reusable**. Everyone is interested in that great piece of code that you
already master and did a great job on, so keep it reusable and modular, with
as little responsibility and as much cohesion as possible.
* **Testable**. Everyone should be confident on the code, so keep it
easy to test and make debugging easier by extracting variables.

... and that follows ...

* **Conventions**. Everyone must understand the code with ease, so follow the
language naming conventions for language elements such as classes, interfaces,
methods, enumerators and for files.
* **Good Practices**. Everyone has great ideas and they are well received, so
please, if you know an already existing design pattern that helps solving the
problem, use it. If you have a great idea that solves common problems that are
not solved yet, go ahead, discuss it, and validate the ideas sharing your
knowledge with other developers and help both to evolve.

## Commiting Guidelines

This project follows [git flow][4] organizational style as methodology. There
is a great tool also called [git flow][5] that follows this methodology.
Consider using these guidelines to improve commits semantics.

| Emoji	             | Emoji Code           | Commit Type                  |
|--------------------|----------------------|------------------------------|
| :tada:             | : tada :             | First commit                 |
| :art:              | : art :              | Improves code structure      |
| :racehorse:        | : racehorse :        | Improves performance         |
| :memo:             | : memo :             | Adds documentation           |
| :bug:              | : bug :              | Fixes bug                    |
| :fire:             | : fire :             | Removes code of files        |
| :green_heart:      | : green_heart :      | Fixes CI builds              |
| :white_check_mark: | : white_check_mark : | Adds tests                   |
| :lock:             | : lock :             | Improves security            |
| :arrow_up:         | : arrow_up :         | Upgrades dependencies        |
| :arrow_down:       | : arrow_down :       | Downgrades dependencies      |
| :poop:             | : poop :             | Deprecates code              |
| :construction:     | : construction :     | Under construction           |
| :rocket:           | : rocket :           | Adds feature                 |
| :see_no_evil:      | : see_no_evil :      | Quick fix (a.k.a. gambiarra) |
| :gift:             | : gift :             | New version                  |

## Version Semantics

This project follows [semantic versioning guidelines][6].

## Changes Guidelines

Do changes via ...

* **Fork**. Fork the target repository into your account and you're good to go.
* **Pull Requests**. Whenever your code is ready to rock and you want to
integrate with the original code, open pull requests to the main repository.
Be sure to synchronize your repository before opening the pull request to avoid
conflicts.

... and never ...

* **Fork a repository and build a separate timeline to keep functionality**.
This movie has been in the scenes in many open source projects and all of us
already know the results of not joining efforts. We will help you help us and
we will make everything we possibly can to see you willing to help us, keeping
the same codebase which will be improved faster.

## Reporting

Something is wrong or missing? Found code that doesn't follow these general
guidelines? Disagree with the rules? Please, don't hesitate to contact us and
address the issue, we will be more than pleased to improve and evolve, the
project, the rules, and even ourselves.

projetosfinanceiros@stone.com.br

[1]: https://git-scm.com
[2]: https://help.github.com/articles/which-remote-url-should-i-use/#cloning-with-https-urls-recommended
[3]: https://help.github.com/articles/which-remote-url-should-i-use/#cloning-with-ssh-urls
[4]: http://nvie.com/posts/a-successful-git-branching-model/
[5]: https://danielkummer.github.io/git-flow-cheatsheet/
[6]: https://semver.org/