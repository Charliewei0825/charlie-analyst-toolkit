---
name: interview-briefing-sop
description: "Three-mode analyst research SOP. Mode A (interview briefing): generate handheld question lists for sell-side analysts, company management, KOLs, or institutional shareholders based on a knowledge base. Mode B (coverage summary): synthesize a single analyst's multi-report, multi-company coverage history into a panoramic view document showing rating/PT evolution, thesis changes, beat/miss track record, and catalyst calendar. Mode C (research PPTX): build structured equity research slide decks in 7-section format matching a reference template's exact formatting (fonts, sizes, bold, table style, language). Use when the user needs interview prep, coverage synthesis, or a research PPTX — mentions '访谈提纲', '观点汇总', '全覆盖', 'SOP', '写研报', '做PPT', 'slides', or references this skill by name."
---

# 分析师研究 SOP（三模式）

> 启动时先确认用户要模式 A / B / C。完整参考手册见 `SOP.md`。

## 模式选择

| 模式 | 输入 | 输出 |
|---|---|---|
| **A · 访谈提纲** | 知识库目录 + 访谈对象 + 覆盖标的 | 手持问题清单 + PDF |
| **B · 全覆盖观点汇总** | 某分析师的多标的长面板研报 | 全景文档 + PDF |
| **C · 研报 PPTX** | 目标公司研报文件夹 + 参考 PPTX 模版 | 7 大板块结构化 PPTX |

- 用户说 "准备访谈问题"、"手持问题清单" → **模式 A**
- 用户说 "总结他的全覆盖观点"、"哪些 top pick"、"观点怎么变的" → **模式 B**
- 用户说 "写研报"、"做一份 PPT"、"做 slides"、"公司深度" → **模式 C**
- 同时需要访谈 + 背景 → **先 B 后 A**（读完研报→出全景文档→基于全景写提纲）

---

## 通用基础设施（两种模式共享）

### PDF 批量提取

```bash
for dir in [知识库目录]/*/; do
  for f in "$dir"*.pdf; do
    pdftotext "$f" "/tmp/extracted/$(basename "$f" .pdf).txt"
  done
done
```

### 联网事实基线（必做）

以下数据点用 Tavily/WebSearch 核实，标注查询日期：
- 当前股价、市值
- 融资动态（增发/现金余额）
- 监管进展（FDA 会议、clinical hold 状态）
- 关键催化剂是否已发生（"Q3 读出"→现在 Q3 了？读了吗？）

---

## 模式 A · 访谈提纲

### A.1 知识库三层分类

| 访谈对象 | L1（此人的话） | L2（别人的话） | L3（事实背景） |
|---|---|---|---|
| 卖方分析师 | 该分析师的研报 | 其他分析师/管理层/股东的纪要 | 模版、NCT、行业报告 |
| 公司管理层 | 该公司 transcript/presentation/股东信 | 其他公司/分析师/竞争者的评论 | 模版、NCT、行业报告 |

**规则**：L2 的话不能安到 L1 对象头上。使用前确认发言人身份。

### A.2 逐份报告阅读

每份 L1 报告提取：日期、标题、评级/PT、报告时股价、核心 thesis（1 句）、模型参数变化、最新数据点。

读完后输出 PT/DCF/PoS 时间线。**以最新报告参数为准**。

### A.3 输出格式

```
# [对象名] · [机构名] 访谈手持问题清单

> **覆盖标的**：A (TICKER) · B (TICKER)
> **对象画像**：[风格]。关键报告："报告名"（日期，参数）。
> **核心论点（摘自其研报）**：
> - [论点1]【来源：报告名，日期】
> **时点**：YYYY-MM-DD。[催化剂状态]。
> **提示**：不要全问——选 3-5 个。

---

## Core · [话题区]

### **Q1** (P1) — 标题

> **背景与预期**:
> [已知数据 + 对方此前观点 + 预期回答方向]
> 【来源：报告名，日期】

**"English question?"**
中文翻译。
关联缺口：G-1 🚨

---

## Pocket Questions

> **背景提示**: [探测目的]

**"Question?"**
中文。

---

## 第三部分 · 查缺补漏扫描表

| 缺口 | 等级 | 对应问题 | 是否覆盖 | 行动 |
|---|---|---|---|---|
| **G-1** | 🚨 [名称] | Q1 | ☐☐☐ | ☐✔️ ☐❓ ☐❗ |
```

