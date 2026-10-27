# 论文写作 · 反过度防御

**让 AI 改论文时少一点预先辩解，多一点有效论证。**

[English](README.en.md) · [查看 Skill](skills/anti-overdefensive-paper-writing/SKILL.md) · [v0.4.0](https://github.com/wmxxhb/anti-overdefensive-paper-writing/tree/v0.4.0)

AI 润色后的论文里，常常多出“不是……而是……”“不意味着”“不代表”“不能认为”。段落开始回应假想的质疑，结尾再补一遍限制，原本清楚的研究发现被埋在解释和自我审查里。

这个 Skill 帮助 AI 清理这些表达，把段落重新组织到研究问题、方法和证据上。支持中文与英文论文的起草、润色、压缩和写作审查。

## 改写前后

**改写前**

> 本研究不是要取代现有检索框架，而是探索一种候选筛选方法。尽管我们在两个同领域数据集上将召回率从 71% 提高至 74%，但必须承认，这不代表它解决了所有检索问题，仍需谨慎看待其潜在价值。

**改写后**

> 候选筛选方法在两个同领域数据集上将召回率从 71% 提高至 74%。

处理的重点是句子的作用：删去后会损失哪项事实、解释或推理条件？有作用的比较、负面结果、适用条件和统计解释随正文保留。

## 它会处理哪些问题

| 常见表现 | 处理方式 |
|---|---|
| “不是……而是……”、`not X but Y`，先否定一个无关对象 | 直接说明研究做了什么 |
| “不意味着”“不代表”“有人可能质疑”，反复预判误读 | 对应当前主张，保留有实际作用的说明 |
| “遗憾的是”“仅是简单改进”“价值有限” | 写清具体收益、代价和比较条件 |
| 每段重复“仍需谨慎”“尚待进一步研究” | 将条件放在它真正限定的主张旁 |
| “先试了 A，后来改成 B”，实验像工作日志 | 围绕每项实验支持的判断安排内容 |
| 段尾同义复述、泛泛升华、空泛未来展望 | 压缩重复，保留跨结果的综合判断 |

全文修改时，还会核对贡献主线、数值与术语、引文支持关系，以及改稿中新添的解释。

## 快速开始

把下面这段话发给 Codex：

```text
安装这个论文写作 Skill：
https://github.com/wmxxhb/anti-overdefensive-paper-writing/tree/main/skills/anti-overdefensive-paper-writing
```

安装后，在下一轮对话中使用。也可以下载仓库，将 `skills/anti-overdefensive-paper-writing` 整个文件夹放入自己的技能目录。

### 润色段落

```text
使用 $anti-overdefensive-paper-writing 润色下面的论文段落，直接给出可用正文。

[粘贴段落]
```

### 压缩摘要

```text
使用 $anti-overdefensive-paper-writing 将摘要压缩到 200 字以内，保留关键结果、代价和适用条件。

[粘贴摘要]
```

### 审查全文

```text
使用 $anti-overdefensive-paper-writing 审查这篇论文的防御性写作。
保留原稿，按位置报告问题和具体改法。

[提供稿件]
```

提供自己的论文片段作为范文，可以进一步校准术语、句式和表达习惯。

## 扫描已有稿件

仓库附带一个只读扫描器，支持 UTF-8 文本、Markdown 和 LaTeX。需要 Python 3.10 及以上，无第三方依赖。

```sh
python skills/anti-overdefensive-paper-writing/scripts/scan_defensive_prose.py paper.md
python skills/anti-overdefensive-paper-writing/scripts/scan_defensive_prose.py paper.tex --format json
```

输出包含候选表达、行列位置和上下文。代码、常见公式区域和引用键会被屏蔽；脚注、列表正文和引文中的可见说明继续扫描。逐项结合上下文决定改法。

## 验证

当前版本通过 **50 项单元测试和 100 项格式探针**，四项实际写作交付均通过独立复核。详见[验证记录](docs/validation.md)。

<details>
<summary>运行测试</summary>

从仓库根目录运行：

```sh
python -B -m unittest discover -s skills/anti-overdefensive-paper-writing/tests -p test_scanner.py
python -B validation/run_probes.py
```

</details>

## 写报告、说明或方案时

研究报告、技术说明、分析文章和项目方案，使用[通用论述写作版](https://github.com/wmxxhb/anti-overdefensive-writing)。它按读者的理解、判断和行动任务组织内容；本仓库侧重论文的贡献定位、实验组织和学术论证。两份 Skill 均可独立安装。

## License

[MIT](LICENSE)
