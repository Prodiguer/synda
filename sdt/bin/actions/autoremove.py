#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

##################################
#  @program        synda
#  @description    climate models data transfer program
#  @copyright      Copyright (c)2009 Centre National de la Recherche Scientifique CNRS.
#                             All Rights ReservedĚ
#  @license        CeCILL (https://raw.githubusercontent.com/Prodiguer/synda/master/sdt/doc/LICENSE)
##################################
from sdt.bin.db import session
from sdt.bin.db import dao
from sdt.bin.commons.utils import sdconfig, sdlog


def get_dataset_versions(dataset):
    """
    Lists all the versions found for a specific dataset.
    Performs db query using the path_without_version as shared key within the version family.
    :param dataset: a Dataset entity
    :return: List of Dataset entities
    """
    return dao.get_datasets(path_without_version=dataset.path_without_version)


def version_compare_datasets(dataset_a, dataset_b):
    """Returns true if d_a is more recent (higher in most case) than d_b, else false.
    Samples
        d_a.version => v20110901
        d_b.version => v1
    :param dataset_a: Dataset entity
    :param dataset_b: Dataset entity
    :returns Boolean
    """
    if len(dataset_a.version) != len(dataset_b.version):

        if dataset_a.timestamp is not None and dataset_b.timestamp is not None:

            if dataset_a.timestamp > dataset_b.timestamp:
                return True
            else:
                return False

        else:
            # Some datasets don't have the timestamp set (e.g. obs4MIPs.PCMDI.CloudSat.mon.v1)
            # we need to fallback to the emergency solution below.
            if len(dataset_a.version) == 9 and len(dataset_b.version) == 2:
                return True
            elif len(dataset_a.version) == 2 and len(dataset_b.version) == 9:
                return False
            else:
                raise SDException("SDDATVER-002", "Incorrect version number ({},{})".format(dataset_a.version,
                                                                                            dataset_b.version))
    else:
        return dataset_a.version > dataset_b.version


def get_list_of_datasets_to_remove():
    """
    Finds latest dataset version and removes the rest.
    :return: List of dataset entities to be removed from db and optionally file system.
    """
    with session.create():
        # Get single dataset per version tree list (also get max version while at it)
        max_version_datasets = dao.get_max_version_datasets_groupby_criterion()
        dataset_to_remove_list = []
        # Flush every dataset version family using path_with_version shared key
        for dset in max_version_datasets:
            # This list contains all the versions of the dataset, including this one.
            # Once the max version has been confirmed, it's removed from the list.
            dsets_to_remove = get_dataset_versions(dset)
            for other_dset in dsets_to_remove:
                max_dset = dset
                if dset.path_without_version == other_dset.path_without_version:
                    if version_compare_datasets(other_dset, dset):
                        max_dset = other_dset
            dsets_to_remove.remove(max_dset)
            dataset_to_remove_list.extend(dsets_to_remove)
    return dataset_to_remove_list


def remove_old_datasets(dataset_list, dry_run=False):
    """
    Removes old dataset versions from db and optionally the file system as well.
    :param dataset_list: List of dataset entities
    :param dry_run: Test run or not, Boolean
    """
    if dry_run:
        for d in dataset_list:
            print(d.get_full_local_path(sdconfig.data_folder))
    else:
        with session.create():
            dao.mark_dataset_transfer_for_delete(dataset_list)
            dao.remove_datasets(dataset_list)


def delete_transfers_lowmem(remove_all=True):
    """
    Deletes the file transfers marked with to delete status
    """
    with session.create():
        transfer_list = dao.get_files_marked_to_delete()
        try:
            for tr in transfer_list:
                # Delete file transfer from db and file system.
                if os.path.isfile(tr.get_full_local_path(sdconfig.data_folder)):
                    try:
                        os.remove(tr.get_full_local_path(sdconfig.data_folder))
                        # note: if data cannot be removed (i.e. exception is raised), we don't remove metadata
                        dao.delete_file(tr)

                    except Exception as e:
                        sdlog.error("SDDELETE-528",
                                    "Error occurs during file suppression ({}, {})".
                                    format(tr.get_full_local_path(sdconfig.data_folder), str(e)))
                        raise
                else:
                    if tr.status == sdconst.TRANSFER_STATUS_DONE:
                        # this case is not normal as the file should exist on filesystem when status is done

                        sdlog.error("SDDELETE-123",
                                    "Can't delete file: file not found ({})".
                                    format(tr.get_full_local_path(sdconfig.data_folder)))
                    else:
                        # this case is for 'waiting' and 'error' status (in these cases,
                        # data do not exist, so we just remove metadata)
                        dao.delete_file(tr)

        except Exception as e:
            sdlog.error("SDDELETE-880", "Error occurs during files suppression ({})".format(str(e)))
            raise  # fatal error


def run(args):
    dataset_list = get_list_of_datasets_to_remove()
    if dataset_list is not None:
        remove_old_datasets(get_list_of_datasets_to_remove(), dry_run=args.dry_run)
        delete_transfers_lowmem(remove_all=args.remove_all)
        sdlog.info('SYNDAATR-001', 'Done with the autoremove.')
    else:
        sdlog.info('SYNDAATR-002', 'No dataset found to remove.')
