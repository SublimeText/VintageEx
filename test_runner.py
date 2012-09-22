import sublime
import sublime_plugin

import os
import unittest
import StringIO


TEST_DATA_FILE_BASENAME = 'vintageex_test_data.txt'
TEST_DATA_PATH = os.path.join(sublime.packages_path(),
                              'VintageEx/tests/data/%s' % TEST_DATA_FILE_BASENAME)


g_test_view = None
g_executing_test_suite = None

test_suites = {
        'parser': ['vintage_ex_run_simple_tests', 'vex.parsers.test_cmdline'],
        'range': ['vintage_ex_run_data_file_based_tests', 'tests.test_range'],
        'location': ['vintage_ex_run_data_file_based_tests', 'tests.test_location'],
        'substitute': ['vintage_ex_run_simple_tests', 'tests.test_substitute'],
        'global': ['vintage_ex_run_simple_tests', 'tests.test_global'],
}


def print_to_view(view, obtain_content):
    edit = view.begin_edit()
    view.insert(edit, 0, obtain_content())
    view.end_edit(edit)
    view.set_scratch(True)

    return view


class ShowVintageExTestSuites(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_quick_panel(sorted(test_suites.keys()), self.run_suite)

    def run_suite(self, idx):
        global g_executing_test_suite

        suite_name = sorted(test_suites.keys())[idx]
        g_executing_test_suite = suite_name
        command_to_run, _ = test_suites[suite_name]

        self.window.run_command(command_to_run, dict(suite_name=suite_name))


class VintageExRunSimpleTestsCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        return os.getcwd() == os.path.join(sublime.packages_path(), 'VintageEx')

    def run(self, suite_name):
        bucket = StringIO.StringIO()
        _, suite = test_suites[suite_name]
        suite = unittest.defaultTestLoader.loadTestsFromName(suite)
        unittest.TextTestRunner(stream=bucket, verbosity=1).run(suite)

        print_to_view(self.window.new_file(), bucket.getvalue)


class VintageExRunDataFileBasedTests(sublime_plugin.WindowCommand):
    def run(self, suite_name):
        self.window.open_file(TEST_DATA_PATH)


class TestDataDispatcher(sublime_plugin.EventListener):
    def on_load(self, view):
        if view.file_name() and os.path.basename(view.file_name()) == TEST_DATA_FILE_BASENAME:
            global g_test_view
            g_test_view = view

            _, suite_name = test_suites[g_executing_test_suite]
            suite = unittest.TestLoader().loadTestsFromName(suite_name)

            bucket = StringIO.StringIO()
            unittest.TextTestRunner(stream=bucket, verbosity=1).run(suite)

            v = print_to_view(view.window().new_file(), bucket.getvalue)
            # In this order, or Sublime Text will fail.
            v.window().focus_view(view)
            view.window().run_command('close')
