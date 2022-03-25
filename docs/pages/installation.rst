==============
Installation
==============


**erdpy** is currently available in Linux and MacOS. Some of its feature as may work on Windows. However, we do not recommend or support its usage on Windows at the moment. 

Before installing **erdpy**, make sure you have a working Python3 environment.
* For Linux or MacOS, version 3.8 or later is recommended.




Smart contract written in **C** require the `ncurses` library routines for compiling. To install the library, run the following command:

.. code-block:: bash

   $sudo apt install libncurses5

Install using `erpdy-up` (recommended)
======================================

To install **erdpy** using the `erdpy-up` installation script, run the following command on your terminal:

.. code-block:: python

   wget -O erdpy-up.py https://raw.githubusercontent.com/ElrondNetwork/elrond-sdk-erdpy/master/erdpy-up.py
   python3.8 erdpy-up.py   

This command creates a python virtual environment (based on the ``venv``) in ``~/elrondsdk/erdpy-venv`` and also includes ``~/elrondsdk`` in your ``$PATH`` variable (by editing the appropriate ``.profile`` file).

Troubleshooting and other notes
===============================

If you are running `Ubuntu 20.04`, you may run into an ``invalid command 'bdist_wheel'`` error. Run the following command then retry ``erdpy-up`` command to clear the error:

.. code-block:: python

    pip3 install wheel
    python3 erdpy-up.py

On MacOS, you can switch to Python 3.8:

.. code-block:: 

    brew info python@3.8
    brew unlink python
    brew link --force python@3.8
    python3 --version

Install without erdpy-up
=========================

You can install without the ``erdpy-up`` as well. If you'd like to install without relying on the easy installation script, kindly read and follow the instructions in this section. Otherwise, feel free to skip it.
Ensure you have ``pip3`` installed.

Prepare PATH
=============

To have the command **erdpy** available in your shell after installation, make sure you adjust the ``PATH`` environment variable as described below:

On Linux in ``~/.profile`` run:

.. code-block::

    export PATH="$HOME/.local/bin:$PATH"

On MacOS in ``~/.bash_profile`` or ``~/.zshrc`` if you’re using ``zsh`` run:

.. code-block::

    export PATH=$HOME/Library/Python/3.8/bin:${PATH}

.. note:: 
    ADD THE RIGHT VERSION:

    In the snippet above, replace ``3.8`` with your actual ``MAJOR.MINOR`` version of Python. This can be found by running:
    
.. code:: 

    python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"

You may need to restart your user session for these changes to take effect. 

Install and smoke test
=======================
To install **erdpy**, run the following command:

.. code-block::

    pip3 install --user --upgrade --no-cache-dir erdpy

Troubleshooting
=================
If you encounter *encoding-related* issues while installing, such as ``UnicodeDecodeError: 'ascii' codec can't decode byte``, set the ``PYTHONENCODING`` environment variable:

.. code-block::

    PYTHONIOENCODING=utf8 pip3 install --user --upgrade --no-cache-dir erdpy
