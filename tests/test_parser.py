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
        values = ('/foo/',
                    '/foo/,/bar/',
                    '/foo/,?bar?',
                    '?foo?,?bar?',
                    '?foo?,/bar/',
                    '/foo/;/bar/',
                    '/foo/;?bar?',
                    '?foo?;?bar?',
                    '?foo?;/bar/',
                    '?foo?',
                    '/foo bar/',
                    '/ foo bar /',
                    '? foo bar ?',)

        for a_range in values:
            self.assertTrue(EX_POSTFIX_ADDRESS.match(a_range))

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
        values = ('%',
                '$',
                '.',
                '1',
                '10',
                '100',)

        for v in values:
            self.assertTrue(EX_STANDALONE_RANGE.match(v))
        
        self.assertFalse(EX_STANDALONE_RANGE.match('a'))

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
                    '.,a',
                    '100,1',)

        for v in values:
            self.assertTrue(EX_STANDALONE_RANGE.match(v))
        
        self.assertFalse(EX_STANDALONE_RANGE.match('a,$'))

    def testSimpleRangesWithOffsets(self):
        values = ('.,$-10',
        '$-10,.+1',
        '.+10,%+1',
        '100+100,1-100',)

        for v in values:
            self.assertTrue(EX_STANDALONE_RANGE.match(v))
        
        values = ('+100,-100',
                    '%-10,.-10',
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
        values = ('%',
                    '$',
                    '.',
                    '1',
                    '10',
                    '100',)
        
        for v in values:
            self.assertTrue(EX_PREFIX_RANGE.match(v))
        
        values = ('a',
                    ':',)
        
        for v in values:
            self.assertFalse(EX_PREFIX_RANGE.match(v))

    def testAddressBySearchOnly(self):
        values = ('/foo/',
                    '/bar/',
                    '/100/',
                    '?foo?',
                    '?bar?',
                    '?100?',)

        for v in values:
            self.assertTrue(EX_PREFIX_RANGE.match(v))
    
    def testAddressWithOffsets(self):
        values = ('/foo/+10',
                    '/bar/-100',
                    '/100/+100',
                    '?foo?-10',
                    '?bar?+10+10',
                    '?100?+10-10',)

        for v in values:
            self.assertTrue(EX_PREFIX_RANGE.match(v))

    def testSimpleRanges(self):
        values = ('.,$',
                    '$,.',
                    '.,%',
                    '$,%',
                    '100,1',)

        for v in values:
            self.assertTrue(EX_PREFIX_RANGE.match(v))

        values = ('%,.',
                    '%,$',
                    'a,$',
                    '.,a',)
        
        for v in values:
            self.assertFalse(EX_PREFIX_RANGE.match(v))

    def testSimpleRangesWithOffsets(self):
        values = ('.,$-10',
                    '$-10,.+1',
                    '.+10+10,%+1',
                    '100+100,1-100',)
        
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
        values = ('/foo/,?bar?',
                    '/foo/,/bar/',
                    '?foo?,?bar?',
                    '/foo/,$',
                    '$,/foo/',
                    '$,/foo/',)
        
        for v in values:
            self.assertTrue(EX_PREFIX_RANGE.match(v))


class TestPartitionRange(unittest.TestCase):
        def testDetectRanges(self):
            values = (
                ('10,20abc',        ('10', '0', ',', '20', '0')),
                ('10+10,20+10abc',  ('10', '+10', ',', '20', '+10')),
                ('.,$abc',          ('.', '0', ',', '$', '0')),
                ('.-10,$-5abc',     ('.', '-10', ',', '$', '-5')),
            )

            for actual, expected in values:
                self.assertEquals(partition_raw_range(actual), EX_RANGE(*expected))
