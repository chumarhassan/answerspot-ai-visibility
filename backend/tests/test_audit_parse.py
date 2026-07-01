from gemini import match_target, parse_business_list
def test_parse_plain_json():
    raw = '{"businesses": ["Acme Roofing", "Best Roofers", "Top Shingle"]}'
    assert parse_business_list(raw) == ["Acme Roofing", "Best Roofers", "Top Shingle"]
def test_parse_json_in_code_fence():
    raw = '```json\n{"businesses": ["Acme Roofing", "Best Roofers"]}\n```'
    assert parse_business_list(raw) == ["Acme Roofing", "Best Roofers"]
def test_parse_json_with_surrounding_prose():
    raw = 'Sure! Here you go:\n{"businesses": ["Acme"]}\nHope that helps.'
    assert parse_business_list(raw) == ["Acme"]
def test_parse_empty_list_is_valid():
    assert parse_business_list('{"businesses": []}') == []
def test_parse_garbage_returns_empty():
    assert parse_business_list("the AI could not answer") == []
    assert parse_business_list("") == []
def test_parse_dedupes_case_insensitively():
    raw = '{"businesses": ["Acme", "ACME", "Best"]}'
    assert parse_business_list(raw) == ["Acme", "Best"]
def test_parse_ignores_non_strings():
    raw = '{"businesses": ["Acme", 5, null, "Best"]}'
    assert parse_business_list(raw) == ["Acme", "Best"]
def test_match_found_returns_position():
    businesses = ["Acme Roofing", "Joe's Plumbing", "Best Roofers"]
    assert match_target(businesses, "Joe's Plumbing") == (True, 2)
def test_match_not_found():
    businesses = ["Acme Roofing", "Best Roofers"]
    assert match_target(businesses, "Nonexistent Co") == (False, None)
def test_match_is_fuzzy_on_suffix():
    businesses = ["Joe's Plumbing LLC"]
    assert match_target(businesses, "Joe's Plumbing") == (True, 1)
def test_match_empty_list():
    assert match_target([], "Anything") == (False, None)
def test_match_empty_target():
    assert match_target(["Acme"], "") == (False, None)