"""a simple 'parser' for :ex commands
"""


from collections import namedtuple
from itertools import takewhile, dropwhile
import re


# holds info about a parsed ex command
EX_CMD = namedtuple('ex_command', 'name command forced range args')
# defines an ex command data for later parsing
ex_cmd_data = namedtuple('ex_cmd_data', 'command args wants_plusplus wants_plus args_parser')

EX_RANGE_REGEXP = re.compile(r'^(:?([.$%]|(:?/.*?/|\?.*?\?){1,2}|\d+|[\'`][a-zA-Z0-9<>])([-+]\d+)?)(([,;])(:?([.$]|(:?/.*?/|\?.*?\?){1,2}|\d+|[\'`][a-zA-Z0-9<>])([-+]\d+)?))?')
EX_ONLY_RANGE_REGEXP = re.compile(r'^(?:([%$.]|\d+|/.*?(?<!\\)/|\?.*?\?)([-+]\d+)*(?:([,;])([%$.]|\d+|/.*?(?<!\\)/|\?.*?\?)([-+]\d+)*)?)|(^[/?].*)$')


EX_COMMANDS = {
    ('write', 'w'): ex_cmd_data(
                                command='ex_write_file',
                                args=[],
                                wants_plusplus=True,
                                wants_plus=True,
                                args_parser='extract_write_args'),
    ('wall', 'wa'): ex_cmd_data(
                                command='ex_write_all',
                                args=[],
                                wants_plusplus=False,
                                wants_plus=False,
                                args_parser=None),
    ('pwd', 'pw'): ex_cmd_data(
                                command='ex_print_working_dir',
                                args=[],
                                wants_plusplus=False,
                                wants_plus=False,
                                args_parser=None),
    ('buffers', 'buffers'): ex_cmd_data(
                                command='ex_prompt_select_open_file',
                                args=[],
                                wants_plusplus=False,
                                wants_plus=False,
                                args_parser=None),
    ('files', 'files'): ex_cmd_data(
                                command='ex_prompt_select_open_file',
                                args=[],
                                wants_plusplus=False,
                                wants_plus=False,
                                args_parser=None),
    ('ls', 'ls'): ex_cmd_data(
                                command='ex_prompt_select_open_file',
                                args=[],
                                wants_plusplus=False,
                                wants_plus=False,
                                args_parser=None),
    ('map', 'map'): ex_cmd_data(
                                command='ex_map',
                                args=[],
                                wants_plusplus=False,
                                wants_plus=False,
                                args_parser=None),
    ('abbreviate', 'ab'): ex_cmd_data(
                                command='ex_abbreviate',
                                args=[],
                                wants_plusplus=False,
                                wants_plus=False,
                                args_parser=None),
    ('read', 'r'): ex_cmd_data(
                                command='ex_read_shell_out',
                                args=['name'],
                                wants_plusplus=True,
                                wants_plus=False,
                                args_parser=None),
    ('enew', 'ene'): ex_cmd_data(
                                command='ex_new_file',
                                args=[],
                                wants_plusplus=True,
                                wants_plus=True,
                                args_parser=None),
    ('ascii', 'as'): ex_cmd_data(
                                command='ex_ascii',
                                args=[],
                                wants_plusplus=False,
                                wants_plus=False,
                                args_parser=None),
    ('file', 'f'): ex_cmd_data(
                                command='ex_file',
                                args=[],
                                wants_plusplus=False,
                                wants_plus=False,
                                args_parser=None),
    ('move', 'move'): ex_cmd_data(
                                command='ex_move',
                                args=['address'],
                                wants_plusplus=False,
                                wants_plus=False,
                                args_parser=None),
    ('copy', 'co'): ex_cmd_data(
                                command='ex_copy',
                                args=['address'],
                                wants_plusplus=False,
                                wants_plus=False,
                                args_parser=None),
    ('t', 't'): ex_cmd_data(
                                command='ex_copy',
                                args=['address'],
                                wants_plusplus=False,
                                wants_plus=False,
                                args_parser=None),
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


def extract_write_args(args):
    if '>>' in args:
        left, operator, right = args.partition('>>')
    elif '!' in args and not ('! ' in args or args.endswith('!')):
        left, operator, right = args.partition('!')
    else:
        left = args
        operator = None
        right = ''

    if operator:
        if operator == '!':
            return {
                'operator': operator,
                'plusplus_args': left,
                'subcmd': right
            }
        else:
            return {
                'operator': operator,
                'plusplus_args': left,
                'target_redirect': right
            }
    
    left_tokens = left.split(' ')
    return {'file_name': ' '.join(dropwhile(lambda x: x.startswith('++') or
                                not x, left_tokens)),
            'plusplus_args': ' '.join(takewhile(lambda x: x.startswith('++')
                                    or not x, left_tokens))
    }


def extract_args(cmd_line):
    plus_args = []
    plusplus_args = []
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
            raise RuntimeError("Unexpected condition.")
    
    return ' '.join(plus_args), ' '.join(plusplus_args), \
                                    ' '.join(args).strip()


def parse_command(cmd):
    # strip :
    cmd_name = cmd[1:]

    # first the odd commands
    if is_only_range(cmd_name):
        return EX_CMD(name=':',
                        command='ex_goto',
                        forced=False,
                        range=cmd_name,
                        args={},
                        )

    if cmd_name.startswith('!'):
        cmd_name = '!'
        args = cmd[2:]
        return EX_CMD(name=cmd_name,
                        command=None,
                        forced=False,
                        range=None,
                        args={'shell_cmd': args},
                        )

    range_ = get_cmd_line_range(cmd_name)
    if range_: cmd_name = cmd_name[len(range_):]

    command = extract_command_name(cmd_name)
    args = cmd_name[len(command):]

    bang = False
    if args.startswith('!'):
        bang = True
        args = args[1:]

    cmd_data = find_command(command)
    if not cmd_data: return None
    cmd_data = EX_COMMANDS[cmd_data]

    if cmd_data.wants_plusplus or cmd_data.wants_plus:
        plus_args, plusplus_args, args = extract_args(args)
    else:
        plus_args = '',
        plusplus_args= '',

    cmd_args = {}
    if cmd_data.wants_plus:
        cmd_args['plus_args'] = plus_args
    if cmd_data.wants_plusplus:
        cmd_args['plusplus_args'] = plusplus_args
        
    if cmd_data.args_parser:
        func = globals()[cmd_data.args_parser]
        cmd_args = func(args)
    else:
        if cmd_data.args and args:
            cmd_args = dict(zip(cmd_data.args, [args]))

    return EX_CMD(name=command,
                    command=cmd_data.command,
                    forced=bang,
                    range=range_,
                    args=cmd_args,
                    )
