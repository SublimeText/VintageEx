import unittest
import rangeparser


class ParserBase(unittest.TestCase):
    def setUp(self):
        self.parser = rangeparser.ParserBase("foo")

    def testIsInitCorrect(self):
        self.assertEqual(self.parser.source, "foo")
        self.assertEqual(self.parser.c, "f")

    def testCanConsume(self):
        rv = []
        while self.parser.c != rangeparser.EOF:
            rv.append(self.parser.c)
            self.parser.consume()
        self.assertEqual(rv, list("foo"))

    def testCanConsumeEmpty(self):
        parser = rangeparser.ParserBase('')
        self.assertEqual(parser.c, rangeparser.EOF)


class VimParser(unittest.TestCase):
    def testCanParseEmptyInput(self):
        parser = rangeparser.VimParser('')
        rv = parser.parse_range()
        self.assertEqual(rv, rangeparser.default_range_info)

    def testCanMatchMinusSignOffset(self):
        parser = rangeparser.VimParser('-')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_offset'] = -1
        expected['text_range'] = '-'
        self.assertEqual(rv, expected)

    def testCanMatchPlusSignOffset(self):
        parser = rangeparser.VimParser('+')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_offset'] = 1
        expected['text_range'] = '+'
        self.assertEqual(rv, expected)

    def testCanMatchMultiplePlusSignsOffset(self):
        parser = rangeparser.VimParser('++')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 2
        expected['text_range'] = '++'
        self.assertEqual(rv, expected)

    def testCanMatchMultipleMinusSignsOffset(self):
        parser = rangeparser.VimParser('--')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = -2
        expected['text_range'] = '--'
        self.assertEqual(rv, expected)

    def testCanMatchPositiveIntegerOffset(self):
        parser = rangeparser.VimParser('+100')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.' 
        expected['left_offset'] = 100 
        expected['text_range'] = "+100"
        self.assertEqual(rv, expected)

    def testCanMatchMultipleSignsAndPositiveIntegetOffset(self):
        parser = rangeparser.VimParser('++99')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 100 
        expected['text_range'] = '++99'
        self.assertEqual(rv, expected)

    def testCanMatchMultipleSignsAndNegativeIntegerOffset(self):
        parser = rangeparser.VimParser('--99')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = -100 
        expected['text_range'] = '--99'
        self.assertEqual(rv, expected)

    def testCanMatchPlusSignBeforeNegativeInteger(self):
        parser = rangeparser.VimParser('+-101')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = -100 
        expected['text_range'] = '+-101'
        self.assertEqual(rv, expected)

    def testCanMatchPostFixMinusSign(self):
        parser = rangeparser.VimParser('101-')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_offset'] = 100
        expected['text_range'] = '101-'
        self.assertEqual(rv, expected)

    def testCanMatchPostfixPlusSign(self):
        parser = rangeparser.VimParser('99+')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_offset'] = 100
        expected['text_range'] = '99+'
        self.assertEqual(rv, expected)

    def testCanMatchCurrentLineSymbol(self):
        parser = rangeparser.VimParser('.')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['text_range'] = '.'
        self.assertEqual(rv, expected)

    def testCanMatchLastLineSymbol(self):
        parser = rangeparser.VimParser('$')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['text_range'] = '$'
        self.assertEqual(rv, expected)

    def testCanMatchWholeBufferSymbol(self):
        parser = rangeparser.VimParser('%')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '%'
        expected['text_range'] = '%'
        self.assertEqual(rv, expected)

    def testCanMatchMarkRef(self):
        parser = rangeparser.VimParser("'a")
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = "'a"
        expected['text_range'] = "'a"
        self.assertEqual(rv, expected)

    def testCanMatchUppsercaseMarkRef(self):
        parser = rangeparser.VimParser("'A")
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = "'A"
        expected['text_range'] = "'A"
        self.assertEqual(rv, expected)

    def testMarkRefsMustBeAlpha(self):
        parser = rangeparser.VimParser("'0")
        self.assertRaises(SyntaxError, parser.parse_range)

    def testWholeBufferSymbolCannotHavePostfixOffsets(self):
        parser = rangeparser.VimParser('%100')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testWholeBufferSymbolCannotHavePrefixOffsets(self):
        parser = rangeparser.VimParser('100%')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testCurrentLineSymbolCannotHavePrefixOffsets(self):
        parser = rangeparser.VimParser('100.')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testLastLineSymbolCannotHavePrefixOffsets(self):
        parser = rangeparser.VimParser('100$')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testLastLineSymbolCanHavePostfixNoSignIntegerOffsets(self):
        parser = rangeparser.VimParser('$100')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['left_offset'] = 100
        expected['text_range'] = '$100'
        self.assertEqual(rv, expected)

    def testLastLineSymbolCanHavePostfixSignedIntegerOffsets(self):
        parser = rangeparser.VimParser('$+100')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['left_offset'] = 100
        expected['text_range'] = '$+100'
        self.assertEqual(rv, expected)

    def testLastLineSymbolCanHavePostfixSignOffsets(self):
        parser = rangeparser.VimParser('$+')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['left_offset'] = 1
        expected['text_range'] = '$+'
        self.assertEqual(rv, expected)

    def testCurrentLineSymbolCanHavePostfixNoSignIntegerOffsets(self):
        parser = rangeparser.VimParser('.100')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 100
        expected['text_range'] = '.100'
        self.assertEqual(rv, expected)

    def testCurrentLineSymbolCanHavePostfixSignedIntegerOffsets(self):
        parser = rangeparser.VimParser('.+100')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 100
        expected['text_range'] = '.+100'
        self.assertEqual(rv, expected)

    def testCurrentLineSymbolCanHavePostfixSignOffsets(self):
        parser = rangeparser.VimParser('.+')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 1
        expected['text_range'] = '.+'
        self.assertEqual(rv, expected)

    def testCanMatchSearchBasedOffsets(self):
        parser = rangeparser.VimParser('/foo/')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'foo', 0]]
        expected['text_range'] = '/foo/'
        self.assertEqual(rv, expected)

    def testCanMatchReverseSearchBasedOffsets(self):
        parser = rangeparser.VimParser('?foo?')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_search_offsets'] = [['?', 'foo', 0]]
        expected['text_range'] = '?foo?'
        self.assertEqual(rv, expected)

    def testCanMatchReverseSearchBasedOffsetsWithPostfixOffset(self):
        parser = rangeparser.VimParser('?foo?100')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_search_offsets'] = [['?', 'foo', 100]]
        expected['text_range'] = '?foo?100'
        self.assertEqual(rv, expected)

    def testCanMatchReverseSearchBasedOffsetsWithSignedIntegerOffset(self):
        parser = rangeparser.VimParser('?foo?-100')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_search_offsets'] = [['?', 'foo', -100]]
        expected['text_range'] = '?foo?-100'
        self.assertEqual(rv, expected)

    def testCanMatchSearchBasedOffsetsWithPostfixOffset(self):
        parser = rangeparser.VimParser('/foo/100')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'foo', 100]]
        expected['text_range'] = '/foo/100'
        self.assertEqual(rv, expected)

    def testCanMatchSearchBasedOffsetsWithSignedIntegerOffset(self):
        parser = rangeparser.VimParser('/foo/-100')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'foo', -100]]
        expected['text_range'] = '/foo/-100'
        self.assertEqual(rv, expected)

    def testSearchBasedOffsetsCanEscapeForwardSlash(self):
        parser = rangeparser.VimParser('/foo\/-100')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'foo/-100', 0]]
        expected['text_range'] = '/foo\/-100'
        self.assertEqual(rv, expected)

    def testSearchBasedOffsetsCanEscapeQuestionMark(self):
        parser = rangeparser.VimParser('?foo\?-100')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_search_offsets'] = [['?', 'foo?-100', 0]]
        expected['text_range'] = '?foo\?-100'
        self.assertEqual(rv, expected)

    def testSearchBasedOffsetsCanEscapeBackSlash(self):
        parser = rangeparser.VimParser('/foo\\\\?-100')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'foo\\?-100', 0]]
        expected['text_range'] = '/foo\\\\?-100'
        self.assertEqual(rv, expected)

    def testSearchBasedOffsetsEscapeAnyUnknownEscapeSequence(self):
        parser = rangeparser.VimParser('/foo\\h')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'fooh', 0]]
        expected['text_range'] = '/foo\\h'
        self.assertEqual(rv, expected)

    def testCanHaveMultipleSearchBasedOffsets(self):
        parser = rangeparser.VimParser('/foo//bar/?baz?')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'foo', 0],
                                           ['/', 'bar', 0],
                                           ['?', 'baz', 0],
                                          ]
        expected['text_range'] = '/foo//bar/?baz?'
        self.assertEqual(rv, expected)

    def testCanHaveMultipleSearchBasedOffsetsWithInterspersedNumericOffets(self):
        parser = rangeparser.VimParser('/foo/100/bar/+100--+++?baz?')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_search_offsets'] = [['/', 'foo', 100],
                                           ['/', 'bar', 101],
                                           ['?', 'baz', 0],
                                          ]
        expected['text_range'] = '/foo/100/bar/+100--+++?baz?'
        self.assertEqual(rv, expected)

    def testWholeBufferSymbolCannotHavePostfixSearchBasedOffsets(self):
        parser = rangeparser.VimParser('%/foo/')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testCurrentLineSymbolCannotHavePrefixSearchBasedOffsets(self):
        parser = rangeparser.VimParser('/foo/.')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testLastLineSymbolCannotHavePrefixSearchBasedOffsets(self):
        parser = rangeparser.VimParser('/foo/$')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testWholeBufferSymbolCannotHavePrefixSearchBasedOffsets(self):
        parser = rangeparser.VimParser('/foo/%')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testCurrentLineSymbolCanHavePostfixSearchBasedOffsets(self):
        parser = rangeparser.VimParser('./foo/+10')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_search_offsets'] = [['/', 'foo', 10]]
        expected['text_range'] = './foo/+10'
        self.assertEqual(rv, expected)

    def testLastLineSymbolCanHavePostfixSearchBasedOffsets(self):
        parser = rangeparser.VimParser('$?foo?+10')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['left_search_offsets'] = [['?', 'foo', 10]]
        expected['text_range'] = '$?foo?+10'
        self.assertEqual(rv, expected)

    def testLastLineSymbolCanHaveMultiplePostfixSearchBasedOffsets(self):
        parser = rangeparser.VimParser('$?foo?+10/bar/100/baz/')
        rv = parser.parse_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['left_search_offsets'] = [['?', 'foo', 10],
                                           ['/', 'bar', 100],
                                           ['/', 'baz', 0],
                                          ]
        expected['text_range'] = '$?foo?+10/bar/100/baz/'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegers(self):
        parser = rangeparser.VimParser('100,100')
        rv = parser.parse_full_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_offset'] = 100
        expected['separator'] = ','
        expected['right_offset'] = 100
        expected['text_range'] = '100,100'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegersWithOffsets(self):
        parser = rangeparser.VimParser('+100++--+;++100-')
        rv = parser.parse_full_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 101
        expected['separator'] = ';'
        expected['right_ref'] = '.'
        expected['right_offset'] = 100
        expected['text_range'] = '+100++--+;++100-'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegersSymbols_1(self):
        parser = rangeparser.VimParser('%,%')
        rv = parser.parse_full_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '%'
        expected['separator'] = ','
        expected['right_ref'] = '%'
        expected['text_range'] = '%,%'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegersSymbols_2(self):
        parser = rangeparser.VimParser('.,%')
        rv = parser.parse_full_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['separator'] = ','
        expected['right_ref'] = '%'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegersSymbols_2(self):
        parser = rangeparser.VimParser('%,.')
        rv = parser.parse_full_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '%'
        expected['separator'] = ','
        expected['right_ref'] = '.'
        expected['text_range'] = '%,.'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegersSymbols_3(self):
        parser = rangeparser.VimParser('$,%')
        rv = parser.parse_full_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['separator'] = ','
        expected['right_ref'] = '%'
        expected['text_range'] = '$,%'
        self.assertEqual(rv, expected)
        
    def testCanMatchFullRangeOfIntegersSymbols_4(self):
        parser = rangeparser.VimParser('%,$')
        rv = parser.parse_full_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '%'
        expected['separator'] = ','
        expected['right_ref'] = '$'
        expected['text_range'] = '%,$'
        self.assertEqual(rv, expected)

    def testCanMatchFullRangeOfIntegersSymbols_5(self):
        parser = rangeparser.VimParser('$,.')
        rv = parser.parse_full_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '$'
        expected['separator'] = ','
        expected['right_ref'] = '.'
        expected['text_range'] = '$,.'
        self.assertEqual(rv, expected)
        
    def testCanMatchFullRangeOfIntegersSymbols_6(self):
        parser = rangeparser.VimParser('.,$')
        rv = parser.parse_full_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['separator'] = ','
        expected['right_ref'] = '$'
        expected['text_range'] = '.,$'
        self.assertEqual(rv, expected)

    def testFullRangeCanMatchCommandOnly(self):
        parser = rangeparser.VimParser('foo')
        rv = parser.parse_full_range()
        expected = rangeparser.default_range_info.copy()
        self.assertEqual(rv, expected)

    def testInFullRangeLineSymbolsCannotHavePrefixOffsets_1(self):
        parser = rangeparser.VimParser('100.,%')
        self.assertRaises(SyntaxError, parser.parse_range)

    def testInFullRangeLineSymbolsCannotHavePrefixOffsets_2(self):
        parser = rangeparser.VimParser('%,100$')
        self.assertRaises(SyntaxError, parser.parse_full_range)

    def testInFullRangeLineSymbolsCannotHavePrefixOffsets_3(self):
        parser = rangeparser.VimParser('%,100.')
        self.assertRaises(SyntaxError, parser.parse_full_range)

    def testInFullRangeLineSymbolsCannotHavePrefixOffsets_4(self):
        parser = rangeparser.VimParser('100%,.')
        self.assertRaises(SyntaxError, parser.parse_full_range)

    def testComplexFullRange(self):
        parser = rangeparser.VimParser(".++9/foo\\bar/100?baz?--;'b-100?buzz\\\\\\??+10")
        rv = parser.parse_full_range()
        expected = rangeparser.default_range_info.copy()
        expected['left_ref'] = '.'
        expected['left_offset'] = 10
        expected['left_search_offsets'] = [['/', 'foobar', 100], ['?', 'baz', -2]]
        expected['separator'] = ';'
        expected['right_ref'] = "'b"
        expected['right_offset'] = -100
        expected['right_search_offsets'] = [['?', 'buzz\\?', 10]]
        expected['text_range'] = ".++9/foo\\bar/100?baz?--;'b-100?buzz\\\\\\??+10"
        self.assertEqual(rv, expected)

    def testFullRangeMustEndInAlpha(self):
        parser = rangeparser.VimParser('100%,.(')
        self.assertRaises(SyntaxError, parser.parse_full_range)


