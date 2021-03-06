# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

#cython: language_level=3

import numpy as np
cimport numpy as np
cimport cython

from cpython cimport bool
from maro.backends.backend cimport BackendAbc, SnapshotListAbc

cdef class NumpyBackend(BackendAbc):
    """Backend using numpy array to hold data, this backend only support fixed size array for now"""
    cdef:
        # used to store real data, key is node name, value is np.ndarray
        dict _node_data_dict

        # node name -> node number in frame
        dict _node_num_dict

        # used to cache attribute by node name
        # node name -> list of (name, type, slot), used to construct numpy structure array
        dict _node_attr_dict        

        # quick look up table to query with (node_name, attr_name) -> AttrInfo
        dict _node_attr_lut

        bool _is_snapshot_enabled

        IF NODES_MEMORY_LAYOUT == "ONE_BLOCK":
            char* _data

            # memory size
            size_t _data_size 


cdef class NPBufferedMmap:
    """Used to dump snapshot history using memory mapping with a fixed size in-memory buffer"""
    cdef:
        str _path

        np.dtype _dtype

        # used to define the shape, as we do not exactly know the number we need to save
        int _buffer_size

        # current offset, used to specified the offset in dumped file, to avoid reach the mmap limitation
        int _offset

        # current record item number,
        int _current_record_number

        int _node_number

        # memory mapping np array
        np.ndarray _data_arr

    cdef void reload(self) except *


cdef class NPSnapshotList(SnapshotListAbc):
    """Numpy based snapshot list, this snapshot will keep specified number Frame state in memory"""
    cdef:
        NumpyBackend _backend

        # tick -> index mapping
        dict _tick2index_dict
        
        # index -> tick mapping
        dict _index2tick_dict

        # current index to insert snapshot, default should be 1, never be 0
        int _cur_index

        int _max_size

        #
        bool _is_history_enabled

        # key: node name, value: history buffer
        dict _history_dict

    cdef void enable_history(self, str history_folder) except *