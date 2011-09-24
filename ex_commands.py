import sublime
import sublime_plugin

import os
import subprocess

import ex_range


class ExShellOut(sublime_plugin.TextCommand):
    def run(self, edit, args='', **kwargs):
        term = os.path.expandvars("$COLORTERM")
        if ' ' in args:
            args = "'" + args + "'"
        subprocess.Popen([term, '-e', "bash -c %s;read" % args])


class ExReadShellOut(sublime_plugin.TextCommand):
    def run(self, edit, shell_cmd='', forced=False, **kwargs):
        if forced:
            shell = os.path.expandvars("$SHELL")
            p = subprocess.Popen([shell, '-c', shell_cmd],
                                                stdout=subprocess.PIPE)
            self.view.insert(edit, self.view.sel()[0].begin(),
                                                        p.communicate()[0])


class ExPromptSelectOpenFile(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        self.file_names = [list(os.path.split(v.file_name()))[::-1]
                                        for v in self.view.window().views()]
        self.view.window().show_quick_panel(self.file_names, self.on_done)

    def on_done(self, idx):
        sought_fname = self.file_names[idx]
        for v in self.view.window().views():
            if v.file_name == sought_fname:
                self.view.window().focus(v)


class ExMap(sublime_plugin.TextCommand):
    # do at least something moderately useful: open the user's .sublime-keymap
    # file
    def run(self, edit, **kwargs):
        if os.name == 'nt':
            plat = 'Windows'
        elif os.name == 'posix':
            plat = 'Linux'
        else:
            plat = 'OSX'
        self.view.window().run_command('open_file', {'file':
                                        '${packages}/User/Default (%s).sublime-keymap' % plat})        


class ExAbbreviate(sublime_plugin.TextCommand):
    # for them moment, just open a completions file.
    def run(self, edit, **kwargs):
        abbreviations_file = os.path.join(
                                    sublime.packages_path(),
                                    'User/Vintage Abbreviations.sublime-completions'
                                    )
        if not os.path.exists(abbreviations_file):
            with open(abbreviations_file, 'w'):
                pass
        
        self.view.window().run_command('open_file', {'file': abbreviations_file})


class ExPrintWorkingDir(sublime_plugin.TextCommand):
    def run(self, edit, **kwargs):
        sublime.status_message(os.getcwd())


class ExWriteFile(sublime_plugin.TextCommand):
    def run(self, edit, file_name='', range=None, **kwargs):
        if range:
            a,b = ex_range.calculate_range(self.view, range)
            if file_name and file_name != os.path.basename(
                                                        self.view.file_name()):
                v = self.view.window().new_file()
                v.set_name(file_name)
                # get lines a,b
                r = sublime.Region(self.view.text_point(a - 1, 0),
                                    self.view.line(
                                        self.view.text_point(b - 1, 0)).end())
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
    def run(self, edit, **kwargs):
        for v in self.view.window().views():
            v.run_command('save')
