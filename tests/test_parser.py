import re
import unittest

from ex_command_parser import ADDRESS_OFFSET
from ex_command_parser import ADDRESS_SEPARATOR
from ex_command_parser import EX_POSTFIX_ADDRESS
from ex_command_parser import EX_PREFIX_RANGE
from ex_command_parser import EX_STANDALONE_RANGE
from ex_command_parser import OPENENDED_SEARCH_ADDRESS
from ex_command_parser import POSTFIX_ADDRESS
from ex_command_parser import PREFIX_ADDRESS
from ex_command_parser import find_command
from ex_command_parser import is_only_range
from ex_command_parser import get_cmd_line_range
from ex_command_parser import extract_command_name
from ex_command_parser import parse_command
from ex_command_parser import EX_CMD
from ex_range import EX_RANGE
from ex_range import partition_raw_range


rx_ADDRESS_OFFSET = re.compile(ADDRESS_OFFSET)
rx_ADDRESS_SEPARATOR = re.compile(ADDRESS_SEPARATOR)
rx_OPENENDED_SEARCH_ADDRESS = re.compile(OPENENDED_SEARCH_ADDRESS)
rx_POSTFIX_ADDRESS = re.compile(POSTFIX_ADDRESS)
rx_PREFIX_ADDRESS = re.compile(PREFIX_ADDRESS)


class RegexTestCaseMixin(object):
    def assertRegexGroupWithManyCases(self, regex, values):
        for value, expected in values:
            self.assertEquals(regex.search(value).group(), expected)

    def asserRegexCapturesWithManyCases(self, regex, values):
        for actual, expected in values:
            actual = regex.search(actual).groupdict()
            self.assertEquals(actual, dict(zip(actual.keys(), expected)))

class OpenendedSearchAddress(unittest.TestCase, RegexTestCaseMixin):
    def testCanFindOpenendedSearchAddress(self):
        values = (
            ('/blah100 \\ 10,20', '/blah100 \\ 10,20'),
            ('?blah100 \\ 10,20', '?blah100 \\ 10,20'),
        )

        self.assertRegexGroupWithManyCases(rx_OPENENDED_SEARCH_ADDRESS, values)


class AddressSeparator(unittest.TestCase, RegexTestCaseMixin):
    def testCanFindAddressSeparator(self):
        values = (
            (',', ','),
            (';', ';'),
        )

        self.assertRegexGroupWithManyCases(rx_ADDRESS_SEPARATOR, values)


class AddressOffset(unittest.TestCase, RegexTestCaseMixin):
    def testCanFindOffsets(self):
        values = (
            ('+1', '+1'),
            ('+100', '+100'),
            ('-1', '-1'),
            ('-100', '-100'),
        )

        self.assertRegexGroupWithManyCases(rx_ADDRESS_OFFSET, values)


class PostfixAddress(unittest.TestCase, RegexTestCaseMixin):
    def testSymbols(self):
        values = (
            ('$', '$'),
            ('.', '.'),
        )

        self.assertRegexGroupWithManyCases(rx_POSTFIX_ADDRESS, values)

    def testAddressBySearch(self):
        values = (
            ('/foo/', '/foo/'),
            ('/foo\\//', '/foo\\//'),
            ('/ foo /', '/ foo /'),
            ('/foo//foo/', '/foo//foo/'),
            ('?foo?', '?foo?'),
            ('?foo\\??', '?foo\\??'),
            ('?foo??foo?', '?foo??foo?'),
            ('? foo ?', '? foo ?'),
        )

        self.assertRegexGroupWithManyCases(rx_POSTFIX_ADDRESS, values)

    def testNumericAddresses(self):
        values = (
            ('1', '1'),
            ('100', '100'),
            ('+100', '+100'),
            ('-100', '-100'),
        )

        self.assertRegexGroupWithManyCases(rx_POSTFIX_ADDRESS, values)

    def testAddressByBookmark(self):
        values = (
            ("'1", "'1"),
            ("'9", "'9"),
            ("'a", "'a"),
            ("'z", "'z"),
            ("'A", "'A"),
            ("'Z", "'Z"),
            ("'<", "'<"),
            ("'>", "'>"),
        )

        self.assertRegexGroupWithManyCases(rx_POSTFIX_ADDRESS, values)


