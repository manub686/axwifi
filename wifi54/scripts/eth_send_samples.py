#!/usr/bin/env python

from pcap import pcap
from sys import stderr, stdout
from time import sleep
from socket import socket, PF_PACKET, SOCK_RAW
from sys import argv
from fcntl import ioctl
import ctypes

class ifreq(ctypes.Structure):
	_fields_ = [("ifr_ifrn", ctypes.c_char * 16), ("ifr_flags", ctypes.c_short)]

MAC_ADDR = "\x00\x0c\x29\x4c\x1c\x51"

SAMPLE_SIZE = 4
SAMPLES_PER_SYMBOL = 80
ETH_INTERFACE = "eth0"

ETH_IP_UDP_HEADER = (\
	"\x00\x01\x01\x01\x01\x01"  # Dest MAC
	+ MAC_ADDR +                # Src MAC
	"\x08\x00"                  # Ethertype
	"\x45\x00\x00\x00"          # IP version, services, total length
	"\x00\x00\x00\x00"          # IP ID, flags, fragment offset
	"\x05\x11\x32\x26"          # IP ttl, protocol (UDP), hdr checksum
 	"\x00\x00\x00\x00"          # Source IP address
	"\x00\x00\x00\x01"          # Destination IP address
	"\xAD\x51\xAD\x50"          # UDP source port, dest port
	"\x00\x00\x00\x00")         # UDP len, UDP checksum

stderr.write("Notice: Don't forget to update the source MAC address. Ethernet interface is \"%s\".\n" % ETH_INTERFACE)

# read samples
f = open(argv[1], "r")
samples = f.read()

# setup raw ethernet socket
s = socket(PF_PACKET, SOCK_RAW)
s.bind((ETH_INTERFACE,0))

# setup pcap
pc = pcap(name=ETH_INTERFACE)

# transmit each
for i in range(0,len(samples),SAMPLES_PER_SYMBOL*SAMPLE_SIZE):
	stderr.write("SEND\n")
	print "PACKET: ",
	for c in samples[i:i+(SAMPLES_PER_SYMBOL*SAMPLE_SIZE)]:
		print "{:02x}".format(ord(c)),
	print ""
	s.send(ETH_IP_UDP_HEADER + samples[i:i+(SAMPLES_PER_SYMBOL*SAMPLE_SIZE)])

	# wait for flow control reply
	m = ""
	while (m[34:36] != "\xAD\x50"):
		ts, m = pc.next()
