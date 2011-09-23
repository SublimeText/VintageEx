import sublime
import sublime_plugin

from collections import namedtuple
import re


# holds info about an ex command
EX_CMD = namedtuple('ex_command', 'name command forced range args')
EX_RANGE_REGEXP = re.compile(r'^(([.$]|(/.*?/|\?.*?\?){1,2}|\d+)([-+]\d+)?)([,;](([.$]|(/.*?/|\?.*?\?){1,2}|\d+)([-+]\d+)?))?')
EX_COMMANDS = {
    ('write', 'w'): {'command': 'ex_write_file', 'args': ['file_name']},
    ('wall', 'wa'): {'command': 'ex_write_all', 'args': []},
    ('pwd', 'pw'): {'command': 'ex_print_working_dir', 'args': []},
}


def find_command(cmd_name):
    names = [x for x in EX_COMMANDS.keys() if x[0].startswith(cmd_name)]
    # unknown command name
    if not names: return None
    # check for matches in known aliases and full names
    full_match = [(x, y) for (x, y) in names if cmd_name in (x, y)]
    if full_match:
        return full_match[0]
    else:
        # partial match, but not a known alias
        return names[0]


def get_cmd_line_range(cmd_line):
    try:
        start, end = EX_RANGE_REGEXP.search(cmd_line).span()
    except AttributeError:
        return None
    return cmd_line[start:end]


def parse_command(cmd):
    # strip :
    cmd_name = cmd[1:]

    range = get_cmd_line_range(cmd_name)
    if range: cmd_name = cmd_name[len(range):]

    cmd_name, _, args = cmd_name.partition(' ')
    args = re.sub(r' {2,}', ' ', args)
    args = args.split(' ')

    bang =False
    if cmd_name.endswith('!'):
        cmd_name = cmd_name[:-1]
        bang = True

    cmd_data = find_command(cmd_name)
    if not cmd_data: return None
    cmd_data = EX_COMMANDS[cmd_data]

    cmd_args = {}
    if cmd_data['args'] and args:
        cmd_args = dict(zip(cmd_data['args'], args))

    return EX_CMD(name=cmd_name,
                    command=cmd_data['command'],
                    forced=bang,
                    range=range,
                    args=cmd_args
                    )


class ViColonInput(sublime_plugin.TextCommand):
    def run(self, edit):
        self.view.window().show_input_panel('', ':', self.on_done, None, None)
    
    def on_done(self, cmd_line):
        ex_cmd = parse_command(cmd_line)
        if ex_cmd:
            self.view.run_command(ex_cmd.command)
        else:
            self.view.window().show_input_panel('', ':', self.on_done, None,
                                                                        None)
