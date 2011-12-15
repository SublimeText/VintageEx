import plat
import plat.linux
import plat.windows


def run_and_wait(cmd):
    if plat.HOST_PLATFORM == plat.WINDOWS:
        plat.windows.run_and_wait(cmd)   
    elif plat.HOST_PLATFORM == plat.LINUX:
        plat.linux.run_and_wait(cmd)
    else:
        raise NotImplementedError


def filter_thru_shell(view, regions, cmd):
    try:
        # XXX: make this a ShellFilter class instead
        edit = view.begin_edit()
        if plat.HOST_PLATFORM == plat.WINDOWS:
            filter_func = plat.windows.filter_region
        elif plat.HOST_PLATFORM == plat.LINUX:
            filter_func = plat.linux.filter_region
        else:
            raise NotImplementedError

        for r in reversed(regions):
            rv = filter_func(view.substr(r), cmd)
            view.replace(edit, r, rv)
    finally:
        view.end_edit(edit)
