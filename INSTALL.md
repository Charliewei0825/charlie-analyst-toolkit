# 安装指南

## 1. 克隆仓库

```bash
git clone https://github.com/Charliewei0825/interview-briefing-toolkit.git
```

## 2. 添加 Skill 到 Claude Code

将 SOP 注册为 Claude Code 的 skill，之后在对话中输入 `/interview-briefing-sop` 即可自动加载全部规范：

```bash
# 创建 skills 目录（如不存在）
mkdir -p ~/.claude/skills

# 拷贝 SOP
cp interview-briefing-toolkit/SOP.md ~/.claude/skills/interview-briefing-sop.md
```

验证：

```bash
ls ~/.claude/skills/
# 应看到 interview-briefing-sop.md
```

之后在 Claude Code 中输入 `/interview-briefing-sop` 即可调用。

> 如果希望每次对话自动加载（无需手动调用），可在 `~/.claude/settings.json` 中将该文件路径加入 `systemPrompt` 或 `additionalDirectories`。

## 3. 安装 PDF 生成依赖

```bash
# pandoc（MD → HTML）
brew install pandoc

# poppler（pdftotext 提取 PDF 文字）
brew install poppler

# Google Chrome（HTML → PDF，原生中文字体渲染）
# 需已安装 Chrome。如未安装：
# brew install --cask google-chrome
```

验证：

```bash
pandoc --version | head -1    # 应显示 pandoc 3.x
pdftotext -v | head -1        # 应显示版本号
ls "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"  # 应存在
```

## 4. 安装 Typora 主题（可选）

Typora 用于编辑 Markdown 提纲。装完 Fugu 主题后，层级的视觉区分（H1/H2/H3/blockquote 颜色）与 PDF 输出一致：

```bash
git clone https://github.com/sinlatansen/typora-theme-Fugu.git /tmp/fugu
cp /tmp/fugu/fugu.css ~/Library/Application\ Support/abnerworks.Typora/themes/
cp -r /tmp/fugu/fugu ~/Library/Application\ Support/abnerworks.Typora/themes/
```

Typora 菜单 → 主题 → Fugu。

## 5. 快速测试

```bash
cd interview-briefing-toolkit
./pdf-pipeline.sh template.md test-output.pdf
open test-output.pdf
```

应生成一份 1-2 页的 PDF，中文正常、页眉显示「访谈手持问题清单 · CONFIDENTIAL」。

## 6. 工作流

```
1. 克隆项目 → 安装依赖 → 注册 skill
2. Claude Code 中输入 /interview-briefing-sop
3. 按 SOP 逐份读材料 → 联网核查 → 生成提纲 MD
4. 用 Typora（Fugu 主题）做最后的文字润色
5. 跑 ./pdf-pipeline.sh xxx.md → 出 PDF
```
