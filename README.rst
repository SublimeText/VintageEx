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

VintageEx aims at full cross-platform compatibility. Presently, most command
will work fine on all three OSes as long as they don't interact with shells.

Installation
============

Download the `latest version`_, put it under ``Installed Packages`` and restart
Sublime Text.

.. _latest version: https://bitbucket.org/guillermooo/vintageex/downloads/VintageEx.sublime-package
.. TOOD: add link to Vintage's help file

VintageEx doesn't replace Vintage. If you want to use vi key bindings, you need
to have installed and enable the Vintage package (shipped with Sublime Text).
VintageEx extends the vi-like functionality available in Sublime Text by adding
a command-line mode that tries to remain close to Vim's. Furthermore, VintageEx
uses commands in the Vintage package, so you will need to enable Vintage if you
want to use VintageEx.

Overview
========

To open the command line, press `:`.

VintageEx offers tab completion of top-level commands, so you can type a letter
and press `Tab` to cycle through available commands.

To see the implemented commands, you can look through `ex_commands.py`.
