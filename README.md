# Interview Briefing Toolkit

分析师研究的三模式工具包：生成访谈手持问题清单、汇总单一分析师全覆盖观点、构建结构化研报 PPTX。

## 三模式

| 模式 | 你需要什么 | 输出 |
|------|-----------|------|
| **A · 访谈提纲** | 跟分析师/管理层/KOL开会时要问什么 | 手持问题清单（三组件：背景→双语Q&A→缺口矩阵） + PDF |
| **B · 全覆盖观点汇总** | 理解一个分析师的全部覆盖观点——哪些 top pick、观点怎么变的、beat了什么miss了什么、未来6个月催化剂有哪些 | 全景文档（7 个固定板块：分析师画像→覆盖矩阵→逐家详解→观点变化→Beat/Miss记分卡→催化剂日历→模式分析） + PDF |
| **C · 研报 PPTX** | 基于目标公司研报 PDF 和参考模版，生成结构化公司深度 slides | 32-41 页 PPTX + Markdown 文字底稿 + 图片建议清单。7 大板块（行业/公司基本情况/核心业务分析/竞争分析/其他/财务及盈利预测/估值分析），格式严格匹配参考模版（字体/字号/加粗/表格/对齐） |

## 快速开始

```bash
git clone https://github.com/Charliewei0825/interview-briefing-toolkit.git
cd interview-briefing-toolkit
```

### 安装依赖

```bash
brew install pandoc poppler          # MD→HTML + PDF 文字提取
pip install python-pptx              # 模式 C: PPTX 生成
# 需已安装 Google Chrome（HTML→PDF）
```

### 注册为 Claude Code Skill

```bash
mkdir -p ~/.claude/skills
cp SOP.md ~/.claude/skills/interview-briefing-sop.md
```

在 Claude Code 中输入 `/interview-briefing-sop` 即可加载全部规范。加载后会自动确认你要模式 A / B / C。

### 生成第一份文档

```bash
# 模式 A：访谈提纲
cp template.md my-interview.md
./pdf-pipeline.sh my-interview.md

# 模式 B：全覆盖观点汇总
cp template-summary.md my-coverage-summary.md
./pdf-pipeline.sh my-coverage-summary.md

# 模式 C：研报 PPTX
# 在 Claude Code 中输入：
# "帮我写一份 XX 公司的研报 PPT，参考这个模版 [模版路径]，研报在 [研报目录]"
```

## 包里有什么

| 文件 | 用途 |
|------|------|
| `SOP.md` | **完整参考手册**：三模式全部细节、示例、故障排查 |
| `SKILL.md` | **操作摘要**：三模式核心流程、格式骨架、核对清单（Claude Code skill 入口） |
| `template.md` | 模式 A 骨架空模版（访谈提纲） |
| `template-summary.md` | 模式 B 骨架空模版（全覆盖观点汇总） |
| `style.css` | PDF 渲染样式（深蓝配色、中文字体） |
| `pdf-pipeline.sh` | 一行命令 Markdown → PDF |
| `checklist.md` | 提交前核对清单（模式 A 15 项 + 模式 B 10 项 + 模式 C 15 项） |
| `INSTALL.md` | 详细安装指南（含 Typora 主题配置） |

## 致谢

本工具的 PDF 批量提取流程集成了 [pdf-word-reader-zh](https://github.com/20041002liu-cloud/pdf-word-reader-zh)，用于结构化提取 PDF/DOCX 中的文本、表格和页码。

## 模式 A 输出格式

严格对标三组件结构：

1. **背景与预期**（`>` blockquote）→ 已知信息和期望答案
2. **双语提问**（英文粗体 + 中文紧随）→ 每个问题带关联缺口编号
3. **查缺补漏扫描表**（Gap-to-Question Matrix）→ 访谈后逐项评分

## 模式 B 输出格式

7 个固定板块，直接、朴实、具体的文风：

1. 分析师特征总结
2. 全覆盖矩阵（单表：评级/PT/现价/上涨空间/市值/Top Pick）
3. 按确信度排列的逐家详解（每家一张表）
4. 过去 12 个月重大观点变化（之前→触发事件→之后）
5. 超预期与低于预期记分卡（具体数字对比）
6. 6 个月催化剂日历（时间/公司/类型）
7. 覆盖模式分析

## 模式 C 输出格式

7 大板块 PPTX + Markdown 底稿，全程执行反修辞文风：

1. 行业（疾病/技术背景、市场规模、竞争格局全景、趋势总结）
2. 公司基本情况（公司概览、管线总表、平台/技术底层）
3. 核心业务分析（Lead 资产数据、试验设计、差异化对比、业务总结）
4. 竞争分析（竞品对比表、技术路径对比、赛道位置判断）
5. 其他（催化剂日历、投资风险、管理层/董事会）
6. 财务及盈利预测（EPS 对比、现金/融资、收入模型）
7. 估值分析（方法论对比、敏感性分析、Bull-Base-Bear 总结）

格式规范由用户提供的参考 PPTX 模版决定，不可凭记忆猜测。文风规则：直接、朴实、具体——禁止比喻、明喻、暗喻、排比、夸张。

## 适用场景

- 卖方分析师访谈（问模型参数、排序、监管判断）
- 公司管理层访谈（问管线进展、商业化、战略）
- KOL/医生访谈（问临床实践、竞品对比）
- 机构股东访谈（问持仓逻辑、仓位配置）
- 分析师全覆盖研究（总结单一分析师多标的、跨年度观点演变）
- 公司深度研报 PPTX（研报文件夹 + 参考模版 → 结构化 slides）
