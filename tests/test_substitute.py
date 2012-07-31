import unittest

from substitute import SubstituteLexer


class TestSubstituteLexer(unittest.TestCase):
    def setUp(self):
        self.lexer = SubstituteLexer()

    def testCanParseEmptyInput(self):
        actual = self.lexer.parse('')

        self.assertEqual(actual, ['', ''])

    def testCanParseShortFormWithFlagsOnly(self):
        one_flag = self.lexer.parse(r'g')
        many_flags = self.lexer.parse(r'gi')

        self.assertEqual(one_flag, ['g', ''])
        self.assertEqual(many_flags, ['gi', ''])

    def testCanParseShortFormWithCountOnly(self):
        actual = self.lexer.parse(r'100')

        self.assertEqual(actual, ['', '100'])

    def testCanParseShortFormWithFlagsAndCount(self):
        actual_1 = self.lexer.parse(r'gi100')
        actual_2 = self.lexer.parse(r'  gi  100  ')

        self.assertEqual(actual_1, ['gi', '100'])
        self.assertEqual(actual_2, ['gi', '100'])

    def testThrowErrorIfCountIsFollowedByAnything(self):
        self.assertRaises(SyntaxError, self.lexer.parse, r"100gi")

    def testThrowErrorIfShortFormIsFollowedByAnythingOtherThanFlagsOrCount(self):
        self.assertRaises(SyntaxError, self.lexer.parse, r"x")

    def testCanParseOneSeparatorOnly(self):
        actual = self.lexer.parse(r"/")

        self.assertEqual(actual, ['', '', '', ''])

    def testCanParseTwoSeparatorsOnly(self):
        actual = self.lexer.parse(r"//")

        self.assertEqual(actual, ['', '', '', ''])

    def testCanParseThreeSeparatorsOnly(self):
        actual = self.lexer.parse(r"///")

        self.assertEqual(actual, ['', '', '', ''])

    def testCanParseOnlySearchPattern(self):
        actual = self.lexer.parse(r"/foo")

        self.assertEqual(actual, ['foo', '', '', ''])

    def testCanParseOnlyReplacementString(self):
        actual = self.lexer.parse(r"//foo")

        self.assertEqual(actual, ['', 'foo', '', ''])

    def testCanParseOnlyFlags(self):
        actual = self.lexer.parse(r"///gi")

        self.assertEqual(actual, ['', '', 'gi', ''])

    def testCanParseOnlyCount(self):
        actual = self.lexer.parse(r"///100")

        self.assertEqual(actual, ['', '', '', '100'])

    def testCanParseOnlyFlagsAndCount(self):
        actual = self.lexer.parse(r"///gi100")

        self.assertEqual(actual, ['', '', 'gi', '100'])

    def testThrowIfFlagsAndCountAreReversed(self):
        self.assertRaises(SyntaxError, self.lexer.parse, r"///100gi")

    def testThrowIfFlagsAndCountAreInvalid(self):
        self.assertRaises(SyntaxError, self.lexer.parse, r"///x")

    def testCanEscapeDelimiter(self):
        actual = self.lexer.parse(r"/foo\/")

        self.assertEqual(actual, ['foo/', '', '', ''])

    def testCanEscapeDelimiterComplex(self):
        actual = self.lexer.parse(r"/foo\//hello")

        self.assertEqual(actual, ['foo/', 'hello', '', ''])
