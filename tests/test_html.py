# this_file: tests/test_html.py
"""Tests for HTML processing utilities."""

from playpi.html import html_to_markdown


def test_html_to_markdown_basic():
    """Test basic HTML to Markdown conversion."""
    html = "<h1>Title</h1><p>This is a paragraph with <strong>bold</strong> text.</p>"
    result = html_to_markdown(html)

    assert "# Title" in result
    assert "This is a paragraph with **bold** text." in result


def test_html_to_markdown_links():
    """Test HTML links conversion."""
    html = '<p>Visit <a href="https://example.com">Example</a> for more info.</p>'
    result = html_to_markdown(html)

    assert "[Example](https://example.com)" in result


def test_html_to_markdown_lists():
    """Test HTML lists conversion."""
    html = """
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
    </ul>
    """
    result = html_to_markdown(html)

    assert "* Item 1" in result
    assert "* Item 2" in result


def test_html_to_markdown_empty():
    """Test empty HTML conversion."""
    result = html_to_markdown("")
    assert result == ""


def test_html_to_markdown_whitespace_cleanup():
    """Test that excessive whitespace is cleaned up."""
    html = """

    <h1>Title</h1>


    <p>Paragraph</p>


    """
    result = html_to_markdown(html)

    # Should not have excessive blank lines
    assert "\n\n\n" not in result
    assert result.strip().startswith("# Title")
    assert result.strip().endswith("Paragraph")