class PrefixAddress(unittest.TestCase, RegexTestCaseMixin):
    def testSymbols(self):
        values = (
            ('$', '$'),
            ('.', '.'),
            ('%', '%'),
        )

        self.assertRegexGroupWithManyCases(rx_PREFIX_ADDRESS, values)

    def testAddressBySearch(self):
        values = (
            ('/foo/', '/foo/'),
            ('/ foo /', '/ foo /'),
            ('/foo//foo/', '/foo//foo/'),
            ('?foo?', '?foo?'),
            ('?foo??foo?', '?foo??foo?'),
            ('? foo ?', '? foo ?'),
        )

        self.assertRegexGroupWithManyCases(rx_PREFIX_ADDRESS, values)

    def testNumericAddresses(self):
        values = (
            ('1', '1'),
            ('100', '100'),
            ('+100', '+100'),
            ('-100', '-100'),
        )

        self.assertRegexGroupWithManyCases(rx_PREFIX_ADDRESS, values)

    def testAddressByBookmark(self):
        values = (
            ("'1", "'1"),
            ("'9", "'9"),
            ("'a", "'a"),
            ("'z", "'z"),
            ("'A", "'A"),
            ("'Z", "'Z"),
            ("'<", "'<"),
            ("'>", "'>"),
        )

        self.assertRegexGroupWithManyCases(rx_PREFIX_ADDRESS, values)


class PostfixAddressParser(unittest.TestCase, RegexTestCaseMixin):
    def testSimpleAddresses(self):
        values = (
            ('$', ('$',)),
            ('.', ('.',)),
            ('1', ('1',)),
            ('100', ('100',)),
            ('+100', ('+100',)),
            ('-100', ('-100',)),
            ('100XXX', ('100',)),
            ("'a", ("'a",)),
            ("'aXX", ("'a",)),
            ("'z", ("'z",)),
            ("'1", ("'1",)),
            ("'9", ("'9",)),
            ("'<", ("'<",)),
            ("'>", ("'>",)),
        )

        self.asserRegexCapturesWithManyCases(EX_POSTFIX_ADDRESS, values)

    def testInvaliSimpleAddresses(self):
        values = ('%', 'a', 'aa', 'a10')

        for value in values:
            self.assertFalse(EX_POSTFIX_ADDRESS.match(value))

    def testSimpleRanges(self):
        values = (
            ('$,$', ('$',)),
            ('.,.', ('.',)),
            ('.,$', ('.',)),
            ('$,.', ('$',)),
            ('1,0', ('1',)),
            ('10,10', ('10',)),
            ('20,20', ('20',)),
            ('.,100', ('.',)),
            ('100,.', ('100',)),
            ('$;.', ('$',)),
            ('$;$', ('$',)),
            ('.;.', ('.',)),
            ('.;$', ('.',)),
            ('20,30XX', ('20',)),
        )

        self.asserRegexCapturesWithManyCases(EX_POSTFIX_ADDRESS, values)

    def testInvalidSimpleRanges(self):
        values = ('%', '%;.', '%,.')
        for v in values:
            self.assertFalse(EX_POSTFIX_ADDRESS.match(v))

    def testSimpleRangesWithOffsets(self):
        values = (
                ('$-10,$+5', ('$-10',)),
                ('.+10,%-5', ('.+10',)),
                ('10-10,10+50', ('10-10',)),
        )

        self.asserRegexCapturesWithManyCases(EX_POSTFIX_ADDRESS, values)

    def testRangesBySearching(self):
        values = (
                ('/foo/', ('/foo/',)),
                ('/foo/,/bar/', ('/foo/',)),
                ('/foo/,?bar?', ('/foo/',)),
                ('?foo?,?bar?', ('?foo?',)),
                ('?foo?,/bar/', ('?foo?',)),
                ('/foo/;/bar/', ('/foo/',)),
                ('/foo/;?bar?', ('/foo/',)),
                ('?foo?;?bar?', ('?foo?',)),
                ('?foo?;/bar/', ('?foo?',)),
                ('?foo?', ('?foo?',)),
                ('/foo bar/', ('/foo bar/',)),
                ('/ foo bar /', ('/ foo bar /',)),
                ('? foo bar ?', ('? foo bar ?',)),
                )

        self.asserRegexCapturesWithManyCases(EX_POSTFIX_ADDRESS, values)

    def testSearchBasedAddressesWithEscapes(self):
        values = (
            ('/foo\//,$', ('/foo\//',)),
            ('?foo\??,$', ('?foo\??',)),
        )

        self.asserRegexCapturesWithManyCases(EX_POSTFIX_ADDRESS, values)

    def testOpenEndedSearches(self):
        values = (
            ('/foo bar', ('/foo bar',)),
            ('?foo bar', ('?foo bar',)),
        )

        self.asserRegexCapturesWithManyCases(EX_POSTFIX_ADDRESS, values)


