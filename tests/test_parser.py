import unittest

from ex_command_parser import EX_POSTFIX_ADDRESS
from ex_command_parser import EX_STANDALONE_RANGE
from ex_command_parser import EX_PREFIX_RANGE
from ex_range import partition_raw_range
from ex_range import EX_RANGE


class TestAddressParser(unittest.TestCase):
    def testSimpleAddresses(self):
        values = (
            ('$', '$'),
            ('.', '.'),
            ('1', '1'),
            ('100', '100'),
        )

        for actual, expected in values:
            actual = EX_POSTFIX_ADDRESS.search(actual).groupdict()
            self.assertEquals(actual, dict(address=expected))
    
    def testInvaliSimpleAddresses(self):
        values = ('%', 'a', 'aa')

        for value in values:
            self.assertFalse(EX_POSTFIX_ADDRESS.match(value))
    
    def testSimpleRanges(self):
        # todo
        ('%;.', ('%;.', '%', None, ';', '.', None, None))
        # ('%,.', ('%,.', '%', None, ',', '.', None, None)),
        tests = (
            ('$,$', '$'),
            ('.,.', '.'),
            ('.,$', '.'),
            ('$,.', '$'),
            ('$;$', '$'),
            ('.;.', '.'),
            ('.;$', '.'),
            ('$;.', '$'),
            ('1,0', '1'),
            ('10,10', '10'),
            ('20,20', '20'),
            ('.,100', '.'),
            ('100,.', '100'),
        )

        for t in tests:
            actual = EX_POSTFIX_ADDRESS.search(t[0]).groupdict()
            self.assertEquals(actual, dict(address=t[1]))

    def testInvalidSimpleRanges(self):
        values = ('%;.', '%,.')
        for v in values:
            self.assertFalse(EX_POSTFIX_ADDRESS.match(v))

    def testSimpleRangesWithOffsets(self):
        values = (
                ('$-10,$+5', '$-10'),
                ('.+10,%-5', '.+10'),
                ('10-10,10+50', '10-10'),
        )

        for v in values:
            actual = EX_POSTFIX_ADDRESS.search(v[0]).groupdict()
            self.assertEquals(actual, dict(address=v[1]))

    def testRangesSearching(self):
        self.assertTrue(EX_POSTFIX_ADDRESS.match('/foo/'))
        self.assertTrue(EX_POSTFIX_ADDRESS.match('/foo/,/bar/'))
        self.assertTrue(EX_POSTFIX_ADDRESS.match('/foo/,?bar?'))
        self.assertTrue(EX_POSTFIX_ADDRESS.match('?foo?,?bar?'))
        self.assertTrue(EX_POSTFIX_ADDRESS.match('?foo?,/bar/'))
        self.assertTrue(EX_POSTFIX_ADDRESS.match('/foo/;/bar/'))
        self.assertTrue(EX_POSTFIX_ADDRESS.match('/foo/;?bar?'))
        self.assertTrue(EX_POSTFIX_ADDRESS.match('?foo?;?bar?'))
        self.assertTrue(EX_POSTFIX_ADDRESS.match('?foo?;/bar/'))
        self.assertTrue(EX_POSTFIX_ADDRESS.match('?foo?'))
        self.assertTrue(EX_POSTFIX_ADDRESS.match('/foo bar/'))
        self.assertTrue(EX_POSTFIX_ADDRESS.match('/ foo bar /'))
        self.assertTrue(EX_POSTFIX_ADDRESS.match('? foo bar ?'))

    def testSearchBasedAddressesWithEscapes(self):
        values = (
            (EX_POSTFIX_ADDRESS.search(r'/foo\//,$').groupdict(), {'address': r'/foo\//'}),
            (EX_POSTFIX_ADDRESS.search(r'?foo\??,$').groupdict(), {'address': r'?foo\??'}),
        )

        for actual, expected in values:
            self.assertEquals(actual, expected)
    
    def testOpenEndedSearches(self):
        values = (
            (r'/foo bar', r'/foo bar'),
            (r'?foo bar', r'?foo bar'),
        )

        for actual, expected in values:
            actual = EX_POSTFIX_ADDRESS.search(actual).groupdict()
            self.assertEquals(actual, dict(address=expected))

    # def testExtractRange(self):
    #     foo = EX_POSTFIX_ADDRESS.search(r'100,200delete')
    #     self.assertEquals(foo.group(), '100,200')
    #     foo = EX_POSTFIX_ADDRESS.search('.,200delete')
    #     self.assertEquals(foo.group(), '.,200')
    #     foo = EX_POSTFIX_ADDRESS.search(r'.+100,/foo/-20delete')
    #     self.assertEquals(foo.group(), '.+100,/foo/-20')


