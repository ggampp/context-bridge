from __future__ import annotations

from context_bridge.sources.lat_md.code_refs import code_ref_node_id, parse_code_ref
from context_bridge.sources.lat_md.wiki_links import parse_wiki_links


def test_parse_code_ref_with_symbol():
    (link,) = parse_wiki_links("[[src/auth.ts#validateToken]]")
    ref = parse_code_ref(link)
    assert ref is not None
    assert ref.path == "src/auth.ts"
    assert ref.symbol == "validateToken"


def test_parse_code_ref_without_symbol():
    (link,) = parse_wiki_links("[[src/auth.ts]]")
    ref = parse_code_ref(link)
    assert ref is not None
    assert ref.path == "src/auth.ts"
    assert ref.symbol is None


def test_parse_code_ref_returns_none_for_domain_link():
    (link,) = parse_wiki_links("[[billing#Plan Limits]]")
    assert parse_code_ref(link) is None


def test_code_ref_node_id_is_stable_and_slugified():
    (link,) = parse_wiki_links("[[src/auth.ts#validateToken]]")
    ref = parse_code_ref(link)
    assert code_ref_node_id(ref) == "lat-code-src-auth-ts-validatetoken"


def test_code_ref_node_id_without_symbol():
    (link,) = parse_wiki_links("[[src/auth.ts]]")
    ref = parse_code_ref(link)
    assert code_ref_node_id(ref) == "lat-code-src-auth-ts"
