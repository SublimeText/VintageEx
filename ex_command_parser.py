"""a simple 'parser' for :ex commands
"""


from collections import namedtuple
from itertools import takewhile
import re


# holds info about an ex command
EX_CMD = namedtuple('ex_command', 'name command forced range plusplus_args plus_args args cmd_arg args_extra')
ex_cmd_data = namedtuple('ex_cmd_data', 'command args')
EX_RANGE_REGEXP = re.compile(r'^(:?([.$%]|(:?/.*?/|\?.*?\?){1,2}|\d+)([-+]\d+)?)(([,;])(:?([.$]|(:?/.*?/|\?.*?\?){1,2}|\d+)([-+]\d+)?))?')
EX_ONLY_RANGE_REGEXP = re.compile(r'^(?:([%$.]|\d+|/.*?(?<!\\)/|\?.*?\?)([-+]\d+)*(?:([,;])([%$.]|\d+|/.*?(?<!\\)/|\?.*?\?)([-+]\d+)*)?)|(^[/?].*)$')


EX_COMMANDS = {
    ('write', 'w'): ex_cmd_data(
                                command='ex_write_file',
                                args=['file_name']),
    ('wall', 'wa'): ex_cmd_data(
                                command='ex_write_all',
                                args=[]),
    ('wall', 'wa'): ex_cmd_data(
                                command='ex_write_all',
                                args=[]),
    ('pwd', 'pw'): ex_cmd_data(
                                command='ex_print_working_dir',
                                args=[]),
    ('buffers', 'buffers'): ex_cmd_data(
                                command='ex_prompt_select_open_file',
                                args=[]),
    ('ls', 'ls'): ex_cmd_data(
                                command='ex_prompt_select_open_file',
                                args=[]),
    ('map', 'map'): ex_cmd_data(
                                command='ex_map',
                                args=[]),
    ('abbreviate', 'ab'): ex_cmd_data(
                                command='ex_abbreviate',
                                args=[]),
    ('read', 'r'): ex_cmd_data(
                                command='ex_read_shell_out',
                                args=['shell_cmd']),
    ('enew', 'ene'): ex_cmd_data(
                                command='ex_new_file',
                                args=['']),
}


def find_command(cmd_name):
    partial_matches = [name for name in EX_COMMANDS.keys()
                                            if name[0].startswith(cmd_name)]
    if not partial_matches: return None
    full_match = [(ln, sh) for (ln, sh) in partial_matches
                                                if cmd_name in (ln, sh)]
    if full_match:
        return full_match[0]
    else:
        return partial_matches[0]


def is_only_range(cmd_line):
    try:
        return EX_ONLY_RANGE_REGEXP.search(cmd_line) and \
                    EX_RANGE_REGEXP.search(cmd_line).span()[1] == len(cmd_line)
    except AttributeError:
        return EX_ONLY_RANGE_REGEXP.search(cmd_line)


def get_cmd_line_range(cmd_line):
    try:
        start, end = EX_RANGE_REGEXP.search(cmd_line).span()
    except AttributeError:
        return None
    return cmd_line[start:end]


def extract_command_name(cmd_line):
    return ''.join(takewhile(lambda c: c.isalpha(), cmd_line))


def extract_args(cmd_line):
    plus_args = []
    plusplus_args = []
    cmd_args = []
    args = []
    for i, token in enumerate(cmd_line.split(' ')):
        if token and token.startswith('++'):
            plusplus_args.append(token)
        elif token and token.startswith('+'):
            plus_args = cmd_line.split(' ')[i:]
            break
        elif not token.startswith('!'):
            args.append(token)
        else:
            cmd_args = cmd_line.split(' ')[i:]
            break
    
    return ' '.join(plus_args), ' '.join(plusplus_args), \
                                    ' '.join(args).strip(), ' '.join(cmd_args)


def parse_command(cmd):
    # strip :
    cmd_name = cmd[1:]

    # first the odd commands
    if is_only_range(cmd_name):
        return EX_CMD(name=':',
                        command='ex_goto',
                        forced=False,
                        range=cmd_name,
                        args='',
                        args_extra='',
                        plusplus_args='',
                        plus_args='',
                        cmd_arg=''
                        )

    if cmd_name.startswith('!'):
        cmd_name = '!'
        args = cmd[2:]
        return EX_CMD(name=cmd_name,
                        command=None,
                        forced=False,
                        range=None,
                        args=args,
                        args_extra='',
                        plusplus_args='',
                        plus_args='',
                        cmd_arg=''
                        )

    range_ = get_cmd_line_range(cmd_name)
    if range_: cmd_name = cmd_name[len(range_):]

    command = extract_command_name(cmd_name)
    args = cmd_name[len(command):]

    bang = False
    if args.startswith('!'):
        bang = True
        args = args[1:]

    plus_args, plusplus_args, args, cmd_arg = extract_args(args)

    cmd_data = find_command(command)
    if not cmd_data: return None
    cmd_data = EX_COMMANDS[cmd_data]

    cmd_args = {}
    args = args.split(' ')
    cmd_args_extra = ''
    if cmd_data.args and args:
        cmd_args = dict(zip(cmd_data.args, args))
    if len(args) > len(cmd_data.args):
        cmd_args['_extra'] = ' '.join(args[len(cmd_data.args):])

    return EX_CMD(name=command,
                    command=cmd_data.command,
                    forced=bang,
                    range=range_,
                    args=cmd_args,
                    args_extra=cmd_args_extra,
                    plusplus_args=plusplus_args,
                    plus_args=plus_args,
                    cmd_arg=cmd_arg 
                    )
