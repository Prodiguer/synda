#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

##################################
#  @program        synda
#  @description    climate models data transfer program
#  @copyright      Copyright (c)2009 Centre National de la Recherche Scientifique CNRS.
#                             All Rights Reserved
#  @license        CeCILL (https://raw.githubusercontent.com/Prodiguer/synda/master/sdt/doc/LICENSE)
##################################

"""This script changes existing transfer attributes.

Notes
    - This filter terminates a pipeline
    - This module is intended to be plugged to sdfilepipeline output
      (i.e. stream must be duplicate free and each file must contain status attribute).
"""

# import sdreplica

from sdtools import print_stderr
from sdt.bin.db import dao
from sdt.bin.commons.utils import sdlog, sdconst
from sdt.bin.db import session


def retry_all():
    sdlog.info("SDMODIFY-343", "Moving transfer from error to waiting..")
    with session.create():
        nbr = dao.retry_all()
        session.commit()
    sdlog.info("SDMODIFY-226", "{} transfer marked for retry".format(nbr))
    return nbr


def replica_next(file_, replicas):
    if file_.status in [sdconst.TRANSFER_STATUS_ERROR,
                        sdconst.TRANSFER_STATUS_WAITING]:  # replica can only be changed for those file statuses

        new_replica = sdreplica.replica_next(file_.url,
                                             replicas)  # TODO: maybe use replica object instead of tuple here
        if new_replica is None:
            print_stderr("No other replica found (file_functional_id=%s)" % file_.file_functional_id)
        else:
            sdmodifyquery.change_replica(file_.file_functional_id, new_replica)

            sdlog.info("SDMODIFY-100", "File replica set to %s (previous_replica=%s,file_functional_id=%s)" % (
                new_replica[1], file_.url, file_.file_functional_id))
    else:
        print_stderr("Replica cannot be changed (local file incorrect status).")
