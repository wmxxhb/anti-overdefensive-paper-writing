#!/usr/bin/env python3
"""Locate candidate defensive prose in UTF-8 text, Markdown, or LaTeX."""
from __future__ import annotations

import argparse
import bisect
import json
import re
import sys
from pathlib import Path


PATTERNS = {
    "negative-contrast": [
        r"(?:不是|并非|不在于|不只是|不仅仅是).{1,140}?(?:而是|而在于|关键在于|真正.{0,8}?是)",
        r"(?:不是|并非)[^。！？\n]{1,90}[。！？]\s*(?:真正|关键|实际|本质|问题在于|它是|这是)",
        r"(?:这|本文|本研究|该方法|我们的?(?:工作|目的|目标))(?:并非|(?:并)?不是)[^。！？\n]{1,80}",
        r"而不是|而非",
        r"\b(?:not|isn['’]t|aren['’]t|wasn['’]t)\b.{1,180}?\b(?:but|rather)\b",
        r"\b(?:not|isn['’]t|aren['’]t|wasn['’]t)\b[^.!?\n]{1,140}[.!?]\s*(?:it\s+is|it['’]s|this\s+is|the\s+(?:real\s+)?(?:issue|point|answer|story)\s+is)\b",
        r"[,;—]\s*(?:and\s+)?not\s+[^.!?;\n]{1,100}",
        r"[,;—]\s*no\s+(?:guessing|fluff|magic|hype)\b",
        r"\bno\s+[^.!?\n]{1,70}[.!?]\s*no\s+[^.!?\n]{1,70}[.!?]\s*just\s+[^.!?\n]{1,100}",
        r"\brather\s+than\b",
    ],
    "preemptive-denial": [
        r"(?:并)?不(?:意味着|代表|等于|表示|说明|意在)|不能(?:据此)?(?:认为|推断|断言|理解为)|(?:我们|本文|本研究)并?不(?:声称|试图|宣称)",
        r"不能(?:据此)?(?:将|把)[^。！？;；\n]{1,60}?(?:理解为|视为|当作|看作)",
        r"\b(?:(?:does|do|did)\s+not|(?:doesn|don|didn)['’]t)\s+(?:mean|imply|represent|prove|establish)\b",
        r"\b(?:we|this\s+(?:study|paper))\s+(?:(?:do|does)\s+not|(?:don|doesn)['’]t)\s+claim\b|\bnot\s+intended\s+to\b",
    ],
    "anticipated-objection": [
        r"(?:为(?:了)?(?:避免|防止)).{0,30}?(?:质疑|误解)|(?:有人|读者|审稿人).{0,8}?可能.{0,8}?(?:认为|质疑|误以为)",
        r"\b(?:one\s+might|some\s+may|critics\s+might)\s+(?:argue|object|think)\b",
    ],
    "generic-caution": [
        r"(?:仍|还|尚)(?:然)?需.{0,12}?(?:进一步|更多).{0,8}?研究|(?:应|需要|必须).{0,6}?谨慎(?:理解|看待|解读)",
        r"\b(?:more|further)\s+research\s+is\s+needed\b|\bshould\s+be\s+interpreted\s+with\s+caution\b",
    ],
    "authorial-apology": [
        r"遗憾的是|必须承认|仅(?:是|仅是)(?:一[个种项])?简单|(?:本文|本研究|该方法).{0,12}?(?:价值有限|严重不足)",
        r"\bunfortunately\b|\bwe\s+must\s+acknowledge\b|\bmerely\s+a\s+simple\b",
    ],
}
COMPILED = {
    name: [re.compile(pattern, re.IGNORECASE | re.DOTALL) for pattern in patterns]
    for name, patterns in PATTERNS.items()
}
HEDGES = re.compile(
    r"可能|或许|也许|似乎|初步|一定程度上|潜在|提示|"
    r"\b(?:may|might|could|potentially|possibly|perhaps|tentatively|suggest)\b",
    re.IGNORECASE,
)
LABELS = {
    "negative-contrast": "否定对照",
    "preemptive-denial": "否定式澄清",
    "anticipated-objection": "预判质疑",
    "generic-caution": "泛化谨慎语",
    "authorial-apology": "作者自我削弱",
    "hedge-stack": "相邻限定词叠加",
}


def group_end(text: str, start: int, opening: str, closing: str) -> int | None:
    """Find a balanced TeX argument, respecting escapes and nested braces."""
    if start >= len(text) or text[start] != opening:
        return None
    stack = [closing]
    index = start + 1
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if char == stack[-1]:
            stack.pop()
            if not stack:
                return index + 1
        elif char == "{":
            stack.append("}")
        elif char == opening and stack[-1] != "}":
            stack.append(closing)
        index += 1
    return None


