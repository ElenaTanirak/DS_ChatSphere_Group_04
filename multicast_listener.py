# import of required modules
import hosts
import socket
import sys
import struct
import pickle


# Configuration for multicast communication
server_address = ('', hosts.multicast_port)
multicast_ip = hosts.multicast_address
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)


def multicast_starts_listening():
    """"
    Sets up a multicast receiver using a UDP socket.
    Listens for incoming data packets and responds based on the content of the data,
    handling chat client joins and network topology changes.
    """
    # Bind the socket to the server address
    sock.bind(server_address)

    # Join the multicast group
    multicast_group = socket.inet_aton(multicast_ip)
    multicast_request = struct.pack('4sL', multicast_group, socket.INADDR_ANY)
    sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, multicast_request)
    print(f'\n[Multicast Listener - {hosts.my_ip}]: Starting UDP Socket and listening on Port {hosts.multicast_port}')

    while True:
        try:
            # Receive data from multicast group
            data_received, address = sock.recvfrom(hosts.buffer_size)
            print(f'\n[Multicast Listener - {hosts.my_ip}]: Received data from {address}\n')

            # Handle client join request
            if hosts.leader == hosts.my_ip and pickle.loads(data_received)[0] == 'JOIN':
                message = pickle.dumps([hosts.leader, ''])
                print(f'[Multicast Listener - {hosts.my_ip}]: The Client ({address}) wants to join the Chat Room.\n')
                sock.sendto(message, address)

            # Update server list if necessary
            if len(pickle.loads(data_received)[0]) == 0:
                hosts.server_list.append(address[0]) if address[0] not in hosts.server_list else hosts.server_list
                sock.sendto('ack'.encode(hosts.unicode), address)
                hosts.is_network_changed = True

            # Update network topology if necessary
            elif pickle.loads(data_received)[1] and hosts.leader != hosts.my_ip or pickle.loads(data_received)[3]:
                hosts.server_list = pickle.loads(data_received)[0]
                hosts.leader = pickle.loads(data_received)[1]
                hosts.client_list = pickle.loads(data_received)[4]
                print(f'[Multicast Listener - {hosts.my_ip}]: There is nothing new to learn, so relax :)')
                sock.sendto('ack'.encode(hosts.unicode), address)
                hosts.is_network_changed = True

        except KeyboardInterrupt:
            print(f'[Multicast Listener - {hosts.my_ip}]: UDP Socket is now closed.')