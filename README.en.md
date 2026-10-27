# Anti-overdefensive Paper Writing

[中文](README.md) · [Skill](skills/anti-overdefensive-paper-writing/SKILL.md) · [Validation](docs/validation.md) · [MIT License](LICENSE)

A writing skill for drafting, revising, compressing, and reviewing Chinese and English academic prose. It helps sentences advance an argument while preserving evidence, meaningful comparisons, and necessary conditions.

**Version: 0.4.0.** Skill instructions are primarily in Chinese, with examples and tests for both languages.

## What it does

- Organizes a manuscript around its research question, supported contribution, mechanism, and evidence.
- Detects uninvited objections, empty negative contrasts, repeated caveats, authorial apologies, and generic conclusions.
- Preserves numbers, polarity, scope, inference strength, source status, quotations, and citation support.
- Distinguishes repeated statements from synthesis across methods, conditions, and trade-offs.
- Matches supplied author examples and the intended reader; checks whether editing adds useful information.
- Includes a read-only candidate scanner for UTF-8 text, Markdown, and LaTeX.

For example, when the evidence is recall increasing from 71% to 74% on two in-domain datasets, the paragraph can state that result directly. A defensive preface about replacing every retrieval framework adds little. Actual adverse results, statistical interpretation boundaries, and competing explanations remain part of the argument.

## Install

Ask Codex:

```text
Install this GitHub skill:
https://github.com/wmxxhb/anti-overdefensive-paper-writing/tree/main/skills/anti-overdefensive-paper-writing
```

Alternatively, copy `skills/anti-overdefensive-paper-writing` into your skills directory, normally `~/.codex/skills` or `$CODEX_HOME/skills` when configured. Use it on the next conversation turn:

```text
Use $anti-overdefensive-paper-writing to polish this paragraph. Return the prose only.
```

```text
Use $anti-overdefensive-paper-writing to review this paper. Keep the original and give location-specific recommendations.
```

Automatic selection is enabled when the task matches. Other assistants that support file-based skills can read `SKILL.md` and its relevant references.

## Scanner and tests

Requires Python 3.10+. The scanner and tests use the standard library.

```sh
python skills/anti-overdefensive-paper-writing/scripts/scan_defensive_prose.py paper.tex --format json
python -B -m unittest discover -s skills/anti-overdefensive-paper-writing/tests -p test_scanner.py
python -B validation/run_probes.py
```

Use `-` for standard input, adding `--latex` for LaTeX input. Markdown blockquotes are excluded by default; use `--include-blockquotes` to inspect them. The scanner reports candidates with their original positions and context. Editorial decisions depend on each sentence's role in the argument.

The release includes **50 unit tests, 100 formatting probes, and 14 development behavior cases**. Four writing outputs also received independent outcome review. See [validation scope and results](docs/validation.md).

## Attribution and contributions

Eight open-source projects informed the design. See the [design sources](skills/anti-overdefensive-paper-writing/references/source-notes.md) and [third-party notices](THIRD_PARTY_NOTICES.md). This project is licensed under [MIT](LICENSE).

For a writing issue, provide a shareable minimal passage, the information that must survive, and the actual output. For scanner issues, include the format, expected candidates, and actual positions.
