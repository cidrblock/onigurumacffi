import pytest

import onigurumacffi

FOO_RE = onigurumacffi.compile('^foo')
ABC_RE = onigurumacffi.compile('(a+)B+(c+)')
UNICODE_RE = onigurumacffi.compile('.*?(🙃+)')


def test_region_free():
    region = onigurumacffi._lib.onig_region_new()
    onigurumacffi._region_free(region)


def test_regex_compiles():
    assert FOO_RE is not None


def test_regex_repr():
    assert repr(FOO_RE) == "onigurumacffi.compile('^foo')"


def test_regex_compile_failure():
    with pytest.raises(onigurumacffi.OnigError):
        onigurumacffi.compile('(')


def test_match_failure():
    assert FOO_RE.match('bar') is None


def test_match_success():
    assert FOO_RE.match('food') is not None


def test_match_groups():
    match = ABC_RE.match('aaaaaBBBBBcccDDD')
    assert match is not None
    assert match[0] == 'aaaaaBBBBBccc'
    assert match.group(0) == 'aaaaaBBBBBccc'
    assert match[1] == 'aaaaa'
    assert match.group(1) == 'aaaaa'
    assert match[2] == 'ccc'
    assert match.group(2) == 'ccc'
    with pytest.raises(IndexError):
        match[3]


def test_match_starts_ends():
    match = ABC_RE.match('aaaBBBcccddd')
    assert match is not None
    assert match.start() == 0
    assert match.end() == 9
    assert match.start(1) == 0
    assert match.end(1) == 3
    assert match.start(2) == 6
    assert match.end(2) == 9


def test_match_start():
    match = ABC_RE.match('aaaBBBcccddd', start=1)
    assert match is not None
    assert match.start() == 1
    assert match.end() == 9
    assert match[1] == 'aa'


def test_unicode_match():
    match = UNICODE_RE.match('ohai☃🙃🙃🙃wat')
    assert match is not None
    assert match[0] == 'ohai☃🙃🙃🙃'
    assert match[1] == '🙃🙃🙃'
    assert match.start() == 0
    assert match.end() == 8


def test_unicode_match_start():
    match = UNICODE_RE.match('☃☃☃🙃🙃🙃', start=1)
    assert match is not None
    assert match[0] == '☃☃🙃🙃🙃'


def test_re_compile_unicode_escape():
    pattern = onigurumacffi.compile(r'"\u2603++"')
    assert pattern.match('"☃☃☃☃"')


def test_search():
    match = ABC_RE.search('zzzaaaBccczzz')
    assert match is not None
    assert match.group() == 'aaaBccc'
    assert match.start() == 3


def test_search_start():
    match = ABC_RE.search('zzzaaaBccczzz', start=4)
    assert match is not None
    assert match.group() == 'aaBccc'
    assert match.start() == 4


def test_search_no_match():
    match = ABC_RE.search('zzz')
    assert match is None


def test_expand():
    match = ABC_RE.match('aaaBccccddd')
    assert match is not None
    assert match.expand(r'foo\1\1\1') == 'fooaaaaaaaaa'
    assert match.expand(r'foo\2\1') == 'fooccccaaa'
