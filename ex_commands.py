import sublime
import sublime_plugin
import os

import ex_range


class ExPrintWorkingDir(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message(os.getcwd())


class ExWriteFile(sublime_plugin.TextCommand):
    def run(self, edit, file_name='', range=None, **kwargs):
        if range:
            a,b = ex_range.calculate_range(self.view, range)
            if file_name and file_name != os.path.basename(self.view.file_name()):
                v = self.view.window().new_file()
                v.set_name(file_name)
                # get lines a,b
                r = sublime.Region(self.view.text_point(a, 0),
                                    self.view.line(
                                            self.view.text_point(b, 0)).end())
                v_edit = v.begin_edit()
                v.insert(v_edit, 0, self.view.substr(r))
                v.end_edit(v_edit)
                return

        if file_name and file_name != os.path.basename(self.view.file_name()):
            v = self.view.window().new_file()
            v.set_name(file_name)
            return
        
        self.view.run_command('save')


class ExWriteAll(sublime_plugin.TextCommand):
    def run(self, edit):
        for v in self.view.window().views():
            v.run_command('save')
