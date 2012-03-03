import unittest
import re

from test_runner import g_test_view
from tests import select_bof
from tests import select_eof
from tests import select_line

from ex_range import calculate_range_part
from ex_range import EX_RANGE
from ex_range import partition_raw_only_range
from ex_range import calculate_range
from ex_range import calculate_relative_ref
from ex_range import calculate_address
from ex_command_parser import INCOMPLETE_RANGE_SEPARATOR


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
    def StartUp(self):
        select_bof(g_test_view)

    def tearDown(self):
        select_bof(g_test_view)

    def testCalculateRelativeRef(self):
        values = (
            (calculate_relative_ref(g_test_view, '.'), 1),
            (calculate_relative_ref(g_test_view, '.', start_line=100), 101),
            (calculate_relative_ref(g_test_view, '$'), 538),
            (calculate_relative_ref(g_test_view, '$', start_line=100), 538),
        )

        for actual, expected in values:
            self.assertEquals(actual, expected)

    def testCalculateRelativeRef2(self):
        self.assertEquals(calculate_relative_ref(g_test_view, '.'), 1)
        self.assertEquals(calculate_relative_ref(g_test_view, '$'), 538)

        select_line(g_test_view, 100)
        self.assertEquals(calculate_relative_ref(g_test_view, '.'), 100)

        select_line(g_test_view, 200)
        self.assertEquals(calculate_relative_ref(g_test_view, '.'), 200)



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
            (calculate_range(g_test_view, '0'), [(0, 0)]),
            (calculate_range(g_test_view, '1'), [(1, 1)]),
            (calculate_range(g_test_view, '1,1'), [(1, 1)]),
            (calculate_range(g_test_view, '%,1'), [(1, 538)]),
            (calculate_range(g_test_view, '1,%'), [(1, 538)]),
            (calculate_range(g_test_view, '1+99,160-10'), [(100, 150)]),
            (calculate_range(g_test_view, '/THIRTY/+10,100'), [(40, 100)]),
        )

        select_line(g_test_view, 31)
        values += (
            (calculate_range(g_test_view, '10,/THIRTY/'), [(10, 31)]),
            (calculate_range(g_test_view, '10;/THIRTY/'), [(10, 30)]),
        )

        for actual, expected in values:
            self.assertEquals(actual, expected)

    def tearDown(self):
        select_bof(g_test_view)


class TestIncompleteRanges(unittest.TestCase):
    def testMatchOnlyOneSide(self):
        values = (
            (r',', r','),
        )

        rx = re.compile(INCOMPLETE_RANGE_SEPARATOR)
        for v, expected in values:
            self.assertEquals(rx.match(v).group(), expected)


class CalculateAddress(unittest.TestCase):
    def setUp(self):
        select_eof(g_test_view)

    def tearDown(self):
        select_bof(g_test_view)

    def testCalculateAddressCorrectly(self):
        values = (
            ('100', 99),
            ('200', 199),
        )

        for v, expected in values:
            self.assertEquals(calculate_address(g_test_view, v), expected)

    def testOutOfBoundsAddressShouldReturnNone(self):
        self.assertEquals(calculate_address(g_test_view, '1000'), None)

    def testInvalidAddressShouldReturnNone(self):
        self.assertRaises(AttributeError, calculate_address, g_test_view, 'XXX')