class TestOnlyRange(unittest.TestCase):
    def testSimpleAddresses(self):
        self.assertTrue(EX_STANDALONE_RANGE.match('%'))
        self.assertTrue(EX_STANDALONE_RANGE.match('$'))
        self.assertTrue(EX_STANDALONE_RANGE.match('.'))
        self.assertTrue(EX_STANDALONE_RANGE.match('1'))
        self.assertTrue(EX_STANDALONE_RANGE.match('10'))
        self.assertTrue(EX_STANDALONE_RANGE.match('100'))
        self.assertFalse(EX_STANDALONE_RANGE.match('a'))
        self.assertFalse(EX_STANDALONE_RANGE.match(':'))

    def testAddressBySearchOnly(self):
        self.assertTrue(EX_STANDALONE_RANGE.match('/foo/'))
        self.assertTrue(EX_STANDALONE_RANGE.match('/bar/'))
        self.assertTrue(EX_STANDALONE_RANGE.match('/100/'))
        self.assertTrue(EX_STANDALONE_RANGE.match('?foo?'))
        self.assertTrue(EX_STANDALONE_RANGE.match('?bar?'))
        self.assertTrue(EX_STANDALONE_RANGE.match('?100?'))
    
    def testAddressWithOffsets(self):
        self.assertTrue(EX_STANDALONE_RANGE.match('/foo/+10'))
        self.assertTrue(EX_STANDALONE_RANGE.match('/bar/-100'))
        self.assertTrue(EX_STANDALONE_RANGE.match('/100/+100'))
        self.assertTrue(EX_STANDALONE_RANGE.match('?foo?-10'))
        self.assertTrue(EX_STANDALONE_RANGE.match('?bar?+10+10'))
        self.assertTrue(EX_STANDALONE_RANGE.match('?100?+10-10'))

    def testSimpleRanges(self):
        self.assertTrue(EX_STANDALONE_RANGE.match('.,$'))
        self.assertTrue(EX_STANDALONE_RANGE.match('$,.'))
        self.assertTrue(EX_STANDALONE_RANGE.match('%,.'))
        self.assertTrue(EX_STANDALONE_RANGE.match('.,%'))
        self.assertTrue(EX_STANDALONE_RANGE.match('$,%'))
        self.assertTrue(EX_STANDALONE_RANGE.match('%,$'))
        self.assertFalse(EX_STANDALONE_RANGE.match('a,$'))
        # FIXME: This one is legal in Vim, but I don't what it does.
        self.assertTrue(EX_STANDALONE_RANGE.match('.,a'))
        self.assertTrue(EX_STANDALONE_RANGE.match('100,1'))

    def testSimpleRangesWithOffsets(self):
        self.assertTrue(EX_STANDALONE_RANGE.match('.,$-10'))
        self.assertTrue(EX_STANDALONE_RANGE.match('$-10,.+1'))
        self.assertFalse(EX_STANDALONE_RANGE.match('%-10,.-10'))
        self.assertTrue(EX_STANDALONE_RANGE.match('.+10,%+1'))
        # FIXME: This should be illegal.
        self.assertFalse(EX_STANDALONE_RANGE.match('$+a,%'))
        self.assertTrue(EX_STANDALONE_RANGE.match('100+100,1-100'))
        # Not valid in Vim either.
        self.assertFalse(EX_STANDALONE_RANGE.match('+100,-100'))

    def testComplexRanges(self):
        self.assertTrue(EX_STANDALONE_RANGE.match('/foo/,?bar?'))
        self.assertTrue(EX_STANDALONE_RANGE.match('/foo/,/bar/'))
        self.assertTrue(EX_STANDALONE_RANGE.match('?foo?,?bar?'))
        self.assertTrue(EX_STANDALONE_RANGE.match('/foo/,$'))
        self.assertTrue(EX_STANDALONE_RANGE.match('$,/foo/'))
        self.assertTrue(EX_STANDALONE_RANGE.match('$,/foo/'))


