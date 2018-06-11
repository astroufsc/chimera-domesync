chimera-domesync plugin
=======================

This plugin creates a meta-dome, which acts like a normal dome, but translates the azimuth of a german equatorial mount
 to the dome azimuth to have the telescope placed right on the dome slit.

Usage
-----

This plugin needs the geometrical parameters of the dome-telescope configuration. These parameters are ``dome_radius``,
``mount_dec_height``, ``mount_dec_length`` and ``mount_dec_offset``. Which are R, Zdome0, r and Xdome0, respectively:


.. image:: https://github.com/astroufsc/chimera-domesync/raw/master/docs/DomeSynchronisation.png


Installation
------------

To install `chimera-domesync` plugin, run:

::

    pip install -U git+https://github.com/astroufsc/chimera-domesync.git


Configuration Example
---------------------

The configuration must follow the example, where the meta-instrument ``DomeSync`` must be the first dome on the domes
configuration parameter.

::

    domes:
      - name: ds
        type: DomeSync
        dome: /FakeDome/fake

      - name: fake
        type: FakeDome
        mode: track
        telescope: False


Contact
-------

For more information, contact us on chimera's discussion list:
https://groups.google.com/forum/#!forum/chimera-discuss

Bug reports and patches are welcome and can be sent over our GitHub page:
https://github.com/astroufsc/chimera-domesync/
