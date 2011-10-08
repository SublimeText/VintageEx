import sublime
import sublime_plugin

from ex_command_parser import parse_command, EX_COMMANDS


class ViColonInput(sublime_plugin.TextCommand):
    def __init__(self, view):
        sublime_plugin.TextCommand.__init__(self, view)

    def run_(self, args):
        if args:
            if 'event' in args:
                del args['event']
            return self.run(**args)
        return self.run()
        
    def run(self, initial_text=':', cmd_line=''):
        # non-interactive call
        if cmd_line:
            self.on_done(cmd_line)
            return
        v = self.view.window().show_input_panel('', initial_text,
                                                    self.on_done, None, None)
        v.set_syntax_file('Packages/VintageEx/VintageEx Cmdline.tmLanguage')
        v.settings().set('gutter', False)
        v.settings().set('rulers', [])
    
    def on_done(self, cmd_line):
        ex_cmd = parse_command(cmd_line)
        print ex_cmd

        if ex_cmd and ex_cmd.parse_errors:
            sublime.status_message('VintageEx: %s' % ex_cmd.parse_errors[0])
            return
        if ex_cmd and ex_cmd.name:
            if ex_cmd.range:
                ex_cmd.args['range'] = ex_cmd.range
            if ex_cmd.forced:
                ex_cmd.args['forced'] = ex_cmd.forced
            self.view.run_command(ex_cmd.command, ex_cmd.args)
        else:
            sublime.status_message('VintageEx: unknown command (%s)' % 
                                                                    cmd_line)


COMPLETIONS = sorted([x[0] for x in EX_COMMANDS.keys()])


class ExCompletionsProvider(sublime_plugin.EventListener):
    CACHED_COMPLETIONS = []
    CACHED_COMPLETION_PREFIXES = []

    def on_query_completions(self, view, prefix, locations):
        if view.score_selector(0, 'text.excmdline') == 0:
            return []
        
        if len(prefix) + 1 != view.size():
            return []
        
        if prefix and prefix in self.CACHED_COMPLETION_PREFIXES:
            return self.CACHED_COMPLETIONS

        compls = [x for x in COMPLETIONS if x.startswith(prefix)]
        self.CACHED_COMPLETION_PREFIXES = [prefix] + compls
        self.CACHED_COMPLETIONS = zip([prefix] + compls, compls + [prefix])
        return self.CACHED_COMPLETIONS
