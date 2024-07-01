# import of required modules
import socket
import hosts


"""
This module provides functions to manage and maintain a ring topology 
for a distributed system. It includes functionality to form a sorted ring 
of IP addresses, find neighboring nodes, and initiate leader election.
"""

def form_ring(members):
    """"
    Sorts and forms a ring of IP addresses from a list of members (servers).
    
    Parameters:
    members (list): List of IP addresses as strings.
    
    Returns:
    list: Sorted list of IP addresses forming a ring.
    """
    sorted_ring = sorted([socket.inet_aton(member) for member in members])
    sorted_ip_ring = [socket.inet_ntoa(node) for node in sorted_ring]
    return sorted_ip_ring


def get_neighbour(ring, current_node_ip, direction='left'):
    """
    Finds the neighbour node in the ring from the view of the current node.
    
    Parameters:
    ring_members (list): List of IP addresses in the ring.
    current_node_ip (str): IP address of the current node.
    direction (str): Direction to find the neighbour ('left' or 'right').
    
    Returns:
    str: IP address of the neighboring node or None if not found.
    """
    # Find the index of the current node in the ring
    current_node_index = ring.index(current_node_ip) if current_node_ip in ring else -1
    if current_node_index != -1:
        if direction == 'left':
            if current_node_index + 1 == len(ring):
                return ring[0]
            else:
                return ring[current_node_index + 1]
        else:
            if current_node_index == 0:
                return ring[-1]
            else:
                return ring[current_node_index - 1]
    else:
        # Return None if the current node IP is not in the ring members
        print(f'\nThe current Node is not in the ring.')
        return None


def starting_server_leader_election(server_list, leader_server):
    """
    Initiates the server leader election in the  ring.
    
    Parameters:
    server_list (list): List of IP addresses of the servers.
    leader_server (str): IP address of the current leader server.
    
    Returns:
    str: IP address of the next node to contact for election.
    """
    # Form the ring from the list of servers
    ring = form_ring(server_list)
    # print(f'\n****** The Server Leader will be elected from the following Servers: \n {server_list}')
    print(f'Ring: {ring}')
    
    # Get the neighbour in the specified direction
    neighbour = get_neighbour(ring, leader_server, 'right')
    print(f'\n******* The current Neighbour is: {neighbour}')
    
    # Return the next node to contact for election, ensuring it's not the same as the current node
    return neighbour if neighbour != hosts.my_ip else None