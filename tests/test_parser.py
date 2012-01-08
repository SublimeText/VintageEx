import unittest

from ex_command_parser import EX_ADDRESS_REGEXP
from ex_command_parser import EX_ONLY_RANGE_REGEXP
from ex_command_parser import EX_RANGE_REGEXP
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
            actual = EX_ADDRESS_REGEXP.search(actual).groupdict()
            self.assertEquals(actual, dict(address=expected))
    
    def testInvaliSimpleAddresses(self):
        values = ('%', 'a', 'aa')

        for value in values:
            self.assertFalse(EX_ADDRESS_REGEXP.match(value))
    
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
            actual = EX_ADDRESS_REGEXP.search(t[0]).groupdict()
            self.assertEquals(actual, dict(address=t[1]))

    def testInvalidSimpleRanges(self):
        values = ('%;.', '%,.')
        for v in values:
            self.assertFalse(EX_ADDRESS_REGEXP.match(v))

    def testSimpleRangesWithOffsets(self):
        values = (
                ('$-10,$+5', '$-10'),
                ('.+10,%-5', '.+10'),
                ('10-10,10+50', '10-10'),
        )

        for v in values:
            actual = EX_ADDRESS_REGEXP.search(v[0]).groupdict()
            self.assertEquals(actual, dict(address=v[1]))

    def testRangesSearching(self):
        self.assertTrue(EX_ADDRESS_REGEXP.match('/foo/'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('/foo/,/bar/'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('/foo/,?bar?'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('?foo?,?bar?'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('?foo?,/bar/'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('/foo/;/bar/'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('/foo/;?bar?'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('?foo?;?bar?'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('?foo?;/bar/'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('?foo?'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('/foo bar/'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('/ foo bar /'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('? foo bar ?'))

    def testSearchBasedAddressesWithEscapes(self):
        values = (
            (EX_ADDRESS_REGEXP.search(r'/foo\//,$').groupdict(), {'address': r'/foo\//'}),
            (EX_ADDRESS_REGEXP.search(r'?foo\??,$').groupdict(), {'address': r'?foo\??'}),
        )

        for actual, expected in values:
            self.assertEquals(actual, expected)

    # def testExtractRange(self):
    #     foo = EX_ADDRESS_REGEXP.search(r'100,200delete')
    #     self.assertEquals(foo.group(), '100,200')
    #     foo = EX_ADDRESS_REGEXP.search('.,200delete')
    #     self.assertEquals(foo.group(), '.,200')
    #     foo = EX_ADDRESS_REGEXP.search(r'.+100,/foo/-20delete')
    #     self.assertEquals(foo.group(), '.+100,/foo/-20')


class TestOnlyRange(unittest.TestCase):
    def testSimpleAddresses(self):
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('%'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('$'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('.'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('1'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('10'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('100'))
        self.assertFalse(EX_ONLY_RANGE_REGEXP.match('a'))
        self.assertFalse(EX_ONLY_RANGE_REGEXP.match(':'))

    def testAddressBySearchOnly(self):
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('/foo/'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('/bar/'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('/100/'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('?foo?'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('?bar?'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('?100?'))
    
    def testAddressWithOffsets(self):
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('/foo/+10'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('/bar/-100'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('/100/+100'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('?foo?-10'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('?bar?+10+10'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('?100?+10-10'))

    def testSimpleRanges(self):
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('.,$'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('$,.'))
        self.assertFalse(EX_ONLY_RANGE_REGEXP.match('%,.'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('.,%'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('$,%'))
        self.assertFalse(EX_ONLY_RANGE_REGEXP.match('%,$'))
        self.assertFalse(EX_ONLY_RANGE_REGEXP.match('a,$'))
        # FIXME: This one is legal in Vim, but I don't what it does.
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('.,a'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('100,1'))

    def testSimpleRangesWithOffsets(self):
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('.,$-10'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('$-10,.+1'))
        self.assertFalse(EX_ONLY_RANGE_REGEXP.match('%-10,.-10'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('.+10,%+1'))
        # FIXME: This should be illegal.
        self.assertFalse(EX_ONLY_RANGE_REGEXP.match('$+a,%'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('100+100,1-100'))
        # Not valid in Vim either.
        self.assertFalse(EX_ONLY_RANGE_REGEXP.match('+100,-100'))

    def testComplexRanges(self):
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('/foo/,?bar?'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('/foo/,/bar/'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('?foo?,?bar?'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('/foo/,$'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('$,/foo/'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('$,/foo/'))


class TestRange(unittest.TestCase):
    def testSimpleAddresses(self):
        self.assertTrue(EX_RANGE_REGEXP.match('%'))
        self.assertTrue(EX_RANGE_REGEXP.match('$'))
        self.assertTrue(EX_RANGE_REGEXP.match('.'))
        self.assertTrue(EX_RANGE_REGEXP.match('1'))
        self.assertTrue(EX_RANGE_REGEXP.match('10'))
        self.assertTrue(EX_RANGE_REGEXP.match('100'))
        self.assertFalse(EX_RANGE_REGEXP.match('a'))
        self.assertFalse(EX_RANGE_REGEXP.match(':'))

    def testAddressBySearchOnly(self):
        self.assertTrue(EX_RANGE_REGEXP.match('/foo/'))
        self.assertTrue(EX_RANGE_REGEXP.match('/bar/'))
        self.assertTrue(EX_RANGE_REGEXP.match('/100/'))
        self.assertTrue(EX_RANGE_REGEXP.match('?foo?'))
        self.assertTrue(EX_RANGE_REGEXP.match('?bar?'))
        self.assertTrue(EX_RANGE_REGEXP.match('?100?'))
    
    def testAddressWithOffsets(self):
        self.assertTrue(EX_RANGE_REGEXP.match('/foo/+10'))
        self.assertTrue(EX_RANGE_REGEXP.match('/bar/-100'))
        self.assertTrue(EX_RANGE_REGEXP.match('/100/+100'))
        self.assertTrue(EX_RANGE_REGEXP.match('?foo?-10'))
        self.assertTrue(EX_RANGE_REGEXP.match('?bar?+10+10'))
        self.assertTrue(EX_RANGE_REGEXP.match('?100?+10-10'))

    def testSimpleRanges(self):
        self.assertTrue(EX_RANGE_REGEXP.match('.,$'))
        self.assertTrue(EX_RANGE_REGEXP.match('$,.'))
        self.assertFalse(EX_RANGE_REGEXP.match('%,.'))
        self.assertTrue(EX_RANGE_REGEXP.match('.,%'))
        self.assertTrue(EX_RANGE_REGEXP.match('$,%'))
        self.assertFalse(EX_RANGE_REGEXP.match('%,$'))
        self.assertFalse(EX_RANGE_REGEXP.match('a,$'))
        self.assertFalse(EX_RANGE_REGEXP.match('.,a'))
        self.assertTrue(EX_RANGE_REGEXP.match('100,1'))

    def testSimpleRangesWithOffsets(self):
        self.assertTrue(EX_RANGE_REGEXP.match('.,$-10'))
        self.assertTrue(EX_RANGE_REGEXP.match('$-10,.+1'))
        self.assertFalse(EX_RANGE_REGEXP.match('%-10,.-10-10'))
        self.assertTrue(EX_RANGE_REGEXP.match('.+10+10,%+1'))
        # This should be illegal.
        self.assertFalse(EX_RANGE_REGEXP.match('$+a,%'))
        self.assertTrue(EX_RANGE_REGEXP.match('100+100,1-100'))
        # Not valid in Vim either.
        self.assertFalse(EX_RANGE_REGEXP.match('+100,-100'))

    def testComplexRanges(self):
        self.assertTrue(EX_RANGE_REGEXP.match('/foo/,?bar?'))
        self.assertTrue(EX_RANGE_REGEXP.match('/foo/,/bar/'))
        self.assertTrue(EX_RANGE_REGEXP.match('?foo?,?bar?'))
        self.assertTrue(EX_RANGE_REGEXP.match('/foo/,$'))
        self.assertTrue(EX_RANGE_REGEXP.match('$,/foo/'))
        self.assertTrue(EX_RANGE_REGEXP.match('$,/foo/'))


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
