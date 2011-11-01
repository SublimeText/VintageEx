import sublime


def get_line_nr(view, point):
    return view.rowcol(point)[0] + 1


# TODO: Move this to sublime_lib; make it accept a point or a region.
def getEOL(view, point):
    return view.line(point).end()


# TODO: Move this to sublime_lib; make it accept a point or a region.
def getBOL(view, point):
    return view.line(point).begin()


def find_line(view, start=0, end=-1, target=0):
    """Performs binary search to locate `target` line number.
    Returns `Region` comprising line no. `target` or -1 if can't find `target`.
    """
    if  target < 0 or target > view.size():
        return -1

    if end == -1: end = view.size()

    lo, hi = start, end
    while lo <= hi:
        middle = lo + (hi - lo) / 2
        if get_line_nr(view, middle) < target:
            lo = getEOL(view, middle) + 1
        elif get_line_nr(view, middle) > target:
            hi = getBOL(view, middle) - 1
        else:
            return view.full_line(middle)
    return -1


# TODO: Move this to sublime_lib; make it accept a point or a region.
def BOL(line):
    return line.begin()


# TODO: Move this to sublime_lib; make it accept a point or a region.
def EOL(line):
    return line.end()


def search_in_range(view, what, start, end):
    match = view.find(what, start)
    if match and ((match.begin() >= start) and (match.end() <= end)):
        return True


def find_last_match(view, what, start, end):
    match = view.find(what, start)
    new_match = None
    while match:
        new_match = view.find(what, match.end())
        if new_match and new_match.end() <= end:
            match = new_match
        else:
            return match


def reverse_search(view, what, start=0, end=-1):
    if end == -1: end = view.size()
    end = EOL(view.line(end))
    
    last_match = None

    lo, hi = start, end
    while True:
        middle = (lo + hi) / 2    
        line = view.line(middle)
        middle, eol = BOL(line), EOL(line)

        if search_in_range(view, what, middle, hi):
            lo = middle
        elif search_in_range(view, what, lo, middle - 1):
            hi = middle -1
        else:
            return calculate_relative_ref(view, '.')

        # Don't search forever the same line.
        if last_match and line.contains(last_match):
            match = find_last_match(view, what, lo, hi)
            return view.rowcol(match.begin())[0] + 1
        
        last_match = sublime.Region(line.begin(), line.end())    


def search(view, what, start_line=None):
    if start_line:
        start = view.text_point(start_line, 0)
    else:
        start = view.sel()[0].begin()
    reg = view.find(what, start)
    if not reg is None:
        row = (view.rowcol(reg.begin())[0] + 1)
    else:
        row = calculate_relative_ref(view, '.', start_line=start_line)
    return row


def calculate_relative_ref(view, where, start_line=None):
    if where == '$':
        return view.rowcol(view.size())[0] + 1
    if where == '.':
        if start_line:
            return view.rowcol(view.text_point(start_line, 0))[0] + 1
        return view.rowcol(view.sel()[0].begin())[0] + 1