class TestRange(unittest.TestCase):
    def testSimpleAddresses(self):
        self.assertTrue(EX_PREFIX_RANGE.match('%'))
        self.assertTrue(EX_PREFIX_RANGE.match('$'))
        self.assertTrue(EX_PREFIX_RANGE.match('.'))
        self.assertTrue(EX_PREFIX_RANGE.match('1'))
        self.assertTrue(EX_PREFIX_RANGE.match('10'))
        self.assertTrue(EX_PREFIX_RANGE.match('100'))
        self.assertFalse(EX_PREFIX_RANGE.match('a'))
        self.assertFalse(EX_PREFIX_RANGE.match(':'))

    def testAddressBySearchOnly(self):
        self.assertTrue(EX_PREFIX_RANGE.match('/foo/'))
        self.assertTrue(EX_PREFIX_RANGE.match('/bar/'))
        self.assertTrue(EX_PREFIX_RANGE.match('/100/'))
        self.assertTrue(EX_PREFIX_RANGE.match('?foo?'))
        self.assertTrue(EX_PREFIX_RANGE.match('?bar?'))
        self.assertTrue(EX_PREFIX_RANGE.match('?100?'))
    
    def testAddressWithOffsets(self):
        self.assertTrue(EX_PREFIX_RANGE.match('/foo/+10'))
        self.assertTrue(EX_PREFIX_RANGE.match('/bar/-100'))
        self.assertTrue(EX_PREFIX_RANGE.match('/100/+100'))
        self.assertTrue(EX_PREFIX_RANGE.match('?foo?-10'))
        self.assertTrue(EX_PREFIX_RANGE.match('?bar?+10+10'))
        self.assertTrue(EX_PREFIX_RANGE.match('?100?+10-10'))

    def testSimpleRanges(self):
        self.assertTrue(EX_PREFIX_RANGE.match('.,$'))
        self.assertTrue(EX_PREFIX_RANGE.match('$,.'))
        self.assertFalse(EX_PREFIX_RANGE.match('%,.'))
        self.assertTrue(EX_PREFIX_RANGE.match('.,%'))
        self.assertTrue(EX_PREFIX_RANGE.match('$,%'))
        self.assertFalse(EX_PREFIX_RANGE.match('%,$'))
        self.assertFalse(EX_PREFIX_RANGE.match('a,$'))
        self.assertFalse(EX_PREFIX_RANGE.match('.,a'))
        self.assertTrue(EX_PREFIX_RANGE.match('100,1'))

    def testSimpleRangesWithOffsets(self):
        self.assertTrue(EX_PREFIX_RANGE.match('.,$-10'))
        self.assertTrue(EX_PREFIX_RANGE.match('$-10,.+1'))
        self.assertFalse(EX_PREFIX_RANGE.match('%-10,.-10-10'))
        self.assertTrue(EX_PREFIX_RANGE.match('.+10+10,%+1'))
        # This should be illegal.
        self.assertFalse(EX_PREFIX_RANGE.match('$+a,%'))
        self.assertTrue(EX_PREFIX_RANGE.match('100+100,1-100'))
        # Not valid in Vim either.
        self.assertFalse(EX_PREFIX_RANGE.match('+100,-100'))

    def testComplexRanges(self):
        self.assertTrue(EX_PREFIX_RANGE.match('/foo/,?bar?'))
        self.assertTrue(EX_PREFIX_RANGE.match('/foo/,/bar/'))
        self.assertTrue(EX_PREFIX_RANGE.match('?foo?,?bar?'))
        self.assertTrue(EX_PREFIX_RANGE.match('/foo/,$'))
        self.assertTrue(EX_PREFIX_RANGE.match('$,/foo/'))
        self.assertTrue(EX_PREFIX_RANGE.match('$,/foo/'))


class TestPartitionRange(unittest.TestCase):
        def testDetectRanges(self):
            actual = partition_raw_range('10,20abc')
            expected = EX_RANGE('10', '0', ',', '20', '0')
            self.assertEquals(actual, expected)
            actual = partition_raw_range('10+10,20+10abc')
            expected = EX_RANGE('10', '+10', ',', '20', '+10')
            self.assertEquals(actual, expected)
            actual = partition_raw_range('.,$abc')
            expected = EX_RANGE('.', '0', ',', '$', '0')
            self.assertEquals(actual, expected)
            actual = partition_raw_range('.-10,$-5abc')
            expected = EX_RANGE('.', '-10', ',', '$', '-5')
            self.assertEquals(actual, expected)
