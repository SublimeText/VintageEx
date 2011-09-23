import sublime
import sublime_plugin
import os


class ExPrintWorkingDir(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message(os.getcwd())


class ExWriteFile(sublime_plugin.TextCommand):
    def run(self, edit, file_name='', range=None, **kwargs):
        if file_name and file_name != os.path.basename(self.view.file_name()):
            v = self.view.window().new_file()
            v.set_name(file_name)
            return
        
        if range:
            sublime.status_message('VintageEx: Command not implemented.')
            return

        self.view.run_command('save')


class ExWriteAll(sublime_plugin.TextCommand):
    def run(self, edit):
        for v in self.view.window().views():
            v.run_command('save')
