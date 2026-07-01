from __future__ import annotations

from context_bridge.sources.lat_md.wiki_links import is_code_ref, parse_wiki_links


def test_parse_simple_target():
    links = parse_wiki_links("See [[billing]] for details.")
    assert len(links) == 1
    assert links[0].target == "billing"
    assert links[0].section is None


def test_parse_target_with_section():
    links = parse_wiki_links("See [[billing#Plan Limits]] for details.")
    assert links[0].target == "billing"
    assert links[0].section == "Plan Limits"


def test_parse_same_file_section_ref():
    links = parse_wiki_links("See [[#Session Refresh]] above.")
    assert links[0].target == ""
    assert links[0].section == "Session Refresh"


def test_parse_display_text_is_ignored():
    links = parse_wiki_links("See [[billing#Plan Limits|the plan limits section]].")
    assert links[0].target == "billing"
    assert links[0].section == "Plan Limits"


def test_parse_multiple_links():
    links = parse_wiki_links("[[auth]] and [[billing#Plan Limits]] and [[src/auth.ts#validateToken]]")
    assert len(links) == 3


def test_parse_no_links_returns_empty():
    assert parse_wiki_links("plain text, no links here") == []


def test_is_code_ref_for_path_with_slash():
    (link,) = parse_wiki_links("[[src/auth.ts#validateToken]]")
    assert is_code_ref(link)


def test_is_code_ref_false_for_domain_link():
    (link,) = parse_wiki_links("[[billing#Plan Limits]]")
    assert not is_code_ref(link)


def test_is_code_ref_true_for_bare_extension_no_slash():
    (link,) = parse_wiki_links("[[auth.py#helper]]")
    assert is_code_ref(link)
