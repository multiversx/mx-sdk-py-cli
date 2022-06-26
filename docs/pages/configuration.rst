===================
Configuring erdpy
===================

**erdpy** can be configured using the ``erdpy config`` command.

In order to view the current configuration, you can run the ``erdpy config dump`` command. 

You should have this output. For example:

.. code::

    {
    "proxy": "https://gateway.elrond.com",
    "txVersion": "1",
    "dependencies.llvm.tag": "v...",
    "dependencies.vmtools.tag": "v...",
    "chainID": "...",
    "dependencies.rust.tag": ""
    }

You can alter the current configuration using the ``erdpy config set`` command. For 

For example, in order to set the *proxy URL* or the *chain ID*, run the following:

.. code:: bash

    $ erdpy config set chainID 1...
    $ erdpy config set proxy https://gateway.elrond.com

.. note::
    For *mainnet* use proxy: https://gateway.elrond.com and chainID: 1.

    For *devnet* use proxy: https://devnet-gateway.elrond.com and chainID: D.

    For *testnet* use proxy: https://testnet-api.elrond.com and chainID: T.

.. tip::
    erdpy's configuration is stored in the file ``~/elrondsdk/erdpy.json``.

