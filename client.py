# import of required modules
import hosts
import multicast_sender
import socket
import threading
import os
from time import sleep


def connect_to_server(username):
    """
    Create client socket and connect to the server leader.
    
    Parameters:
    username (str): The username of the client.
    """
    global sock

    # Create a new socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # Check if the server exists and send join request
    server_exist = multicast_sender.sending_join_request()

    if server_exist:
        leader_address = (hosts.leader, hosts.server_port)
        print(f'\nConnection successful! The Server leader is located at: {leader_address}')

        # Connect to the server leader
        sock.connect(leader_address)
        # Send a join message with the username
        sock.send(f'JOIN {username}'.encode(hosts.unicode))
        print(f'Hey {username}, welcome to the Chat Room! You have successfully connected to the Server Leader.')

    else:
        print('Unable to find a Server at the moment. Please try to connect again later.')
        os._exit(0)


def receive_messages():
    """
    Receive messages from the server leader.
    """
    global sock
    while True:
        try:
            data_received = sock.recv(hosts.buffer_size)
            print(f"{data_received.decode(hosts.unicode)}")
            if not data_received:
                print(f'\nThe Connection to the Server has been lost. Attempting to reconnect...')
                sock.close()
                sleep(3)
                connect_to_server(username)

        except socket.error as e:
            if e.errno == 10054:
                sock.close()
                print(f'\nThe Connection to the Server has been unexpectedly lost. Attempting to reconnect...')
                sleep(4)
                connect_to_server(username)

        except Exception as e:
            print(f'An Error occurred: {e}')
            sock.close()
            break


def send_messages(username):
    """
    Send messages to the server leader.
    
    Parameters:
    username (str): The username of the client.
    """
    global sock
    while True:
        message = input('Type in your Message here: ')

        try:
            send_message = f"{username}: '{message}'".encode(hosts.unicode)
            sock.send(send_message)
            print(f'\n----> Your Message was sent.')

        except Exception as e:
            print(f'An Error occurred while sending your Message: {e}')
            sock.close()
            break


def thread(target, args):
    """
    Creates and start a new daemon thread.
    
    Parameters:
    target (function): The target function to be executed in the thread.
    args (tuple): The arguments to be passed to the target function.
    """
    thread = threading.Thread(target=target, args=args)
    thread.daemon = True
    thread.start()



# Main Thread
if __name__ == '__main__':
    """
    The following block of code will only run if this script is executed directly. 
    If the script is imported as a module in another script, this block will not run.
    This is controlled by checking if the special variable `__name__` is set to `'__main__'`.
    """
    try:
        print('Attempting to enter the chat room.')
        username = input('Please enter your username: ')

        # Establish connection to the server leader
        connect_to_server(username)

        # Start threads
        thread(send_messages, (username,))
        thread(receive_messages, ())

        # Keep the main thread running to keep the daemon threads active
        while True:
            pass

    except KeyboardInterrupt:
        print(f'\nYou have exited the Chat Room. Goodbye!')
        # soc.send(f"{username} left".encode(hosts.unicode))
