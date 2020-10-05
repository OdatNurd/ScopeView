# ScopeView

This is a simple package that allows you to display the syntax scope of the
current character as well as visualizing the parts of the buffer that match a
particular scope selector.

This is an enhanced version of the plugin used in the [Scopes and Scope Selectors](https://youtu.be/37pcH9aQ76I)
video on my [YouTube Channel](https://youtube.com/c/OdatNurd).

See that video for a demonstration on what this plugin does.

## Installation

You can manually install this as a package by cloning it directly into your
`Packages` folder. Alternatively, you can also use the `Package Control: Add Repository`
command from the command palette and give it the URL of this repository, which
will make the package available via Package Control.


### ScopeView: Toggle Scope Display

Toggles display of the scope under the cursor on and off for the currently
active `view`. The display of the scope is controlled by the following settings:

* `display_scope` controls whether the scope of the character under the cursor
is displayed or not. The default is to have this turned on.

* `display_trace` controls whether the context stack for the character under
the cursor is displayed or not. This allows you to inspect how the syntax got
to the point where it applied the scope that it did. This requires build 4087
or greater of Sublime.

* `restore_at_startup` controls whether or not views that had this turned on
when you quit Sublime still have it turned on when you restart Sublime. The
default is to have this turned on.

* `display_at_eof` controls whether the inline display appears at the bottom of
the file or on the line under the first caret in the file. The default for this
is the line under the file, but for clarity in the YouTube video this was turned
on.

### ScopeView: View Scopes (alt+shift+s)

Prompts you for a scope selector, and then marks the content of the file to show
what text (if any) matches that scope. If nothing matches, the status bar will
tell you (and nothing else exciting happens).

Scopes are displayed in the color of the first matching scope (as determined by
your color scheme). Matched scopes do not persist if you close and reopen the
file or quit and restart Sublime.

### ScopeView: Clear Scopes (alt+shift+c)

Clears away the marked scopes that were previously added, if any. This is safe
(and does nothing) if no scopes are being displayed.