### A.4 问题分层

- **Core（P1）**：3-5 个，当前最紧迫、只能问这个人的问题
- **Secondary（P2）**：3-5 个，重要但可压缩
- **Pocket**：2-3 个，暖场/收尾/探测真实情绪

### A.5 八维度覆盖

①临床数据读出 ②疗效假设验证 ③安全性底线 ④竞争护城河 ⑤商业化路径 ⑥监管与申报 ⑦管线协同价值 ⑧公司战略优先级。每个维度 ≥1 个正式问题。分析师侧重 ①②④⑧，公司管理层侧重 ①③⑤⑥⑦。

### A.6 问题设计

- ✅ 好问题：基于研报里的具体数字追问、让对象做选择题/排序、探测报告中回避的矛盾
- ❌ 差问题："你怎么看这家公司？"（太宽泛）、跟此人覆盖标的无关

### A.7 来源标注

```
> Pete 在 Jun 22 报告中写道 "..."
> 【来源：Cantor "LSDelivering the Goods"，Jun 22, 2026】
```

### A.8 PDF 生成

```bash
pandoc input.md -f markdown-tex_math_dollars -t html5 --standalone \
  -H <(echo "<style>[CSS]</style>") -o output.html
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --headless --disable-gpu --no-sandbox \
  --print-to-pdf=output.pdf --no-pdf-header-footer file://output.html
```

配色：深蓝 #1a3a5c / 浅蓝 #e8edf5。CSS 详见 `SOP.md` §4.2。

### A.9 核对清单

```
□ L1 逐份阅读（共 __ 份），每份 8 字段
□ L2 发言人分类正确，无混入 L1
□ PT/DCF 时间线已追踪，提纲用最新值
□ 市值/股价联网核实（标日期）
□ 八维度全覆盖
□ 每数据点标来源
□ PDF 中文无乱码、$ 正常、表格完整
```

---

## 模式 B · 全覆盖观点汇总

### B.1 逐标的研报阅读

对每个标的子文件夹，按日期排序逐份读，提取：日期、标题、评级、PT（含从多少调整）、报告时股价、核心 thesis（1-2 句）、模型参数变化、关键催化剂、语气/定性标签（"top pick" / 标准 OW 等）。

读完后输出 PT 演变时间线：

```
BBIO PT 演变：
  Oct 23, 2023: $50（启动）
  Feb 20, 2025: $95
  Oct 27, 2025: $100（BBP-418 阳性）
  Oct 29, 2025: $110（encaleret 阳性 + Q3 beat）
```

### B.2 输出文档结构（7 个固定板块）

1. **分析师特征**：评级分布、估值方法（DCF 折现率范围）、报告频率、卖出记录（几次降级）
2. **全覆盖矩阵**：单表——Ticker / 公司 / 评级 / PT / 现价 / 上涨空间 / 市值 / 是否 Top Pick
3. **按确信度排列的逐家详解**：每家一张表（核心产品 · PT 演变 · 最近数据 · 峰值假设 · 最近催化剂 · 主要风险），Top Pick 优先、催化剂紧迫的优先
4. **过去 12 个月重大观点变化**：每条 = 之前（日期+观点）→ 触发事件（日期）→ 之后（日期+新观点）+ 分析师原文引用
5. **超预期与低于预期记分卡**：三类（持续超预期 / 好坏参半 / 严重低于预期），每项有具体数字对比
6. **6 个月催化剂日历**：时间 / 公司 / 催化剂 / 类型（二元事件 / 季度财报 / 监管里程碑 / 数据读出 / 竞品事件）
7. **覆盖模式分析**：评级信息量、PT 调整行为、观点粘性 + 该分析师在哪方面提供价值

