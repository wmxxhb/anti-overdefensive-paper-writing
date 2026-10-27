import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "scan_defensive_prose.py"
spec = importlib.util.spec_from_file_location("defensive_scanner", SCRIPT)
scanner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(scanner)


class ScannerBehaviorTests(unittest.TestCase):
    def kinds(self, text, **kwargs):
        return {item["kind"] for item in scanner.scan_text(text, **kwargs)}

    def test_full_chinese_contrast_is_one_candidate(self):
        findings = scanner.scan_text("该模块不是为了替代检索器，而是缩小候选集合。")
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["kind"], "negative-contrast")

    def test_reversed_contrast_from_reviewed_document(self):
        self.assertIn("negative-contrast", self.kinds("简化以理解成本而不是行数为目标。"))

    def test_split_contrast_has_original_line_positions(self):
        text = "说明。\n\n这不是参数规模问题。\n真正的问题在于缺少跨层交换。"
        item = next(item for item in scanner.scan_text(text) if item["kind"] == "negative-contrast")
        self.assertEqual(item["line"], 3)
        self.assertEqual(item["end_line"], 4)
        self.assertIn("\n", item["matched"])

    def test_requested_denials(self):
        text = "结果不意味着通用能力，也不能认为覆盖所有场景，且不代表全面验证。"
        matches = scanner.scan_text(text)
        self.assertEqual([item["matched"] for item in matches], ["不意味着", "不能认为", "不代表"])

    def test_english_split_and_reversed_contrasts(self):
        self.assertIn("negative-contrast", self.kinds("This is not a replacement. Rather, it narrows the candidate set."))
        self.assertIn("negative-contrast", self.kinds("We optimize comprehension rather than line count."))

    def test_contrast_does_not_cross_paragraphs(self):
        self.assertNotIn("negative-contrast", self.kinds("This is not a replacement.\n\nBut the next unrelated topic concerns storage."))

    def test_ordinary_calibration_is_not_a_hedge_stack(self):
        self.assertNotIn("hedge-stack", self.kinds("The observations may suggest a seasonal effect."))

    def test_dense_hedges_are_found(self):
        self.assertIn("hedge-stack", self.kinds("结果或许可能初步提示存在潜在改善。"))
        self.assertIn("hedge-stack", self.kinds("The result could potentially possibly suggest an improvement."))

    def test_markdown_code_and_frontmatter_keep_real_prose_locations(self):
        text = "---\ndescription: 不是甲而是乙\n---\n```python\nprint('不代表')\n```\n`不能认为`\n正文不代表全面验证。"
        findings = scanner.scan_text(text)
        self.assertEqual(len(findings), 1)
        self.assertEqual((findings[0]["line"], findings[0]["column"]), (8, 3))

    def test_latex_comments_math_and_citation_keys_are_ignored(self):
        text = "% 不是甲而是乙\n\\begin{verbatim}\n不意味着\n\\end{verbatim}\n$x=\\text{不代表}$ \\cite{不能认为}\n正文不代表全面验证。"
        findings = scanner.scan_text(text, latex=True)
        self.assertEqual(len(findings), 1)
        self.assertEqual(findings[0]["line"], 6)

    def test_percent_in_prose_does_not_hide_later_candidate(self):
        self.assertIn("preemptive-denial", self.kinds("准确率为 85%，不代表全面验证。"))
        self.assertIn("preemptive-denial", self.kinds(r"准确率为 85\%，不代表全面验证。", latex=True))

    def test_unclosed_frontmatter_does_not_hide_whole_document(self):
        self.assertIn("preemptive-denial", self.kinds("---\n正文不代表全面验证。"))

    def test_necessary_negation_is_a_candidate_without_an_edit_verdict(self):
        findings = scanner.scan_text("相关性不代表因果性；本研究没有控制混杂。")
        self.assertEqual(len(findings), 1)
        self.assertNotIn("delete", findings[0])
        self.assertNotIn("severity", findings[0])

    def test_cli_json_is_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "paper.tex"
            original = "% 不代表\n方法不是替代检索器，而是缩小集合。\\cite{key}\n"
            path.write_text(original, encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(path), "--format", "json"], capture_output=True, text=True, encoding="utf-8", check=True)
            output = json.loads(result.stdout)
            self.assertEqual(output["candidate_count"], 1)
            self.assertEqual(output["findings"][0]["line"], 2)
            self.assertEqual(path.read_text(encoding="utf-8"), original)

    def test_cli_accepts_chinese_stdin(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "-", "--format", "json"], input="结果不意味着通用能力。", capture_output=True, text=True, encoding="utf-8", check=True)
        self.assertEqual(json.loads(result.stdout)["candidate_count"], 1)

    def test_cli_reports_missing_input(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, str(SCRIPT), str(Path(directory) / "absent.md")], capture_output=True, text=True, encoding="utf-8")
            self.assertEqual(result.returncode, 2)

    def test_direct_prose_has_no_candidates(self):
        self.assertEqual(scanner.scan_text("在三个数据集上，平均准确率提高 1.2 个百分点。"), [])

    def test_english_split_without_but_or_rather(self):
        for text in ["This isn't a new benchmark. It is a retrieval module.",
                     "This is not a benchmark. It's a retrieval module.",
                     "The answer isn't scale. The real issue is information exchange."]:
            with self.subTest(text=text):
                self.assertIn("negative-contrast", self.kinds(text))

    def test_english_appended_negation(self):
        for text in ["Fast retrieval, not universal answers.",
                     "The module is good for retrieval, not for universal answers.",
                     "It merges lists, and not datasets.", "The score comes from the selected item, no guessing."]:
            with self.subTest(text=text):
                self.assertIn("negative-contrast", self.kinds(text))

    def test_english_negation_countdown(self):
        self.assertIn("negative-contrast", self.kinds("No new benchmark. No universal theory. Just candidate merging."))
        self.assertNotIn("negative-contrast", self.kinds("No treatment effect was detected."))

    def test_chinese_denial_with_inserted_object(self):
        for text in ["不能将该结果理解为全面验证。", "不能把该关联视为因果关系。"]:
            with self.subTest(text=text):
                self.assertIn("preemptive-denial", self.kinds(text))

    def test_closed_math_environments_keep_surrounding_prose(self):
        for env in ["equation", "equation*", "align", "align*", "gather", "multline", "displaymath", "math"]:
            with self.subTest(env=env):
                text = "前文。\n\\begin{" + env + "}\n\\text{not X but Y}\n\\end{" + env + "}\n正文不代表全面验证。"
                matches = scanner.scan_text(text, latex=True)
                self.assertEqual(len(matches), 1)
                self.assertEqual((matches[0]["line"], matches[0]["column"]), (5, 3))

    def test_inline_math_environment_keeps_prose_on_both_sides(self):
        text = r"不代表通用性。\begin{equation}\text{not X but Y}\end{equation}不意味着全面验证。"
        self.assertEqual([x["matched"] for x in scanner.scan_text(text, latex=True)], ["不代表", "不意味着"])

    def test_unclosed_math_environment_does_not_hide_rest_of_paper(self):
        self.assertIn("preemptive-denial", self.kinds("\\begin{align}\n正文不代表全面验证。", latex=True))

    def test_blockquotes_default_exclusion_and_opt_in(self):
        text = '> 原话不是甲而是乙。\n> 原话不代表全面验证。\n\n正文不代表通用性。'
        matches = scanner.scan_text(text)
        self.assertEqual(len(matches), 1)
        self.assertEqual((matches[0]["line"], matches[0]["column"]), (4, 3))
        self.assertEqual(len(scanner.scan_text(text, include_blockquotes=True)), 3)

    def test_lazy_blockquote_continuation_and_heading_boundary(self):
        text = '> 这是原话。\n这不代表全面验证。\n# 正文\n正文不代表通用性。'
        matches = scanner.scan_text(text)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["line"], 4)

    def test_quoted_candidates_can_be_requested_via_cli(self):
        result = subprocess.run([sys.executable, str(SCRIPT), "-", "--format", "json", "--include-blockquotes"],
                                input="> 原话不代表全面验证。", capture_output=True, text=True, encoding="utf-8", check=True)
        self.assertEqual(json.loads(result.stdout)["candidate_count"], 1)

    def test_formal_logic_in_math_is_ignored_but_real_prose_is_reviewable(self):
        text = r"$\text{P, not Q}$。差异来自模块而非额外特征。"
        matches = scanner.scan_text(text, latex=True)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]["matched"], "而非")
        self.assertNotIn("delete", matches[0])

    def test_english_split_does_not_cross_empty_paragraph(self):
        self.assertNotIn("negative-contrast", self.kinds("This isn't a new benchmark.\n\nIt is raining today."))

    def test_markdown_footnote_first_line_and_continuation_are_prose(self):
        text = "正文[^1]。\n\n[^1]: 这不意味着全面验证。\n    这不代表通用性。"
        findings = scanner.scan_text(text)
        self.assertEqual([(x["line"], x["column"]) for x in findings], [(3, 8), (4, 6)])

    def test_markdown_footnote_labels_and_link_definitions_are_not_prose(self):
        text = "正文[^not-X-but-Y]。\n\n[^not-X-but-Y]: 有效正文。\n[link]: https://example.test/ 不代表"
        self.assertEqual(scanner.scan_text(text), [])

    def test_common_citation_keys_are_masked_without_hiding_neighbors(self):
        for command in ["cite", "citet", "citep", "citeauthor", "citeyearpar", "autocite", "parencite", "textcite", "footcite", "smartcite", "supercite", "nocite", "Cite", "Textcite"]:
            with self.subTest(command=command):
                text = "\\" + command + "{not-X-but-Y}。不代表通用性。"
                matches = scanner.scan_text(text, latex=True)
                self.assertEqual(len(matches), 1)
                self.assertEqual(matches[0]["matched"], "不代表")

    def test_citation_optional_notes_remain_visible(self):
        text = r"\parencite*[这不意味着全面验证][第3页]{not-X-but-Y}"
        matches = scanner.scan_text(text, latex=True)
        self.assertEqual([x["matched"] for x in matches], ["不意味着"])

    def test_citation_text_command_is_visible_prose(self):
        matches = scanner.scan_text(r"\citetext{这不代表通用性；参见\cite{not-X-but-Y}}", latex=True)
        self.assertEqual([x["matched"] for x in matches], ["不代表"])

    def test_independent_chinese_negative_positioning(self):
        for text in ["我们的目的并非替代现有检索器。", "本文并非一个完整理论。", "这并不是参数规模问题。"]:
            with self.subTest(text=text):
                self.assertIn("negative-contrast", self.kinds(text))

    def test_english_contracted_denial_variants(self):
        for text in ["This doesn't mean the method is universal.", "We don't claim a universal theory.", "We don’t claim superiority.", "This didn't prove equivalence."]:
            with self.subTest(text=text):
                matches = scanner.scan_text(text)
                self.assertIn("preemptive-denial", {x["kind"] for x in matches})
                self.assertTrue(all("delete" not in x for x in matches))

    def test_standalone_indented_code_keeps_neighboring_prose_positions(self):
        for indent in ["    ", "\t"]:
            with self.subTest(indent=repr(indent)):
                text = indent + "print('不是甲而是乙')\n\n正文不代表通用性。"
                findings = scanner.scan_text(text)
                self.assertEqual([(x["line"], x["column"], x["matched"]) for x in findings], [(3, 3, "不代表")])

    def test_indented_paragraph_continuation_remains_prose(self):
        text = "正文已有说明，\n    这不代表通用性。"
        self.assertEqual([x["matched"] for x in scanner.scan_text(text)], ["不代表"])

    def test_footnote_and_list_prose_after_blank_line_remain_visible(self):
        for text in ["[^a]: 说明。\n\n    这不代表通用性。",
                     "- 说明。\n\n    这不代表通用性。",
                     "1. 说明。\n\n    这不代表通用性。"]:
            with self.subTest(text=text):
                self.assertEqual([x["matched"] for x in scanner.scan_text(text)], ["不代表"])

    def test_nested_indented_code_is_excluded_inside_prose_containers(self):
        for text in ["[^a]: 说明。\n\n        print('不是甲而是乙')\n\n    这不代表通用性。",
                     "- 说明。\n\n      print('不是甲而是乙')\n\n  这不代表通用性。"]:
            with self.subTest(text=text):
                self.assertEqual([x["matched"] for x in scanner.scan_text(text)], ["不代表"])

    def test_latex_indentation_is_not_markdown_code(self):
        self.assertEqual([x["matched"] for x in scanner.scan_text("    这不代表通用性。", latex=True)], ["不代表"])

    def test_nested_list_prose_and_return_from_code_remain_visible(self):
        for text in ["- a\n\n    - b\n\n      不代表。",
                     "- a\n\n    - b\n\n          print('不是甲而是乙')\n\n      不代表。",
                     "- a\n\n    - b\n\n      不代表。\n\n    - c\n\n      不意味着。",
                     "[^a]: 注释。\n\n    - b\n\n      不代表。"]:
            with self.subTest(text=text):
                findings = scanner.scan_text(text)
                self.assertEqual([x["matched"] for x in findings], ["不代表", "不意味着"] if "不意味着" in text else ["不代表"])

    def test_latex_verb_delimiters_keep_neighbors_and_offsets(self):
        for command in [r"\verb", r"\verb*"]:
            for delimiter in ["|", "+", "!"]:
                with self.subTest(command=command, delimiter=delimiter):
                    text = command + delimiter + "not X but Y" + delimiter + "。正文不代表通用性。"
                    findings = scanner.scan_text(text, latex=True)
                    self.assertEqual([(x["line"], x["column"], x["matched"]) for x in findings], [(1, text.index("不代表") + 1, "不代表")])

    def test_percent_and_fake_environment_inside_verb_do_not_hide_prose(self):
        text = r"\verb|% \begin{minted} not X but Y| 正文不代表通用性。"
        self.assertEqual([x["matched"] for x in scanner.scan_text(text, latex=True)], ["不代表"])

    def test_unclosed_verb_does_not_hide_later_prose(self):
        text = "\\verb|not X but Y\n正文不代表通用性。"
        self.assertIn("不代表", [x["matched"] for x in scanner.scan_text(text, latex=True)])

    def test_literal_verb_inside_verb_is_not_reinterpreted(self):
        for command in [r"\verb", r"\verb*"]:
            with self.subTest(command=command):
                text = command + r"|\verb!| 不代表。!"
                findings = scanner.scan_text(text, latex=True)
                self.assertEqual([(x["column"], x["matched"]) for x in findings], [(text.index("不代表") + 1, "不代表")])

    def test_multicite_keys_are_masked_but_following_prose_remains(self):
        for command in ["cites", "autocites", "parencites", "textcites", "footcites", "smartcites", "supercites", "Parencites"]:
            with self.subTest(command=command):
                text = "\\" + command + "{not-X-but-Y}{not-A-but-B}。正文不代表通用性。"
                self.assertEqual([x["matched"] for x in scanner.scan_text(text, latex=True)], ["不代表"])

    def test_multicite_global_and_per_item_notes_remain_prose(self):
        text = r"\autocites(不代表通用性)(说明)[这不意味着全面验证][第3页]{not-X-but-Y}[不能认为等效]{second-key}"
        self.assertEqual([x["matched"] for x in scanner.scan_text(text, latex=True)], ["不代表", "不意味着", "不能认为"])

    def test_nested_citation_notes_and_unrelated_braces_stay_visible(self):
        text = r"\parencites[见{图[2]}，这不代表通用性]{not-X-but-Y}[不意味着全面验证]{other} 正文{不能认为等效}"
        self.assertEqual([x["matched"] for x in scanner.scan_text(text, latex=True)], ["不代表", "不意味着", "不能认为"])

    def test_incomplete_multicite_does_not_hide_following_paragraph(self):
        text = "\\autocites{valid}[缺少闭括号\n\n正文不代表通用性。"
        self.assertIn("不代表", [x["matched"] for x in scanner.scan_text(text, latex=True)])


if __name__ == "__main__":
    unittest.main()
