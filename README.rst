=========
VintageEx
=========

A rendition of Vim's command-line mode for Sublime Text 2.

License
=======

This whole package is distributed under the MIT license (see LICENSE.txt).

Compatibility
=============

* Windows (good)
* Linux (less good)
* OSX (worst)

VintageEx aims at full cross-platform compatibility. Presently, most commands
will work fine on all three OSes as long as they don't interact with shells.

Installation
============

Download the `latest version`_, put it under ``Installed Packages`` and restart
Sublime Text.

.. _latest version: https://bitbucket.org/guillermooo/vintageex/downloads/VintageEx.sublime-package
.. TOOD: add link to Vintage's help file

**VintageEx doesn't replace Vintage**: To use vi key bindings, you need to
enable the `Vintage`_ package (shipped with Sublime Text and *ignored* by default).

.. _Vintage: http://www.sublimetext.com/docs/2/vintage.html

VintageEx extends the vi-like functionality provided py Vintage by adding
a command-line mode that tries to remain close to Vim's.

Also, because VintageEx uses commands in the Vintage package, this package
must be under your ``Packages`` folder with that name. This is mostly important
to keep in mind if you contribute code to Vintage and have deleted the original
package.

Overview
========

To open the command line, press ``:``.

VintageEx offers tab completion of top-level commands, so you can type a letter
and press `Tab` to cycle through available commands.

To see the implemented commands, you can look through ``ex_commands.py``.
