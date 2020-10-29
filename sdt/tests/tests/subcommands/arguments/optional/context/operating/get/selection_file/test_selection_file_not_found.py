# -*- coding: utf-8 -*-
##################################
#  @program        synda
#  @description    climate models data transfer program
#  @copyright      Copyright "(c)2009 Centre National de la Recherche Scientifique CNRS.
#                             All Rights Reserved"
#  @license        CeCILL (https://raw.githubusercontent.com/Prodiguer/synda/master/sdt/doc/LICENSE)
##################################
"""
 Tests driven by pytest

 Sub-command : GET
 Optional argument : selection_file
 Operating context : file doesn't exist
"""
import os
import sys
import pytest

from sdt.tests.constants import DATADIR

from sdt.bin import synda
from sdt.bin.sdexception import SDException


@pytest.mark.on_all_envs
def test_selection_file_not_found():

    selection_file = os.path.join(
        DATADIR,
        "test_selection_00.txt",
    )

    sys.argv = ['', "get", "--selection_file", selection_file]

    with pytest.raises(SDException) as exception:
        synda.run()

    assert exception.value.code == 'SDBUFFER-002'