TOKEN_ESCAPE = "\\" # r"\" is SyntaxError, but len(r"\\") > len("\\") !!!
TOKEN_WHITE_SPACE = ' \t'
TOKEN_ESCAPED_CHARS = '\\'
TOKEN_SEPARATORS = '!$:/&@%'
TOKEN_FLAGS = 'gi'

class SubstituteCommandParser(object):
    """
        Parses a substitute: command and returns [PATTERN, REPLACEMENT, FLAGS, COUNT].

        GRAMMAR
            # substitute : short | long
            # short      : (FLAGS)? (COUNT)?
            # long       : SEP string (SEP (string)? (SEP (FLAGS)? (COUNT)?)?)?
            # string     : CHAR | ESCAPE
            # SEP        : [!$:/]
            # CHAR       : [^\]
            # ESCAPE     : '\'
            # FLAGS      : [gi]+
            # COUNT      : [0-9]+
    """

    def __init__(self, string):
        self.string = string
        self.index = 0
        self.result = []
        self.current_token = ''
        self.current_separator = ''

    def advance_one(self):
        self.index += 1

    def advance_while_white_space(self):
        while not self.at_eof() and (self.get_char() in TOKEN_WHITE_SPACE):
            self.index += 1

    def at_eof(self):
        return self.index >= len(self.string)

    def get_char(self):
        return self.string[self.index]

    def match_CHAR(self):
        while True:
            if (self.at_eof() or
                (self.get_char() == TOKEN_ESCAPE) or
                (self.get_char() == self.current_separator)):
                    break
            self.current_token += self.get_char()
            self.advance_one()

    def match_FLAG(self):
        self.advance_while_white_space()
        while True:
            if self.at_eof():
                    break
            elif self.get_char() in TOKEN_FLAGS:
                self.current_token += self.get_char()
                self.advance_one()
            else:
                break

    def match_COUNT(self):
        self.advance_while_white_space()
        while True:
            if self.at_eof():
                    break
            elif self.get_char().isdigit():
                self.current_token += self.get_char()
                self.advance_one()
            else:
                break

    def match_SEPARATOR(self):
        if self.at_eof():
            raise SyntaxError("Expected a separator, found EOF.")
        elif self.get_char() in TOKEN_SEPARATORS:
            if self.current_separator and self.current_separator != self.get_char():
                raise SyntaxError("Expected '%s' separator, found %s." % (self.current_separator, self.get_char()))
            else:
                self.current_token += self.get_char()
                self.current_separator = self.get_char()
                self.advance_one()
        else:
            raise SyntaxError("Expected a separator, found %s." % self.get_char())

    def match_ESCAPE(self):
        if self.at_eof():
            raise SyntaxError("Expected an escape sequence, found EOF.")
        elif self.get_char() in TOKEN_ESCAPED_CHARS + self.current_separator:
            self.current_token += self.get_char()
            self.advance_one()
        else:
            raise SyntaxError("Expected an escape sequence, found %s." % self.get_char())

    def parse_string(self):
        while True:
            if self.at_eof():
                break
            elif self.get_char() == self.current_separator:
                break
            elif self.get_char() == TOKEN_ESCAPE:
                self.current_token += self.get_char()
                self.advance_one()
                self.match_ESCAPE()
            else:
                self.match_CHAR()

    def clear_current_token(self):
        self.current_token = ''

    def update_result(self):
        self.result.append(self.current_token)
        self.clear_current_token()

    def parse(self):
        if self.get_char() in TOKEN_SEPARATORS:
            self.parse_long()
        else:
            self.parse_short()

        return self.result

    def parse_short(self):
        if not self.at_eof():
            self.match_FLAG()
            self.update_result()

        if not self.result:
            self.result.append('')

        if not self.at_eof():
            self.match_COUNT()
            self.update_result()

        if len(self.result) < 2:
            self.result.append('')

    def parse_long(self):
        self.match_SEPARATOR()
        self.clear_current_token()

        if not self.at_eof():
            self.parse_string()
            self.update_result()

        if not self.at_eof():
            self.match_SEPARATOR()
            self.clear_current_token()

        if not self.at_eof():
            self.parse_string()
            self.update_result()

        if not self.at_eof():
            self.match_SEPARATOR()
            self.clear_current_token()

        if not self.at_eof():
            self.match_FLAG()
            self.update_result()

        if not self.at_eof():
            self.match_COUNT()
            self.update_result()

        if not self.at_eof():
            raise SyntaxError("Trailing characters.")

        while len(self.result) < 4:
            self.result.append('')


if __name__ == '__main__':
    invocations = (
            r":",
            r"g",
            r"g100",
            r"g 100",
            r"100",
            r":foo",
            r":foo\\x::gi100",
            r":foo::",
            r":::",
            r"::foo:",
            r":bar:foo",
            r": xxx : foo ",
            r": xxx : foo : gi100",
            r"$\$foo\$$\\Xfoo\\X$ gi100",
        )

    for inv in invocations:
        p = SubstituteCommandParser(inv)
        print p.parse()
