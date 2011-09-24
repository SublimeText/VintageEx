from ex_command_parser import EX_ONLY_RANGE_REGEXP


def test_is_only_range_regexp():
    assert EX_ONLY_RANGE_REGEXP.search('/foo').groups() == (None, None, None, None, None, '/foo') 
    assert EX_ONLY_RANGE_REGEXP.search('/foo bar').groups() == (None, None, None, None, None, '/foo bar') 
    assert EX_ONLY_RANGE_REGEXP.search('?foo').groups() == (None, None, None, None, None, '?foo')
    assert EX_ONLY_RANGE_REGEXP.search('?foo bar').groups() == (None, None, None, None, None, '?foo bar')

    assert EX_ONLY_RANGE_REGEXP.search('/foo/').groups() == ('/foo/', None, None, None, None, None)
    assert EX_ONLY_RANGE_REGEXP.search('?foo?').groups() == ('?foo?', None, None, None, None, None)

    assert EX_ONLY_RANGE_REGEXP.search('/foo/+10').groups() == ('/foo/', '+10', None, None, None, None)
    assert EX_ONLY_RANGE_REGEXP.search('?foo?+10').groups() == ('?foo?', '+10', None, None, None, None)

    assert EX_ONLY_RANGE_REGEXP.search('.').groups() == ('.', None, None, None, None, None)
    assert EX_ONLY_RANGE_REGEXP.search('%').groups() == ('%', None, None, None, None, None)
    assert EX_ONLY_RANGE_REGEXP.search('$').groups() == ('$', None, None, None, None, None)

    assert EX_ONLY_RANGE_REGEXP.search('0').groups() == ('0', None, None, None, None, None)
    assert EX_ONLY_RANGE_REGEXP.search('100').groups() == ('100', None, None, None, None, None)

    assert EX_ONLY_RANGE_REGEXP.search('.,.').groups() == ('.', None, ',', '.', None, None)
    assert EX_ONLY_RANGE_REGEXP.search('.,$').groups() == ('.', None, ',', '$', None, None)
    assert EX_ONLY_RANGE_REGEXP.search('$,.').groups() == ('$', None, ',', '.', None, None)

    assert EX_ONLY_RANGE_REGEXP.search('.+10,$-5').groups() == ('.', '+10', ',', '$', '-5', None)
    assert EX_ONLY_RANGE_REGEXP.search('/foo/+10,$-5').groups() == ('/foo/', '+10', ',', '$', '-5', None)

    assert EX_ONLY_RANGE_REGEXP.search(r'/foo\//').groups() == (r'/foo\//', None, None, None, None, None)