class TestCaseCommandLineParser(unittest.TestCase):
    def testCanParseCommandOnly(self):
        parser = rangeparser.CommandLineParser('foo')
        rv = parser.parse_cmd_line()
        expected_range = rangeparser.default_range_info.copy()
        expected = dict(
                range=expected_range,
                commands=[{"cmd":"foo", "args":"", "forced": False}],
                errors=[]
            )
        self.assertEqual(rv, expected)

    def testCanParseWithErrors(self):
        parser = rangeparser.CommandLineParser('10$foo')
        rv = parser.parse_cmd_line()
        expected = dict(
                range=None,
                commands=[],
                errors=['E492 Not an editor command.']
            )
        self.assertEqual(rv, expected)

    def testCanParseCommandWithArgs(self):
        parser = rangeparser.CommandLineParser('foo! bar 100')
        rv = parser.parse_cmd_line()
        expected_range = rangeparser.default_range_info.copy()
        expected = dict(
                range=expected_range,
                commands=[{"cmd":"foo", "args":"bar 100", "forced": True}],
                errors=[]
            )
        self.assertEqual(rv, expected)
        
    def testCanParseCommandWithArgsAndRange(self):
        parser = rangeparser.CommandLineParser('100foo! bar 100')
        rv = parser.parse_cmd_line()
        expected_range = rangeparser.default_range_info.copy()
        expected_range['left_offset'] = 100
        expected_range['text_range'] = '100'
        expected = dict(
                range=expected_range,
                commands=[{"cmd":"foo", "args":"bar 100", "forced": True}],
                errors=[],
            )
        self.assertEqual(rv, expected)

    def testCanParseDoubleAmpersandCommand(self):
        parser = rangeparser.CommandLineParser('&&')
        rv = parser.parse_cmd_line()
        expected_range = rangeparser.default_range_info.copy()
        expected = dict(
                range=expected_range,
                commands=[{"cmd":"&&", "args":"", "forced": False}],
                errors=[],
            )
        self.assertEqual(rv, expected)

    def testCanParseAmpersandCommand(self):
        parser = rangeparser.CommandLineParser('&')
        rv = parser.parse_cmd_line()
        expected_range = rangeparser.default_range_info.copy()
        expected = dict(
                range=expected_range,
                commands=[{"cmd":"&", "args":"", "forced": False}],
                errors=[],
            )
        self.assertEqual(rv, expected)

    def testCanParseBangCommand(self):
        parser = rangeparser.CommandLineParser('!')
        rv = parser.parse_cmd_line()
        expected_range = rangeparser.default_range_info.copy()
        expected = dict(
                range=expected_range,
                commands=[{"cmd":"!", "args":"", "forced": False}],
                errors=[],
            )
        self.assertEqual(rv, expected)

    def testCanParseBangCommandWithRange(self):
        parser = rangeparser.CommandLineParser('.!')
        rv = parser.parse_cmd_line()
        expected_range = rangeparser.default_range_info.copy()
        expected_range['text_range'] = '.'
        expected_range['left_ref'] = '.'
        expected = dict(
                range=expected_range,
                commands=[{"cmd":"!", "args":"", "forced": False}],
                errors=[],
            )
        self.assertEqual(rv, expected)


