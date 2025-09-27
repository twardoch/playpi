#!/usr/bin/env python3
html_content = """<span class="r-4qtqp9" style="min-width: 4px; min-height: 4px;"></span><div class="css-175oi2r"><div class="css-175oi2r"><div class="css-175oi2r r-tbyq58"><div class="css-175oi2r" data-testid="markdown-code-block"><div class="css-175oi2r r-1awozwy r-g2wdr4 r-ne48ov r-1nna3df r-6413gk r-43g30s r-l4nmg1 r-1u658rm r-1mbrv82 r-vmopo1 r-13qz1uu"><div dir="ltr" class="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-rjixqe r-16dba41 r-1aiqnjv r-n6v787" style="text-overflow: unset; color: rgb(231, 233, 234);"><span class="css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3" style="text-overflow: unset;">html</span></div><div class="css-175oi2r r-1ybcz0z"><button aria-label="Copy to clipboard" role="button" class="css-175oi2r r-sdzlij r-1phboty r-rs99b7 r-lrvibr r-1ceczpf r-lp5zef r-1loqt21 r-o7ynqc r-6416eg r-1ny4l3l" type="button" style="background-color: rgba(0, 0, 0, 0); border-color: rgba(0, 0, 0, 0);"><div dir="ltr" class="css-146c3p1 r-bcqeeo r-qvutc0 r-37j5jr r-q4m81j r-a023e6 r-rjixqe r-b88u0q r-1awozwy r-6koalj r-18u37iz r-16y2uox r-1777fci" style="text-overflow: unset; color: rgb(239, 243, 244);"><svg viewBox="0 0 24 24" aria-hidden="true" class="r-4qtqp9 r-yyyyoo r-dnmrzs r-bnwqim r-lrvibr r-m6rgpd r-10ptun7 r-1janqcz" style="color: rgb(239, 243, 244);"><g><path d="M19.5 2C20.88 2 22 3.12 22 4.5v11c0 1.21-.86 2.22-2 2.45V4.5c0-.28-.22-.5-.5-.5H6.05c.23-1.14 1.24-2 2.45-2h11zm-4 4C16.88 6 18 7.12 18 8.5v11c0 1.38-1.12 2.5-2.5 2.5h-11C3.12 22 2 20.88 2 19.5v-11C2 7.12 3.12 6 4.5 6h11zM4 19.5c0 .28.22.5.5.5h11c.28 0 .5-.22.5-.5v-11c0-.28-.22-.5-.5-.5h-11c-.28 0-.5.22-.5.5v11z"></path></g></svg><span class="css-1jxf684 r-dnmrzs r-1udh08x r-3s2u2q r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3 r-1b43r93 r-1cwl3u0" style="text-overflow: unset; border-bottom: 2px solid rgb(239, 243, 244);"></span></div></button></div></div><pre style="display: block; overflow-x: auto; padding: 8px; color: rgb(171, 178, 191); background: rgb(32, 35, 39); font-family: monospace; white-space: pre; font-size: 13px; width: 100%; box-sizing: border-box; border-bottom-left-radius: 4px; border-bottom-right-radius: 4px; margin-top: 0px;"><code class="language-text" style="white-space: pre;"><span>&lt;h3&gt;Variable Fonts in August 2024&lt;/h3&gt; </span>&lt;ul&gt;     &lt;li&gt;&lt;strong&gt;Variable Fonts in Design Software:&lt;/strong&gt; Variable fonts are now supported in design tools like Figma, allowing for dynamic adjustments in font weight and slant directly within the design process. This feature enhances the flexibility for designers to explore typography in real-time without needing multiple font files.&lt;/li&gt;          &lt;li&gt;&lt;strong&gt;New Variable Font Releases:&lt;/strong&gt; There's a growing trend towards releasing fonts with variable features, such as Cera Mono, which offers six weights and is designed for motion graphics, indicating a shift towards more dynamic typography in digital media.&lt;/li&gt;          &lt;li&gt;&lt;strong&gt;Creative Use in Branding:&lt;/strong&gt; Brands and designers are leveraging variable fonts for unique branding experiences. For instance, the use of fonts like Flux, which transitions between serif and sans-serif styles, showcases how variable fonts can adapt to different design needs within a single typeface.&lt;/li&gt;          &lt;li&gt;&lt;strong&gt;Community Engagement:&lt;/strong&gt; The typography community on platforms like X shows an active interest in exploring and sharing new variable fonts, with users discussing and sharing their experiences, like the use of Neue Machina in portfolios, highlighting a community-driven trend towards experimentation with variable typography.&lt;/li&gt; &lt;/ul&gt;</code></pre></div></div><br><div dir="ltr" class="css-146c3p1 r-bcqeeo r-1ttztb7 r-qvutc0 r-37j5jr r-a023e6 r-rjixqe r-16dba41" style="text-overflow: unset; color: rgb(231, 233, 234);"><span class="css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3" style="text-overflow: unset;"><span class="css-1jxf684 r-bcqeeo r-1ttztb7 r-qvutc0 r-poiln3" style="text-overflow: unset;">This summary reflects the current trends and discussions around variable fonts in August 2024, based on the latest insights and user interactions on platforms like X.</span></span></div></div></div>"""