### B.3 文风规则

- 直接、朴实、具体——只陈述事实和数字
- 不比喻、不排比、不夸张
- 分析师研报原文以直接引语保留
- 每个数据点标注来源报告日期

### B.4 格式规范

#### 全覆盖矩阵

```markdown
| Ticker | 公司 | 评级 | PT | 现价 | 上涨空间 | 市值 | 是否称 Top Pick |
|--------|------|------|-----|------|----------|------|-----------|
| **BBIO** | BridgeBio | OW | $110 | ~$68.63 | +60% | $14.1B | 是（自启动起每份报告重申） |
```

#### 逐家详解

```markdown
### BBIO（BridgeBio）——排列理由

| 项目 | 内容 |
|---|---|
| **核心产品** | Attruby（acoramidis），TTR 稳定剂，ATTR-CM |
| **PT 演变** | $50（2023.10）→ $95（2025.02）→ $110（2025.10） |
| **最近数据** | Q1 2026 收入 $180.6M |
| **峰值假设** | 合计 peak $6-8B |
| **最近催化剂** | CARDIO-TTRansform（2H26）· encaleret NDA |
| **主要风险** | TAF 仿制药 · Amvuttra 竞争 |
```

#### 观点变化

```markdown
### NBIX：IRA 假设修正（2026 年 3 月）

- **之前**（2025.05-2026.02）：PT 停留在 $170，9 个月未变。"The Ingrezza trade is done for the time being."
- **触发**（2026.03）：管理层会谈后意识到 Austedo XR 即使 IRA 降价后仍比 Ingrezza 贵
- **之后**（2026.03-05）：PT $170→$210。Josh："We were previously concerned... we no longer have that view."
```

#### 催化剂日历

```markdown
| 时间 | 公司 | 催化剂 | 类型 |
|------|------|--------|------|
| **本周** | CGON | PIVOT-006 topline | 二元事件 |
| 2026 H2 | BBIO | CARDIO-TTRansform | 二元事件 |
| 2026 Q4 | CMPS | NDA 提交 | 监管里程碑 |
```

### B.5 核对清单

```
□ 每标的研报逐份读完（共 __ 家、__ 份），每份 9 字段
□ 每标的 PT 时间线已追踪，用最新值
□ 市值/股价联网核实（标日期）
□ 已发生的催化剂已确认结果（PDUFA 过了？数据读了？）
□ 7 个板块全部包含
□ 观点变化每条有 "之前→触发→之后" 链条
□ Beat/Miss 每项有数字对比
□ 催化剂日历覆盖 6 个月
□ 文风直接朴实
□ PDF 中文无乱码、$ 正常、表格完整
```

---

## 模式 C · 研报 PPTX

> **触发场景**：用户需要基于目标公司的研报文件夹（PDF）和参考 PPTX 模版，生成一份结构化公司深度研报 slides。
> **输入**：目标公司研报目录 + 参考 PPTX 模版路径（可选，但强烈建议提供）
> **输出**：32-41 页 PPTX + Markdown 文字底稿 + 图片建议清单

### C.1 工作流程（5 步）

**Step 1 — 读取参考模版**

如果用户提供了参考 PPTX，必须先完整解析其格式规范。用 `python-pptx` 提取以下参数，不可凭记忆猜测：

```bash
python3 -c "
from pptx import Presentation
prs = Presentation('reference.pptx')
# 1. 主题字体（从 theme XML）
# 2. 各级字号、加粗、颜色
# 3. 表格样式（有无背景填充、表头是否加粗）
# 4. 正文对齐方式
# 5. 封面布局
"
```

