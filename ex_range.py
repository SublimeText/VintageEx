"""helpers to manage :ex mode ranges
"""

from collections import namedtuple

from ex_command_parser import EX_STANDALONE_RANGE


EX_RANGE = namedtuple('ex_range', 'left left_offset separator right right_offset')


def partition_raw_only_range(range):
    parts = EX_STANDALONE_RANGE.search(range).groupdict()
    if parts['openended']:
        return EX_RANGE(
                    left=parts['openended'],
                    left_offset='0',
                    separator='',
                    right='',
                    right_offset='0'
                    )
    elif parts['incomplete']:
        return EX_RANGE(
                    left=parts['inc_laddress'] or '.',
                    left_offset=parts['inc_loffset'] or '0',
                    separator=parts['suf_alt_separator'] or parts['pref_alt_separator'],
                    right=parts['inc_raddress'] or '.',
                    right_offset=parts['inc_loffset'] or '0',
                    )
    else:
        return EX_RANGE(
                    left=parts['laddress'],
                    left_offset=parts['loffset'] or '0',
                    separator=parts['separator'],
                    right=parts['raddress'],
                    right_offset=parts['roffset'] or '0',
                    )


def partition_raw_range(range):
    """takes a text range and breaks it up into its constituents:
            /foo/+10;$-15
            ...would yield...

            left: /foo/
            left_offset: +10
            separator: ;
            right: $
            right_offset: -15
    """
    # At this point we can be sure that ``range`` is a valid prefix range.
    # ``EX_PREFIX_RANGE`` won't match correctly here because the suffixed
    # command has been stripped, so we use ``EX_STANDALONE_RANGE`` instead.
    # parts = EX_PREFIX_RANGE.search(range).groupdict()
    parts = EX_STANDALONE_RANGE.search(range).groupdict()
    if parts['incomplete']:
        return EX_RANGE(
                    left=parts['inc_laddress'] or '.',
                    left_offset=parts['inc_loffset'] or '0',
                    separator=parts['suf_alt_separator'] or parts['pref_alt_separator'],
                    right=parts['inc_raddress'] or '.',
                    right_offset=parts['inc_loffset'] or '0',
                    )

    return EX_RANGE(
                left=parts['laddress'],
                left_offset=parts['loffset'] or '0',
                separator=parts['separator'],
                right=parts['raddress'],
                right_offset=parts['roffset'] or '0'
                )


# XXX at the moment it won't work with /foo//bar/ parts.
def calculate_range_part(view, range_part, start_line=None):
    """takes the left or right part of a range and returns the actual buffer
    line they refer to.
        returns: a 1-based line number
    """
    if range_part.isdigit():
        return int(range_part)

    if range_part.startswith(('+', '-')):
        return calculate_relative_ref(view, '.', start_line) + int(range_part)

    if range_part.startswith(('/', '?')):
        # we need to strip the search marks. FIXME won't work in edge cases
        # like ?foo\/ (doublecheck with vim)
        if (not range_part.endswith((r'\/', r'\?'))
            and range_part.endswith(('?', '/'))):
                search_term = range_part[1:-1]
        else:
            search_term = range_part[1:]
        if range_part.startswith('?'):
            if start_line:
                end = view.line(view.text_point(start_line, 0)).end()
            else:
                end = view.sel()[0].begin()
            return ex_location.reverse_search(view, search_term, end=end)
        return ex_location.search(view, search_term, start_line=start_line)
    if range_part in ('$', '.'):
        return calculate_relative_ref(view, range_part, start_line)


def calculate_range(view, raw_range, is_only_range=False):
    """Takes an unparsed :ex range as a string and returns the actual lines it
    refers to (1-based).

        Returns: A tuple representing a line range in :view:.

        :view:
            Buffer where the range will be calculated.
        :raw_range:
            :ex range (string) used to calculate the actual line range.
        :is_only_range:
            Whether :raw_range: is followed by a command or not.
    """
    # FIXME: Ugly quick solution: .groups() are different for the REGEXES used.
    if not is_only_range:
        parsed_range = partition_raw_range(raw_range)
    else:
        parsed_range = partition_raw_only_range(raw_range)

    # FIXME: make sure this works with whitespace between markers, and doublecheck
    # with Vim to see whether '<;>' is allowed.
    # '<,>' returns all selected line blocks
    if parsed_range.left == "'<" and parsed_range.right == "'>":
        all_line_blocks = []
        for sel in view.sel():
            start = view.rowcol(sel.begin())[0] + 1
            end = view.rowcol(sel.end())[0] + 1
            all_line_blocks.append((start, end))
        return all_line_blocks

    # In full ranges, '%' can appear in any (or both) sides and will make the
    # range span the whole buffer. (Examples: %,% or %,$ or 10;%)
    # TODO:
    # In Vim, %-10 is illegal and throws an error, but we simply ignore
    # offsets with %.
    if parsed_range.left == '%' or parsed_range.right == '%':
        left, loffset = '1', '0'
        right, roffset = '$', '0'
    elif parsed_range.separator:
        left, loffset = parsed_range.left, parsed_range.left_offset
        right, roffset = parsed_range.right, parsed_range.right_offset
    elif parsed_range.left:
        left = calculate_range_part(view, parsed_range.left) + \
                                            int(parsed_range.left_offset)
        return [(left, left)]

    # In ranges separated by ";", the right-hand address is calculated starting
    # at the left-side address, and not based on the caret's position.
    if parsed_range.separator == ';':
        left = calculate_range_part(view, left) + int(loffset)
        right = calculate_range_part(view, right, start_line=left - 1) + \
                                                                int(roffset)
        # Vim asks the user before reversing ranges, but we won't because
        # reversing the order will be the desired choice most of the time.
        return [(min(left, right), max(left, right))]

    return [(calculate_range_part(view, left) + int(loffset), \
               calculate_range_part(view, right) + int(roffset))]


def calculate_relative_ref(view, where, start_line=None):
    if where == '$':
        return view.rowcol(view.size())[0] + 1
    if where == '.':
        if start_line:
            return view.rowcol(view.text_point(start_line, 0))[0] + 1
        return view.rowcol(view.sel()[0].begin())[0] + 1


def calculate_address(view, text_range):
    """Calculates a single-line address based on ``text_range``, which is a
    string that should be a valid Vi(m) address.

    Return values:
        - SUCCESS: address (0-based line address, positive integer)
        - ERROR: None (can't calculate valid address)
    """
    # XXX strip in the parsing phase instead
    text_range = text_range.strip()
    # Note that some address error checking is also performed at the parsing
    # stage, so that '%' doesn't reach here, for example.
    a, b = calculate_range(view, text_range.strip())[0]
    # FIXME: 0 should be a valid address?
    if not (0 < a <= view.rowcol(view.size())[0] + 1):
        return None
    return a - 1

# Avoid circular import.
import ex_location
