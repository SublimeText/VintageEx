import sublime
import sublime_plugin

import os
import subprocess

try:
    import ctypes
except ImportError:
    ctypes = None

import ex_range


def handle_not_implemented():
    sublime.status_message('VintageEx: Not implemented')


def gather_buffer_info(v):
    """gathers data to be displayed by :ls or :buffers
    """
    path = v.file_name()
    if path:
        parent, leaf = os.path.split(path)
        parent = os.path.basename(parent)
        path = os.path.join(parent, leaf)
    else:
        path = v.name() or str(v.buffer_id())
        leaf = v.name() or 'untitled'

    status = [] 
    if not v.file_name():
        status.append("t")
    if v.is_dirty():
        status.append("*")
    if v.is_read_only():
        status.append("r")
    
    if status:
        leaf += ' (%s)' % ', '.join(status)
    return [leaf, path]


def get_region_by_range(view, text_range):
    a, b = ex_range.calculate_range(view, text_range)
    r = sublime.Region(view.text_point(a - 1, 0),
                        view.line(
                            view.text_point(b - 1, 0)).end())    
    return r


def calculate_address(view, text_range):
    """calculates single line address based on a range.
    """
    # doublecheck allowed ranges with vim
    # xxx strip in the parsing phase instead
    a, b = ex_range.calculate_range(view, text_range.strip())
    address = (max(a, b) if all((a, b)) else (a or b)) or 0
    return address - 1


def get_oem_cp():
    codepage = ctypes.windll.kernel32.GetOEMCP()
    return str(codepage)


def get_startup_info():
    # Hide the child process window.
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return startupinfo


class ExGoto(sublime_plugin.TextCommand):
    def run(self, edit, range=''):
        assert range, 'Range required.'
        a, b = ex_range.calculate_range(self.view, range, is_only_range=True)
        target = (max(a, b) if all((a, b)) else (a or b)) or 0
        self.view.run_command('vi_goto_line', {'repeat': target})


class ExShellOut(sublime_plugin.TextCommand):
    def run(self, edit, shell_cmd=''):
        sels = self.view.sel()
        if all([(s.a != s.b) for s in sels]):
            if os.name == 'nt':
                for s in self.view.sel():
                    p = subprocess.Popen(
                                        ['cmd.exe', '/C', shell_cmd],
                                        stdout=subprocess.PIPE,
                                        startupinfo=get_startup_info()
                                        )
                    cp = 'cp' + get_oem_cp()
                    rv = p.communicate()[0].decode(cp)[:-2].strip()
                    self.view.replace(edit, s, rv)
                return
            elif os.name == 'posix':
                for s in self.view.sel():
                    shell = os.path.expandvars("$SHELL")
                    p = subprocess.Popen([shell, '-c', shell_cmd],
                                                        stdout=subprocess.PIPE)
                    self.view.replace(edit, s, p.communicate()[0][:-1])
                return
        elif os.name == 'posix':
            term = os.path.expandvars("$COLORTERM") or \
                                                    os.path.expandvars("$TERM")
            subprocess.Popen([term, '-e',
                    "bash -c \"%s; read -p 'Press RETURN to exit.'\"" %
                                                            shell_cmd]).wait()
            return
        elif os.name == 'nt':
            subprocess.Popen(['cmd.exe', '/c', shell_cmd + '&& pause']).wait()
            return 

        sublime.status_message('VintageEx: Not implemented.')


class ExReadShellOut(sublime_plugin.TextCommand):
    def run(self, edit, range='', name='', plusplus_args='', forced=False):
        # cheat a little bit to get the parsing right:
        #   - forced == True means we need to execute a command
        if forced:
            if os.name == 'posix':
                for s in self.view.sel():
                    shell = os.path.expandvars("$SHELL")
                    p = subprocess.Popen([shell, '-c', name],
                                                        stdout=subprocess.PIPE)
                    self.view.insert(edit, s.begin(), p.communicate()[0][:-1])
            elif os.name == 'nt':
                for s in self.view.sel():
                    p = subprocess.Popen(
                                        ['cmd.exe', '/C', name],
                                        stdout=subprocess.PIPE,
                                        startupinfo=get_startup_info()
                                        )
                    cp = 'cp' + get_oem_cp()
                    rv = p.communicate()[0].decode(cp)[:-2].strip()
                    self.view.insert(edit, s.begin(), rv)
        else:
            # xxx read file "name"
            # we need proper filesystem autocompletion here
            sublime.status_message('VintageEx: Not implemented.')


class ExPromptSelectOpenFile(sublime_plugin.TextCommand):
    def run(self, edit):
        self.file_names = [gather_buffer_info(v)
                                        for v in self.view.window().views()]
        self.view.window().show_quick_panel(self.file_names, self.on_done)

    def on_done(self, idx):
        if idx == -1: return
        # focus the file chosen
        sought_fname = self.file_names[idx]
        for v in self.view.window().views():
            if v.file_name() and v.file_name().endswith(sought_fname[1]):
                self.view.window().focus_view(v)
            # xxx probably all checks should be based on the buffer id
            elif v.buffer_id() == int(sought_fname[1]):
                self.view.window().focus_view(v)