格式参数至少包括：幻灯片尺寸、中文字体、英文字体、章节标题字号/加粗、页面标题字号/加粗、正文字号、表格字号、来源标注字号、正文对齐方式、表格有无表头填充/斑马条纹。

**Step 2 — 批量提取所有研报 PDF**

```bash
for f in [研报目录]/*.pdf; do
  pdftotext -l 30 "$f" - 2>/dev/null
done
```

同时读取公司 presentation、transcript、expert interview 等材料。

**Step 3 — 联网核实事实基线**

与模式 A/B 共享：股价、市值、融资动态、催化剂状态（是否已发生）。标注查询日期。

**Step 4 — 编写 Markdown 逐页底稿**

按 7 大板块组织内容，每页写清楚：页面标题、正文内容（2-4 段，600-1300 字/页）、表格数据、资料来源。同时标注每页建议放什么类型的图片（机制图/数据柱状图/时间轴等）。

**Step 5 — 生成 PPTX**

用 `python-pptx` 逐页构建。**严格遵守 Step 1 提取的格式参数。** 最后输出至用户指定目录。

### C.2 固定 7 板块结构

| # | 板块 | 典型页数 | 内容 |
|---|------|---------|------|
| 1 | **行业** | 4-8 页 | 疾病/技术背景、市场规模、未满足需求、行业趋势、赛道竞争格局 |
| 2 | **公司基本情况** | 3 页 | 公司概览（成立/总部/创始人/定位/市值/现金）、管线总表、平台/技术底层 |
| 3 | **核心业务分析** | 5-7 页 | Lead 资产逐一深度展开：机制、临床数据、试验设计、第二适应症、差异化总结 |
| 4 | **竞争分析** | 4 页 | 同赛道竞品横向对比表、不同技术路径对比、公司在赛道中的位置判断 |
| 5 | **其他** | 3 页 | 催化剂日历表、投资风险分类、管理层/董事会/合作伙伴 |
| 6 | **财务及盈利预测** | 4 页 | 覆盖券商 EPS/评级对比表、现金/融资表、收入模型（峰值销售 × PoS） |
| 7 | **估值分析** | 3 页 | 券商估值方法论对比表、敏感性分析表、Bull-Base-Bear 估值总结 |

### C.3 内容密度标准

- 纯正文页（无大表格）：600-1300 字
- 表格页：表格行数 4-9 行，列数 2-6 列，单元格支持 `\n` 多行
- 每页至少 2 段正文，通常 2-4 段
- 每页标注资料来源（底部，与参考模版位置一致）

### C.4 文风规则（全过程执行）

```
☐ 直接、朴实、具体 — 只陈述事实和数字
☐ 禁止比喻、明喻、暗喻、排比、夸张
☐ 禁止诗意化、抽象化、装饰性语言
☐ 减少箭头（→）和破折号（——）的使用
☐ 常见禁止词/句式：
   - "打开了...的大门" ❌ → "使...成为可能" / 直接陈述事实 ✅
   - "堪称惊人" ❌ → "数据显示 X 降低了 Y%" ✅
   - "像是...的瑞士军刀" ❌ → 直接描述功能和特征 ✅
   - "在...的舞台上" ❌ → 去掉比喻，直接说赛道/行业 ✅
☐ 每个数据点标注来源（报告名 + 日期）
☐ 英文术语保留原文，首字母大写（如 NLRP3、hsCRP、Ph2a）
☐ 数字格式：金额 $1.2B / $385M，股价 $19.84，百分比 86%
```

### C.5 格式参数（从参考模版提取，不可凭空编造）

以下是本次 BioAge 任务从用户模版提取的规范，**实际执行时以 Step 1 从用户提供的参考 PPTX 提取为准**：

