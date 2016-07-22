import logging
import random
import pickle
import os
import inspect
import subprocess
import zmq
import time
import platform
import numpy as np
import iptc
import csv
import shutil

import wishful_module_wifi
import wishful_upis as upis

from wmp_structure import UPI_R
from adaptation_module.libb43 import *

import wishful_framework as wishful_module
from wishful_framework.classes import exceptions

__author__ = "Domenico Garlisi"
__copyright__ = "Copyright (c) 2015, Technische Universität Berlin"
__version__ = "0.1.0"
__email__ = "{gomenico.garlisi@cnit.it}"

# Used by local controller for communication with mac processor
LOCAL_MAC_PROCESSOR_CTRL_PORT = 1217

@wishful_module.build_module
class WmpModule(wishful_module_wifi.WifiModule):
    def __init__(self):
        super(WmpModule, self).__init__()
        self.log = logging.getLogger('WmpModule')
        self.SUCCESS = 0
        self.PARTIAL_SUCCESS = 1
        self.FAILURE = 2
        self.b43_phy=None

    @wishful_module.bind_function(upis.radio.set_parameter_lower_layer)
    def set_parameter_lower_layer(self, myargs):
        self.log.warning('setParameterLowerLayer(): %s' % (str(myargs)))
        ret_lst = []

        #manage TDMA slot parameter
        super_frame_size = 0
        number_of_sync_slot = 0
        if UPI_R.TDMA_SUPER_FRAME_SIZE in myargs:
            super_frame_size = myargs[UPI_R.TDMA_SUPER_FRAME_SIZE]
        if UPI_R.TDMA_NUMBER_OF_SYNC_SLOT in myargs:
            number_of_sync_slot = myargs[UPI_R.TDMA_NUMBER_OF_SYNC_SLOT]
        if super_frame_size != 0 or number_of_sync_slot !=0 :
            return self.FAILURE


        #manage other parameter
        # if  UPI_R.IEEE80211_CHANNEL in myargs:
        #     ret_lst.append( self.setRfChannel(myargs) )
        # if  UPI_R.IEEE80211_CONNECT_TO_AP in myargs:
        #     ret_lst.append( self.connectToAP(myargs) )
        if  UPI_R.CSMA_CW in myargs:
            ret_lst.append( self.setRadioProgramParameters(UPI_R.CSMA_CW, myargs[UPI_R.CSMA_CW]) )
        if  UPI_R.CSMA_CW_MIN in myargs:
            ret_lst.append( self.setRadioProgramParameters(UPI_R.CSMA_CW_MIN, myargs[UPI_R.CSMA_CW_MIN]) )
        if  UPI_R.CSMA_CW_MAX in myargs:
            ret_lst.append( self.setRadioProgramParameters(UPI_R.CSMA_CW_MAX, myargs[UPI_R.CSMA_CW_MAX]) )
        if  UPI_R.TDMA_ALLOCATED_SLOT in myargs:
            ret_lst.append( self.setRadioProgramParameters(UPI_R.TDMA_ALLOCATED_SLOT, myargs[UPI_R.TDMA_ALLOCATED_SLOT] ) )
        if  UPI_R.TDMA_ALLOCATED_MASK_SLOT in myargs:
            ret_lst.append( self.setRadioProgramParameters(UPI_R.TDMA_ALLOCATED_MASK_SLOT, myargs[UPI_R.TDMA_ALLOCATED_MASK_SLOT] ) )
        if  UPI_R.MAC_ADDR_SYNCHRONIZATION_AP in myargs:
                mac_address_end = myargs[UPI_R.MAC_ADDR_SYNCHRONIZATION_AP]
                self.log.debug('ADDRESS 1: %s' % mac_address_end)
                mac_address_end = mac_address_end.replace(':', '')
                self.log.debug('ADDRESS 2: %s' % mac_address_end)
                mac_address_end = mac_address_end[-2:] + mac_address_end[-4:-2]
                self.log.debug('ADDRESS 3: %s' % mac_address_end)
                int_mac_address_end = int(mac_address_end, 16)
                ret_lst.append( self.setRadioProgramParameters(UPI_R.MAC_ADDR_SYNCHRONIZATION_AP, int_mac_address_end ) )

        return ret_lst

    def setRadioProgramParameters(self, offset_parameter=0, value=0):
        b43 = B43(self.b43_phy)
        write_share = False
        write_gpr = False

        value = int(value)
        self.log.debug('setRadioProgramParameters(): offset = %s - value = %s' % (str(offset_parameter), str(value)))
        gpr_byte_code_value = b43.shmRead16(b43.B43_SHM_REGS, b43.BYTECODE_ADDR_OFFSET);
        active_slot=0

        if  not (offset_parameter==UPI_R.CSMA_CW or offset_parameter==UPI_R.CSMA_CW_MIN or offset_parameter== UPI_R.CSMA_CW_MAX or offset_parameter == UPI_R.REGISTER_1 or offset_parameter == UPI_R.REGISTER_2 or offset_parameter == UPI_R.MAC_ADDR_SYNCHRONIZATION_AP):
            if gpr_byte_code_value == b43.PARAMETER_ADDR_OFFSET_BYTECODE_1 :
                active_slot = 1
                #self.log.debug('detected active slot 1')
            elif gpr_byte_code_value == b43.PARAMETER_ADDR_OFFSET_BYTECODE_2 :
                active_slot = 2
                #self.log.debug('detected active slot 2')
            else :
                self.log.error('readRadioProgramParameters(): no active slot')
                return False

        if offset_parameter == UPI_R.MAC_ADDR_SYNCHRONIZATION_AP:
            offset_parameter_gpr= b43.MAC_ADDR_SYNCHRONIZATION_AP_GPR
            write_gpr = True
        elif offset_parameter == UPI_R.CSMA_CW:
            offset_parameter_share= b43.SHM_EDCFQCUR + b43.SHM_EDCFQ_CWCUR
            offset_parameter_gpr= b43.GPR_CUR_CONTENTION_WIN
            write_share = True
            write_gpr = True
        elif offset_parameter == UPI_R.CSMA_CW_MIN:
            offset_parameter_share= b43.SHM_EDCFQCUR + b43.SHM_EDCFQ_CWMIN
            offset_parameter_gpr= b43.GPR_MIN_CONTENTION_WIN
            write_share = True
            write_gpr = True
        elif offset_parameter == UPI_R.CSMA_CW_MAX:
            offset_parameter_share= b43.SHM_EDCFQCUR + b43.SHM_EDCFQ_CWMAX
            offset_parameter_gpr= b43.GPR_MAX_CONTENTION_WIN
            write_share = True
            write_gpr = True
        elif offset_parameter == UPI_R.REGISTER_1:
            offset_parameter_gpr= b43.PROCEDURE_REGISTER_1
            write_gpr = True
        elif offset_parameter == UPI_R.REGISTER_2:
            offset_parameter_gpr= b43.PROCEDURE_REGISTER_2
            write_gpr = True
        elif offset_parameter == UPI_R.TDMA_SUPER_FRAME_SIZE :
            #self.log.debug('start : write super frame size %d' % value)
            if active_slot == 1 :
                b43.shmWrite16(b43.B43_SHM_SHARED, b43.SHM_SLOT_1_TDMA_SUPER_FRAME_SIZE, value)
                #self.log.debug('slot 1 : write super frame size %d' % value)
            else :
                b43.shmWrite16(b43.B43_SHM_SHARED, b43.SHM_SLOT_2_TDMA_SUPER_FRAME_SIZE, value)
                #self.log.debug('slot 2 : write super frame size %d' % value)
        elif offset_parameter == UPI_R.TDMA_NUMBER_OF_SYNC_SLOT:
            if active_slot == 1 :
                b43.shmWrite16(b43.B43_SHM_SHARED, b43.SHM_SLOT_1_TDMA_NUMBER_OF_SYNC_SLOT, value)
            else :
                b43.shmWrite16(b43.B43_SHM_SHARED, b43.SHM_SLOT_2_TDMA_NUMBER_OF_SYNC_SLOT, value)
        elif offset_parameter == UPI_R.TDMA_ALLOCATED_SLOT  :
            if active_slot == 1 :
                b43.shmWrite16(b43.B43_SHM_SHARED, b43.SHM_SLOT_1_TDMA_ALLOCATED_SLOT, value)
            else :
                b43.shmWrite16(b43.B43_SHM_SHARED, b43.SHM_SLOT_2_TDMA_ALLOCATED_SLOT, value)
        elif offset_parameter == UPI_R.TDMA_ALLOCATED_MASK_SLOT  :
            if active_slot == 1 :
                b43.shmWrite32(b43.B43_SHM_SHARED, b43.SHM_SLOT_1_TDMA_ALLOCATED_MASK_SLOT, value)
            else :
                b43.shmWrite32(b43.B43_SHM_SHARED, b43.SHM_SLOT_2_TDMA_ALLOCATED_MASK_SLOT, value)
        else :
            self.log.error('setRadioProgramParameters(): unknown parameter')
            return self.FAILURE

        if write_share :
            b43.shmWrite16(b43.B43_SHM_SHARED, offset_parameter_share, value)
        if write_gpr :
            b43.shmWrite16(b43.B43_SHM_REGS, offset_parameter_gpr, value)

        return self.SUCCESS
