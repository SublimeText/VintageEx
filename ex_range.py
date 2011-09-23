from collections import namedtuple

from vintage_ex import EX_RANGE_REGEXP
import location


EX_RANGE = namedtuple('ex_range', 'left left_offset separator right right_offset')


def get_range_parts(range):
    parts = EX_RANGE_REGEXP.search(range).groups()
    return EX_RANGE(
                left=parts[1],
                left_offset=parts[3] or '0',
                separator=parts[5],
                right=parts[7],
                right_offset=parts[9] or '0'
                )


def calculate_range(view, range):
    parsed_range = get_range_parts(range)
    if parsed_range.left == '%':
        left, left_offset = '1', '0'
        right, right_offset = '$', '0'
    elif parsed_range.separator:
        left, left_offset = parsed_range.left, parsed_range.left_offset
        right, right_offset = parsed_range.right, parsed_range.right_offset
    
    return calculate_range_part(view, left) + int(left_offset), \
                calculate_range_part(view, right) + int(right_offset)


def calculate_range_part(view, p):
    if p.isdigit():
        return int(p)
    if p.startswith('/') or p.startswith('?'):
        if p.startswith('?'):
            return location.reverse_search(view, p[1:-1],
                                            end=view.sel()[0].begin())
        return location.search(view, p[1:-1])
    if p in ('$', '.'):
        return location.calculate_relative_ref(view, p)
