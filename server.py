import socket
import pyperclip
import threading
import time

# SETTING UP CONSTANTS
# HardCode IP (or check network adapter settings) if there is problem fetching IP
# Change PORT if 9999 not available
SERVER = socket.gethostbyname(socket.gethostname())
PORT = 9999
ADDR = (SERVER, PORT)
HEADER = 64
FORMAT = 'utf-8'
SEND = True
PREVIOUS = ' '
CANCELLABLE = True
DISCONNECT = '  '

# DATA RECEIVER
# First receives number of bytes to receive
# Then runs loop until all bytes are received
def receiveData(client):
    global SEND
    global PREVIOUS
    while True:
        try:
            text_length = client.recv(HEADER).decode(FORMAT)
            if text_length:
                text_length = int(text_length)
                received = 0
                text = ""
                while received != text_length:
                    bytes = client.recv(text_length - received)
                    received += len(bytes)
                    text += bytes.decode(FORMAT)
                if text == DISCONNECT:
                    break
                SEND = False
                PREVIOUS = text
                print('Received')
                pyperclip.copy(text)
        except:
            break
    client.close()
    while CANCELLABLE:
        pyperclip.copy(' ')


# DATA SENDER
# First sends number of bytes being sent
# Then runs loop until all data is sent
def send(msg):
    message = msg.encode(FORMAT)
    msg_length = len(message)
    send_length = str(msg_length)
    send_length += ' ' * (HEADER - len(send_length))
    send_length = send_length.encode(FORMAT)
    try:
        conn.send(send_length)
        sent = 0
        while sent != msg_length:
            sent += conn.send(message[sent:])
    except:
        return False
    print('Sent')
    return True


# CREATING / BINDING / LISTENING
print("[STARTING] Server starting...")
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)
server.listen()
print("[STARTED] Server started...")
print('[IP] Server IP:', SERVER)
print('[PORT] Server Port:', PORT)
print("[READY] Ready to connect client...")

# ACCEPTING CONNECTION
conn, addr = server.accept()
print('[CONNECTED] Connected to', addr)

# SETTING UP RECEIVER THREAD
# noinspection PyTypeChecker
thread = threading.Thread(target=receiveData, args=(conn,))
thread.start()

# SEND DATA WHEN CLIPBOARD TEXT CHANGES
while True:
    CANCELLABLE = True
    pyperclip.waitForNewPaste()
    if SEND:
        if not send(pyperclip.paste()):
            CANCELLABLE = False
            break
    SEND = True

thread.join()
if PREVIOUS != ' ':
    pyperclip.copy(PREVIOUS)
    
server.close()
print('[DISCONNECT] Client Disconnected...')
print('[CLOSING] Closing server...')
input('Press ENTER to exit...')
