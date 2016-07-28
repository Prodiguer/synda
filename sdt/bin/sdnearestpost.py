#!/usr/bin/env python
# -*- coding: ISO-8859-1 -*-

##################################
#  @program        synda
#  @description    climate models data transfer program
#  @copyright      Copyright “(c)2009 Centre National de la Recherche Scientifique CNRS. 
#                             All Rights Reserved”
#  @license        CeCILL (https://raw.githubusercontent.com/Prodiguer/synda/master/sdt/doc/LICENSE)
##################################

"""This filter select the nearest replica using geolocation routines.

Notes
    - This filter do the same job as 'sdnearestpre' filter, except it operates
      in the 'file pipeline' instead of the 'query pipeline'.
    - This module is called 'sdnearestpost' as it operates post-call (i.e. after the search-API call).
    - This module can be used to process different metadata types (File and Dataset).
"""

import os
import argparse
import json
import sdnearestutils
import sdpostpipelineutils
import sdprint
import sdrtt
import sdconfig
import sdlog
import sdgc
from sdexception import SDException

def run(metadata):
    light_metadata=sdlmattrfilter.run(metadata,[functional_id_keyname]) # create light list with needed columns only not to overload system memory

    # build score table
    score=dict(((f[functional_id_keyname],f['data_node']), False) for f in light_metadata) # list of dict => dict (id=>bool)
    metadata=sdpipelineprocessing.run_pipeline(sdconst.PROCESSING_FETCH_MODE_GENERATOR,metadata,keep_nearest,functional_id_keyname,score)

    # score based filter
    FIXME

    return metadata

def keep_nearest(files,functional_id_keyname,score):

    for f in files:
        uniq_id=(f[functional_id_keyname],f['data_node']) # tuple
        if score[uniq_id] is None:
            # there is a previous instance of this file (e.g. another replica)

            score[uniq_id]=True

        else:
            if compare_file(f,new_files[id_]):
                new_files[id_]=f # replace as 'f' is the nearest

    return files

def old_algo(files):
    """
    Note
        Use a lot of memory.

    Not used.
    """
    new_files={}

    for f in files:
        id_=sdpostpipelineutils.get_functional_identifier_value(f)
        if id_ in new_files:
            # there is a previous instance of this file (e.g. another replica)

            if compare_file(f,new_files[id_]):
                new_files[id_]=f # replace as 'f' is the nearest
        else:
            new_files[id_]=f

    return new_files.values()

def compare_file(f1,f2):
    return compare_dn(f1['data_node'],f2['data_node'])

def compare_dn(datanode_1,datanode_2):
    mode=sdconfig.config.get('behaviour','nearest_mode')

    if mode=='geolocation':
        return (get_distance(datanode_1) < get_distance(datanode_2))
    elif mode=='rtt':
        return (get_RTT(datanode_1) < get_RTT(datanode_2))
    else:
        raise SDException("SDNEARES-001","Incorrect nearest mode (%s)"%mode)

def get_RTT(remote_host):

    if remote_host not in sdgc.RTT_cache:
        sdlog.info("SDNEARES-012","Compute RTT for '%s' host."%remote_host)
        sdgc.RTT_cache[remote_host]=compute_RTT(remote_host)

    return sdgc.RTT_cache[remote_host]

def compute_RTT(remote_host):
    """Returns round trip time between the client and the file (i.e. the file's datanode)."""
    rtt=0.0

    try:
        rtt=sdrtt.compute_RTT(remote_host)
    except SDException,e:
        if e.code=='SYNDARTT-002':
            # when here, it means no response from host

            sdlog.info("SDNEARES-006","No reply to ICMP request (ping) from '%s' host."%remote_host)

            # in this case, we return a high RTT to prevent using this host

            return 20000.0 # 20 seconds
        else:
            raise

    return rtt

def get_distance(remote_host):

    if remote_host not in sdgc.GEO_cache:
        sdgc.GEO_cache[remote_host]=compute_distance(remote_host)

    return sdgc.GEO_cache[remote_host]

def compute_distance(remote_host):
    """Returns distance between the client and the file (i.e. the file's datanode)."""
    client_place=sdnearestutils.get_client_place() # our location
    datanode_place=sdnearestutils.get_datanode_place(remote_host)
    distance=sdnearestutils.compute_distance(client_place,datanode_place)
    return distance

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-1','--print_only_one_item',action='store_true')
    parser.add_argument('-F','--format',choices=sdprint.formats,default='raw')
    args = parser.parse_args()

    files=json.load( sys.stdin )
    files=run(files)
    sdprint.print_format(files,args.format,args.print_only_one_item)
