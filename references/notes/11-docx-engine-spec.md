# DOCX 生成引擎规范

## 目标

本 skill 需要被安装后直接可用，因此 `.docx` 生成路径不应建立在外部第三方 Python 包之上。

仓库默认只保留运行所需内容：

- `SKILL.md`
- `agents/`
- `scripts/`
- `assets/`
- `references/`

默认要求如下：

- skill 自带生成器；
- 不依赖 `python-docx`；
- 不要求额外 `pip install`；
- 不以插件可用性作为基础交付前提。

## 默认生成路径

优先使用：

```bash
python3 scripts/generate_resume_docx.py --output output/resume.docx
```

该脚本使用：

- Python 标准库
- 直接写入 Word OOXML zip 结构

因此只要环境中有 `python3`，就应能生成基础可用的 `.docx`。

生成后可继续运行：

```bash
python3 scripts/verify_resume_docx.py output/resume.docx --expected-cn-font STKaiti
```

检查分三层：

- 第一层：检查 `.docx` zip 结构和关键 OOXML 文件；
- 第二层：如果环境中有 `textutil`，做文本读取检查；
- 第三层：如果环境中有 `soffice` 或 `libreoffice`，再做渲染验证；
- 如无渲染工具，可明确跳过，但不阻断交付。

## 默认字体规则

- 中文默认字体按平台分流：
  - macOS：`STKaiti`
  - Windows：`楷体`
  - 其他环境：默认回退到 `STKaiti`
- 英文默认字体：`Calibri`

如有必要，可通过参数覆盖：

```bash
python3 scripts/generate_resume_docx.py \
  --input-json data.json \
  --output output/resume.docx \
  --cn-font STKaiti \
  --en-font Calibri
```

## 输入方式

### 无输入 JSON

不传 `--input-json` 时，脚本使用内置示例数据，主要用于：

- 验证脚本是否可运行；
- 验证 skill 安装后的最小可用性；
- 做 smoke test。

### 传入 JSON

实际生成用户简历时，应把整理后的内容写成 JSON 再传给脚本。

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

## 支持的 block 类型

- `entry`：机构、日期、岗位和 bullet
- `paragraph`：普通整段文字
- `title`：模块内小标题
- `subtitle`：研究题目或副标题
- `bullets`：一组普通 bullet

## 对 skill 的直接要求

当用户要求生成 Word 或导出 `.docx` 时，应优先走内置脚本路径，而不是把成功与否建立在外部包是否可用之上。

## 渲染验证

如果环境中具备：

- LibreOffice 或 `soffice`
- PDF 或图片渲染能力

可以在此基础上追加视觉 QA；如果没有，也不影响完成基础 `.docx` 交付。
