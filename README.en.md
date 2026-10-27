# Anti-overdefensive Paper Writing

**Help AI-assisted papers spend fewer words on pre-emptive defence and more on the argument.**

[中文](README.md) · [View the skill](skills/anti-overdefensive-paper-writing/SKILL.md) · [v0.4.0](https://github.com/wmxxhb/anti-overdefensive-paper-writing/tree/v0.4.0)

AI revisions often add “not X but Y,” “this does not imply,” and “we do not claim.” Paragraphs start answering hypothetical objections, end with another caveat, and bury a clear finding under self-explanation.

This skill helps the assistant remove that clutter and organize the prose around the research question, method, and evidence. It supports drafting, polishing, compression, and writing review in Chinese and English.

## Before and after

**Before**

> This study is not intended to replace existing retrieval frameworks, but to explore candidate filtering. Although recall increased from 71% to 74% on two in-domain datasets, we must acknowledge that this does not mean the method solves every retrieval problem, and its potential value should be interpreted with caution.

**After**

> Candidate filtering increased recall from 71% to 74% on two in-domain datasets.

The editing question is practical: what fact, explanation, or inference condition would be lost by removing a sentence? Meaningful comparisons, adverse results, scope conditions, and statistical interpretation remain in the paper.

## What it catches

| Pattern | Editing goal |
|---|---|
| Empty “not X but Y” contrasts | State what the research does |
| Repeated denials and hypothetical objections | Keep explanations that affect the current claim |
| Apologies and blanket judgments of limited value | Report specific benefits, costs, and comparison conditions |
| The same caution in every paragraph | Place each condition beside the claim it qualifies |
| Experiments narrated as a development diary | Organize results around the judgments they support |
| Repeated closers and generic future work | Cut restatement while preserving synthesis across results |

For full manuscripts, the skill also checks the contribution's thread, numbers and terminology, citation support, and explanations added during revision.

## Quick start

Ask Codex:

```text
Install this paper-writing skill:
https://github.com/wmxxhb/anti-overdefensive-paper-writing/tree/main/skills/anti-overdefensive-paper-writing
```

Use it on the next conversation turn. You can also download the repository and copy the entire `skills/anti-overdefensive-paper-writing` folder into your skills directory.

### Polish a paragraph

```text
Use $anti-overdefensive-paper-writing to polish this paragraph. Return the revised prose only.

[paste paragraph]
```

### Shorten an abstract

```text
Use $anti-overdefensive-paper-writing to shorten this abstract to 150 words. Preserve the key results, costs, and conditions.

[paste abstract]
```

### Review a manuscript

```text
Use $anti-overdefensive-paper-writing to review this manuscript for defensive writing.
Keep the original and give location-specific findings and recommendations.

[provide manuscript]
```

Include a sample of your own writing to calibrate terminology, sentence structure, and voice. Skill instructions are primarily in Chinese, with examples for both languages.

## Scan an existing draft

The read-only scanner supports UTF-8 text, Markdown, and LaTeX. It requires Python 3.10+ and uses the standard library.

```sh
python skills/anti-overdefensive-paper-writing/scripts/scan_defensive_prose.py paper.md
python skills/anti-overdefensive-paper-writing/scripts/scan_defensive_prose.py paper.tex --format json
```

Output includes candidate expressions, original positions, and context. Supported code, math regions, and citation keys are masked; footnotes, list prose, and visible citation notes remain reviewable. Decide edits in context.

## Validation

The current version passes **50 unit tests and 100 formatting probes**. Four actual writing outputs also passed independent outcome review. See the [validation record](docs/validation.md).

<details>
<summary>Run the tests</summary>

From the repository root:

```sh
python -B -m unittest discover -s skills/anti-overdefensive-paper-writing/tests -p test_scanner.py
python -B validation/run_probes.py
```

</details>

## License

[MIT](LICENSE)
