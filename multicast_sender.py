# import of required modules
import hosts
import socket
import sys
import struct
import pickle
from time import sleep


# Configuration for multicast communication
multicast_address = (hosts.multicast_address, hosts.multicast_port)
time_to_live = struct.pack('b', 1)

# Create a socket for multicast communication
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.settimeout(2)
sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, time_to_live)


def sending_join_request():
    """
    Sends a chat room join request and determines the server leader.
    
    Returns:
    bool: True if a server leader is found, False otherwise.
    """
    message = pickle.dumps(['JOIN', '', '', ''])
    sock.sendto(message, multicast_address)
    print(f'\n[Multicast Sender - {hosts.my_ip}]: The request to join the Chat has been sent to Multicast Address ({multicast_address})')

    try:
        # Attempt to receive response from the server leader
        data_received, address = sock.recvfrom(hosts.buffer_size)
        hosts.leader = pickle.loads(data_received)[0]
        print(f'[Multicast Sender - {hosts.my_ip}]: Data received from Server.')
        return True

    except socket.timeout:
        print(f'[Multicast Sender - {hosts.my_ip}]: Unfortunately, the Multicast Listener was not found. The Server is probably offline.')
        return False
    

def sending_request_to_multicast():
    """
    Sends data to multicast receivers and waits for a response, synchronizing host variables.
    
    Returns:
    bool: True if synchronization with multicast listeners is successful, False otherwise.
    """
    sleep(1)

    # Prepare and send the message to multicast listeners
    message = pickle.dumps([hosts.server_list, hosts.leader, hosts.is_leader_server_crashed, hosts.has_server_replication_crashed, str(hosts.client_list)])
    sock.sendto(message, multicast_address)
    print(f'\n[Multicast Sender - {hosts.my_ip}]: Data is sent to the Multicast Listener ({multicast_address})')

    try:
        # Attempt to receive acknowledgment from a multicast listener
        sock.recvfrom(hosts.buffer_size)

        if hosts.leader == hosts.my_ip:
            print(f'[Multicast Sender - {hosts.my_ip}]: All Servers are up to date.\n')
        return True

    except socket.timeout:
        print(f'[Multicast Sender - {hosts.my_ip}]: Unfortunately, no Multicast Listener was found.')
        return False

