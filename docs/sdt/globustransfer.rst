.. _globus:

Download with Globus
====================

Requirement
***********

- Synda 3.3+

- Synda must be installed from source to transfer files with Globus Transfer (not available yet with system package based installation).

Installation
************

First you need to retrieve the installer:

.. code-block:: bash

    wget --no-check-certificate https://raw.githubusercontent.com/Prodiguer/synda/master/sdc/install.sh
    chmod +x ./install.sh

Then use one of the methods below to install the globus module.

- Install ``globustransfer`` module over an already existing synda installation:

.. code-block:: bash

    ./install.sh globustransfer

- Install a new installation of synda and globustransfer:

.. code-block:: bash

    ./install.sh synda globustransfer

Configuration
*************

- Edit ``sdt/conf/credentials.conf``

.. code-block:: text

    [globustransfer]
    username=
    password=

- Edit ``sdt/conf/sdt.conf``

.. code-block:: bash

    [module]
    globustransfer=1

    [globustransfer]
    destination_endpoint = destination#endpoint
    esgf_endpoints = /esg/config/esgf_endpoints.xml

- Edit ``/esg/config/esgf_endpoints.xml``

.. code-block:: bash

    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <endpoints xmlns="http://www.esgf.org/whitelist">
        <endpoint
            name="cedaesgf#esgf-data1"
            gridftp="esgf-data1.ceda.ac.uk:2811"
            path_out="/"
            path_in=”/”
        />
        <endpoint
        name="esganl#7c3cf794-d9a4-11e5-ac97-22000b460624"
            gridftp="esg.anl.gov:2811"
            path_out="/"
            path_in=”/”
        />
        <endpoint
            name="esganl#5a43068a-d669-11e5-9765-22000b9da45e"
            gridftp="app006.cels.anl.gov:2811"
            path_out="/"
            path_in=”/”
        />
    </endpoints>