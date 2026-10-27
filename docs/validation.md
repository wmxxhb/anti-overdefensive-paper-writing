# Validation of 0.4.0

Date: 2026-10-27. The eight Skill files match the frozen development release. [Manifest](../validation/skill-manifest-0.4.0.json).

## Reproducible checks

Run from the repository root with Python 3.10+:

```sh
python -B -m unittest discover -s skills/anti-overdefensive-paper-writing/tests -p test_scanner.py
python -B validation/run_probes.py
```

| Check | Recorded result | Public material |
|---|---|---|
| Scanner unit tests | 50 passed | `skills/anti-overdefensive-paper-writing/tests/test_scanner.py` |
| Prior determinate probes | 46 passed | First 46 cases of `validation/probes.json` |
| Independent formatting cases | 54 passed after fixes | Remaining 54 cases of `validation/probes.json` |
| Development writing cases | 14 available | `skills/anti-overdefensive-paper-writing/tests/behavior_cases.json` |
| Four actual writing outputs | All passed independent outcome review | Described below; this repository provides the development cases for further trials |

The 100 public probes are the 46 prior cases plus 54 independent cases. Unit tests overlap some of those formats. These counts describe test inputs, rather than estimates of writing quality or routing accuracy.

The scanner checks candidates and original locations while masking supported non-prose regions. The suite covers fenced and indented Markdown code, footnotes, lists and nested lists, blockquote options, math regions, LaTeX `\verb` and `\verb*`, and common single- and multiple-citation commands. Citation notes and surrounding prose remain visible.

An independent initial pass found two remaining issues: nested-list continuations were mistaken for code, and a literal pseudo-command inside `\verb` was reparsed. Their four failing inputs were retained. Both were fixed; all 54 cases then passed, including candidate locations.

## Writing outcome review

The final frozen version was used for four requests. The executor received the original materials and Skill, without prior outputs or review conclusions. A separate reviewer checked the original task and final delivery before consulting the pre-recorded criteria.

1. **Published simulation results:** an eight-unit excerpt, including a figure caption, from Saito and Rehmsmeier (2015), [PLOS ONE, e0118432](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432). The review retained the cross-plot synthesis while identifying local repetition, and preserved real comparisons, conditions and caption roles. The paper is attributed at its publisher; its XML and full text are not bundled here.
2. **Chinese review across workloads:** retained the synthesis of conditional strategy rankings and the supplied latency criterion.
3. **English compression:** 71 whitespace-separated words within a 95-word limit; retained all measured values, the reversal in accuracy ranking, and the shared time advantage.
4. **Chinese methods revision:** retained the mapping and access operations and all reported results; removed the unraised replacement contrast and generic defensive ending.

The independent reviewer passed all four outputs. This was a targeted check of the observed synthesis/repetition problem. It used a different fresh execution after the final scanner changes. No general model comparison or aggregate effectiveness claim follows from these four outcomes.

For further behavioral evaluation, give an executor only each development case's `task` and `input`. Keep `criteria` for the reviewer. Check factual correspondence and inference scope alongside whether the prose advances the argument.
