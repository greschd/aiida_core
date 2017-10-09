.. _aiida-sphinxext:

AiiDA Sphinx extension
++++++++++++++++++++++

AiiDA defines a Sphinx extension to simplify documenting some of its features. To use this extension, you need to add  ``aiida.sphinxext`` to the ``extensions`` list in your Sphinx ``conf.py`` file.

WorkChain directive
-------------------

The following directive can be used to auto-document AiiDA workchains:

::

    .. aiida-workchain:: my_plugin.MyWorkChain
        :hidden-ports:

The argument ``my_plugin.MyWorkChain`` is the fully qualified (importable) name of the workchain. If the ``:hidden-ports:`` option is given, inputs and outputs starting with ``_`` will also be documented.
