import unittest

from ex_command_parser import EX_ADDRESS_REGEXP


class TestAddressParser(unittest.TestCase):
    def test_SimpleAddresses(self):
        self.assertTrue(EX_ADDRESS_REGEXP.match('$'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('.'))
        self.assertFalse(EX_ADDRESS_REGEXP.match('%'))
        self.assertFalse(EX_ADDRESS_REGEXP.match('a'))
        self.assertFalse(EX_ADDRESS_REGEXP.match('aa'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('1'))
        self.assertTrue(EX_ADDRESS_REGEXP.match('123'))
    
    def test_SimpleRanges(self):
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

    def test_SimpleRangesWithOffsets(self):
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
