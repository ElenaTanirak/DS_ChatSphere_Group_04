# import of required modules
import socket
import leader_election
import hosts
from time import sleep


def starting_heartbeats():
    """
    Periodically sends heartbeat messages to ensure fault tolerance.
    The leader server sends a message to all other servers to indicate its presence.
    """
    while True:
         # Create a TCP socket for sending heartbeats
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.settimeout(1)

        # Determine the current neighbour for the heartbeat
        hosts.neighbour = leader_election.starting_server_leader_election(hosts.server_list, hosts.my_ip)
        #print(f'{hosts.neighbour}')
        host_address = (hosts.neighbour, hosts.server_port)

        if hosts.neighbour:
            sleep(5)
            print(f'Heartbeat: Here is the current list of all servers: \n{hosts.server_list}')

            try:
                # Attempt to connect to the neighbour
                sock.connect(host_address)
                print(f'Heartbeat: Neighbour ({hosts.neighbour}) responds.')
                #sock.send(b'HEARTBEAT') #added

            except:
                # Handle the failure to connect to the neighbour
                print(f'Heartbeat: Failed to connect to Neighbour ({hosts.neighbour}).')
                hosts.server_list.remove(hosts.neighbour)

                if hosts.leader == hosts.neighbour:
                    print(f'Heartbeat: >>>>> The Server Leader ({hosts.neighbour}) crashed.')
                    hosts.is_leader_server_crashed = True
                    hosts.leader = hosts.my_ip
                    hosts.is_network_changed = True

                else:
                    print(f'Heartbeat: Server Reproduction ({hosts.neighbour}) crashed.')
                    hosts.has_server_replication_crashed = 'True'

            finally:
                sock.close()
        else:
            print(f'Heartbeat: No neighbours found in the ring.')
            sleep(5)
