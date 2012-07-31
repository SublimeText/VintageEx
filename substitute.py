EOF = -1

class Lexer(object):
    def __init__(self):
        self.c = None # current character
        self.cursor = 0
        self.string = None

    def _reset(self):
        self.c = None
        self.cursor = 0
        self.string = None

    def consume(self):
        self.cursor += 1
        if self.cursor >= len(self.string):
            self.c = EOF
        else:
            self.c = self.string[self.cursor]

    def _do_parse(self):
        pass

    def parse(self, string):
        self._reset()
        self.string = string
        if not string:
            self.c = EOF
        else:
            self.c = string[0]
        return self._do_parse()


class SubstituteLexer(Lexer):
    DELIMITER = "/:"
    WHITE_SPACE = ' \t'
    FLAG = 'giI'

    def __init__(self):
        self.delimiter = None

    def _match_white_space(self):
        while self.c != EOF and self.c in self.WHITE_SPACE:
            # print "WHITESPACE", ":" + self.c + ":"
            self.consume()

    def _match_count(self):
        buf = []
        while self.c != EOF and self.c.isdigit():
            buf.append(self.c)
            self.consume()
        return ''.join(buf)

    def _match_flags(self):
        buf = []
        while self.c != EOF and not self.c.isdigit():
            if self.c in self.FLAG:
                buf.append(self.c)
                self.consume()
                continue
            # TODO(guillermooo): should actually raise "Trailing characters" error.
            raise SyntaxError("Invalid flag or not implemented.")
        return ''.join(buf)

    def _match_pattern(self):
        buf = []
        while self.c != EOF and self.c != self.delimiter:
            if self.c == '\\':
                buf.append(self.c)
                self.consume()
                if self.c in '\\':
                    # Don't store anything, we're escaping \.
                    self.consume()
                elif self.c == self.delimiter:
                    # Overwrite the \ we've just stored.
                    buf[-1] = self.delimiter
                    self.consume()

                if self.c == EOF:
                    break
            else:
                buf.append(self.c)
                self.consume()

        return ''.join(buf)

    def _parse_short(self):
        buf = []
        if self.c == EOF:
            return ['', ''] # no flags, no count

        if self.c.isalpha():
            buf.append(self._match_flags())
            self._match_white_space()
        else:
            buf.append('')

        if self.c != EOF and self.c.isdigit():
            buf.append(self._match_count())
            self._match_white_space()
        else:
            buf.append('')

        if self.c != EOF:
            raise SyntaxError("Trailing characters.")

        return buf

    def _parse_long(self):
        buf = []

        self.delimiter = self.c
        self.consume()

        if self.c == EOF:
            return ['', '', '', '']

        buf.append(self._match_pattern())

        if self.c != EOF:
            # We're at a separator now --we MUST be.
            self.consume()
            buf.append(self._match_pattern())
        else:
            buf.append('')

        if self.c != EOF:
            self.consume()
            self._match_white_space()
            buf.append(self._match_flags())
        else:
            buf.append('')

        if self.c != EOF:
            self._match_white_space()
            buf.append(self._match_count())
        else:
            buf.append('')

        self._match_white_space()
        if self.c != EOF:
            raise SyntaxError("Trailing characters.")

        return buf

    def _do_parse(self):
        self._match_white_space()
        if self.c != EOF and self.c in self.DELIMITER:
            return self._parse_long()
        else:
            return self._parse_short()


def split(s):
    return SubstituteLexer().parse(s)
