#!/usr/bin/env python2
# Copyright 2019 Belma Turkovic
# TU Delft Embedded and Networked Systems Group.
# NOTICE: THIS FILE IS BASED ON https://github.com/p4lang/tutorials/tree/master/exercises/p4runtime, BUT WAS MODIFIED UNDER COMPLIANCE
# WITH THE APACHE 2.0 LICENCE FROM THE ORIGINAL WORK.
import argparse
import grpc
import os
import sys
from time import sleep

# Import P4Runtime lib from parent utils dir
# Probably there's a better way of doing this.
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "utils/"))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), "."))
import p4_cli.bmv2 as bmv2
from p4_cli.switch import ShutdownAllSwitchConnections
from p4_cli.convert import encodeNum
import p4_cli.helper as helper

def printGrpcError(e):
    print("gRPC Error:", e.details(), end="")
    status_code = e.code()
    print("(%s)" % status_code.name, end="")
    traceback = sys.exc_info()[2]
    print("[%s:%d]" % (traceback.tb_frame.f_code.co_filename, traceback.tb_lineno))


def main(p4info_file_path, bmv2_file_path):
    # Instantiate a P4Runtime helper from the p4info file
    p4info_helper = helper.P4InfoHelper(p4info_file_path)

    try:
        # Create a switch connection object for s1;
        # this is backed by a P4Runtime gRPC connection.
        # Also, dump all P4Runtime messages sent to switch to given txt files.
        s1 = bmv2.Bmv2SwitchConnection(
            name="s0",
            address="127.0.0.1:51001",
            device_id=1,
            proto_dump_file="p4runtime.log",
        )

        # Send master arbitration update message to establish this controller as
        # master (required by P4Runtime before performing any other write operation)
        MasterArbitrationUpdate = s1.MasterArbitrationUpdate()
        print(MasterArbitrationUpdate)
        if MasterArbitrationUpdate == None:
            print("Failed to establish the connection")

        # Install the P4 program on the switches
        try:
            s1.SetForwardingPipelineConfig(
                p4info=p4info_helper.p4info, bmv2_json_file_path=bmv2_file_path
            )
            print("Installed P4 Program using SetForwardingPipelineConfig on s1")
        except Exception as e:
            print("Forwarding Pipeline added.")
            print(e)
            # Forward all packet to the controller (CPU_PORT 255)
        writeIpv4Rules(p4info_helper, sw_id=s1, dst_ip_addr="172.16.1.1", port=255)
        # read all table rules
        readTableRules(p4info_helper, s1)
        print("Finished reading.")

        while True:
            packetin = s1.PacketIn()  # Packet in!
            if packetin is not None:
                print("PACKET IN received")
                #print(packetin)
                packet = packetin.packet.payload
                packetout = p4info_helper.buildPacketOut(
                    payload=packet,  # send the packet in you received back to output port 3!
                    metadata={
                        1: encodeNum(3, 16),
                    },  # egress_spec (check @controller_header("packet_out") in the p4 code)
                )

    except KeyboardInterrupt:
        print(" Shutting down.")
    except grpc.RpcError as e:
        printGrpcError(e)

    ShutdownAllSwitchConnections()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="P4Runtime Controller")
    parser.add_argument(
        "--p4info",
        help="p4info proto in text format from p4c",
        type=str,
        action="store",
        required=False,
        default="./p4src/build/p4info.txt",
    )
    parser.add_argument(
        "--bmv2-json",
        help="BMv2 JSON file from p4c",
        type=str,
        action="store",
        required=False,
        default="./p4src/build/main.json",
    )
    args = parser.parse_args()

    if not os.path.exists(args.p4info):
        parser.print_help()
        print("\np4info file %s not found!" % args.p4info)
        parser.exit(1)
    if not os.path.exists(args.bmv2_json):
        parser.print_help()
        print("\nBMv2 JSON file %s not found!" % args.bmv2_json)
        parser.exit(2)
    main(args.p4info, args.bmv2_json)
