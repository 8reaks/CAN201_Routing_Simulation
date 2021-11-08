import json
import struct
import sys
from socket import *
from threading import Thread
from time import sleep

local_socket = socket(AF_INET, SOCK_DGRAM)
local_distances = {}


def get_sys_info(s):  # Method of getting command line argument
    node = s[2]
    return node


def file_reader(filename):  # Read json file information
    file_path = 'CWD/' + filename
    f = open(file_path, 'r')
    file_info = json.loads(f.read())
    f.close()
    return file_info


def ip_getter(n):
    file_name = n + '_ip.json'
    ips_info = file_reader(file_name)
    return ips_info


def init(n):
    global local_socket
    local_ip_info = ip_getter(n)[n]
    local_ip = local_ip_info[0]
    local_port = local_ip_info[1]
    print('local ip_info: ' + str(local_ip_info))
    local_socket.bind(('', local_port))
    print('local socket starting...')
    print('')


def info_handler(n):
    file_name = n + '_distance.json'
    distance_info = file_reader(file_name)
    return distance_info


def info_sender(info, address):
    json_head = json.dumps(info).encode()
    head_len = struct.pack("i", len(json_head))
    local_socket.sendto(head_len, address)
    local_socket.sendto(json_head, address)


def info_receiver(this_node):
    # local_distances = info_handler(this_node)
    distances_data = {}
    output_data = {}
    while True:
        try:
            head_len, _ = local_socket.recvfrom(4)
            head_len = struct.unpack("i", head_len)[0]
            json_head, ip = local_socket.recvfrom(head_len)
            head = json.loads(json_head)
            # print(head)
            file_name = this_node + '_ip.json'
            ips_info = file_reader(file_name)
            for key in ips_info.keys():
                if ips_info[key][1] == ip[1]:
                    distances_data[key] = head
                    # print(distances_data)
                    for node1 in local_distances.keys():
                        d_all = []
                        for node2 in local_distances.keys():
                            if node2 == node1:
                                c = local_distances[node2] + 0
                            elif (node2 in distances_data.keys()) and (node1 in distances_data[node2].keys()):
                                c = local_distances[node2] + distances_data[node2][node1]
                            d_all.append(c)
                        if len(d_all) > 0:
                            print(d_all)
                            d_min = min(d_all)
                            output_data[node1] = {'distance': d_min, 'next_hop': 0}
                    print(output_data)
            # for node in output_data.keys():
            #     if node in local_distances.keys():
            #         local_distances[node] = output_data[node]['distance']
        except ConnectionResetError:
            sleep(0.1)


def main():
    global local_distances
    node_num = get_sys_info(sys.argv)  # Gets the command-line arguments
    print('node_num: ' + str(node_num))
    init(node_num)

    local_distances = info_handler(node_num)

    thread1 = Thread(target=info_receiver, args=node_num)  # Create a thread to accept the new connection
    thread1.start()

    while True:
        for key in local_distances.keys():
            ip_info = ip_getter(node_num)[key]
            route_address = (ip_info[0], ip_info[1])
            info_sender(local_distances, route_address)
            print(node_num + ' successfully send ' + str(local_distances) + ' to ' + key + ': ' + str(route_address))
        sleep(2)


if __name__ == '__main__':
    main()
