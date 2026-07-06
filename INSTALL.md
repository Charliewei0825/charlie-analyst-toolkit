# 安装指南 · Charlie Analyst Toolkit

## 前置要求

| 工具 | macOS | Windows | Linux |
|------|-------|---------|-------|
| Git | 系统自带或 `brew install git` | `winget install git` | `apt install git` |
| Python 3 | 系统自带 | `winget install python3` | `apt install python3` |
| pandoc | `brew install pandoc` | `choco install pandoc` | `apt install pandoc` |
| pdftotext | `brew install poppler` | `scoop install poppler` | `apt install poppler-utils` |
| Chrome | 系统自带 | 系统自带 | `apt install chromium-browser` |

> PDF 生成功能需要 pandoc + Chrome。纯 Markdown 输出不需要。

## 1. 克隆仓库

```bash
# Clone 到 Claude Code skills 目录
mkdir -p ~/.claude/skills
git clone https://github.com/Charliewei0825/charlie-analyst-toolkit.git \
  ~/.claude/skills/charlie-analyst-toolkit
```

## 2. 验证 Skill 加载

重启 Claude Code，skill 自动注册。在对话中输入 `/charlie-analyst-toolkit` 或提到触发词（如"访谈提纲""会议纪要""猹狸百科"）即可调用。

## 3. 安装 Python 依赖

```bash
pip install pymupdf python-docx python-pptx PyYAML
```

> 完整依赖列表见 `requirements.txt`

## 4. 配置联网搜索（可选，推荐）

- **Tavily API**：注册 https://tavily.com → 取得 API key → 写入 `~/.claude/settings.local.json`:
  ```json
  { "env": { "TAVILY_API_KEY": "tvly-xxx" } }
  ```
- **WebSearch**：Claude Code 内置，无需配置

## 5. 配置学术文献检索（可选）

```bash
# Clone paper-search-pro 到 skills 目录
git clone https://github.com/O0000-code/paper-search-pro.git \
  ~/.claude/skills/paper-search-pro

# 配置 API keys（OpenAlex / NCBI 必须，约 15 分钟）
# 详见 paper-search-pro 的 references/setup.md
```

配置写入 `~/.paper-search-pro/config.yaml`。

## 6. 快速测试

```bash
# 测试 PDF 生成
cd ~/.claude/skills/charlie-analyst-toolkit
./pdf-pipeline.sh template.md test-output.pdf

# macOS:  open test-output.pdf
# Windows: start test-output.pdf
# Linux:   xdg-open test-output.pdf
```

## 7. 工作流

```
1. 克隆项目 → 安装依赖 → 配置 API keys
2. 在 Claude Code 中提及触发词或调用 skill
3. 选择模式 A/B/C/D/E/F
4. Claude 自动执行 → 输出文件到桌面或指定目录
```
