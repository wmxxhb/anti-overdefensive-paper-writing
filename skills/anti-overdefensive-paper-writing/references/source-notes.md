# 来源与设计记录

版本：0.4.0；日期：2026-10-27。

主要需求来自本次对话：论文中的句子应推进解释和论证；预判质疑、反复否定和追加限制会中断这一过程。我们生成的研究报告也出现了同类问题，尤其漏检了否定对照。本 Skill 因此同时约束起草、修订与完成前检查。

## 参考仓库与采用内容

| 仓库固定提交 | 采用内容 |
|---|---|
| [Adkid-Zephyr/anti-defensive-writing-Skill · 82d3140](https://github.com/Adkid-Zephyr/anti-defensive-writing-Skill/tree/82d31402caa0db1790026824399044538483171b) | 围绕成立的贡献组织问题与证据；清理实验流水账、主动自我削弱和假想反对意见。 |
| [Evidence-Bound Revision · 33e6c3a](https://github.com/lensback940701/Evidence-Bound-Press-Conference-Revision-Skill/tree/33e6c3a2f69c8c27dfd328e7b8df97609c81687f) | 用句子功能、删除损失和证据上限判断；共同条件集中说明；保留实际反例与材料状态。 |
| [blader/humanizer · 8c307f3](https://github.com/blader/humanizer/tree/8c307f367c91bd974002f10f2be2965d642c13df) | 优先检查否定对照及其变体；清理无人提出的反对意见、自证旁白与模板收尾。 |
| [Avtr99/antidote · ccb043e](https://github.com/Avtr99/antidote/tree/ccb043e79a3926f2648c4fd93ffea3da35248327) | 结构借鉴：先改准主张和段落关系，减少反复在句末追加免责声明的补丁。 |
| [obra/superpowers · 2ce8aa1](https://github.com/obra/superpowers/tree/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b) | 方法借鉴：让具体判断对应证据；对最后文本实际检查；通过代表性任务验证行为。 |
| [addyosmani/agent-skills · aeac41d](https://github.com/addyosmani/agent-skills/tree/aeac41d4d005999432bb7312f7ff06383a91d59d) | 用理解成本评价简化；保全语义和用户指定范围。 |
| [khasky/awesome-agent-skills · 58ea4e8](https://github.com/khasky/awesome-agent-skills/tree/58ea4e8915de64907d04cc909a1b8c6e5cf0fcb7) | awesome-humanize-en 的隐蔽对照、语义锚点及科学语体边界；awesome-document-style 的具体性、改写后回读与立场保全；审查定位与合并。 |
| [cbsteh/anti-ai-writing · 26d0f14](https://github.com/cbsteh/anti-ai-writing/tree/26d0f14a492306be8e18625c170ea1319425b4e6) | 具体说明不确定来源；匹配结论力度与材料；保留量化事实和引用功能。 |

核心规则独立编写，参考仓库均为 MIT 许可证。编程项目提供结构方法借鉴。运行本 Skill 使用包内文件。

本轮新增的直接写作来源：[awesome-humanize-en](https://github.com/khasky/awesome-agent-skills/blob/58ea4e8915de64907d04cc909a1b8c6e5cf0fcb7/skills/awesome-humanize-en/SKILL.md)、[全文结构与误判边界](https://github.com/khasky/awesome-agent-skills/blob/58ea4e8915de64907d04cc909a1b8c6e5cf0fcb7/skills/awesome-humanize-en/references/structure-pass.md)、[awesome-document-style](https://github.com/khasky/awesome-agent-skills/blob/58ea4e8915de64907d04cc909a1b8c6e5cf0fcb7/skills/awesome-document-style/SKILL.md)。

编辑增量的删除检查与替换回退检查来自 [edit-trace](https://github.com/khasky/awesome-agent-skills/blob/58ea4e8915de64907d04cc909a1b8c6e5cf0fcb7/skills/awesome-humanize-en/references/edit-trace.md)。采用给定范文优先校准及读者简要，检查风格样本中的事实没有被移植。

## 本版实现选择

- 用积极的段落任务指导生成，关键词定位支持最后一轮审读。
- 扫描器输出候选和上下文；编辑决定由句子在实际论证中的作用给出。
- 将共同的证据保全规则集中陈述，例子只补充会改变处理方式的具体条件。
- 将来源记录与案例放在按需读取的参考文件；正文任务直接交付论文内容。

全文模式增加贡献层级、实验职责、证据对照、候选登记与最终回读。局部修改保留短流程。来源中的“隐藏劣势”、纯关键词删改、为去 AI 味强改语体及固定评分阈值未采用；采用有证据的价值定位和必要条件保全。与其他写作工具共同使用时按用户范围应用这些约束。

候选扫描支持常见否定对照与澄清、预判质疑、自贬及相邻限定词。屏蔽代码、部分引用命令、常见公式分隔符与闭合的 equation／align／alignat／gather／multline／flalign 及其星号形式、displaymath／math 环境。Markdown 引用块默认屏蔽，`--include-blockquotes` 可纳入。脚本处理常用格式；未闭合的公式环境保留为可读区域，以免吞掉后续正文。跨段重复、贡献层级和证据作用通过语义复核完成。

Markdown 独立缩进代码按段落及容器缩进识别，脚注和列表的正文续行仍扫描，普通链接定义屏蔽。LaTeX 的闭合 `\verb`、`\verb*` 行内代码先于注释解析，避免字面 `%` 屏蔽后文。常见 cite、citet、citep、autocite、parencite、textcite 等单组引文，以及 cites、autocites、parencites、textcites、footcites、smartcites、supercites 多组引文，屏蔽命令名与引用键；可见的全局说明、逐项说明继续审读。脚本按已支持的语法定位；复杂宏及抽取后的文档仍需按正文实际结构检查。

公开论文扩展验证暴露了局部总结与跨方法综合混判的问题。本版据此增加对象、条件、推断层级和篇章职责的对照；压缩意见应定位局部重述，并保留由既有结果形成的综合关系。格式修复对应同轮实测的缩进代码、行内代码与多组引文候选，连同脚注正文和引文说明反例一起复测。

## 维护和验证

扫描器测试：在 Skill 目录运行 `python -m unittest discover -s tests -p test_scanner.py`。

行为样例在 `tests/behavior_cases.json`，覆盖起草、修改、审查、LaTeX、真实替代解释、英文稿件、全文重构、来源状态和实验组织。将 task 与 input 提供给执行者；criteria 留给核对者。检查实际输出中的命题、数值对应、极性、范围、来源状态与引文作用，再核对论证是否直接推进。来源或基线未支持的信息应保持未决。

比较时分别记录 Skill 版本、是否显式加载、输入、输出、实际文件变化和逐项判断。单元测试验证脚本；单次行为样例验证该次交付；目录描述选择测试只是路由近似。自动触发需要宿主的真实加载记录，正负样句本身无法证明。与无 Skill 的独立会话比较时记录具体差异，按实例解释，不据单次样例宣称总体提升。

将包内案例视为开发回归，未见验收材料单独保留。验收前冻结包指纹，再执行完整一轮任务，记录执行者实际读取的版本；修订规则后重新执行受影响的验收轮次。保留每轮完整输出及问题，最终结论指向同一冻结版本，避免拼接不同规则状态的优选结果。先记录判定标准，再核对数值、含义和表达；长稿与真实宿主加载分别验证。

维护时优先处理真实失败或核查发现的具体缺口；更新后复核局部任务、全文任务与相邻任务边界。普通论文写作不加载测试素材或维护记录。