```
幻灯片尺寸:    13.3 × 7.5 inches (Widescreen)
中文字体:      华文楷体
英文/数字字体:  Calibri
──────────────────────────────────
封面公司名:     华文楷体 32pt, 不加粗, 居中
封面代码:      华文楷体 24pt, 不加粗, 居中
章节标签:      华文楷体 24pt, 不加粗
目录条目:      Calibri 继承大小
页面标题:      华文楷体 20pt, 加粗
正文段落:      华文楷体 18pt, 不加粗（仅段落引导词加粗）
表格文字:      华文楷体 18pt, 不加粗（表头同数据行）
来源标注:      华文楷体 12pt, 不加粗
──────────────────────────────────
正文对齐:      JUSTIFY (两端对齐)
表格填充:      无背景填充, 无斑马条纹, 无深色表头
页面坐标:      章节标签 (0.56,0.36) 标题 (0.56,1.02) 正文 (0.56,1.60) 来源 (~6.69)
```

### C.6 PPTX 生成技术要求

- 使用 `python-pptx`，从空白 layout (`slide_layouts[6]`) 逐页构建
- 字体用 `add_textbox` 显式设置，不可依赖母版继承（因为从空白 layout 构建时无母版）
- 表格用 `add_table`，表头和数据行分别设置相同的字体参数
- 每页添加幻灯片编号（右下角）
- 数据表优先用表格呈现，而非项目符号列表
- 输出文件命名为 `[Ticker]_[公司名]_Research.pptx`

### C.7 输出物清单

```
□ Markdown 文字底稿（逐页完整正文 + 图片建议）
□ PPTX 文件（严格匹配参考模版格式）
□ 页数 32-41 页，7 个板块全覆盖
□ 每页有资料来源标注
□ 每页有幻灯片编号
□ 图片建议已标注（每页 1 条，说明放什么类型的图）
```

### C.8 常见错误速查（模式 C 专属）

| 错误 | 正确做法 |
|------|---------|
| 凭记忆写格式参数 | 必须先 python-pptx 解析参考模版提取实际参数 |
| 正文用左对齐 | 参考模版通常是 JUSTIFY（两端对齐），照模版来 |
| 表格加背景色/斑马纹 | 参考模版通常是纯白无填充 |
| 表头加粗 | 参考模版表头通常不加粗 |
| 内容偏少（200-300 字/页） | 研报 slides 通常 600-1300 字/页，2-4 段长文 |
| 使用比喻/夸张修辞 | 全程直接、朴实、具体。禁止比喻排比夸张 |
| 箭头/破折号泛滥 | 仅在技术语境（信号传导路径）中保留，其余用文字 |
| PPTX 用 JS (pptxgenjs) 生成 | JS 处理中文有编码坑，统一用 python-pptx |
| 字号凭猜测 | 必须从参考模版提取，正文常见 18pt，不是 12pt |

---

## PDF 配色参数

```css
@page { size: A4; margin: 1.6cm 1.5cm 1.8cm 1.5cm; }
body { font-family: "STHeiti", "PingFang SC", "Hiragino Sans GB", sans-serif; font-size: 9pt; line-height: 1.6; }
h1 { color: #1a3a5c; border-bottom: 2.5pt solid #1a3a5c; }
h2 { background: #1a3a5c; color: white; padding: 6pt 10pt; }
h3 { background: #e8edf5; color: #1a3a5c; border-left: 3pt solid #1a3a5c; }
blockquote { background: #f2f5fa; border-left: 4pt solid #1a3a5c; font-size: 8pt; }
th { background: #1a3a5c; color: white; }
table { font-size: 7pt; width: 100%; border-collapse: collapse; }
```

---

## 常见错误速查

| 错误 | 正确做法 |
|---|---|
| 用旧报告 PT | 按日期排序，用最新报告的值 |
| 观点张冠李戴 | 纪要中所有引用先确认发言人身份 |
| 市值凭记忆写 | 必须联网查当前值，标查询日期 |
| 只读一份报告 | 读完所有报告再下结论 |

---

*SKILL.md 是操作摘要。完整规范、详细示例、故障排查见 `SOP.md`。*
