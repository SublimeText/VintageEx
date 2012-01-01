"""a simple 'parser' for :ex commands
"""

from collections import namedtuple
import re
from itertools import takewhile

import ex_error


# Defines an ex command. This data is used to parse strings into ex commands.
# More precisely, the invocations element defines possible arguments for the
# corresponding command.
#   
#   command
#       The Sublime Text command to be executed. 
#   invocations
#       Tuple of regexes representing valid calls for this command: arguments,
#       bang, etc.
#   error_on
#       Tuple of error codes. The parsed command is checked for errors based
#       on this information.
#       For example: (ex_error.ERR_TRAILING_CHARS,)
ex_cmd_data = namedtuple('ex_cmd_data', 'command invocations error_on')

# Holds a parsed ex command.
EX_CMD = namedtuple('ex_command', 'name command forced range args parse_errors')

# This regex matches any type of range except open-ended /foo and ?bar
# addresses. These are matched by EX_ONLY_RANGE_REGEXP instead. We don't need
# to match them here, because they are not possible when a range precedes a
# command.
# FIXME: 2,del will be accepted, but I'm not sure what it should do.
EX_RANGE_REGEXP = re.compile(r'''(?x)
        ^(?:
            (?P<laddress>
                %| # % can only appear in left address or on its own
                (?:[.$]|
                (?:/.*?/|\?.*?\?){1,2}|\d+|[\'`][a-zA-Z0-9<>])
            )
                (?P<loffset>[-+]\d+)*
        )
        (?:
            (?P<separator>[,;])
            (?P<raddress>[.$%]|(?:/.*?/|\?.*?\?){1,2}|\d+|[\'`][a-zA-Z0-9<>])
            (?P<roffset>[-+]\d+)*
        )?
    ''')

EX_ONLY_RANGE_REGEXP = re.compile(r'''(?x)
        ^(?:
            (?P<laddress>
                [$.]|
                %$|
                \d+|
                /.*?(?<!\\)/|
                \?.*?\?
            )
                (?P<loffset>[-+]\d+)*
            (?: # optional right address
                (?P<separator>[,;])
                (?P<raddress>
                    [%$.]|
                    \d+|
                    /.*?(?<!\\)/|
                    \?.*?\?
                )
                (?P<roffset>[-+]\d+)*
            )?
        )|
        (?P<openended>^[/?].*)
        ''')

