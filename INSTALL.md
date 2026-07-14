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

**Claude Code：**
```bash
mkdir -p ~/.claude/skills
git clone https://github.com/Charliewei0825/charlie-analyst-toolkit.git \
  ~/.claude/skills/charlie-analyst-toolkit
```

**Codex CLI：**
```bash
mkdir -p ~/.agents/skills
git clone https://github.com/Charliewei0825/charlie-analyst-toolkit.git \
  ~/.agents/skills/charlie-analyst-toolkit
```

## 2. 验证 Skill 加载

- **Claude Code**：重启后输入 `/charlie-analyst-toolkit` 或提触发词（"访谈提纲""会议纪要""猹狸百科"）
- **Codex CLI**：重启后输入 `$charlie-analyst-toolkit` 或直接描述任务（Codex 根据 description 自动匹配 skill）

## 3. 安装 Python 依赖

```bash
pip install pymupdf python-docx python-pptx PyYAML
```

> 完整依赖列表见 `requirements.txt`

## 4. 配置联网搜索

- **Claude Code**：需配 Tavily MCP key（注册 https://tavily.com → 写入 `~/.claude/settings.local.json`）
- **Codex CLI**：自带 `web_search`，无需额外配置

## 5. 配置学术文献检索（可选）

```bash
# Claude Code
git clone https://github.com/O0000-code/paper-search-pro.git \
  ~/.claude/skills/paper-search-pro
# Codex CLI
git clone https://github.com/O0000-code/paper-search-pro.git \
  ~/.agents/skills/paper-search-pro

# 配置 API keys（OpenAlex / NCBI 必须，约 15 分钟）
# 详见 paper-search-pro 的 references/setup.md
```

## 6. 快速测试

```bash
cd ~/.claude/skills/charlie-analyst-toolkit  # 或 ~/.agents/skills/charlie-analyst-toolkit
./pdf-pipeline.sh template.md test-output.pdf
```

## 7. 工作流

```
1. 克隆到对应目录 → 安装依赖 → 配置搜索
2. Claude Code: /charlie-analyst-toolkit  |  Codex: $charlie-analyst-toolkit
3. 选择模式 A/B/C/D/E/F
4. 自动执行 → 输出文件到桌面或指定目录
```