#!/usr/bin/env python3
import html

from bs4 import BeautifulSoup, NavigableString, Tag
from html2text import HTML2Text


def html_to_markdown(html_content: str) -> str:
    """Convert HTML content to Markdown or plain text."""
    h = HTML2Text()
    h.body_width = 0
    h.bypass_tables = False
    h.close_quote = """
    h.default_image_alt = "image"
    h.emphasis_mark = "_"
    h.escape_snob = False
    h.google_doc = False
    h.google_list_indent = 0
    h.hide_strikethrough = False
    h.ignore_emphasis = False
    h.ignore_images = False
    h.ignore_links = False
    h.ignore_mailto_links = False
    h.ignore_tables = False
    h.images_as_html = False
    h.images_to_alt = False
    h.images_with_size = False
    h.inline_links = True
    h.links_each_paragraph = False
    h.mark_code = True
    h.open_quote = """
    h.pad_tables = True
    h.protect_links = True
    h.single_line_break = False
    h.skip_internal_links = False
    h.strong_mark = "**"
    h.tag_callback = None
    h.ul_item_mark = "-"
    h.unicode_snob = True
    h.use_automatic_links = True
    h.wrap_links = False
    h.wrap_list_items = False
    h.wrap_tables = False
    return h.handle(html_content)


def prune_html(soup):
    # List of elements to remove
    elements_to_remove = ["svg", "button", "input", "textarea", "select", "option"]

    for element in soup.find_all(elements_to_remove):
        element.decompose()

    return soup


def recursive_unescape(element):
    if isinstance(element, NavigableString):
        return html.unescape(str(element))

    if isinstance(element, Tag):
        if element.name in ["code", "pre"]:
            # For code and pre tags, unescape the content without wrapping
            return html.unescape("".join(str(child) for child in element.contents))
        # For other tags, recursively process their contents
        unescaped_children = "".join(recursive_unescape(child) for child in element.contents)
        if element.name == "[document]":
            return unescaped_children  # Remove the document tag
        attrs = " ".join(f'{k}="{v}"' for k, v in element.attrs.items())
        return f"<{element.name}{' ' + attrs if attrs else ''}>{unescaped_children}</{element.name}>"

    return ""


def convert_html_to_markdown(html_content: str) -> str:
    # Parse the HTML
    soup = BeautifulSoup(html_content, "html.parser")

    # Prune unwanted elements
    pruned_soup = prune_html(soup)

    # Recursively unescape and extract content
    unescaped_html = recursive_unescape(pruned_soup)

    # Convert the unescaped HTML to Markdown
    final_markdown = html_to_markdown(unescaped_html)

    # Remove any remaining lone backticks
    final_markdown = final_markdown.replace("`\n\n", "\n\n").replace("\n\n`", "\n\n")

    return final_markdown.strip()


# Example usage
