# 论文写作 · 反过度防御

[English](README.en.md) · [Skill](skills/anti-overdefensive-paper-writing/SKILL.md) · [验证记录](docs/validation.md) · [MIT License](LICENSE)

让论文中的句子推进论证，保留有用的证据、比较和条件。适用于中文与英文论文的起草、润色、压缩和写作审查。

**当前版本：0.4.0。**

## 解决什么问题

AI 改稿常在句子里预先回应无人提出的质疑：

> 本研究不是要取代所有检索框架，而是探索候选筛选。这不意味着它具有通用能力，也不能认为实验代表全面验证。

假设材料给出的事实是“两项同领域测试中，候选筛选使召回率从 71% 提高至 74%”，正文可以直接写：

> 在两项同领域测试中，候选筛选使召回率从 71% 提高至 74%。

Skill 检查否定对照、预判质疑、反复限定、自我贬低、自证旁白和空泛总结，并结合上下文判断它们的作用。真实负面结果、方法条件、统计解释与实际竞争观点按证据保留。

## 核心能力

- 围绕研究问题、贡献、机制和证据组织全文，明确实验各自支持什么判断。
- 清理“不是……而是……”“不意味着”“不代表”“不能认为”及中英文隐蔽变体。
- 保全数值与对应关系、肯否极性、适用范围、推断力度、来源状态和引文作用。
- 区分局部重述与跨结果综合，保留条件归纳、方法比较和收益与代价的权衡。
- 按作者范文和目标读者校准表达，检查修订中新添的解释是否有实际作用。
- 提供只读候选扫描器，定位 UTF-8 文本、Markdown 和 LaTeX 中的已配置句式。

## 安装与使用

在 Codex 中提出：

```text
安装这个 GitHub Skill：
https://github.com/wmxxhb/anti-overdefensive-paper-writing/tree/main/skills/anti-overdefensive-paper-writing
```

也可以将仓库内 `skills/anti-overdefensive-paper-writing` 文件夹复制到自己的技能目录。默认个人技能目录为 `~/.codex/skills`；设置过 `CODEX_HOME` 时使用其 `skills` 子目录。

安装后，在下一轮对话中调用：

```text
使用 $anti-overdefensive-paper-writing 润色下面的论文段落，直接给出正文。
```

```text
使用 $anti-overdefensive-paper-writing 审查这篇论文的防御性写作。
保留原稿，按位置报告问题、后果和具体改法。
```

```text
使用 $anti-overdefensive-paper-writing 压缩摘要，保留全部关键结果与代价。
```

Skill 的说明允许任务匹配时自动选用。其他支持文件式技能的助手可读取 `SKILL.md` 及其按需引用的资源。

## 单独使用扫描器

Python 3.10 及以上；扫描器和测试只使用标准库。

```sh
python skills/anti-overdefensive-paper-writing/scripts/scan_defensive_prose.py paper.md
python skills/anti-overdefensive-paper-writing/scripts/scan_defensive_prose.py paper.tex --format json
python skills/anti-overdefensive-paper-writing/scripts/scan_defensive_prose.py paper.md --include-blockquotes
```

标准输入用 `-`；LaTeX 标准输入加 `--latex`。结果包含候选类型、行列位置和上下文，文件保持原样。编辑时根据句子的论证作用判断。

常用代码、公式区域及引用键会被屏蔽，脚注、列表正文和引文中的可见说明继续扫描。Markdown 引用块默认排除，可按需纳入。

## 运行验证

从仓库根目录运行：

```sh
python -B -m unittest discover -s skills/anti-overdefensive-paper-writing/tests -p test_scanner.py
python -B validation/run_probes.py
```

当前包有 **50 项单元测试和 100 项格式探针**。另有 14 项开发行为材料，以及四项实际写作交付的独立复核记录说明。测试范围和结果见[验证记录](docs/validation.md)。

## 目录

```text
skills/anti-overdefensive-paper-writing/
  SKILL.md                 入口与核心规则
  agents/openai.yaml       展示与调用说明
  references/              全文工作流、例子与来源
  scripts/                 只读候选扫描器
  tests/                   单元测试与开发行为材料
validation/                可复现格式探针与包指纹
docs/validation.md         验证范围与结果
```

## 来源与贡献

设计参考了八个开源项目，采用内容和固定版本见[来源记录](skills/anti-overdefensive-paper-writing/references/source-notes.md)，原许可证见 [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md)。本项目采用 [MIT 许可证](LICENSE)。

欢迎提交问题和修改。写作问题请提供可公开的最小上下文、应保留的信息及实际输出；扫描器问题请提供输入格式、预期候选和实际位置。
