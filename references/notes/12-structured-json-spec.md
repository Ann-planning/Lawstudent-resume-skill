# 结构化 JSON 规范

## 目标

当 skill 已生成定向简历正文后，为了输出 `.docx`，还需要把正文稳定映射为结构化 JSON。

因此文件交付模式不应是先写长文本再临时拼成 Word，而应是：

1. 先整理定向简历正文；
2. 再将正文映射为固定 JSON 结构；
3. 用 `scripts/generate_resume_docx.py` 读取 JSON 生成 `.docx`；
4. 用 `scripts/verify_resume_docx.py` 做结构检查。

## 顶层字段

JSON 顶层默认包括：

- `name`
- `summary_line`
- `contact_line`
- `sections`

## sections 组织原则

每个 section 都应包含：

- `title`
- `blocks`

默认顺序：

1. 教育背景
2. 实习经历
3. 法律研究与课程实践
4. 技能与证书
5. 校园经历（仅在需要时保留）

## blocks 映射规则

### 机构、日期、岗位

```json
{
  "kind": "entry",
  "org": "XX律师事务所",
  "date": "2024.07 - 2024.08",
  "role": "实习生",
  "bullets": [
    "围绕案件争议焦点开展法律检索。",
    "协助整理证据目录及时间线。"
  ]
}
```

### 普通整段说明

```json
{
  "kind": "paragraph",
  "text": "主修课程：民法总论、刑法总论、知识产权法"
}
```

### 模块中的小标题

```json
{
  "kind": "title",
  "text": "知识产权研究选题"
}
```

### 研究题目或副标题

```json
{
  "kind": "subtitle",
  "text": "《互联网平台语境下商标侵权认定的困境与规则重构——以混淆可能性标准为中心》"
}
```

### 一组普通 bullet

```json
{
  "kind": "bullets",
  "items": [
    "围绕互联网平台场景下商标侵权认定问题展开研究。",
    "结合裁判逻辑与平台机制提出补充判断因素。"
  ]
}
```

## 对 skill 的直接要求

当用户要求输出 `.docx` 时，skill 应明确完成两步：

### 第一步：整理为可投递正文

包括：

- 姓名
- 摘要行
- 联系方式
- 各模块正文

### 第二步：映射为 JSON

优先以：

- `assets/resume-template.json`
- `references/notes/11-docx-engine-spec.md`

为模板，再生成本地 `.docx`。

## 结果要求

最终交付链路应为：

`定向简历正文 -> JSON -> .docx -> verify`

而不是：

`定向简历正文 -> 手工临时排版 -> .docx`
