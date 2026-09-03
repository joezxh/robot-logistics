import io

src = "d:/projects/robot-logic/docs/mujoco-manual/XMLreference.md"
out = "d:/projects/robot-logic/docs/mujoco-manual/XMLreference_CN.md"
lines = io.open(src, encoding="utf-8").read().split("\n")

intro_trans = {
    "# XML Reference": "# XML 参考手册",
    "## Introduction": "## 简介",
    "This chapter is the reference manual for the MJCF modeling language used in MuJoCo.":
        "本章是 MuJoCo 中使用的 MJCF 建模语言的参考手册。",
    "### XML schema": "### XML 模式",
    "The dropdown below summarizes the XML elements and their attributes in MJCF. All information in MJCF is entered through elements and attributes. Text content in elements is not used; if present, the parser ignores it.":
        "以下下拉列表汇总了 MJCF 中的 XML 元素及其属性。MJCF 中的所有信息都通过元素和属性输入。元素内的文本内容不被使用；如果存在，解析器会忽略它。",
    "The icons to the right of each element name have the following meaning:":
        "每个元素名称右侧的图标含义如下：",
    "Expand All Collapse All": "展开全部 折叠全部",
}
table_trans = {
    "| required element, can appear only once  ": "| 必需元素，只能出现一次  ",
    "---|---": "---|---",
    "| optional element, can appear multiple times recursively  ":
        "| 可选元素，可递归出现多次  ",
    "| optional element, can appear only once  ": "| 可选元素，只能出现一次  ",
    "\u200b | optional element, can appear multiple times (default case, no icon)  ":
        "\u200b | 可选元素，可多次出现（默认情况，无图标）  ",
}
trans = {}
trans.update(intro_trans)
trans.update(table_trans)

result = []
for ln in lines[0:4201]:
    s = ln.strip()
    if s.startswith("[") and "(" in s and s.endswith(")"):
        result.append(ln)
    elif ln in trans:
        result.append(trans[ln])
    else:
        result.append(ln)

with io.open(out, "w", encoding="utf-8") as f:
    f.write("\n".join(result))

print("TOC lines written:", len(result))
print("first 10:", result[:10])
print("last 3:", result[-3:])