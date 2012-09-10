# TODO(guillermooo): All of this functionality, along with key bindings, rather
# belongs in Vintage, but we need to extract the necessary functions out of
# VintageEx first. This is a temporary solution.

import sublime
import sublime_plugin

import ex_location


class SearchImpl(object):
    last_term = ""
    def __init__(self, view, cmd):
        if not cmd:
            return
        self.view = view
        self.reversed = cmd.startswith("?")
        if not cmd.startswith(("?", "/")):
            cmd = "/" + cmd
        if len(cmd) == 1 and SearchImpl.last_term:
            cmd += SearchImpl.last_term
        elif not cmd:
            return
        self.cmd = cmd[1:]

    def search(self):
        if not getattr(self, "cmd", None):
            return
        SearchImpl.last_term = self.cmd
        sel = self.view.sel()[0]

        next_match = None
        if self.reversed:
            current_line = self.view.line(self.view.sel()[0])
            left_side = sublime.Region(current_line.begin(), self.view.sel()[0].begin())
            if ex_location.search_in_range(self.view, self.cmd, left_side.begin(), left_side.end()):
                next_match = ex_location.find_last_match(self.view, self.cmd, left_side.begin(), left_side.end())
            else:
                line_nr = ex_location.reverse_search(self.view, self.cmd,
                                                end=current_line.begin() - 1)
                if line_nr:
                    pt = self.view.text_point(line_nr - 1, 0)
                    next_match = self.view.find(self.cmd, pt)
        else:
            next_match = self.view.find(self.cmd, sel.end())
        if next_match:
            self.view.sel().clear()
            self.view.sel().add(next_match)
            self.view.show(next_match)
        else:
            sublime.status_message("VintageEx: Could not find:" + self.cmd)


class ViRepeatSearchBackward(sublime_plugin.TextCommand):
   def run(self, edit):
       SearchImpl(self.view, "?" + SearchImpl.last_term).search()


class ViRepeatSearchForward(sublime_plugin.TextCommand):
    def run(self, edit):
        SearchImpl(self.view, SearchImpl.last_term).search()


class ViSearch(sublime_plugin.TextCommand):
   def run(self, edit, initial_text=""):
       self.view.window().show_input_panel("", initial_text, self.on_done, None, None)

   def on_done(self, s):
        SearchImpl(self.view, s).search()
