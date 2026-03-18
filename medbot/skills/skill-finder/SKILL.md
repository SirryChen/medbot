---
name: skill-finder
description: Search, discover, inspect, and install agent skills related to the user's current task. Use when the user asks for relevant skills, available skills, skill recommendations, skill installation, or similar capabilities from ClawHub, GitHub, or AgentSkill.work.
metadata:
  medbot:
    emoji: 🔍
    requires:
      bins:
        - curl
---

# Skill Finder

Discover and install skills from five complementary sources:

| Source | Coverage | Search | Install |
|--------|----------|--------|---------|
| `ClawHub` | official and packaged skills | semantic search | `npx clawhub install <slug>` |
| `GitHub` | broad public repos | GitHub Search API | `git clone` or `npx clawhub install <owner>/<repo>` |
| `AgentSkill.work` | indexed skill repos with enriched metadata | REST API search | `npx clawhub install` or `git clone` |
| `VitaClaw` | health-focused skill library | repo `skills/` directory search | sparse checkout or copy selected skill |
| `OpenClaw-Medical-Skills` | large medical skill library | repo `skills/` directory search | sparse checkout or copy selected skill |

Always search all sources. They overlap, but each may contain unique skills.

## Workflow

### 1. Search

Search from all sources using the current task intent, not just literal keywords.

#### ClawHub

```bash
npx --yes clawhub@latest search "<query>" --limit 10
```

#### GitHub

```bash
curl -s "https://api.github.com/search/repositories?q=<query>+topic:openclaw+language:python&sort=stars&order=desc&per_page=10"
curl -s "https://api.github.com/search/repositories?q=<query>+openclaw+in:name,description,readme&sort=stars&order=desc&per_page=10"
curl -s "https://api.github.com/search/repositories?q=topic:openclaw+skill&sort=stars&order=desc&per_page=10"
```

#### AgentSkill.work

```bash
curl -s "https://agentskill.work/api/skills?q=<query>&limit=10&sort=stars"
curl -s "https://agentskill.work/api/skills?topic=<topic>&limit=10&sort=stars"
curl -s "https://agentskill.work/api/skills?language=Python&limit=10&sort=stars"
```

#### VitaClaw

Use this source when the task is health management, medical records, report interpretation, drug safety, or daily wellness tracking.

Repository:

- `https://github.com/vitaclaw/vitaclaw`

Search the `skills/` directory and README:

```bash
curl -s "https://api.github.com/repos/vitaclaw/vitaclaw/contents/skills"
curl -s "https://api.github.com/search/code?q=<query>+repo:vitaclaw/vitaclaw+path:skills"
curl -s "https://api.github.com/search/code?q=<query>+repo:vitaclaw/vitaclaw+filename:SKILL.md"
```

#### OpenClaw-Medical-Skills

Use this source when the user needs deeper clinical, biomedical, genomics, or medical research skills.

Repository:

- `https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills`

Search the `skills/` directory and README:

```bash
curl -s "https://api.github.com/repos/FreedomIntelligence/OpenClaw-Medical-Skills/contents/skills"
curl -s "https://api.github.com/search/code?q=<query>+repo:FreedomIntelligence/OpenClaw-Medical-Skills+path:skills"
curl -s "https://api.github.com/search/code?q=<query>+repo:FreedomIntelligence/OpenClaw-Medical-Skills+filename:SKILL.md"
```

## 2. Present Results

Merge results into a single short list. For each candidate show:

- name
- one-line description
- stars or popularity when available
- source
- install command

For repository-backed results, also show the upstream repository name and the skill directory path when known.

If the user speaks Chinese, prefer Chinese descriptions when the source provides them.

## 3. Inspect Before Installing

Before recommending or installing any third-party skill, read `skill-filter` and review the candidate skill.

Useful commands:

```bash
npx --yes clawhub@latest inspect <slug> --json
npx --yes clawhub@latest inspect <slug> --files
npx --yes clawhub@latest inspect <slug> --file SKILL.md
curl -s "https://agentskill.work/api/skills/<owner>/<repo>"
curl -s "https://raw.githubusercontent.com/vitaclaw/vitaclaw/main/skills/<skill-name>/SKILL.md"
curl -s "https://raw.githubusercontent.com/FreedomIntelligence/OpenClaw-Medical-Skills/main/skills/<skill-name>/SKILL.md"
```

If the review result is:

- `allow`: continue
- `warn`: explain the concern and ask the user
- `block`: do not install or recommend the skill

## 4. Install

Preferred:

```bash
npx --yes clawhub@latest install <slug> --workdir ~/.medbot/workspace
```

Fallback:

```bash
git clone <html_url> ~/.medbot/workspace/skills/<skill-name>
```

After cloning, verify `SKILL.md` exists.

### Install A Single Skill From VitaClaw

Use sparse checkout so you do not pull the full repository:

```bash
tmpdir="$(mktemp -d)" && cd "$tmpdir"
git clone --depth=1 --filter=blob:none --sparse https://github.com/vitaclaw/vitaclaw.git
cd vitaclaw
git sparse-checkout set "skills/<skill-name>"
cp -R "skills/<skill-name>" ~/.medbot/workspace/skills/
```

### Install A Single Skill From OpenClaw-Medical-Skills

```bash
tmpdir="$(mktemp -d)" && cd "$tmpdir"
git clone --depth=1 --filter=blob:none --sparse https://github.com/FreedomIntelligence/OpenClaw-Medical-Skills.git
cd OpenClaw-Medical-Skills
git sparse-checkout set "skills/<skill-name>"
cp -R "skills/<skill-name>" ~/.medbot/workspace/skills/
```

After copying, verify:

```bash
ls ~/.medbot/workspace/skills/<skill-name>
```

## 5. Verify

After install:

```bash
npx --yes clawhub@latest list --workdir ~/.medbot/workspace
```

Remind the user to start a new session if needed so the new skill is loaded.

## Tips

- Start with `ClawHub` for the best packaged result.
- Use `GitHub` to find newer or less curated skills.
- Use `AgentSkill.work` for enriched metadata and related discovery.
- Use `VitaClaw` first for personal health and daily health management skills.
- Use `OpenClaw-Medical-Skills` for broader medical, clinical, genomics, and research workflows.
- If no suitable skill is found, help the user directly, then suggest creating one with `skill-creator`.
