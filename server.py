# import of required modules
import socket
import hosts
import multicast_sender
import multicast_listener
import heartbeat
import sys
import threading
import queue


# Create a new TCP socket for the server
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# Get the server's own IP address from the hosts module
host_address = (hosts.my_ip, hosts.server_port)

# Create a First-In-First-Out (FIFO) queue for storing messages
fifoQueue = queue.Queue()

# Boolean flag to indicate if the server is running
server_running = True


def handle_clients(client, address, username):
    """
    Handle received messages from connected clients.
    
    Parameters:
    client (socket): The client socket.
    address (tuple): The client's address.
    username (str): The client's username.
    """
    while True:
        try:
            data_received = client.recv(hosts.buffer_size)
            if not data_received:
                print(f'\nClient with Address {address} and Username {username} has disconnected.')
                fifoQueue.put(f'\nClient with Address {address} and Username {username} has disconnected.\n')
                break

            username, message = data_received.decode(hosts.unicode).split(': ', 1)
            fifoQueue.put(f'\n----> {username} wrote: {message}')
            print(f'\n==> New Message from {username}: {message}')

        except Exception as e:
            print(f'----> {username} has left the Chat.')
            break

    if client in hosts.client_list:
        hosts.client_list.remove(client)
    client.close()


def send_message_to_client():
    """
    Send all messages waiting in the queue to all clients.
    """
    message = ''
    while not fifoQueue.empty():
        message += f'{fifoQueue.get()}'
        message += '\n' if not fifoQueue.empty() else ''

    if message:
        for member in hosts.client_list:
            member.send(message.encode(hosts.unicode))


def show_participants():
    """
    Display information about the current server and client situation.
    """
    print(f'\nActive Servers: {hosts.server_list} >>>>>>>>> The current LEADER SERVER is: {hosts.leader}')
    print(f'\nActive Clients: {hosts.client_list}')
    print(f'\nServer Neighbour: {hosts.neighbour}\n')


def socket_binding():
    """
    Bind the TCP Server Socket and listen for connections.
    """
    sock.bind(host_address)
    sock.listen()
    print(f'\nThe Server has started and is listening on IP {hosts.my_ip} and Port {hosts.server_port}')

    while server_running:
        try:
            client, address = sock.accept()
            data_received = client.recv(hosts.buffer_size)

            if data_received.startswith(b'JOIN'):
                username = data_received.decode(hosts.unicode).split(' ', 1)[1]
                fifoQueue.put(f'\n===> Client {username} from {address} has joined the Chat.\n')
                print(f'\n===> Client {username} from {address} has joined the Chat.')
                hosts.client_list.append(client)
                thread(handle_clients, (client, address, username))  

        except Exception as e:
            print(f'An Error occurred: {e}', file=sys.stderr)
            break


def thread(target, args):
    """
    Create and start a new daemon thread.

    Parameters:
    target (function): The target function is to be executed in the thread.
    args (tuple): The arguments to be passed to the target function.
    """
    thread = threading.Thread(target=target, args=args)
    thread.daemon = True
    thread.start()


if __name__ == '__main__':
    """
    The following block of code will only run if this script is executed directly.
    It will set up the server, handle clients, and manage the server's state.
    """
    multicast_receiver_exist = multicast_sender.sending_request_to_multicast()

    if not multicast_receiver_exist:
        hosts.server_list.append(hosts.my_ip)
        hosts.leader = hosts.my_ip

    thread(multicast_listener.multicast_starts_listening, ())
    thread(socket_binding, ())
    thread(heartbeat.starting_heartbeats, ())

    while True:
        try:
            if hosts.leader == hosts.my_ip and hosts.is_network_changed or hosts.has_server_replication_crashed:
                if hosts.is_leader_server_crashed:
                    hosts.client_list = []
                multicast_sender.sending_request_to_multicast()
                hosts.is_leader_server_crashed = False
                hosts.is_network_changed = False
                hosts.replica_crashed = ''
                show_participants()

            if hosts.leader != hosts.my_ip and hosts.is_network_changed:
                hosts.is_network_changed = False
                show_participants()

            send_message_to_client()

        except KeyboardInterrupt:
            server_running = False
            print(f'\nServer on IP {hosts.my_ip} with Port {hosts.server_port} is shutting down.', file=sys.stderr)
            sock.close()
            break


