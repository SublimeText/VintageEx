import sublime
import sublime_plugin

import os
import unittest
import StringIO

# import itertools

g_test_view = None
g_testing_what = None

TEST_DATA_PATH = os.path.join(sublime.packages_path(), 'VintageEx/tests/data/vintageex_test_data.txt')
DATA_FILE_BASENAME = 'vintageex_test_data.txt'


test_suites = {
        'parser': ['vintage_ex_run_parser_tests'],
        'range': ['vintage_ex_run_data_file_based_tests'],
        'location': ['vintage_ex_run_data_file_based_tests'],
        'commands': [],
}
# FIXME: Running multiple test suites breaks them
# test_suites['all'] = list(itertools.chain(*[suite for suite in
                                                # test_suites.itervalues()]))


class VintageExTestRunnerCommander(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_quick_panel(sorted(test_suites.keys()), self.run_suite)

    def run_suite(self, idx):
        global g_testing_what
        g_testing_what = 'test_' + sorted(test_suites.keys())[idx]
        for runner_name in test_suites[sorted(test_suites.keys())[idx]]:
            self.window.run_command(runner_name)


class VintageExRunParserTestsCommand(sublime_plugin.WindowCommand):
    def is_enabled(self):
        return os.getcwd() == os.path.join(sublime.packages_path(), 'VintageEx')
        
    def run(self):
        from tests import test_parser
        bucket = StringIO.StringIO()
        suite = unittest.TestLoader().loadTestsFromModule(test_parser)
        # suite = unittest.TestLoader().loadTestsFromModule(test_commands)
        unittest.TextTestRunner(stream=bucket, verbosity=1).run(suite)

        v = self.window.new_file()
        edit = v.begin_edit()
        v.insert(edit, 0, bucket.getvalue())
        v.end_edit(edit)
        v.set_scratch(True)


class VintageExRunDataFileBasedTests(sublime_plugin.WindowCommand):
    def run(self):
        self.window.open_file(TEST_DATA_PATH)
    

def reset_caret(view):
    view.sel().clear()
    view.sel().add(sublime.Region(0, 0))


class TestDataDispatcher(sublime_plugin.EventListener):
    def on_load(self, view):
        if view.file_name() and os.path.basename(view.file_name()) == DATA_FILE_BASENAME:
            global g_test_view
            g_test_view = view
            current_tests = __import__('tests.%s' % g_testing_what,
                                       globals(), locals(), [], -1)

            bucket = StringIO.StringIO()
            suite = unittest.TestLoader().loadTestsFromModule(getattr(current_tests, g_testing_what))
            unittest.TextTestRunner(stream=bucket, verbosity=1).run(suite)

            v = view.window().new_file()
            edit = v.begin_edit()
            v.insert(edit, 0, bucket.getvalue())
            v.end_edit(edit)
            v.set_scratch(True)

            v.window().focus_view(view)
            view.window().run_command('close')
    
    def on_activated(self, view):
        if view.file_name() and os.path.basename(view.file_name()) == DATA_FILE_BASENAME:
            reset_caret(view)
   
    def on_deactivated(self, view):
        # Make sure we always start with a single selection at BOF.
        if view.file_name() and os.path.basename(view.file_name()) == DATA_FILE_BASENAME:
            reset_caret(view)
