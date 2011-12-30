import unittest

from test_runner import g_test_view

from ex_range import calculate_range_part
from ex_range import EX_RANGE
from ex_range import partition_raw_only_range
from ex_range import calculate_range
from ex_location import calculate_relative_ref

import sublime


def select_point(view, left_end, right_end=None):
    if right_end is None:
        right_end = left_end 

    view.sel().clear()
    view.sel().add(sublime.Region(left_end, right_end))


def select_eof(view):
    select_point(view, view.size(), view.size())


def select_bof(view):
    select_point(view, 0, 0)
 

class TestCalculateRangeParts(unittest.TestCase):
    def testCalculateRangeParts(self):
        values = (
            (calculate_range_part(g_test_view, '/FIFTY'), 50),
            (calculate_range_part(g_test_view, '1'), 1),
            (calculate_range_part(g_test_view, '10'), 10),
            (calculate_range_part(g_test_view, '/FIFTY/'), 50),
        )

        select_eof(g_test_view)

        values += (
            (calculate_range_part(g_test_view, r'?\*\*TEN\*\*?'), 10),
        )

        for actual, expected in values:
            self.assertEquals(actual, expected)
    
    def tearDown(self):
        select_bof(g_test_view)
        

class TestCalculateRelativeRef(unittest.TestCase):
    def testCalculateRelativeRef(self):
        values = (
            (calculate_relative_ref(g_test_view, '.'), 1),
            (calculate_relative_ref(g_test_view, '.', start_line=100), 101),
            (calculate_relative_ref(g_test_view, '$'), 538),
            (calculate_relative_ref(g_test_view, '$', start_line=100), 538),
        )

        for actual, expected in values:
            self.assertEquals(actual, expected)
            

class TestPatitioningRanges(unittest.TestCase):
    def testPartitionRawOnlyRange(self):
        values = (
            (partition_raw_only_range('1,1'), EX_RANGE('1', '0', ',', '1', '0')),
            (partition_raw_only_range('1000,1000'), EX_RANGE('1000', '0', ',', '1000', '0')),
            (partition_raw_only_range('1+10,1-1'), EX_RANGE('1', '+10', ',', '1', '-1')),
            (partition_raw_only_range('1000+1000,1000-1000'), EX_RANGE('1000', '+1000', ',', '1000', '-1000')),
            (partition_raw_only_range('100,%'), EX_RANGE('100', '0', ',', '%', '0')),
            # FIXME: If right == '', then roffset should also be ''??
            (partition_raw_only_range('/100+10'), EX_RANGE('/100+10', '0', '', '', '0')),
        )

        for actual, expected in values:
            self.assertEquals(actual, expected)


class TestCalculatingRanges(unittest.TestCase):
    def testCalculateCorrectRange(self):
        values = (
            ('0', (0, 0)),
            ('1', (1, 1)),
            ('1,1', (1, 1)),
            ('%,1', (1, 538)),
            ('1,%', (1, 538)),
            ('1+99,160-10', (100, 150)),
            ('/THIRTY/+10,100', (40, 100)),
        )

        for raw_range, expected_result in values:
            self.assertEquals(calculate_range(g_test_view, raw_range), expected_result)
