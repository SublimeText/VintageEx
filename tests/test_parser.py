from ex_command_parser import EX_ONLY_RANGE_REGEXP, extract_args, \
                                extract_command_name, EX_RANGE_REGEXP


def test_full_cmd_regexp():
    # assert EX_RANGE_REGEXP.search('/foo/').groups() == ('/foo')
    assert EX_RANGE_REGEXP.search("'<,'>cmd").groups() == ('/foo')


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


def test_extract_args():
    assert extract_args('++opt1 ++opt2 +cmd1') == ('+cmd1', '++opt1 ++opt2', '', '')
    assert extract_args('++opt1 ++opt2') == ('', '++opt1 ++opt2', '', '')
    assert extract_args('++opt1') == ('', '++opt1', '', '')
    assert extract_args('+cmd') == ('+cmd', '', '', '')
    assert extract_args('hello world !cmd') == ('', '', 'hello world', '!cmd')
    assert extract_args('++opt1 hello world !cmd with args') == ('', '++opt1', 'hello world', '!cmd with args')


def test_extract_command_name():
    assert extract_command_name('whatever!') == 'whatever'
    assert extract_command_name('hello world') == 'hello'
    assert extract_command_name('hello++opt1=foo') == 'hello'
