span_templ = "<span id='{id}' class='value {type}' title='{title}'>{content}</span>"
value_link_templ = "<a href='{url}' id='{id}' class='value {type}' title='{title}' target='list'>{content}</a>"
list_link_templ = "<a href='{url}' id='{id}' class='link {type}' title='{title}' target='list'>{content}</a>"

tale_templ = """<!DOCTYPE html>
<html lang="en" xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
    <title>{title}</title>
    <link rel="stylesheet" href="../../style.css">
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
    <link rel="stylesheet" href="../style.css">
    <link rel="stylesheet" href="values.css">
    <style>
.value {{
    line-height: 1.4em;
}}
    </style>
  </head>
<body>
    <a href="map.html" target="_top">Tales vs Labels Heatmap</a><br/>
    <a href="keywords.svg" target="_top">Labels Venn Diagram</a>
    <h3>{title}</h3>{body}</body></html>"""

venn_templ = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg xmlns="http://www.w3.org/2000/svg" height="700" width="700">
  <circle cx="37.5%" cy="37.5%" r="40%" style="fill:#aaffaa;fill-opacity:.5" />
  <circle cx="62.5%" cy="37.5%" r="40%" style="fill:#ffaaaa;fill-opacity:.5" />
  <circle cx="50%" cy="65%" r="40%" style="fill:#aaaaff;fill-opacity:.5" />
  
  <text transform="translate(105,70)" width="20%" height="20%">
    <tspan x="0" y="-10" font-weight="bold">Germany (DE)</tspan>{de}
  </text>
  <text transform="translate(525,70)" width="20%" height="20%">
    <tspan x="0" y="-10" font-weight="bold">Italy (IT)</tspan>{it}
  </text>
  <text transform="translate(405,595)" width="20%" height="20%">
    <tspan x="0" y="-10" font-weight="bold">Portugal (PT)</tspan>{pt}
  </text>

  <text transform="translate(105,350)" width="20%" height="20%">
    {de_pt}
  </text>
  <text transform="translate(535,350)" width="20%" height="20%">
    {it_pt}
  </text>
  <text transform="translate(315,35)" width="20%" height="20%">
    {de_it}
  </text>

  <text transform="translate(315,210)" width="20%" height="20%">
    {de_it_pt}
  </text>
</svg>"""
