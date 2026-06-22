# 内置 DOCX 生成器说明

## 目标

这个 skill 需要被上传到 GitHub 并由其他用户安装使用，因此 `.docx` 生成路径不能建立在“本机刚好装了某个库”之上。

发布到 GitHub 时，skill 仓库应只保留运行所需内容：

- `SKILL.md`
- `agents/`
- `scripts/`
- `assets/`
- `references/`

原始学习视频、本地截图、测试输出文件等只用于本地学习和验证，不应作为发布内容上传。

默认要求是：

- skill 自带生成器；
- 不依赖 `python-docx`；
- 不依赖额外 `pip install`；
- 不依赖 `documents` plugin 才能完成基础 `.docx` 交付。

## 默认生成路径

优先使用：

```bash
python3 scripts/generate_resume_docx.py --output output/resume.docx
```

这个脚本使用：

- Python 标准库
- 直接写入 Word OOXML zip 结构

因此只要环境里有 `python3`，就应能生成基础可用的 `.docx`。

生成后可继续运行：

```bash
python3 scripts/verify_resume_docx.py output/resume.docx --expected-cn-font STKaiti
```

这个检查分三层：

- 第一层：检查 `.docx` zip 结构和关键 OOXML 文件是否完整；
- 第二层：如果环境里有 `textutil`，尝试做文本读取检查，确认系统文档链路可打开；
- 第三层：如果环境里有 `soffice` / `libreoffice`，再尝试做 PDF 级渲染验证；
- 如果没有渲染工具，则明确输出“跳过 render QA”，但不阻断基础交付。

## 默认字体规则

- 中文默认字体：平台分流
  - macOS：`STKaiti`
  - Windows：`楷体`
  - 其他环境：默认回退到 `STKaiti`，必要时可手动传 `--cn-font`
- 英文默认字体：`Calibri`

之所以默认不用直接写“楷体”，是因为在 macOS 的 Word / Pages / 系统文档链路里，`STKaiti` 往往比泛名称“楷体”更稳定、更容易真实落到楷体字形。

如有必要，可通过参数覆盖：

```bash
python3 scripts/generate_resume_docx.py \
  --input-json data.json \
  --output output/resume.docx \
  --cn-font STKaiti \
  --en-font Calibri
```

## 输入方式

### 1. 无输入 JSON

不传 `--input-json` 时，脚本使用内置示例数据，主要用于：

- 验证脚本是否可运行；
- 验证 skill 安装后的最小可用性；
- 做 smoke test。

### 2. 传入 JSON

实际生成用户简历时，应把整理后的内容写成 JSON，再传给脚本。

建议结构：

```json
{
  "name": "张三",
  "summary_line": "女 | 2003.08出生 | XX大学法学院 法学本科在读（大三）",
  "contact_line": "电话：13800000000 | 邮箱：xxx@example.com",
  "sections": [
    {
      "title": "教育背景",
      "blocks": [
        {
          "kind": "entry",
          "org": "XX大学 法学院",
          "date": "2022.09 - 至今",
          "role": "法学本科在读"
        },
        {
          "kind": "paragraph",
          "text": "主修课程：民法总论、刑法总论、知识产权法"
        }
      ]
    }
  ]
}
```

脚本现在应支持真实动态输入，而不是只适配单一示例简历。

## 支持的 block 类型

- `entry`
  - 用于“机构/日期/岗位 + bullet”
- `paragraph`
  - 用于普通整段文字
- `title`
  - 用于模块中的小标题
- `subtitle`
  - 用于研究题目或副标题
- `bullets`
  - 用于一组普通 bullet

## 对 skill 的直接要求

当用户要求：

- “生成 Word”
- “导出 `.docx`”
- “按模板排成文件”

应优先走这个内置脚本路径，而不是把成功与否建立在外部插件或第三方 Python 包是否可用之上。

## 渲染验证

如果环境里后续具备：

- LibreOffice / `soffice`
- PDF 或图片渲染能力

可以在这个基础上追加视觉 QA。

但即便没有，也不影响这个 skill 完成基础 `.docx` 交付。