class StandAloneRangeParser(unittest.TestCase):
    def testSimpleAddresses(self):
        values = (
                '%',
                '$',
                '.',
                '1',
                '10',
                '100',
                '+100',
                '-100',
                )

        for v in values:
            self.assertTrue(EX_STANDALONE_RANGE.match(v))

        self.assertFalse(EX_STANDALONE_RANGE.match('a'))

    def testIncompleteRanges(self):
        values = (
            '100,',
            '+100,',
            '-100,',
            ',100',
            ',+100',
            ',-100',
            '100+100,',
            ',100+100',
            ',/foo/+100',
            '/foo/+100,',
        )

        for v in values:
            self.assertTrue(EX_STANDALONE_RANGE.match(v))

    def testAddressBySearchOnly(self):
        values =  ('/foo/',
                    '/bar/',
                    '/100/',
                    '?foo?',
                    '?bar?',
                    '?100?',)

        for v in values:
            self.assertTrue(EX_STANDALONE_RANGE.match(v))

    def testAddressWithOffsets(self):
        values = ('/foo/+10',
                '/bar/-100',
                '/100/+100',
                '?foo?-10',
                '?bar?+10+10',
                '?100?+10-10',)

        for v in values:
            self.assertTrue(EX_STANDALONE_RANGE.match(v))

    def testSimpleRanges(self):
        values = ('.,$',
                    '$,.',
                    '%,.',
                    '.,%',
                    '$,%',
                    '%,$',
                    # FIXME: This one is legal in Vim, but I don't what it does.
                    '.,',
                    ',.',
                    '100,1',)

        for v in values:
            self.assertTrue(EX_STANDALONE_RANGE.match(v))

        self.assertFalse(EX_STANDALONE_RANGE.match('a,$'))
        self.assertFalse(EX_STANDALONE_RANGE.match('$,qwertyzt'))

    def testSimpleRangesWithOffsets(self):
        values = ('.,$-10',
        '$-10,.+1',
        '.+10,%+1',
        '100+100,1-100',
        '+100,-100',
        # According to Vim, this should be illegal (command error).
        '%-10,.-10',)

        for v in values:
            self.assertTrue(EX_STANDALONE_RANGE.match(v))

        values = (
                    # FIXME: This should be illegal.
                    '$+a,%',)

        for v in values:
            self.assertFalse(EX_STANDALONE_RANGE.match(v))

    def testComplexRanges(self):
        values = ('/foo/,?bar?',
                    '/foo/,/bar/',
                    '?foo?,?bar?',
                    '/foo/,$',
                    '$,/foo/',
                    '$,/foo/',)

        for v in values:
            self.assertTrue(EX_STANDALONE_RANGE.match(v))


