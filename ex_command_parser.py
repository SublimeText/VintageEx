"""a simple 'parser' for :ex commands
"""

from collections import namedtuple
import re
from itertools import takewhile

import ex_error


# Data used to parse strings into ex commands and map them to an actual
# Sublime Text command.
#
#   command
#       The Sublime Text command to be executed.
#   invocations
#       Tuple of regexes representing valid calls for this command.
#   error_on
#       Tuple of error codes. The parsed command is checked for errors based
#       on this information.
#       For example: on_error=(ex_error.ERR_TRAILING_CHARS,) would make the
#       command fail if it was followed by any arguments.
ex_cmd_data = namedtuple('ex_cmd_data', 'command invocations error_on')

# Holds a parsed ex command data.
# TODO: elaborate on params info.
EX_CMD = namedtuple('ex_command', 'name command forced range args parse_errors')

# TODO: Allow escapes in search-based addresses, as in POSTFIX_ADDRESS.
# Address that can only appear in a prefix range (before a command).
PREFIX_ADDRESS = r'[.$%]|(?:/.*?(?<!\\)/|\?.*?(?<!\\)\?){1,2}|[+-]?\d+|[\'][a-zA-Z0-9<>]'
# Address that can only appear after a command.
POSTFIX_ADDRESS = r'[.$]|(?:/.*?(?<!\\)/|\?.*?(?<!\\)\?){1,2}|[+-]?\d+|[\'][a-zA-Z0-9<>]'
ADDRESS_OFFSET = r'[-+]\d+'
ADDRESS_SEPARATOR = r'[,;]'
# Can only appear standalone.
OPENENDED_SEARCH_ADDRESS = r'^[/?].*'

# Can appear as prefix ranges or standalone.
INCOMPLETE_RANGE_SEPARATOR = ','

# Matches ranges preceding commands.
# TODO: +100,-100del should be valid ranges too.
EX_PREFIX_RANGE = re.compile(
                        r'''(?x)
                            # Ranges missing a member, like 10, and ,10
                            ^(?:
                                (?P<incomplete>
                                    (?:
                                        (?P<inc_laddress>%(address)s)
                                        (?P<inc_loffset>%(address_offset)s)*
                                        (?P<suf_alt_separator>%(alt_separator)s)
                                    )|
                                    (?:
                                        (?P<pref_alt_separator>%(alt_separator)s)
                                        (?P<inc_raddress>%(address)s)
                                        (?P<inc_roffset>%(address_offset)s)*
                                    )
                                )|
                                    # A left address...
                                    (?P<laddress>%(address)s)
                                    # with optional offsets...
                                    (?P<loffset>%(address_offset)s)*
                                    # and an optional right address...
                                    (?:
                                       # (which includes the address separator)
                                       (?P<separator>%(address_separator)s)
                                       (?P<raddress>%(address)s)
                                       # with optional offsets.
                                       (?P<roffset>%(address_offset)s)*
                                    )?
                            )
                            # We need to make sure that we match up to the separator, which
                            # comes before the actual ex command. As far as I can tell, ex commands always
                            # start with A-Za-z or !.
                            (?=[a-zA-Z]|!)
                        ''' % {'address':           PREFIX_ADDRESS,
                               'address_separator': ADDRESS_SEPARATOR,
                               'address_offset':    ADDRESS_OFFSET,
                               'alt_separator':     INCOMPLETE_RANGE_SEPARATOR,}
                        )

# Matches ranges that stand alone, without being followed by anything. They
# simply represent an address to move the caret to.
EX_STANDALONE_RANGE = re.compile(
                            r'''(?x)
                                ^(?:
                                    # A full range consisting of...
                                    (?P<incomplete>
                                        (?:
                                            (?P<inc_laddress>%(address)s)
                                            (?P<inc_loffset>%(address_offset)s)*
                                            (?P<suf_alt_separator>%(alt_separator)s)
                                        )|
                                        (?:
                                            (?P<pref_alt_separator>%(alt_separator)s)
                                            (?P<inc_raddress>%(address)s)
                                            (?P<inc_roffset>%(address_offset)s)*
                                        )
                                    )|
                                    (?:
                                        # a left address...
                                        (?P<laddress>%(address)s)
                                        # optionally followed by offsets...
                                        (?P<loffset>%(address_offset)s)*
                                        # and an optional right address...
                                        (?:
                                            # (including the address separator)
                                            (?P<separator>%(address_separator)s)
                                            (?P<raddress>%(address)s)
                                            # and any number of offsets...
                                            (?P<roffset>%(address_offset)s)*
                                        )?
                                    )|
                                    # or an openended search-based address.
                                    (?P<openended>%(openended)s)
                                )$
                            ''' % {'address':           PREFIX_ADDRESS,
                                   'address_separator': ADDRESS_SEPARATOR,
                                   'address_offset':    ADDRESS_OFFSET,
                                   'openended':         OPENENDED_SEARCH_ADDRESS,
                                   'alt_separator':     INCOMPLETE_RANGE_SEPARATOR,}
                            )