class ExMap(sublime_plugin.TextCommand):
    # do at least something moderately useful: open the user's .sublime-keymap
    # file
    def run(self, edit):
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
    def run(self, edit):
        abbreviations_file = os.path.join(
                                    sublime.packages_path(),
                                    'User/Vintage Abbreviations.sublime-completions'
                                    )
        if not os.path.exists(abbreviations_file):
            with open(abbreviations_file, 'w'):
                pass
        
        self.view.window().run_command('open_file', {'file': abbreviations_file})


class ExPrintWorkingDir(sublime_plugin.TextCommand):
    def run(self, edit):
        sublime.status_message(os.getcwd())


class ExWriteFile(sublime_plugin.TextCommand):
    def run(self, edit,
                range=None,
                forced=False,
                file_name='',
                plusplus_args='',
                operator='',
                target_redirect='',
                subcmd=''):
        appending = operator == '>>'
        # if appending: file_name = kwargs['args_extra']

        if range:
            r = get_region_by_range(self.view, range)
            print locals()
            if file_name and file_name != os.path.basename(
                                                        self.view.file_name()):
                if appending:
                    # xxx open with codecs and append to the file
                    pass
                else:
                    v = self.view.window().new_file()
                    v.set_name(file_name)
                    v_edit = v.begin_edit()
                    v.insert(v_edit, 0, self.view.substr(r))
                    v.end_edit(v_edit)
            elif appending:
                    self.view.insert(edit, self.view.size(),
                                                    '\n' + self.view.substr(r))
            else:
                text = self.view.substr(r) 
                self.view.insert(edit, 0, text)
                self.view.replace(edit, sublime.Region(len(text), 
                                            self.view.size()), '')
            return

        if file_name and file_name != os.path.basename(self.view.file_name()):
            # xxx we should probably save right away
            v = self.view.window().new_file()
            v.insert(edit, 0, self.view.substr(
                                        sublime.Region(0, self.view.size())))
            v.set_name(file_name)
            return
        
        if appending:
            content = self.view.substr(sublime.Region(0, self.view.size()))
            self.view.insert(edit, self.view.size(), '\n' + content)
        
        if self.view.is_dirty():
            self.view.run_command('save')


class ExWriteAll(sublime_plugin.TextCommand):
    def run(self, edit, forced=False):
        for v in self.view.window().views():
            if v.is_dirty():
                v.run_command('save')


class ExNewFile(sublime_plugin.TextCommand):
    def run(self, edit, forced=False):
        self.view.window().run_command('new_file')


class ExAscii(sublime_plugin.TextCommand):
    def run(self, edit, range='', forced=False):
        handle_not_implemented()


class ExFile(sublime_plugin.TextCommand):
    def run(self, edit, forced=False):
        # xxx figure out what the right params are. vim's help seems to be
        # wrong
        if self.view.file_name():
            fname = self.view.file_name()
        else:
            fname = 'untitled' 
        
        attrs = ''
        if self.view.is_read_only():
            attrs = 'readonly' 
        
        if self.view.is_scratch():
            attrs = 'modified'
        
        lines = 'no lines in the buffer'
        if self.view.rowcol(self.view.size())[0]:
            lines = self.view.rowcol(self.view.size())[0] + 1
        
        # fixme: doesn't calculate the buffer's % correctly
        if not isinstance(lines, basestring):
            vr = self.view.visible_region()
            start_row, end_row = self.view.rowcol(vr.begin())[0], \
                                              self.view.rowcol(vr.end())[0]
            mid = (start_row + end_row + 2) / 2
            percent = float(mid) / lines * 100.0
        
        msg = fname
        if attrs:
            msg += " [%s]" % attrs
        if isinstance(lines, basestring):
            msg += " -- %s --"  % lines
        else:
            msg += " %d line(s) --%d%%--" % (lines, int(percent))
        
        sublime.status_message('VintageEx: %s' % msg)


class ExMove(sublime_plugin.TextCommand):
    def run(self, edit, range='.', forced=False, address=''):
        range = range or '.'
        if not address:
            sublime.status_message("VintageEx: Invalid address.") 
            return
        address = calculate_address(self.view, address)

        r = get_region_by_range(self.view, range)
        text = self.view.substr(self.view.line(r)) + '\n'
        dest = self.view.line(self.view.text_point(address, 0)).end() + 1
        self.view.insert(edit, dest, text)
        self.view.replace(edit, self.view.full_line(r), '')


class ExCopy(sublime_plugin.TextCommand):
    def run(self, edit, range='.', forced=False, address=''):
        range = range or '.'
        if not address:
            sublime.status_message("VintageEx: Invalid address.") 
            return
        address = calculate_address(self.view, address)

        r = get_region_by_range(self.view, range)
        text = self.view.substr(self.view.line(r)) + '\n'
        dest = self.view.line(self.view.text_point(address, 0)).end() + 1
        self.view.insert(edit, dest, text)
