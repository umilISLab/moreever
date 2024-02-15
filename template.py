span_templ = "<span id='{id}' class='value {type}' title='{title}'>{content}</span>"
value_link_templ = "<a href='{url}' id='{id}' class='value {type}' title='{title}' target='list'>{content}</a>"
list_link_templ = "<a href='{url}' id='{id}' class='link {type}' title='{title}' target='list'>{content}</a>"

text_templ = """<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>{title}</title>
    <link rel="stylesheet" href="../../../style.css">
    <link rel="stylesheet" href="../values.css">
  </head>
<body><h1>{title}</h1>{body}</body></html>"""

list_templ = """<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>{title}</title>
    <link rel="stylesheet" href="{root_path}style.css">
  </head>
<body><h3>{title}</h3>{body}</body></html>"""

values_templ = """<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>{title}</title>
    <link rel="stylesheet" href="../../style.css">
    <link rel="stylesheet" href="values.css">
    <style>
.value {{
    line-height: 1.4em;
}}
    </style>
  </head>
<body>
  <div>
    <a href="map.html" target="_top">Texts vs Labels Heatmap</a><br/>
    <a href="keywords.svg" target="_top">Labels Venn Diagram</a>
  </div>
  <h3>{title}</h3>{body}</body></html>"""

venn_templ = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" height="100%" width="100%">
  <title>{title}</title>
  <svg x="50%" y="50%" overflow="visible" width="700" height="700">
    <g transform="translate(-350,-350)">
      <circle cx="37.5%" cy="37.5%" r="40%" style="fill:#aaffaa;fill-opacity:.5" />
      <circle cx="62.5%" cy="37.5%" r="40%" style="fill:#ffaaaa;fill-opacity:.5" />
      <circle cx="50%" cy="65%" r="40%" style="fill:#aaaaff;fill-opacity:.5" />
      
      <text transform="translate(105,70)" width="20%" height="20%">
        <tspan x="0" y="-10" font-weight="bold">{a_name}</tspan>{a}
      </text>
      <text transform="translate(525,70)" width="20%" height="20%">
        <tspan x="0" y="-10" font-weight="bold">{b_name}</tspan>{b}
      </text>
      <text transform="translate(405,595)" width="20%" height="20%">
        <tspan x="0" y="-10" font-weight="bold">{c_name}</tspan>{c}
      </text>

      <text transform="translate(105,350)" width="20%" height="20%">
        {a_c}
      </text>
      <text transform="translate(535,350)" width="20%" height="20%">
        {b_c}
      </text>
      <text transform="translate(315,35)" width="20%" height="20%">
        {a_b}
      </text>

      <text transform="translate(315,210)" width="20%" height="20%">
        {a_b_c}
      </text>
    </g>
  </svg>
</svg>"""