def mask_markup(text: str, latex: bool = False, include_blockquotes: bool = False) -> str:
    """Mask code and formatting internals while keeping character offsets."""
    chars = list(text)

    def mask(start: int, end: int) -> None:
        for index in range(start, end):
            if chars[index] != "\n":
                chars[index] = " "

    frontmatter = re.match(r"\A---\r?\n.*?\r?\n---(?:\r?\n|$)", text, re.DOTALL)
    if frontmatter:
        mask(0, frontmatter.end())
    if latex:
        # Verbatim delimiters make %, braces and environment names literal.
        verbatim_end = 0
        for match in re.finditer(r"\\verb(?![A-Za-z])\*?([^\s])", text):
            if match.start() < verbatim_end:
                continue
            delimiter = match.group(1)
            end = text.find(delimiter, match.end())
            newline = text.find("\n", match.end())
            if end >= 0 and (newline < 0 or end < newline):
                mask(match.start(), end + 1)
                verbatim_end = end + 1
    offset = 0
    fence = None
    latex_code = None
    blockquote = False
    paragraph_open = False
    container_indent = 0
    container_indents = []
    indented_code = None
    for line in text.splitlines(keepends=True):
        visible_line = "".join(chars[offset:offset + len(line)])
        blank = not visible_line.strip()
        indent = len(visible_line.expandtabs(4)) - len(visible_line.expandtabs(4).lstrip(" "))
        quote_marker = re.match(r"^ {0,3}>", visible_line)
        block_start = re.match(r"^ {0,3}(?:#{1,6}\s|`{3,}|~{3,}|[-+*]\s|\d+[.)]\s|---+\s*$)", visible_line)
        footnote = re.match(r"^ {0,3}\[\^[^\]]+\]:[ \t]*", visible_line)
        list_marker = re.match(r"^[ \t]*(?:[-+*]|\d+[.)])[ \t]+", visible_line)
        list_item = None
        if frontmatter and offset < frontmatter.end():
            paragraph_open = False
        elif latex_code:
            mask(offset, offset + len(line))
            if "\\end{" + latex_code + "}" in visible_line:
                latex_code = None
        elif fence:
            mask(offset, offset + len(line))
            closing = re.match(r"^\s*(`{3,}|~{3,})\s*$", visible_line)
            if closing and closing.group(1)[0] == fence[0] and len(closing.group(1)) >= len(fence):
                fence = None
            paragraph_open = False
        elif not latex and not include_blockquotes and (quote_marker or (blockquote and line.strip() and not block_start)):
            mask(offset, offset + len(line))
            blockquote = True
            paragraph_open = False
        else:
            blockquote = False
            if not latex:
                if indented_code is not None and not blank and indent < indented_code:
                    indented_code = None
                if indented_code is None and not blank:
                    while container_indents and indent < container_indents[-1]:
                        container_indents.pop()
                    container_indent = container_indents[-1] if container_indents else 0
                    if footnote:
                        container_indents = [4]
                    elif list_marker and indent < container_indent + 4:
                        list_item = list_marker
                        container_indents.append(len(list_item.group().expandtabs(4)))
                    container_indent = container_indents[-1] if container_indents else 0
            opening = re.match(r"^\s*(`{3,}|~{3,})", visible_line)
            environment = re.search(r"\\begin\{(verbatim\*?|lstlisting|minted)\}", visible_line) if latex else None
            if not latex and (indented_code is not None or (
                not blank and not paragraph_open and not footnote and not list_item and indent >= container_indent + 4
            )):
                if indented_code is None:
                    indented_code = container_indent + 4
                mask(offset, offset + len(line))
                paragraph_open = False
            elif opening:
                fence = opening.group(1)
                mask(offset, offset + len(line))
                paragraph_open = False
            elif environment:
                latex_code = environment.group(1)
                mask(offset, offset + len(line))
                if "\\end{" + latex_code + "}" in visible_line[environment.end():]:
                    latex_code = None
            elif footnote:
                mask(offset, offset + footnote.end())
                paragraph_open = bool(visible_line[footnote.end():].strip())
            elif re.match(r"^\s*\[(?!\^)[^\]]+\]:\s*", visible_line):
                mask(offset, offset + len(line))
                paragraph_open = False
            elif latex:
                for match in re.finditer("%", visible_line):
                    before = visible_line[:match.start()]
                    escapes = len(before) - len(before.rstrip("\\"))
                    if escapes % 2 == 0:
                        mask(offset + match.start(), offset + len(line))
                        break
            else:
                paragraph_open = not blank and (list_item is not None or block_start is None)
        offset += len(line)
    masked = "".join(chars)
    masks = [
        r"(?P<ticks>`+)(?:(?!(?P=ticks)).)*?(?P=ticks)",
        r"\$\$.*?\$\$",
        r"(?<!\\)\$(?!\$)[^$\n]*?(?<!\\)\$",
        r"\\\[.*?\\\]",
        r"\\\(.*?\\\)",
        r"\[\^[^\]\n]+\]",
        r"\\(?:ref|eqref|label)\*?\{[^}]*\}",
        r"https?://[^\s<>\])]+",
    ]
    if latex:
        masks.insert(0, r"\\begin\{(?P<mathenv>(?:equation|align|alignat|gather|multline|flalign)\*?|displaymath|math)\}.*?\\end\{(?P=mathenv)\}")
    for pattern in masks:
        for match in re.finditer(pattern, masked, re.DOTALL):
            mask(match.start(), match.end())
    citation = re.compile(
        r"\\(?P<name>cite(?:p|t|alt|alp|author|year(?:par)?|title|date|url|num)?|"
        r"(?:auto|paren|text|foot|super|smart)cite|nocite|"
        r"(?:auto|paren|text|foot|super|smart)?cites)(?![A-Za-z])\*?", re.IGNORECASE
    )
    citation_text = "".join(chars)
    whitespace = re.compile(r"\s*")
    for match in citation.finditer(citation_text):
        multiple = match.group("name").lower().endswith("cites")
        cursor = match.end()
        if multiple:
            # Global multicite notes, like per-item notes, remain visible prose.
            for _ in range(2):
                cursor = whitespace.match(citation_text, cursor).end()
                end = group_end(citation_text, cursor, "(", ")")
                if end is None:
                    break
                cursor = end
        while True:
            cursor = whitespace.match(citation_text, cursor).end()
            while cursor < len(citation_text) and citation_text[cursor] == "[":
                end = group_end(citation_text, cursor, "[", "]")
                if end is None:
                    break
                cursor = end
                cursor = whitespace.match(citation_text, cursor).end()
            end = group_end(citation_text, cursor, "{", "}")
            if end is None:
                break
            mask(match.start(), match.end())
            mask(cursor, end)
            cursor = end
            if not multiple:
                break
    return "".join(chars)


