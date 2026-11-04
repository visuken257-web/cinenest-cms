# Chapter 8: Web Features
# Render Markdown -> HTML va sanitize bang whitelist the (bleach) de chong XSS.

import bleach
import markdown as md

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "b", "i", "a", "ul", "ol", "li",
    "blockquote", "code", "pre", "h1", "h2", "h3",
]
ALLOWED_ATTRS = {"a": ["href", "title", "rel"]}

# Bo Markdown danh cho danh gia/comment
COMMENT_ALLOWED_TAGS = ["p", "br", "strong", "em", "b", "i", "a", "code", "blockquote", "ul", "ol", "li"]


def render_markdown(raw_md, allowed_tags=None):
    """
    Chuyen Markdown tho -> HTML, sau do sanitize bang whitelist the (bleach.clean).
    Day la buoc BAT BUOC truoc khi render bang |safe trong template,
    vi neu khong sanitize, nguoi dung co the chen <script> qua Markdown (vi du link/image co JS).
    """
    tags = allowed_tags or ALLOWED_TAGS
    html = md.markdown(raw_md or "", extensions=["fenced_code"])
    clean_html = bleach.clean(html, tags=tags, attributes=ALLOWED_ATTRS, strip=True)
    return clean_html
