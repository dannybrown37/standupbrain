# standupbrain

`standupbrain` reads your Git commit and Jira activity and passes them to a local LLM that reminds you what the heck you did yesterday.

## Install

```bash
uv tool install standupbrain
```

## Usage

### Quickstart

* [Configure your GitHub credentials locally](https://docs.github.com/en/get-started/git-basics/set-up-git)
* Run `standupbrain init` to set up or reset your GitHub username, Git author email, Jira credentials, and preferred LLM model.
* Run `standupbrain recall` to generate your standup summary.
  * Run `--help` or see below for additional options

### Help Commands

Check out the various `--help` options below:

<!-- CLI_HELP_START -->
## `standupbrain --help`

```bash
Usage: standupbrain [OPTIONS] COMMAND [ARGS]...

  CLI for standupbrain, the tool to help you remember what you did yesterday

Options:
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  init    Initialize standupbrain with your preferred LLM and GitHub/Jira...
  recall  Generate a summary of what you did yesterday via GitHub/Jira ->...
```

## `standupbrain init --help`

```bash
Usage: standupbrain init [OPTIONS]

  Initialize standupbrain with your preferred LLM and GitHub/Jira credentials

Options:
  --help  Show this message and exit.
```

## `standupbrain recall --help`

```bash
Usage: standupbrain recall [OPTIONS]

  Generate a summary of what you did yesterday via GitHub/Jira -> LLM

Options:
  -e, --author-email TEXT     Git author email for searching local commits
  -d, --date [%Y-%m-%d]       Specific date to generate update for (YYYY-MM-
                              DD)
  --dry-run, --dry_run        Do not actually prompt the LLM, just query the
                              APIs and print the prompt
  -u, --github-username TEXT  GitHub account username for searching remotes in
                              GitHub
  -v, --verbose               High verbosity for debugging
  --help                      Show this message and exit.
```
<!-- CLI_HELP_END -->