class TestAddressParser(unittest.TestCase):
    def testCanParseSymbolAddress_1(self):
        parser = rangeparser.AddressParser('.')
        rv = parser.parse()
        expected = {'ref': '.', 'search_offsets': [], 'offset': None}
        self.assertEqual(rv, expected)

    def testCanParseSymbolAddress_2(self):
        parser = rangeparser.AddressParser('$')
        rv = parser.parse()
        expected = {'ref': '$', 'search_offsets': [], 'offset': None}
        self.assertEqual(rv, expected)

    def testCanParseOffsetOnItsOwn(self):
        parser = rangeparser.AddressParser('100')
        rv = parser.parse()
        expected = {'ref': None, 'search_offsets': [], 'offset': 100}
        self.assertEqual(rv, expected)

    def testCanParseSignsOnTheirOwn(self):
        parser = rangeparser.AddressParser('++')
        rv = parser.parse()
        expected = {'ref': '.', 'search_offsets': [], 'offset': 2}
        self.assertEqual(rv, expected)

    def testCanParseSignAndNumber(self):
        parser = rangeparser.AddressParser('+1')
        rv = parser.parse()
        expected = {'ref': '.', 'search_offsets': [], 'offset': 1}
        self.assertEqual(rv, expected)

    def testCanParseSymbolAndOffset(self):
        parser = rangeparser.AddressParser('.+1')
        rv = parser.parse()
        expected = {'ref': '.', 'search_offsets': [], 'offset': 1}
        self.assertEqual(rv, expected)

    def testCanParseSearchOffset(self):
        parser = rangeparser.AddressParser('/foo bar')
        rv = parser.parse()
        expected = {'ref': None, 'search_offsets': [['/', 'foo bar', 0]], 'offset': None}
        self.assertEqual(rv, expected)

if __name__ == '__main__':
    unittest.main()
