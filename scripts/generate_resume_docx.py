#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import platform
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape


NS_W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
A4_PAGE_WIDTH_TWIPS = 11906
DEFAULT_MARGIN_CM = 1.0


def xml(text: str) -> str:
    return escape(text, {'"': "&quot;"})


def twips_from_cm(cm: float) -> int:
    return int(round(cm / 2.54 * 1440))


def content_width_twips(margin_cm: float = DEFAULT_MARGIN_CM) -> int:
    margin = twips_from_cm(margin_cm)
    return A4_PAGE_WIDTH_TWIPS - margin * 2


def default_cn_font() -> str:
    system = platform.system().lower()
    if "darwin" in system:
        return "STKaiti"
    if "windows" in system:
        return "楷体"
    return "STKaiti"


def fonts_xml(cn_font: str, en_font: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:fonts xmlns:w="{NS_W}">
  <w:font w:name="{xml(cn_font)}"><w:charset w:val="86"/></w:font>
  <w:font w:name="{xml(en_font)}"><w:charset w:val="00"/></w:font>
</w:fonts>
"""


def content_types_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
  <Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
  <Override PartName="/word/fontTable.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.fontTable+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>
"""


def rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
  <Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>
"""


def document_rels_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/styles" Target="styles.xml"/>
  <Relationship Id="rId2" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/fontTable" Target="fontTable.xml"/>
</Relationships>
"""


def core_xml(title: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"
 xmlns:dc="http://purl.org/dc/elements/1.1/"
 xmlns:dcterms="http://purl.org/dc/terms/"
 xmlns:dcmitype="http://purl.org/dc/dcmitype/"
 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{xml(title)}</dc:title>
  <dc:creator>lawstudent-skill</dc:creator>
  <cp:lastModifiedBy>lawstudent-skill</cp:lastModifiedBy>
</cp:coreProperties>
"""


def app_xml() -> str:
    return """<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
 xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>lawstudent-skill</Application>
</Properties>
"""


def styles_xml(cn_font: str, en_font: str) -> str:
    return f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="{NS_W}">
  <w:docDefaults>
    <w:rPrDefault>
      <w:rPr>
        <w:rFonts w:ascii="{xml(en_font)}" w:hAnsi="{xml(en_font)}" w:eastAsia="{xml(cn_font)}" w:cs="{xml(en_font)}"/>
        <w:sz w:val="22"/>
        <w:szCs w:val="22"/>
      </w:rPr>
    </w:rPrDefault>
    <w:pPrDefault>
      <w:pPr>
        <w:spacing w:after="0" w:line="260" w:lineRule="auto"/>
      </w:pPr>
    </w:pPrDefault>
  </w:docDefaults>
  <w:style w:type="paragraph" w:default="1" w:styleId="Normal">
    <w:name w:val="Normal"/>
    <w:qFormat/>
    <w:rPr>
      <w:rFonts w:ascii="{xml(en_font)}" w:hAnsi="{xml(en_font)}" w:eastAsia="{xml(cn_font)}" w:cs="{xml(en_font)}"/>
      <w:sz w:val="22"/>
      <w:szCs w:val="22"/>
    </w:rPr>
  </w:style>
</w:styles>
"""


def run(text: str, *, bold: bool = False, italic: bool = False, size: int | None = None, font: str | None = None) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if italic:
        props.append("<w:i/>")
    if size is not None:
        props.append(f'<w:sz w:val="{size}"/><w:szCs w:val="{size}"/>')
    if font is not None:
        props.append(
            f'<w:rFonts w:ascii="{xml(font)}" w:hAnsi="{xml(font)}" w:eastAsia="{xml(font)}" w:cs="{xml(font)}"/>'
        )
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f"<w:r>{rpr}<w:t xml:space=\"preserve\">{xml(text)}</w:t></w:r>"


def tab_run(*, font: str | None = None, bold: bool = False) -> str:
    props = []
    if bold:
        props.append("<w:b/>")
    if font is not None:
        props.append(
            f'<w:rFonts w:ascii="{xml(font)}" w:hAnsi="{xml(font)}" w:eastAsia="{xml(font)}" w:cs="{xml(font)}"/>'
        )
    rpr = f"<w:rPr>{''.join(props)}</w:rPr>" if props else ""
    return f"<w:r>{rpr}<w:tab/></w:r>"


def is_cjk_char(ch: str) -> bool:
    code = ord(ch)
    return (
        0x3400 <= code <= 0x4DBF
        or 0x4E00 <= code <= 0x9FFF
        or 0xF900 <= code <= 0xFAFF
        or 0x3000 <= code <= 0x303F
        or 0xFF00 <= code <= 0xFFEF
    )


def styled_text_runs(
    text: str,
    *,
    cn_font: str,
    en_font: str,
    bold: bool = False,
    italic: bool = False,
    size: int | None = None,
) -> list[str]:
    if not text:
        return []

    runs = []
    buf = []
    current_font = cn_font if is_cjk_char(text[0]) else en_font

    for ch in text:
        font = cn_font if is_cjk_char(ch) else en_font
        if font != current_font:
            runs.append(run("".join(buf), bold=bold, italic=italic, size=size, font=current_font))
            buf = [ch]
            current_font = font
        else:
            buf.append(ch)

    if buf:
        runs.append(run("".join(buf), bold=bold, italic=italic, size=size, font=current_font))

    return runs


def paragraph(
    runs: list[str],
    *,
    align: str | None = None,
    before: int = 0,
    after: int = 0,
    line: int = 260,
    first_line: int | None = None,
    left: int | None = None,
    hanging: int | None = None,
    border_bottom: bool = False,
    right_tab: int | None = None,
) -> str:
    ppr = [f'<w:spacing w:before="{before}" w:after="{after}" w:line="{line}" w:lineRule="auto"/>']
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    if right_tab is not None:
        ppr.append(f'<w:tabs><w:tab w:val="right" w:pos="{right_tab}"/></w:tabs>')
    if first_line is not None or left is not None or hanging is not None:
        attrs = []
        if left is not None:
            attrs.append(f'w:left="{left}"')
        if first_line is not None:
            attrs.append(f'w:firstLine="{first_line}"')
        if hanging is not None:
            attrs.append(f'w:hanging="{hanging}"')
        ppr.append(f"<w:ind {' '.join(attrs)}/>")
    if border_bottom:
        ppr.append('<w:pBdr><w:bottom w:val="single" w:sz="8" w:space="1" w:color="000000"/></w:pBdr>')
    return f"<w:p><w:pPr>{''.join(ppr)}</w:pPr>{''.join(runs)}</w:p>"


def bullet_paragraph(text: str, *, cn_font: str, en_font: str) -> str:
    return paragraph(
        styled_text_runs("•  " + text, cn_font=cn_font, en_font=en_font),
        left=340,
        hanging=220,
        after=10,
        line=220,
    )


def entry_line(left_text: str, right_text: str, *, cn_font: str, en_font: str) -> str:
    runs = []
    runs.extend(styled_text_runs(left_text, cn_font=cn_font, en_font=en_font, bold=True))
    runs.append(tab_run(font=cn_font, bold=True))
    runs.extend(styled_text_runs(right_text, cn_font=cn_font, en_font=en_font))
    return paragraph(runs, after=0, line=240, right_tab=content_width_twips())


def section_props(margin_cm: float = 1.0) -> str:
    margin = twips_from_cm(margin_cm)
    return (
        f'<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        f'<w:pgMar w:top="{margin}" w:right="{margin}" w:bottom="{margin}" w:left="{margin}" '
        f'w:header="420" w:footer="420" w:gutter="0"/></w:sectPr>'
    )


def build_document(data: dict, *, cn_font: str = "STKaiti", en_font: str = "Calibri") -> str:
    body = []
    body.append(paragraph(styled_text_runs(data["name"], cn_font=cn_font, en_font=en_font, bold=True, size=32), align="center", after=18, line=230))
    body.append(paragraph(styled_text_runs(data["summary_line"], cn_font=cn_font, en_font=en_font), align="center", after=6, line=220))
    body.append(paragraph(styled_text_runs(data["contact_line"], cn_font=cn_font, en_font=en_font), align="center", after=40, line=220))

    for section in data["sections"]:
        body.append(paragraph(styled_text_runs(section["title"], cn_font=cn_font, en_font=en_font, bold=True, size=24), after=4, line=210, border_bottom=True))
        for block in section["blocks"]:
            kind = block["kind"]
            if kind == "entry":
                body.append(entry_line(block["org"], block["date"], cn_font=cn_font, en_font=en_font))
                body.append(paragraph(styled_text_runs(block["role"], cn_font=cn_font, en_font=en_font, italic=True), after=8, line=210))
                for bullet in block.get("bullets", []):
                    body.append(bullet_paragraph(bullet, cn_font=cn_font, en_font=en_font))
            elif kind == "paragraph":
                body.append(paragraph(styled_text_runs(block["text"], cn_font=cn_font, en_font=en_font), after=12, line=220))
            elif kind == "title":
                body.append(paragraph(styled_text_runs(block["text"], cn_font=cn_font, en_font=en_font, bold=True), after=6, line=210))
            elif kind == "subtitle":
                body.append(paragraph(styled_text_runs(block["text"], cn_font=cn_font, en_font=en_font, italic=True, size=21), after=8, line=210))
            elif kind == "bullets":
                for bullet in block["items"]:
                    body.append(bullet_paragraph(bullet, cn_font=cn_font, en_font=en_font))
            elif kind == "spacer":
                body.append(paragraph([], after=block.get("after", 20), line=210))

    body.append(section_props())
    return (
        f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
        f'<w:document xmlns:w="{NS_W}"><w:body>{"".join(body)}</w:body></w:document>'
    )


def sample_data() -> dict:
    return {
        "name": "XXX",
        "summary_line": "女  |  20XX.XX出生  |  XX大学法学院 法学本科在读（大三）",
        "contact_line": "电话：XXX  |  邮箱：XXX",
        "sections": [
            {
                "title": "教育背景",
                "blocks": [
                    {"kind": "entry", "org": "XX大学 法学院", "date": "20XX.09 - 至今", "role": "法学本科在读"},
                    {
                        "kind": "paragraph",
                        "text": "主修课程：民法总论、刑法总论、合同法、民事诉讼法、行政法、劳动与社会保障法、公司法基础、法理学、中国法律史、知识产权法",
                    },
                ],
            },
            {
                "title": "实习经历",
                "blocks": [
                    {
                        "kind": "entry",
                        "org": "XX律师事务所",
                        "date": "20XX.07 - 20XX.08",
                        "role": "实习生",
                        "bullets": [
                            "协助支持民商事诉讼案件办理，接触合同纠纷、劳动争议及部分商标侵权、不正当竞争相关案件材料整理工作。",
                            "围绕案件争议焦点开展法律检索，累计参与约10-20次检索任务，使用北大法宝、威科先行等数据库检索法条及类案裁判文书。",
                            "对比不同法院裁判思路，整理支持或驳回请求权的理由结构，形成内部Word检索笔记、案例摘要及书面要点，并配合完成口头汇报。",
                            "协助整理商标侵权及相关案件证据材料，按时间顺序、证明目的、法律关系进行分类，并配合制作证据目录及基础事实时间线。",
                            "协助摘录裁判文书要点并标注争议焦点，使用Excel整理案件事实表格及证据对照信息。",
                            "参与起诉状、答辩状等诉讼文书的格式校对与基础内容检查，并协助留存网页截图、平台信息等电子证据材料。",
                            "跟随律师旁听案件讨论及庭审过程，了解知识产权及民商事诉讼案件的基础办理流程与证据要求。",
                        ],
                    }
                ],
            },
            {
                "title": "校园经历",
                "blocks": [
                    {
                        "kind": "entry",
                        "org": "模拟法庭课程项目组",
                        "date": "20XX.03 - 20XX.06",
                        "role": "成员",
                        "bullets": [
                            "参与民事侵权与合同纠纷模拟案件的角色分工，协助完成原告、被告及代理人视角下的基础材料准备。",
                            "协助撰写书面陈述提纲，整理基础证据材料清单，并参与争点梳理与答辩结构设计。",
                            "参与庭审模拟陈述及质证环节讨论，提升对诉讼流程、事实梳理及书面表达的基础理解。",
                        ],
                    },
                    {
                        "kind": "entry",
                        "org": "法学院学生会",
                        "date": "20XX.10 - 20XX.06",
                        "role": "干事",
                        "bullets": [
                            "参与学院迎新、讲座及普法宣传活动的组织与执行，协助完成现场统筹、签到及秩序维护。",
                            "配合完成海报及宣传文案基础撰写与修改，具备一定的文字整理与执行配合能力。",
                        ],
                    },
                ],
            },
            {
                "title": "法律研究与课程实践",
                "blocks": [
                    {"kind": "title", "text": "知识产权研究选题"},
                    {
                        "kind": "subtitle",
                        "text": "《互联网平台语境下商标侵权认定的困境与规则重构——以混淆可能性标准为中心》",
                    },
                    {
                        "kind": "bullets",
                        "items": [
                            "围绕互联网平台场景下商标侵权认定问题开展研究，重点分析搜索推荐、直播带货、算法分发等新型传播结构中“混淆可能性”标准的适用困境。",
                            "梳理我国互联网语境下商标侵权裁判中的适用分歧，聚焦关键词引流、直播带货中的商标展示边界及平台责任归责结构。",
                            "结合平台机制与裁判逻辑，提出在传统判断要素之外引入“注意力占用程度”“流量来源透明度”“平台介入强度”等补充因素。",
                            "对电商平台商标侵权、平台流量分发与竞争秩序之间的关系形成初步研究理解。",
                        ],
                    },
                    {
                        "kind": "entry",
                        "org": "法律文书写作课程实践",
                        "date": "20XX.09 - 20XX.12",
                        "role": "课程实践",
                        "bullets": [
                            "完成起诉状、答辩状、合同文本等基础法律文书写作练习，掌握常见诉讼文书的基本结构与规范表达。",
                            "进行代理词结构练习及证据清单整理训练，形成“事实 - 法律 - 结论”三段式基础写作意识。",
                            "结合课堂作业完成案件分析报告写作，提升案件事实归纳、争点识别与书面表达能力。",
                        ],
                    },
                ],
            },
            {
                "title": "技能与证书",
                "blocks": [
                    {
                        "kind": "bullets",
                        "items": [
                            "法律检索：能够使用北大法宝、威科先行等数据库进行法条、类案裁判文书及基础争点检索。",
                            "诉讼文书支持：具备起诉状、答辩状、代理词、证据清单等基础文书辅助写作与校对能力。",
                            "证据整理：能够进行证据目录整理、案件时间线梳理、Excel证据对照表制作及电子证据归类。",
                            "办公软件：熟练使用Word、Excel、PPT。",
                            "英语能力：CET-6 557分。",
                        ],
                    }
                ],
            },
        ],
    }


def validate_data(data: dict) -> None:
    required_top = ["name", "summary_line", "contact_line", "sections"]
    for key in required_top:
        if key not in data:
            raise ValueError(f"Missing required top-level field: {key}")
    if not isinstance(data["sections"], list) or not data["sections"]:
        raise ValueError("`sections` must be a non-empty list")

    for idx, section in enumerate(data["sections"], start=1):
        if "title" not in section:
            raise ValueError(f"Section {idx} missing `title`")
        if "blocks" not in section or not isinstance(section["blocks"], list):
            raise ValueError(f"Section {idx} missing `blocks` list")
        for jdx, block in enumerate(section["blocks"], start=1):
            kind = block.get("kind")
            if kind not in {"entry", "paragraph", "title", "subtitle", "bullets", "spacer"}:
                raise ValueError(f"Section {idx} block {jdx} has unsupported kind: {kind}")
            if kind == "entry":
                for key in ["org", "date", "role"]:
                    if key not in block:
                        raise ValueError(f"Section {idx} block {jdx} missing `{key}`")
            if kind == "paragraph" and "text" not in block:
                raise ValueError(f"Section {idx} block {jdx} missing `text`")
            if kind in {"title", "subtitle"} and "text" not in block:
                raise ValueError(f"Section {idx} block {jdx} missing `text`")
            if kind == "bullets" and "items" not in block:
                raise ValueError(f"Section {idx} block {jdx} missing `items`")


def write_docx(doc_xml: str, out_path: Path, *, title: str, cn_font: str, en_font: str) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml())
        zf.writestr("_rels/.rels", rels_xml())
        zf.writestr("word/_rels/document.xml.rels", document_rels_xml())
        zf.writestr("word/document.xml", doc_xml)
        zf.writestr("word/styles.xml", styles_xml(cn_font, en_font))
        zf.writestr("word/fontTable.xml", fonts_xml(cn_font, en_font))
        zf.writestr("docProps/core.xml", core_xml(title))
        zf.writestr("docProps/app.xml", app_xml())


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a self-contained DOCX resume without third-party dependencies.")
    parser.add_argument("--input-json", help="Optional JSON file describing the resume content.")
    parser.add_argument("--output", required=True, help="Output .docx path.")
    parser.add_argument("--title", default="法学生简历", help="DOCX metadata title.")
    parser.add_argument("--cn-font", default=default_cn_font(), help="Chinese font family. Platform-aware default: macOS=STKaiti, Windows=楷体.")
    parser.add_argument("--en-font", default="Calibri", help="Latin font family. Default: Calibri.")
    args = parser.parse_args()

    if args.input_json:
        data = json.loads(Path(args.input_json).read_text(encoding="utf-8"))
    else:
        data = sample_data()

    validate_data(data)
    doc_xml = build_document(data, cn_font=args.cn_font, en_font=args.en_font)
    write_docx(doc_xml, Path(args.output), title=args.title, cn_font=args.cn_font, en_font=args.en_font)
    print(args.output)


if __name__ == "__main__":
    main()
