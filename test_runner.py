import sublime
import sublime_plugin

import os
import unittest
import StringIO

# import itertools

g_test_view = None


test_suites = {
        'parser': ['vintage_ex_run_parser_tests'],
        'range': ['vintage_ex_run_range_tests'],
        'commands': [],
}
# FIXME: Running multiple test suites breaks them
# test_suites['all'] = list(itertools.chain(*[suite for suite in
                                                # test_suites.itervalues()]))


class VintageExTestRunnerCommander(sublime_plugin.WindowCommand):
    def run(self):
        self.window.show_quick_panel(sorted(test_suites.keys()), self.run_suite)

    def run_suite(self, idx):
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


class VintageExRunRangeTests(sublime_plugin.WindowCommand):
    def run(self):
        p = os.path.join(sublime.packages_path(), 'VintageEx/tests/data/data.txt')
        self.window.open_file(p)


class TestDataDispatcher(sublime_plugin.EventListener):
    def on_load(self, view):
        if os.path.basename(view.file_name()) == 'data.txt':
            global g_test_view
            g_test_view = view
            from tests import test_range

            bucket = StringIO.StringIO()
            suite = unittest.TestLoader().loadTestsFromModule(test_range)
            unittest.TextTestRunner(stream=bucket, verbosity=1).run(suite)

            v = view.window().new_file()
            edit = v.begin_edit()
            v.insert(edit, 0, bucket.getvalue())
            v.end_edit(edit)
            v.set_scratch(True)

            v.window().focus_view(view)
            view.window().run_command('close')
