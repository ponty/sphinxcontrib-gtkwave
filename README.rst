This Sphinx_ 1.0 extension executes GTKWave_ during the build step and
includes its screenshot into the documentation.
GTKWave_ can display wave files like VCD_ (value change dump).

Links:
 * home: https://github.com/ponty/sphinxcontrib-gtkwave
 * documentation: http://ponty.github.com/sphinxcontrib-gtkwave

Features
-------------
 - development on linux
 
Known problems
------------------
 - Python 3 is not supported
 - PDF output is not perfect
 - no unittests

Basic usage
------------------
::

    .. gtkwave:: docs/gtkwave_output.vcd
    
How it works
------------------

This is a workaround, there is no image export in GTKWave_

#. start Xvfb headless X server using pyvirtualdisplay_
#. redirect GTKWave_ display to Xvfb server by setting $DISPLAY variable.
#. start GTKWave_ with VCD file. Options are set on command-line and in temporary rc file
#. temporary tcl script will set time interval and select all signals 
#. wait until GTKWave_ is displayed
#. take screenshot by pyscreenshot_ which needs scrot.
#. image is processed: toolbar, scrollbar and empty space are removed
#. use ``.. image::`` directive to display image
 

Installation
------------------

General
^^^^^^^^^^^

 * install GTKWave_
 * install Xvfb_ and Xephyr_
 * install PIL_
 * install scrot
 * install pip_
 * install the program::

    # as root
    pip install sphinxcontrib-gtkwave


Ubuntu
^^^^^^^^^^^
::

    sudo apt-get install gtkwave
    sudo apt-get install python-pip
    sudo apt-get install scrot
    sudo apt-get install xvfb
    sudo apt-get install xserver-xephyr
    sudo apt-get install python-imaging
    sudo pip install sphinxcontrib-gtkwave


Uninstall
^^^^^^^^^^^
::

    # as root
    pip uninstall sphinxcontrib-gtkwave


.. _Sphinx: http://sphinx.pocoo.org/latest
.. _`sphinx-contrib`: http://bitbucket.org/birkenfeld/sphinx-contrib
.. _setuptools: http://peak.telecommunity.com/DevCenter/EasyInstall
.. _pip: http://pip.openplans.org/
.. _Xvfb: http://en.wikipedia.org/wiki/Xvfb
.. _Xephyr: http://en.wikipedia.org/wiki/Xephyr
.. _PIL: http://www.pythonware.com/library/pil/
.. _pyscreenshot: https://github.com/ponty/pyscreenshot
.. _pyvirtualdisplay: https://github.com/ponty/PyVirtualDisplay
.. _gtkwave: http://gtkwave.sourceforge.net/
.. _vcd: http://en.wikipedia.org/wiki/Value_change_dump

