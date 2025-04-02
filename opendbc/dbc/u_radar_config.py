#!/usr/bin/env python3
# MIT Non-Commercial License
# Copyright (c) 2025 Rick Lan
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, for non-commercial purposes only, subject to the following conditions:
#
# - The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.
# - Commercial use (e.g., use in a product, service, or activity intended to generate revenue) is prohibited without explicit written permission from Rick Lan. Contact ricklan@gmail.com for inquiries.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import cantools.database
from panda import Panda
from opendbc.car.structs import CarParams
import hashlib
import time
import cantools

db = cantools.database.load_file(
    "u_radar.dbc"
)  # Load the DBC file for the radar configuration

BUS = 1
GET_CONFIG_CAN_ID = 0x201
SET_CONFIG_CAN_ID = 0x200


def get_config_msg(msgs):
    val = None
    for msg in msgs:
        id = msg[0]
        bus = msg[2]
        if id == GET_CONFIG_CAN_ID and bus == BUS:
            val = msg[1]
            break
    return val

def build_config(
    max_distance=160,
    sensor_id=0,
    output_type=1,
    enable_quality=True,
    enable_ext_info=True,
    enable_sort_by_distance=False,
    enable_high_sensitivity=False,
    write_config=True,
):
    if max_distance < 0 or max_distance > 2048:
        raise ValueError("max_distance must be between 0 and 2048")
    config = {
        "MaxDistance_Valid": 0,
        "SensorID_Valid": 0,
        "RadarPower_Valid": 0,
        "OutputType_Valid": 0,
        "SendQuality_Valid": 0,
        "SendExtInfo_Valid": 0,
        "SortIndex_Valid": 0,
        "StoreInNvm_Valid": 0,
        "MaxDistance": max_distance,
        "SensorID": sensor_id,  # Sensor ID (0-255)
        "OutputType": output_type,
        "RadarPower": 0,
        "SendQuality": enable_quality,
        "SendExtInfo": enable_ext_info,
        "SortIndex": enable_sort_by_distance,  # Sort by distance (0: No, 1: Yes)
        "StoreNVM": write_config,  # Store in NVM (0: No, 1: Yes)
        "RCS_Threshold_Valid": 0,
        "RCS_Threshold": enable_high_sensitivity,  # RCS Threshold (0: Normal, 1: High Sensitivity)
        "BaudRate_Valid": 0, # do not change baud rate
        "BaudRate": 0,
    }
    return db.encode_message('Write_RadarConfig', config, scaling=False, padding=False)

def print_config(config, message_name='RadarState'):
    """
    Helper function to print the radar configuration in a readable format.
    """
    try:
        decoded_config = db.decode_message(message_name, config)
        for key, value in decoded_config.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Failed to decode configuration: {e}")
        return

def main():
    panda = Panda()
    msgs = panda.can_recv()
    config_msg = get_config_msg(msgs)
    if config_msg is None:
        print("Radar Config Message not found, maybe on a different bus?")
        return
    
    print("Current Radar Configuration:")
    print_config(config_msg)
    
    config_msg = build_config(
        max_distance=100,
        sensor_id=1,
        output_type=2,
        write_config=True,
        enable_high_sensitivity=True,
    )
    print("Radar Config Message to be sent")
    print_config(config_msg, message_name='Write_RadarConfig')
    
    print("Setting Radar Configuration...")
    panda.set_safety_mode(CarParams.SafetyModel.allOutput)
    print(config_msg.hex())
    panda.can_send(SET_CONFIG_CAN_ID, config_msg, BUS)
    time.sleep(3)
    msgs = panda.can_recv()
    print_config(get_config_msg(msgs))
    print("Radar Configuration update successful.")
    
    panda.close()

if __name__ == "__main__":
    main()
