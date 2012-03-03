import os
import subprocess


def run_and_wait(cmd):
    term = os.path.expandvars("$COLORTERM") or os.path.expandvars("$TERM")
    subprocess.Popen([
            term, '-e', 
            "bash -c \"%s; read -p 'Press RETURN to exit.'\"" % cmd]).wait()


def filter_region(text, command):
    shell = os.path.expandvars("$SHELL")
    p = subprocess.Popen([shell, '-c', 'echo "%s" | %s' % (text, command)],
                         stdout=subprocess.PIPE)
    return p.communicate()[0][:-1]