def scan_text(text: str, latex: bool = False, include_blockquotes: bool = False) -> list[dict]:
    masked = mask_markup(text, latex=latex, include_blockquotes=include_blockquotes)
    line_starts = [0] + [match.end() for match in re.finditer("\n", text)]
    found = []
    for paragraph in re.finditer(r"(?:[^\n]|\n(?![ \t]*\n))+", masked):
        block = paragraph.group()
        if not block.strip():
            continue
        raw = []
        for kind, patterns in COMPILED.items():
            for pattern in patterns:
                for match in pattern.finditer(block):
                    raw.append((kind, match.start(), match.end()))
        hedges = list(HEDGES.finditer(block))
        for index in range(len(hedges) - 2):
            group = hedges[index:index + 3]
            window = block[group[0].start():group[-1].end()]
            limit = 40 if re.search(r"[\u4e00-\u9fff]", window) else 100
            if len(window) <= limit and not re.search(r"[。！？.!?;；\n]", window):
                raw.append(("hedge-stack", group[0].start(), group[-1].end()))
        merged = []
        for kind, start, end in sorted(raw):
            if merged and merged[-1][0] == kind and start <= merged[-1][2]:
                previous = merged[-1]
                merged[-1] = (kind, previous[1], max(previous[2], end))
            else:
                merged.append((kind, start, end))
        for kind, start, end in merged:
            absolute = paragraph.start() + start
            absolute_end = paragraph.start() + end
            line_index = bisect.bisect_right(line_starts, absolute) - 1
            end_index = bisect.bisect_right(line_starts, absolute_end - 1) - 1
            found.append({
                "kind": kind,
                "label": LABELS[kind],
                "line": line_index + 1,
                "column": absolute - line_starts[line_index] + 1,
                "end_line": end_index + 1,
                "matched": text[absolute:absolute_end],
                "context": text[paragraph.start():paragraph.end()].strip(),
            })
    return sorted(found, key=lambda item: (item["line"], item["column"], item["kind"]))


def main() -> int:
    parser = argparse.ArgumentParser(description="定位防御性表达候选，输出位置及上下文。")
    parser.add_argument("path", nargs="?", default="-", help="UTF-8 的 txt/md/tex 文件；- 表示标准输入")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--latex", action="store_true", help="标准输入按 LaTeX 处理；.tex 文件自动启用")
    parser.add_argument("--include-blockquotes", action="store_true", help="将 Markdown 引用块也列为候选审读区域；保留原话")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stdin, "reconfigure") and args.path == "-":
        sys.stdin.reconfigure(encoding="utf-8")
    try:
        text = sys.stdin.read() if args.path == "-" else Path(args.path).read_text(encoding="utf-8-sig")
    except (OSError, UnicodeError) as error:
        parser.error(str(error))
    findings = scan_text(text, latex=args.latex or Path(args.path).suffix.lower() == ".tex", include_blockquotes=args.include_blockquotes)
    if args.format == "json":
        print(json.dumps({"source": args.path, "candidate_count": len(findings), "findings": findings}, ensure_ascii=False, indent=2))
    elif findings:
        print(f"{len(findings)} 处候选；结合段落的论证任务审读。")
        for item in findings:
            print(f"{args.path}:{item['line']}:{item['column']} [{item['label']}] " + " ".join(item["matched"].split()))
            print("  " + " ".join(item["context"].split()))
    else:
        print("未发现已配置模式的候选。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
