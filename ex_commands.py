import sublime
import sublime_plugin
import os


class ExPrintWorkingDir(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message(os.getcwd())


class ExWriteFile(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.run_command('save')


class ExWriteAll(sublime_plugin.TextCommand):
    def run(self, edit):
        for v in self.view.window().views():
            v.run_command('save')
