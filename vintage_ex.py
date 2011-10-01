import sublime
import sublime_plugin

from ex_command_parser import parse_command


class ViColonInput(sublime_plugin.TextCommand):
    def __init__(self, view):
        sublime_plugin.TextCommand.__init__(self, view)

    def run_(self, args):
        if args:
            if 'event' in args:
                del args['event']
            return self.run(**args)
        return self.run()
        
    def run(self):
        self.view.window().show_input_panel('', ':', self.on_done, None, None)
    
    def on_done(self, cmd_line):
        ex_cmd = parse_command(cmd_line)
        if ex_cmd and ex_cmd.name and (ex_cmd.name.isalpha()
                                                    or ex_cmd.name == ':'):
            ex_cmd.args['range'] = ex_cmd.range
            self.view.run_command(ex_cmd.command, ex_cmd.args)
        elif ex_cmd and ex_cmd.name == '!':
            self.view.run_command('ex_shell_out', {'args': ex_cmd.args})
        else:
            self.view.window().show_input_panel('', ':', self.on_done, None,
                                                                        None)
            sublime.status_message('VintageEx: unknown command (%s)' % 
                                                                    cmd_line)
