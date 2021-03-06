import sublime
import sublime_plugin


def plugin_loaded():
    """
    At plugin load, update the scope display for all views that had scopes
    turned on previously.
    """
    settings = sublime.load_settings("ScopeView.sublime-settings")
    restore = settings.get("restore_at_startup", True)

    settings.add_on_change('scope_view', _settings_change)

    for window in sublime.windows():
        for view in window.views():
            if view.settings().get("_display_scopes", False):
                if restore:
                    _display_scope(view)
                else:
                    view.settings().erase("_display_scopes")


def plugin_unloaded():
    """
    At plugin unload, clear any displayed scopes from all views that have them.
    """
    settings = sublime.load_settings("ScopeView.sublime-settings")
    settings.clear_on_change('scope_view')

    for window in sublime.windows():
        for view in window.views():
            view.run_command("clear_scopes")
            view.erase_phantoms("scopes")


def _settings_change():
    """
    Whenever our settings change, redisplay all scopes so that if the location
    setting changes, it's reflected immediately.
    """
    for window in sublime.windows():
        for view in window.views():
            if view.settings().get("_display_scopes", False):
                _display_scope(view)


def _display_scope(view):
    """
    Display the scope of the character under the selection as a phantom,
    optionally also displaying the context stack as well.
    """
    settings = sublime.load_settings("ScopeView.sublime-settings")
    display_scope = settings.get("display_scope", True)
    display_trace = settings.get("display_trace", False) and hasattr(view, "context_backtrace")
    display_at_eof = settings.get("display_at_eof", False)

    if not display_scope and not display_trace:
        return

    if not hasattr(_display_scope, "buffer_table"):
        _display_scope.buffer_table = {}

    # Obtain the phantom set used for this view
    buff_id = view.buffer_id()
    phantoms = _display_scope.buffer_table.get(buff_id, None)
    if phantoms is None:
        phantoms = sublime.PhantomSet(view, "scopes")
        _display_scope.buffer_table[buff_id] = phantoms

    target = view.size() if display_at_eof else view.sel()[0].b
    phantom_region = sublime.Region(view.line(target).a)

    scope_text = ""
    stack_text = ""
    digits_len = 1

    if display_scope:
        scopes = view.scope_name(view.sel()[0].b)
        scope_text = '<div class="scope">%s</div>' % scopes.rstrip().replace(" ", "<br>")

    if display_trace:
        stack = view.context_backtrace(view.sel()[0].b)

        for i, ctx in enumerate(reversed(stack)):
            digits = '%s' % (i + 1)
            digits_len = max(len(digits), digits_len)
            nums = '<span class=nums>%s.</span>' % digits

            if ctx.startswith("anonymous context "):
                ctx = '<em>%s</em>' % ctx
            ctx = '<span class=context>%s</span>' % ctx

            if stack_text:
                stack_text += '\n'
            stack_text += '<div>%s%s<div>' % (nums, ctx)

        stack_text = '<div class="trace">%s</div>' % stack_text
        print(stack_text)

    bg_color = view.style()["background"]

    phantoms.update([
        sublime.Phantom(
            phantom_region,
            """
                <body id="scope_line">
                    <style>
                        div.scope {{
                            margin-top: 0.5rem;
                            border-top: 0.1rem solid color(var(--greenish));
                            background-color: {bg_color};
                        }}
                        div.trace {{
                            margin-top: 0.5rem;
                            border-top: 0.1rem solid color(var(--redish));
                            background-color: {bg_color};
                        }}
                        span.nums {{
                            display: inline-block;
                            text-align: right;
                            width: {digits}em;
                            color: color(var(--foreground) a(0.8))
                        }}
                        span.context {{
                            padding-left: 0.5em;
                        }}
                    </style>
                    {scope}
                    {stack}
                </body>
            """.format(bg_color=bg_color, scope=scope_text, stack=stack_text, digits=digits_len),
            sublime.LAYOUT_BELOW
            )
        ])


class ScopeInputHandler(sublime_plugin.TextInputHandler):
    """
    Prompt the user for a scope selector to match against.
    """
    def __init__(self, initial):
        self.initial = initial.strip()

    def placeholder(self):
        return "scope selector"

    def initial_text(self):
        return self.initial


class ViewScopesCommand(sublime_plugin.TextCommand):
    """
    Find all matches for the given scope selector and add them to a region set
    in the buffer.
    """
    last_scope=""

    def run(self, edit, scope):
        self.last_scope = scope

        matches = self.view.find_by_selector(scope)
        if matches:
            self.view.add_regions("scope_matches", matches, scope,
                                  "dot", sublime.DRAW_NO_FILL)
        else:
            self.view.run_command("clear_scopes")
            sublime.status_message("No matching scopes found")

    def input(self, args):
        if args.get("scope", None) is None:
            return ScopeInputHandler(self.last_scope)

    def input_description(self):
        return "View scopes matching:"


class ClearScopesCommand(sublime_plugin.TextCommand):
    """
    Clear all scopes that might currently be displayed by a previous execution
    of view_scopes.
    """
    def run(self, edit):
        self.view.erase_regions("scope_matches")


class ToggleScopeDisplayCommand(sublime_plugin.TextCommand):
    """
    Toggle the display of the scope under the cursor on and off. Turning the
    display on will immediately update the phantom, while turning it off will
    hide the existing phantom.

    The scope will only be displayed for the first selection caret.
    """
    def run(self, edit):
        display = not self.view.settings().get("_display_scopes", False)
        self.view.settings().set("_display_scopes", display)

        if display:
            _display_scope(self.view)
        else:
            self.view.erase_phantoms("scopes")


class ScopeDisplayListener(sublime_plugin.ViewEventListener):
    """
    For any view that has scope display turned on, update the display whenver
    the selection changes.
    """
    @classmethod
    def is_applicable(cls, settings):
        return settings.get("_display_scopes")

    def on_selection_modified(self):
        _display_scope(self.view)
