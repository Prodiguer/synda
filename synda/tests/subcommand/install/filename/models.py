# -*- coding: utf-8 -*-
##################################
#  @program        synda
#  @description    climate models data transfer program
#  @copyright      Copyright "(c)2009 Centre National de la Recherche Scientifique CNRS.
#                             All Rights Reserved"
#  @license        CeCILL (https://raw.githubusercontent.com/Prodiguer/synda/master/sdt/doc/LICENSE)
##################################
from synda.tests.subcommand.install.models import SubCommand as Base
from synda.tests.exceptions import MethodNotImplemented


class SubCommand(Base):

    def __init__(self, context, exceptions_codes=None):
        super(SubCommand, self).__init__(
            context,
            exceptions_codes=exceptions_codes,
            description="Download with install subcommand, configuration is given by file",
        )
        self.configure(
            context.get_file().get_filename(),
        )

    def configure(self, filename):

        self.set_argv(
            ['synda', self.name, "--yes", filename],
        )