class TestRange(unittest.TestCase):
    def testSimpleAddresses(self):
        values = (
                    '%abc',
                    '$abc',
                    '.abc',
                    '1abc',
                    '10abc',
                    '100abc',
                )

        for v in values:
            self.assertTrue(EX_PREFIX_RANGE.match(v))

        values = ('a',
                    ':',)

        for v in values:
            self.assertFalse(EX_PREFIX_RANGE.match(v))

    def testAddressBySearchOnly(self):
        values = ('/foo/abc',
                    '/bar/abc',
                    '/100/abc',
                    '?foo?abc',
                    '?bar?abc',
                    '?100?abc',)

        for v in values:
            self.assertTrue(EX_PREFIX_RANGE.match(v))

    def testAddressWithOffsets(self):
        values = ('/foo/+10abc',
                    '/bar/-100abc',
                    '/100/+100abc',
                    '?foo?-10abc',
                    '?bar?+10+10abc',
                    '?100?+10-10abc',)

        for v in values:
            self.assertTrue(EX_PREFIX_RANGE.match(v))

    def testSimpleRanges(self):
        values = ('.,$abc',
                    '$,.abc',
                    '.,%abc',
                    '$,%abc',
                    '100,1abc',
                    '%,.abc',
                    '%,$abc',
                    '.,abc',
                )

        for v in values:
            self.assertTrue(EX_PREFIX_RANGE.match(v))

        values = (
                    'a,$',
                )

        for v in values:
            self.assertFalse(EX_PREFIX_RANGE.match(v))

    def testSimpleRangesWithOffsets(self):
        values = ('.,$-10abc',
                    '$-10,.+1abc',
                    '.+10+10,%+1abc',
                    '100+100,1-100abc',)

        for v in values:
            self.assertTrue(EX_PREFIX_RANGE.match(v))

        values = (# This should be illegal.
                  '$+a,%',
                  # Not valid in Vim either.
                  '+100,-100',
                  '%-10,.-10-10',)

        for v in values:
            self.assertFalse(EX_PREFIX_RANGE.match(v))

    def testComplexRanges(self):
        values = ('/foo/,?bar?abc',
                    '/foo/,/bar/abc',
                    '?foo?,?bar?abc',
                    '/foo/,$abc',
                    '$,/foo/abc',
                    '$,/foo/abc',)

        for v in values:
            self.assertTrue(EX_PREFIX_RANGE.match(v))

    def testIncompleteRanges(self):
        values = (
            '100,abc',
            ',100abc',
            '/foo/+100,abc',
            ',/foo/+100abc',
        )

        for v in values:
            self.assertTrue(EX_PREFIX_RANGE.match(v))


class TestPartitionRange(unittest.TestCase):
        def testDetectRanges(self):
            values = (
                ('10,20',        ('10', '0', ',', '20', '0')),
                ('10+10,20+10',  ('10', '+10', ',', '20', '+10')),
                ('.,$',          ('.', '0', ',', '$', '0')),
                ('.-10,$-5',     ('.', '-10', ',', '$', '-5')),
            )

            for actual, expected in values:
                self.assertEquals(partition_raw_range(actual), EX_RANGE(*expected))


class FindCommand(unittest.TestCase):
    def testFindPartial(self):
        values = (
            ('she', ('shell', 'sh')),
            ('brow', ('browse', 'bro')),
        )

        for v, expected in values:
            actual = find_command(v)
            self.assertEquals(actual, expected)

    def testFindExact(self):
        values = (
            ('shell', ('shell', 'sh')),
            ('browse', ('browse', 'bro')),
        )

        for v, expected in values:
            actual = find_command(v)
            self.assertEquals(actual, expected)

    def testFindNone(self):
        actual = find_command('foo')
        self.assertEquals(actual, None)


class IsOnlyRange(unittest.TestCase):
    def testWeFindStandAloneRangesCorrectly(self):
        values = (
            '100,200',
            '100+100',
            '/foo/+100',
        )

        for v in values:
            self.assertTrue(is_only_range(v))

    def testWeDontMatchAgainstRangePlusCommand(self):
        values = (
            '100foo',
            '100+100foo',
            '/foo/+100foo',
            'xxx'
        )

        for v in values:
            self.assertFalse(is_only_range(v))


class GetCommandRange(unittest.TestCase):
    def testExtractCorrectRange(self):
        values = (
            ('100abc', '100'),
            ('100+10abc', '100+10'),
            ('100-10abc', '100-10'),
            ('100,-10abc', '100,-10'),
            ('/100/,-10abc', '/100/,-10'),
            ('.!foo', '.'),
        )

        for v, expected in values:
            self.assertEquals(get_cmd_line_range(v), expected)


class ExtractCommandName(unittest.TestCase):
    def testExtractShortCommandNames(self):
        values = (
            (':', ':'),
            ('!', '!'),
        )

        for v, expected in values:
            self.assertEquals(extract_command_name(v), expected)

    def testExtractValidCommandNamesCorrectly(self):
        values = (
            ('foo100', 'foo'),
            ('foo', 'foo'),
            ('foo:', 'foo'),
            ('foo/', 'foo'),
        )

        for v, expected in values:
            self.assertEquals(extract_command_name(v), expected)


class ParseCommand(unittest.TestCase):
    def testParseCommandsCorrectly(self):
        values = (
            (':100', EX_CMD(
                        name=':',
                        command='ex_goto',
                        forced=False,
                        range='100',
                        args={},
                        parse_errors=[],
                    )),
        )

        for v, expected in values:
            self.assertEquals(parse_command(v), expected)
