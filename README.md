# Ikigai Skills

Agent skills for Claude built around the Ikigai framework — helping a person work out
what they should be doing with their life, by interviewing them rather than lecturing
them.

## Skills

### `ikigai-persona`

Runs a proactive, question-by-question Ikigai interview and produces four things:

1. **A persona** — who this person actually is, with the evidence attached
2. **An Ikigai map** — the four quadrants and their overlaps, filled in from their own
   words, with the thin quadrant named honestly
3. **A purpose statement** — structured and raw versions
4. **Experiments** — two or three small, time-boxed, reversible tests to run next

It triggers on requests about purpose, calling, career direction, feeling stuck or
burned out, choosing between paths, or building a persona — including when the word
"ikigai" never comes up.

```
skills/ikigai-persona/
├── SKILL.md                          # interview flow and principles
└── references/
    ├── interview-guide.md            # question bank + probing techniques
    ├── ikigai-framework.md           # the quadrants, diagnostics, history, limits
    └── output-templates.md           # deliverable templates + worked example
```

## Design notes

Three choices shape the skill:

**It interviews before it answers.** Questions come 2–4 at a time, not as a wall of
twenty — short lists get stories, long lists get one-word answers.

**It mines for episodes, not adjectives.** "Are you creative?" returns a self-image;
"when did you last lose track of time?" returns evidence. Every line in the final output
should trace back to something the person actually said, which is what separates a
useful portrait from a horoscope.

**It is honest about the framework.** The four-circle Venn diagram is a Western
construction from around 2014, not a traditional Japanese teaching — Japanese *ikigai*
is smaller, plural, and carries no requirement that your purpose pay you. The skill
raises this when someone is distressed about lacking a single grand calling, and
otherwise stays out of the way. It also stops and points toward real support rather than
working the framework if it hears signs of genuine distress.

## Installing

The `SKILL.md` format (YAML frontmatter + an instructions body, with an optional
`references/` folder) is shared across several agent CLIs, so the same folder installs
as-is into all of them — no conversion needed. Steps below are verified: each CLI was
installed fresh and used to confirm `ikigai-persona` actually loads, not just copied by
guesswork from docs.

### Claude Code

```bash
mkdir -p ~/.claude/skills
cp -r skills/ikigai-persona ~/.claude/skills/
```

Project-scoped alternative, shared with everyone working in that repo:

```bash
mkdir -p .claude/skills && cp -r skills/ikigai-persona .claude/skills/
```

Claude Code scans its skills directories continuously — no restart required. Confirmed
by copying the folder in mid-session and seeing `ikigai-persona` appear in the live
skill list immediately after.

### OpenAI Codex CLI

```bash
mkdir -p ~/.codex/skills
cp -r skills/ikigai-persona ~/.codex/skills/
```

Project-scoped alternative: `.codex/skills/` or `.agents/skills/` in a repo — Codex walks
up from the current directory to the repo root, so this also works in monorepos.

Confirmed with `codex debug prompt-input`, which renders the exact model-visible prompt:
`ikigai-persona` appeared in the `<skills_instructions>` block, sourced from
`~/.codex/skills/ikigai-persona/SKILL.md`, alongside Codex's own bundled skills.

### OpenClaw

```bash
openclaw skills install skills/ikigai-persona --global
```

Drop `--global` to install into the current workspace's `./skills/` instead of the
shared `~/.openclaw/skills/`. `openclaw skills install` also accepts a ClawHub slug or a
git URL, not just a local path.

Confirmed with `openclaw skills info ikigai-persona`: status `✓ Ready`, `Visible to
model: yes`, path `~/.openclaw/skills/ikigai-persona/SKILL.md`.

### Hermes Agent

```bash
mkdir -p ~/.hermes/skills/personal-growth
cp -r skills/ikigai-persona ~/.hermes/skills/personal-growth/
```

`hermes skills install` expects a registry identifier or URL rather than a local path, so
a skill that only lives in this repo installs by copying it directly into
`~/.hermes/skills/<category>/` — any category name works, it's purely an organizational
folder.

Confirmed with `hermes skills list`, which listed `ikigai-persona | personal-growth |
local | local | enabled`.

### Notes

- All four tools invoke the skill automatically once installed — matching on the
  `description` field — so no further configuration is needed in any of them.
- Versions tested: Claude Code (current as of this repo), Codex CLI 0.146.0, OpenClaw
  2026.6.33, Hermes Agent 0.19.0.
