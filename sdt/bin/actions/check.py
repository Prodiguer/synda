#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

##################################
#  @program        synda
#  @description    climate models data transfer program
#  @copyright      Copyright (c)2009 Centre National de la Recherche Scientifique CNRS.
#                             All Rights ReservedĚ
#  @license        CeCILL (https://raw.githubusercontent.com/Prodiguer/synda/master/sdt/doc/LICENSE)
##################################

from sdt.bin.commons import sddump
from sdt.bin.commons import sdcheckdatasetversion

import sdfields
import sdselectionsgroup, sdpipeline


def run(args):
    status = 0
    if args.action is None:
        print_stderr('Please specify a check to perform.')
        status = 1

    elif args.action == "dataset_version":
        status = sdcheckdatasetversion.run(args)

    elif args.action == "file_variable":
        # subset filter must be the subset coming from the args.parameters
        subset_filter = ['model=CNRM-CM5', 'project=specs', 'realm=atmos', 'variable=tas']
        # subset_filter = args.parameters
        print(subset_filter)
        # subset_filter=['model=CNRM-CM5','project=specs','realm=atmos','variable=tas']

        files = sddump.dump_ESGF(parameter=subset_filter, fields=sdfields.get_file_variable_fields(),
                                 dry_run=args.dry_run, type_='File')

        if not args.dry_run:
            print('{} file(s) retrieved'.format(len(files)))
            errors = 0
            for file_ in files:
                # debug
                print(file_['variable'])
                if len(file_['variable']) > 1:
                    print('File contains many variables ({},{})'.format(file_['title'], str(file_['variable'])))
                    errors += 1

            if errors == 0:
                print('No inconsistency detected')
            else:
                print('%d inconsistencies detected' % errors)

    elif args.action == "selection":

        for selection in sdselectionsgroup.get_selection_list():
            try:
                print_stderr("Checking %s.." % selection.filename)
                sdpipeline.prepare_param(selection=selection)
            except sdexception.IncorrectParameterException as e:
                print_stderr("Error occurs while processing %s (%s)" % (selection.filename, str(e)))



    else:
        print_stderr('Invalid check "%s"' % args.action)
        status = 1

    return status
