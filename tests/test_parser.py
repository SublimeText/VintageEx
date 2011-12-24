import unittest

from ex_command_parser import EX_ADDRESS_REGEXP
from ex_command_parser import EX_ONLY_RANGE_REGEXP
from ex_command_parser import EX_RANGE_REGEXP


class TestAddressParser(unittest.TestCase):
    def testSimpleAddresses(self):
        self.assertTrue(EX_ADDRESS_REGEXP.match('$'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('.'))
        self.assertFalse(EX_ADDRESS_REGEXP.match('%'))
        self.assertFalse(EX_ADDRESS_REGEXP.match('a'))
        self.assertFalse(EX_ADDRESS_REGEXP.match('aa'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('1'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('123'))
    
    def testSimpleRanges(self):
        self.assertTrue(EX_ADDRESS_REGEXP.match('$,$'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('.,.'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('.,$'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('$,.'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('$;$'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('.;.'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('.;$'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('$;.'))
        self.assertFalse(EX_ADDRESS_REGEXP.match('%;.'))
        self.assertFalse(EX_ADDRESS_REGEXP.match('%,.'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('1,0'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('10,10'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('20,20'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('.,100'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('100,.'))

    def testSimpleRangesWithOffsets(self):
        self.assertTrue(EX_ADDRESS_REGEXP.match('$-10,$+5'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('.+10,%-5'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('10-10,10+50'))

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

    def testRangesSearchingWithEscapes(self):
        actual = EX_ADDRESS_REGEXP.search(r'/foo\//,$')
        self.assertEquals(actual.group(), r'/foo\//,$')
        actual = EX_ADDRESS_REGEXP.search(r'?foo\??,$')
        self.assertEquals(actual.group(), r'?foo\??,$')

    def testExtractRange(self):
        foo = EX_ADDRESS_REGEXP.search(r'100,200delete')
        self.assertEquals(foo.group(), '100,200')
        foo = EX_ADDRESS_REGEXP.search('.,200delete')
        self.assertEquals(foo.group(), '.,200')
        foo = EX_ADDRESS_REGEXP.search(r'.+100,/foo/-20delete')
        self.assertEquals(foo.group(), '.+100,/foo/-20')


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
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('%,.'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('.,%'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('$,%'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('%,$'))
        self.assertFalse(EX_ONLY_RANGE_REGEXP.match('a,$'))
        # FIXME: This one is legal in Vim, but I don't what it does.
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('.,a'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('100,1'))

    def testSimpleRangesWithOffsets(self):
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('.,$-10'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('$-10,.+1'))
        self.assertTrue(EX_ONLY_RANGE_REGEXP.match('%-10,.-10'))
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
        self.assertTrue(EX_RANGE_REGEXP.match('%,.'))
        self.assertTrue(EX_RANGE_REGEXP.match('.,%'))
        self.assertTrue(EX_RANGE_REGEXP.match('$,%'))
        self.assertTrue(EX_RANGE_REGEXP.match('%,$'))
        self.assertFalse(EX_RANGE_REGEXP.match('a,$'))
        self.assertFalse(EX_RANGE_REGEXP.match('.,a'))
        self.assertTrue(EX_RANGE_REGEXP.match('100,1'))

    def testSimpleRangesWithOffsets(self):
        self.assertTrue(EX_RANGE_REGEXP.match('.,$-10'))
        self.assertTrue(EX_RANGE_REGEXP.match('$-10,.+1'))
        self.assertTrue(EX_RANGE_REGEXP.match('%-10,.-10-10'))
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