# Matches addresses after commands, like :copy10.
#
# ** IMPORTANT **
# Vim's documentation on valid addresses is wrong. For postfixed addresses,
# as in :copy10,20, only the left end is parsed and used; the rest is discarded
# and not even errors are thrown if the right end is bogus, like in :copy10XXX.
EX_POSTFIX_ADDRESS = re.compile(
                        r'''(?x)
                            ^(?P<address>
                                (?:
                                 # A postfix address...
                                 (?:%(address)s)
                                 # optionally followed by offsets...
                                 (?:%(offset)s)*
                                )|
                                # or an openended search-based address.
                                %(openended)s
                            )
                        ''' %  {'address':      POSTFIX_ADDRESS,
                                'offset':       ADDRESS_OFFSET,
                                'openended':    OPENENDED_SEARCH_ADDRESS}
                        )


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
                                   EX_POSTFIX_ADDRESS,
                                ),
                                error_on=(ex_error.ERR_NO_BANG_ALLOWED,
                                          ex_error.ERR_ADDRESS_REQUIRED,)
                                ),
    ('copy', 'co'): ex_cmd_data(
                                command='ex_copy',
                                invocations=(
                                   EX_POSTFIX_ADDRESS,
                                ),
                                error_on=(ex_error.ERR_NO_BANG_ALLOWED,
                                          ex_error.ERR_ADDRESS_REQUIRED,)
                                ),
    ('t', 't'): ex_cmd_data(
                                command='ex_copy',
                                invocations=(
                                   EX_POSTFIX_ADDRESS,
                                ),
                                error_on=(ex_error.ERR_NO_BANG_ALLOWED,
                                          ex_error.ERR_ADDRESS_REQUIRED,)
                                ),
    ('substitute', 's'): ex_cmd_data(
                                command='ex_substitute',
                                invocations=(re.compile(r'(?P<pattern>.+)'),
                                ),
                                error_on=()
                                ),
    ('&&', '&&'): ex_cmd_data(
                                command='ex_double_ampersand',
                                # We don't want to mantain flag values here, so accept anything and
                                # let :substitute handle the values.
                                invocations=(re.compile(r'(?P<flags>.+?)\s*(?P<count>[0-9]+)'),
                                             re.compile(r'\s*(?P<flags>.+?)\s*'),
                                             re.compile(r'\s*(?P<count>[0-9]+)\s*'),
                                             re.compile(r'^$'),
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
    ('cquit', 'cq'): ex_cmd_data(
                                command='ex_cquit',
                                invocations=(),
                                error_on=(ex_error.ERR_TRAILING_CHARS,
                                          ex_error.ERR_NO_RANGE_ALLOWED,
                                          ex_error.ERR_NO_BANG_ALLOWED,)
                                ),
    # TODO: implement all arguments, etc.
    ('xit', 'x'): ex_cmd_data(
                                command='ex_exit',
                                invocations=(),
                                error_on=()
                                ),
    # TODO: implement all arguments, etc.
    ('exit', 'exi'): ex_cmd_data(
                                command='ex_exit',
                                invocations=(),
                                error_on=()
                                ),
    ('only', 'on'): ex_cmd_data(
                                command='ex_only',
                                invocations=(re.compile(r'^$',),
                                ),
                                error_on=(ex_error.ERR_TRAILING_CHARS,
                                          ex_error.ERR_NO_RANGE_ALLOWED,)
                                ),
    (':', ':'): ex_cmd_data(
                        command='ex_goto',
                        invocations=(),
                        error_on=(),
                        ),
    ('!', '!'): ex_cmd_data(
                        command='ex_shell_out',
                        invocations=(
                                re.compile(r'(?P<shell_cmd>.+)$'),
                        ),
                        # FIXME: :!! is a different command to :!
                        error_on=(ex_error.ERR_NO_BANG_ALLOWED,),
                        )
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
    # Make sure we match a range standing alone (not followed by a command).
    return EX_STANDALONE_RANGE.search(cmd_line) and \
                not EX_PREFIX_RANGE.search(cmd_line)


def get_cmd_line_range(cmd_line):
    try:
        start, end = EX_PREFIX_RANGE.search(cmd_line).span()
    except AttributeError:
        return None
    return cmd_line[start:end]


def is_valid_command_name(cmd_name):
    return (cmd_name[0].isalpha() or cmd_name[0] in r"&")


def extract_command_name(cmd_line):
    if cmd_line[0] in ':!':
        return cmd_line[0]
    if cmd_line:
        return ''.join(takewhile(lambda c: is_valid_command_name(c), cmd_line))


def parse_command(cmd):
    cmd_name = cmd.strip()
    if len(cmd_name) > 1:
        cmd_name = cmd_name[1:]
    elif not cmd_name == ':':
        return None


    if is_only_range(cmd_name):
        range_ = cmd_name
        cmd_name = ':'
    else:
        range_ = get_cmd_line_range(cmd_name)
        if range_:
            cmd_name = cmd_name[len(range_):]

    # FIXME: is this needed?
    if not (cmd_name.startswith(('!', ':')) or
            is_valid_command_name(cmd_name[0])):
        return

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
        if err == ex_error.ERR_ADDRESS_REQUIRED and not cmd_args:
            parse_errors.append(ex_error.ERR_ADDRESS_REQUIRED)

    return EX_CMD(name=command,
                    command=cmd_data.command,
                    forced=bang,
                    range=range_,
                    args=cmd_args,
                    parse_errors=parse_errors
                    )
