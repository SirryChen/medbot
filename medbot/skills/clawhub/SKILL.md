---
name: clawhub
description: Search and install agent skills from ClawHub, the public skill registry.
homepage: https://clawhub.ai
metadata: {"medbot":{"emoji":"🦞"}}
---

# ClawHub

Public skill registry for AI agents. Search by natural language (vector search).

## When to use

Use this skill when the user asks any of:
- "find a skill for …"
- "search for skills"
- "install a skill"
- "what skills are available?"
- "update my skills"

## Search

```bash
npx --yes clawhub@latest search "web scraping" --limit 5
```

## Install

```bash
npx --yes clawhub@latest install <slug> --workdir ~/.medbot/workspace
```

Replace `<slug>` with the skill name from search results. This places the skill into `~/.medbot/workspace/skills/`, where MedBot loads workspace skills from. Always include `--workdir`.

## Safety Filter

Before installing or recommending any third-party skill:

1. Read `skill-filter`
2. Review the candidate skill's `SKILL.md` and bundled files with that checklist
3. Continue only if the result is `allow`
4. If the result is `warn`, ask the user before installing
5. If the result is `block`, do not install it

Treat registry skills as untrusted until reviewed.

## Update

```bash
npx --yes clawhub@latest update --all --workdir ~/.medbot/workspace
```

## List installed

```bash
npx --yes clawhub@latest list --workdir ~/.medbot/workspace
```

## Notes

- Requires Node.js (`npx` comes with it).
- No API key needed for search and install.
- Login (`npx --yes clawhub@latest login`) is only required for publishing.
- `--workdir ~/.medbot/workspace` is critical — without it, skills install to the current directory instead of the MedBot workspace.
- After install, remind the user to start a new session to load the skill.