# Almost identical to above, but exclude '%'.
# Note that Vim's help seems to be wrong about valid address. It says '%' is a
# valid address, but in practice it doesn't work.
# FIXME: add proper names like range, laddress, raddress, loffset, roffset
EX_ADDRESS_REGEXP = re.compile(r'''(?x)
                    ^(?P<address>
                        (
                            [$.]| # relative line symbol or...
                            \d+| # absolute line number or...
                            /.*?(?<!\\)/| # forward search, such as :/foo/ or...
                            \?.*?(?<!\\)\? # reverse search, such as :?bar?
                        )
                        ([-+]\d+)* # optional offset, like in :$-10
                        (?: # optional right address
                            ([,;]) # range separator
                                (
                                    # almost identical as above
                                    [%$.]| # % only valid here
                                    \d+|
                                    /.*?(?<!\\)/|
                                    \?.*?(?<!\\)\?
                                )
                                ([-+]\d+)*
                        )?
                    )
                    |
                    (^[/?].*)$ # covers cases like /foo and ?bar
                ''')


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
                                error_on=(ex_error.ERR_TRAILING_CHARS,)
                                ),
    ('pwd', 'pw'): ex_cmd_data(
                                command='ex_print_working_dir',
                                invocations=(),
                                error_on=(ex_error.ERR_NO_RANGE_ALLOWED,
                                          ex_error.ERR_NO_BANG_ALLOWED,
                                          ex_error.ERR_TRAILING_CHARS)
                                ),
    ('buffers', 'buffers'): ex_cmd_data(
                                command='ex_prompt_select_open_file',
                                invocations=(),
                                error_on=(ex_error.ERR_TRAILING_CHARS,)
                                ),
    ('files', 'files'): ex_cmd_data(
                                command='ex_prompt_select_open_file',
                                invocations=(),
                                error_on=(ex_error.ERR_TRAILING_CHARS,)
                                ),
    ('ls', 'ls'): ex_cmd_data(
                                command='ex_prompt_select_open_file',
                                invocations=(),
                                error_on=(ex_error.ERR_TRAILING_CHARS,)
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
    ('quit', 'q'): ex_cmd_data(
                                command='ex_quit',
                                invocations=(),
                                error_on=(ex_error.ERR_TRAILING_CHARS,
                                          ex_error.ERR_NO_RANGE_ALLOWED,)
                                ),
    ('qall', 'qa'): ex_cmd_data(
                                command='ex_quit_all',
                                invocations=(),
                                error_on=(ex_error.ERR_TRAILING_CHARS,)
                                ),
    # TODO: add invocations
    ('wq', 'wq'): ex_cmd_data(
                                command='ex_write_and_quit',
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
                                error_on=(ex_error.ERR_TRAILING_CHARS,)
                                ),
    ('ascii', 'as'): ex_cmd_data(
                                # This command is implemented in Packages/Vintage.
                                command='show_ascii_info',
                                invocations=(),
                                error_on=(ex_error.ERR_NO_RANGE_ALLOWED,
                                          ex_error.ERR_NO_BANG_ALLOWED,
                                          ex_error.ERR_TRAILING_CHARS)
                                ),
    # vim help doesn't say this command takes any args, but it does
    ('file', 'f'): ex_cmd_data(
                                command='ex_file',
                                invocations=(),
                                error_on=(ex_error.ERR_NO_RANGE_ALLOWED,)
                                ),
    ('move', 'move'): ex_cmd_data(
                                command='ex_move',
                                invocations=(
                                   EX_ADDRESS_REGEXP,
                                ),
                                error_on=(ex_error.ERR_NO_BANG_ALLOWED,
                                          ex_error.ERR_INVALID_RANGE,)
                                ),
    ('copy', 'co'): ex_cmd_data(
                                command='ex_copy',
                                invocations=(
                                   EX_ADDRESS_REGEXP,
                                ),
                                error_on=(ex_error.ERR_NO_BANG_ALLOWED,
                                          ex_error.ERR_INVALID_RANGE,)
                                ),
    ('t', 't'): ex_cmd_data(
                                command='ex_copy',
                                invocations=(
                                   EX_ADDRESS_REGEXP,
                                ),
                                error_on=(ex_error.ERR_NO_BANG_ALLOWED,
                                          ex_error.ERR_INVALID_RANGE,)
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
                                error_on=(ex_error.ERR_NO_RANGE_ALLOWED,
                                          ex_error.ERR_NO_BANG_ALLOWED,
                                          ex_error.ERR_TRAILING_CHARS)
                                ),
    ('delete', 'd'): ex_cmd_data(
                                command='ex_delete',
                                invocations=(
                                    re.compile(r' *(?P<register>[a-zA-Z0-9])? *(?P<count>\d+)?'),
                                ),
                                error_on=(ex_error.ERR_NO_BANG_ALLOWED,)
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
                                error_on=(ex_error.ERR_NO_BANG_ALLOWED,)
                                ),
    ('Print', 'P'): ex_cmd_data(
                                command='ex_print',
                                invocations=(
                                    re.compile(r'\s*(?P<count>\d+)?\s*(?P<flags>[l#p]+)?'),
                                ),
                                error_on=(ex_error.ERR_NO_BANG_ALLOWED,)
                                ),
    ('browse', 'bro'): ex_cmd_data(
                                command='ex_browse',
                                invocations=(),
                                error_on=(ex_error.ERR_NO_BANG_ALLOWED,
                                          ex_error.ERR_NO_RANGE_ALLOWED,
                                          ex_error.ERR_TRAILING_CHARS,)
                                ),
    ('edit', 'e'): ex_cmd_data(
                                command='ex_edit',
                                invocations=(re.compile(r"^$"),),
                                error_on=()
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


def parse_command(cmd):
    # strip :
    cmd_name = cmd[1:]

    # Do nothing if the command's just ":".
    if not cmd_name:
        return EX_CMD(
                name='NOP',
                command='ex_nop',
                forced=False,
                range='.',
                args={},
                parse_errors=None
        )
    
    # first the odd commands
    if is_only_range(cmd_name):
        return EX_CMD(name=':',
                        command='ex_goto',
                        forced=False,
                        range=cmd_name,
                        args={},
                        parse_errors=None
                        )

    range_ = get_cmd_line_range(cmd_name)
    if range_:
        cmd_name = cmd_name[len(range_):]

    if not (cmd_name.startswith('!') or cmd_name[0].isalpha()):
        return
    
    if cmd_name.startswith('!'):
        args = cmd_name[1:]
        cmd_name = '!'
        return EX_CMD(name=cmd_name,
                        command='ex_shell_out',
                        forced=False,
                        range=range_,
                        args={'shell_cmd': args},
                        parse_errors=None
                        )

    command = extract_command_name(cmd_name)
    args = cmd_name[len(command):]

    bang = args.startswith('!')
    if bang: 
        args = args[1:]

    cmd_data = find_command(command)
    if not cmd_data:
        return
    cmd_data = EX_COMMANDS[cmd_data]

    cmd_args = {}
    for pattern in cmd_data.invocations:
        found_args = pattern.search(args)
        if found_args:
            found_args = found_args.groupdict()
            # get rid of unset arguments so they don't clobber defaults
            found_args = dict((k, v) for k, v in found_args.iteritems()
                                                        if v is not None)
            cmd_args.update(found_args)
            break

    parse_errors = []
    for err in cmd_data.error_on:
        if err == ex_error.ERR_NO_BANG_ALLOWED and bang:
            parse_errors.append(ex_error.ERR_NO_BANG_ALLOWED)
        if err == ex_error.ERR_TRAILING_CHARS and args:
            parse_errors.append(ex_error.ERR_TRAILING_CHARS)
        if err == ex_error.ERR_NO_RANGE_ALLOWED and range_:
            parse_errors.append(ex_error.ERR_NO_RANGE_ALLOWED)
        if err == ex_error.ERR_INVALID_RANGE and not cmd_args:
            parse_errors.append(ex_error.ERR_INVALID_RANGE)

    return EX_CMD(name=command,
                    command=cmd_data.command,
                    forced=bang,
                    range=range_,
                    args=cmd_args,
                    parse_errors=parse_errors
                    )
