import socket

"""
This module sets up the initial configuration for a distributed chat application.
It includes the initialization of the socket to determine the server's own IP address,
configuration variables, port and address settings, and other essential variables
for managing the network topology and state.
"""

# Initialization of the socket to determine the own IP address
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
try:
    # Connecting to a remote server to get the local machine's IP address
    sock.connect(("8.8.8.8", 80))
    my_ip = socket.gethostbyname(socket.gethostname())
finally:
    # Close the socket after obtaining the IP address
    sock.close()

# Configuration variables
buffer_size = 4096                  # Size of the buffer for socket communication
unicode = 'utf-8'                   # Character encoding used in the application

# Ports and addresses
server_port = 10001                 # Port used by the server
multicast_port = 10000              # Port used for multicast communication
multicast_address = '224.0.0.0'     # Multicast group address

# Initialization of variables
leader = ''                         # IP address of the leader server
neighbour = ''                      # IP address of the neighbouring server
node_id = ''                        # Unique identifier for the node
server_list = []                    # List of all servers in the network
client_list = []                    # List of all clients connected to the server

# Static variables
is_network_changed = False          # Flag to indicate if the network topology has changed
is_election_in_progess = False      # Flag to indicate if a leader election is in progress
is_leader_server_crashed = ''       # Flag to indicate if the leader server has crashed
has_server_replication_crashed = '' # Flag to indicate if server replication has crashed
