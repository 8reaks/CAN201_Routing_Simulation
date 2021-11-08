import json
import struct
from socket import *

client_socket = socket(AF_INET, SOCK_DGRAM)
client_socket.bind(('', 10000))

head_len, _ = client_socket.recvfrom(4)
head_len = struct.unpack("i", head_len)[0]
print(head_len)
json_head, _ = client_socket.recvfrom(head_len)
head = json.loads(json_head)
print(head)
