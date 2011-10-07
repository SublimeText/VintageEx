"""a simple 'parser' for :ex commands
"""

from collections import namedtuple
from itertools import takewhile, dropwhile
import re


# holds info about a parsed ex command
EX_CMD = namedtuple('ex_command', 'name command forced range args parse_errors')
# defines an ex command data for later parsing
ex_cmd_data = namedtuple('ex_cmd_data', 'command invocations error_on')

EX_RANGE_REGEXP = re.compile(r'^(:?([.$%]|(:?/.*?/|\?.*?\?){1,2}|\d+|[\'`][a-zA-Z0-9<>])([-+]\d+)?)(([,;])(:?([.$]|(:?/.*?/|\?.*?\?){1,2}|\d+|[\'`][a-zA-Z0-9<>])([-+]\d+)?))?')
EX_ONLY_RANGE_REGEXP = re.compile(r'^(?:([%$.]|\d+|/.*?(?<!\\)/|\?.*?\?)([-+]\d+)*(?:([,;])([%$.]|\d+|/.*?(?<!\\)/|\?.*?\?)([-+]\d+)*)?)|(^[/?].*)$')

ERR_UNWANTED_ARGS = 0
ERR_UNWANTED_BANG = 1
ERR_UNWANTED_RANGE = 2


EX_COMMANDS = {
    ('write', 'w'): ex_cmd_data(
                                command='ex_write_file',
                                invocations=(
                                    re.compile(r'^\s*$'),
                                    re.compile(r'(?P<plusplus_args> *\+\+[a-zA-Z0-9_]+)* *(?P<operator>>>) *(?P<target_redirect>.+)?'),
                                    # fixme: raises an error when it shouldn't
                                    re.compile(r'(?P<plusplus_args> *\+\+[a-zA-Z0-9_]+)* *!(?P<subcmd>.+)'),
                                    re.compile(r'(?P<plusplus_args> *\+\+[a-zA-Z0-9_]+)* *(?P<file_name>.+)?'),
                                ),
                                error_on=()
                                ),
    ('wall', 'wa'): ex_cmd_data(
                                command='ex_write_all',
                                invocations=(),
                                error_on=(ERR_UNWANTED_ARGS,)
                                ),
    ('pwd', 'pw'): ex_cmd_data(
                                command='ex_print_working_dir',
                                invocations=(),
                                error_on=(ERR_UNWANTED_RANGE,
                                            ERR_UNWANTED_BANG,
                                            ERR_UNWANTED_ARGS)
                                ),
    ('buffers', 'buffers'): ex_cmd_data(
                                command='ex_prompt_select_open_file',
                                invocations=(),
                                error_on=(ERR_UNWANTED_ARGS,)
                                ),
    ('files', 'files'): ex_cmd_data(
                                command='ex_prompt_select_open_file',
                                invocations=(),
                                error_on=(ERR_UNWANTED_ARGS,)
                                ),
    ('ls', 'ls'): ex_cmd_data(
                                command='ex_prompt_select_open_file',
                                invocations=(),
                                error_on=(ERR_UNWANTED_ARGS,)
                                ),
    ('map', 'map'): ex_cmd_data(
                                command='ex_map',
                                invocations=(),
                                error_on=()
                                ),
    ('abbreviate', 'ab'): ex_cmd_data(
                                command='ex_abbreviate',
                                invocations=(),
                                error_on=()
                                ),
    ('read', 'r'): ex_cmd_data(
                                command='ex_read_shell_out',
                                invocations=(
                                    # xxx: works more or less by chance. fix the command code
                                    re.compile(r'(?P<plusplus> *\+\+[a-zA-Z0-9_]+)* *(?P<name>.+)'),
                                    re.compile(r' *!(?P<name>.+)'),
                                ),
                                # fixme: add error category for ARGS_REQUIRED
                                error_on=()
                                ),
    ('enew', 'ene'): ex_cmd_data(
                                command='ex_new_file',
                                invocations=(),
                                error_on=(ERR_UNWANTED_ARGS,)
                                ),
    ('ascii', 'as'): ex_cmd_data(
                                command='ex_ascii',
                                invocations=(),
                                error_on=(ERR_UNWANTED_RANGE,
                                            ERR_UNWANTED_BANG,
                                            ERR_UNWANTED_ARGS)
                                ),
    # vim help doesn't say this command takes any args, but it does
    ('file', 'f'): ex_cmd_data(
                                command='ex_file',
                                invocations=(),
                                error_on=(ERR_UNWANTED_RANGE,)
                                ),
    ('move', 'move'): ex_cmd_data(
                                command='ex_move',
                                invocations=(
                                   re.compile(r' *(?P<address>\d+)'),
                                ),
                                error_on=(ERR_UNWANTED_BANG,),
                                ),
    ('copy', 'co'): ex_cmd_data(
                                command='ex_copy',
                                invocations=(
                                   re.compile(r' *(?P<address>\d+)'),
                                ),
                                error_on=(ERR_UNWANTED_BANG,),
                                ),
    ('t', 't'): ex_cmd_data(
                                command='ex_copy',
                                invocations=(
                                   re.compile(r' *(?P<address>\d+)'),
                                ),
                                error_on=(ERR_UNWANTED_BANG,),
                                ),
    ('substitute', 's'): ex_cmd_data(
                                command='ex_substitute',
                                invocations=(re.compile(r'(?P<pattern>.+)'),
                                ),
                                error_on=()
                                ),
    ('shell', 'sh'): ex_cmd_data(
                                command='ex_shell',
                                invocations=(),
                                error_on=(ERR_UNWANTED_RANGE,
                                            ERR_UNWANTED_BANG,
                                            ERR_UNWANTED_ARGS)
                                ),
    ('delete', 'd'): ex_cmd_data(
                                command='ex_delete',
                                invocations=(
                                    re.compile(r' *(?P<register>[a-zA-Z0-9]) *(?P<count>\d+)'),
                                ),
                                error_on=(ERR_UNWANTED_BANG,)
                                ),
    ('global', 'g'): ex_cmd_data(
                                command='ex_global',
                                invocations=(
                                    re.compile(r'(?P<pattern>.+)'),
                                ),
                                error_on=()
                                ),
    ('print', 'p'): ex_cmd_data(
                                command='ex_print',
                                invocations=(
                                    re.compile(r'\s*(?P<count>\d+)?\s*(?P<flags>[l#p]+)?'),
                                ),
                                error_on=(ERR_UNWANTED_BANG,)
                                ),
    ('Print', 'P'): ex_cmd_data(
                                command='ex_print',
                                invocations=(
                                    re.compile(r'\s*(?P<count>\d+)?\s*(?P<flags>[l#p]+)?'),
                                ),
                                error_on=(ERR_UNWANTED_BANG,)
                                ),
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
                        parse_errors=None
                        )

    if cmd_name.startswith('!'):
        cmd_name = '!'
        args = cmd[2:]
        return EX_CMD(name=cmd_name,
                        command=None,
                        forced=False,
                        range=None,
                        args={'shell_cmd': args},
                        parse_errors=None
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

    cmd_args = {}
    for pattern in cmd_data.invocations:
        found_args = pattern.search(args)
        if found_args:
            found_args = found_args.groupdict()
            # get rid of unset arguments so they don't clobber defaults
            found_args = dict((k, v) for k, v in found_args.iteritems()
                                                        if not v is None)
            cmd_args.update(found_args)
            break
    
    parse_errors = []
    for err in cmd_data.error_on:
        if err == ERR_UNWANTED_BANG and bang:
            parse_errors.append('No "!" allowed.')
        if err == ERR_UNWANTED_ARGS and args:
            parse_errors.append('Trailing characters.')
        if err == ERR_UNWANTED_RANGE and range_:
            parse_errors.append('Range not allowed.')

    return EX_CMD(name=command,
                    command=cmd_data.command,
                    forced=bang,
                    range=range_,
                    args=cmd_args,
                    parse_errors=parse_errors
                    )
