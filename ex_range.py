"""helpers to manage :ex mode ranges
"""

from collections import namedtuple

from ex_command_parser import EX_RANGE_REGEXP, EX_ONLY_RANGE_REGEXP
import location


EX_RANGE = namedtuple('ex_range', 'left left_offset separator right right_offset')


def partition_raw_only_range(range):
    parts = EX_ONLY_RANGE_REGEXP.search(range).groups()
    if parts[-1]:
        return EX_RANGE(
                    left=parts[-1],
                    left_offset='0',
                    separator='',
                    right='',
                    right_offset='0'
                    )
    else:
        return EX_RANGE(
                    left=parts[0],
                    left_offset=parts[1] or '0',
                    separator=parts[2],
                    right=parts[3],
                    right_offset=parts[4] or '0',
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
    parts = EX_RANGE_REGEXP.search(range).groups()
    # xxx try to make the regexp capture the desired groups only.
    return EX_RANGE(
                left=parts[1],
                left_offset=parts[3] or '0',
                separator=parts[5],
                right=parts[7],
                right_offset=parts[9] or '0'
                )


# XXX at the moment it won't work with /foo//bar/ parts.
def calculate_range_part(view, range_part):
    """takes the left or right part of a range and returns the actual buffer
    line they refer to.
        returns: a 1-based line number
    """
    if range_part.isdigit():
        return int(range_part)
    if range_part.startswith('/') or range_part.startswith('?'):
        # we need to strip the search marks. FIXME won't work in edge cases
        # like ?foo\/ (doublecheck with vim)
        if (not range_part.endswith(r'\/') or range_part.endswith(r'\?')
                and (range_part.endswith('?') or range_part.endswith('/'))):
                search_term = range_part[1:-1]
        else:
            search_term = range_part[1:]
        if range_part.startswith('?'):
            return location.reverse_search(view, search_term,
                                            end=view.sel()[0].begin())
        return location.search(view, search_term)
    if range_part in ('$', '.'):
        return location.calculate_relative_ref(view, range_part)

        
def calculate_range(view, raw_range, is_only_range=False):
    """takes an unparsed :ex range in text and returns the actual lines it
    refers to, 1-based
    """
    # xxx ugly quick solution. .groups() are different for the REGEXES used.
    if not is_only_range:
        parsed_range = partition_raw_range(raw_range)
    else:
        parsed_range = partition_raw_only_range(raw_range)
    if parsed_range.left == '%':
        left, left_offset = '1', '0'
        right, right_offset = '$', '0'
    elif parsed_range.separator:
        left, left_offset = parsed_range.left, parsed_range.left_offset
        right, right_offset = parsed_range.right, parsed_range.right_offset
    elif parsed_range.left:
        left = calculate_range_part(view, 
                            parsed_range.left) + \
                                            int(parsed_range.left_offset)
        return left, left
    
    return calculate_range_part(view, left) + int(left_offset), \
                calculate_range_part(view, right) + int(right_offset)
