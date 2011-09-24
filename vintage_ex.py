import sublime
import sublime_plugin

from collections import namedtuple
import re

from ex_command_parser import parse_command


class ViColonInput(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.window().show_input_panel('', ':', self.on_done, None, None)
    
    def on_done(self, cmd_line):
        ex_cmd = parse_command(cmd_line)
        if ex_cmd and ex_cmd.name and ex_cmd.name.isalpha():
            args = ex_cmd._asdict()
            del args['args']
            args.update(ex_cmd.args)
            self.view.run_command(ex_cmd.command, args)
        elif ex_cmd and ex_cmd.range and ex_cmd.range.isdigit():
            self.view.run_command('vi_goto_line', {'repeat': ex_cmd.range})
        elif ex_cmd and ex_cmd.name == '!':
            self.view.run_command('ex_shell_out', {'args': ex_cmd.args})
        else:
            self.view.window().show_input_panel('', ':', self.on_done, None,
                                                                        None)
            sublime.status_message('VintageEx: unknown command (%s)' % 
                                                                    cmd_line)
