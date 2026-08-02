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

Copy a skill into your personal skills directory:

```bash
cp -r skills/ikigai-persona ~/.claude/skills/
```

Or into a project so it's available to everyone working in that repo:

```bash
mkdir -p .claude/skills && cp -r skills/ikigai-persona .claude/skills/
```

Claude picks it up on the next session and invokes it automatically when a request
matches the description.
