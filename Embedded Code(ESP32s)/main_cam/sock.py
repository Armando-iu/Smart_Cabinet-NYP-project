import socket

def _init(SERVER_IP , SERVER_PORT , name):
    '''
        - For all devices connected to the server must follow this convention when connecting:
            - wait for server to send "id" to ur device
            - after received "id" send "new~(enter device id here)" 
                - Convention is that device id is in 3 letters
            - wait for "send" from the server than u can send information.

        - This is to ensure that the server has registered the device and the device acknowledges this
        - all socket devices in this case send and receive info
    '''
    client_socket = socket.socket()
    client_socket.connect((SERVER_IP, SERVER_PORT)) # cinnect to server
    print("done power socket")

    while True:
        msg = client_socket.recv(35)
        print(msg)
        if b"id" in msg: #wait for the request for id declaration
            break
    
    id_name = b"new~" + name.encode('utf-8') # the "new~" is for registeringthis device for the server
    client_socket.send(id_name) # sends the registration id
    print("confirm")

    '''
     FYI: i dont identify clients by id_name but i identify based on remote address or peer name(which is from clientsocket.getpeername())
     - but for convinience on coding side, i use id to link with remote address(unique address)
         so ex:
            i can link esp32 wroom's id "cab" with "xyz" remote address
            to send info from server I only need to find "cab" to send info to esp32 wroom
                - Hence i can do sending without hard coding remote address on my pc
    '''

    while b"start" not in client_socket.recv(32): # only starts if server got the message of the registration id
        continue 
    return client_socket

def send_b_msg(client_socket , msg):
    '''
    - sending can only be in utf-8 or base64
    - I made a pretty weird convenient that looks like:
        https://www.canva.com/design/DAGJTyrvH_w/cjLpcchwf4Gd9K_r6uydag/edit?utm_content=DAGJTyrvH_w&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton
    - So to ensure there is always space for data packets to come into the server
    - However, u dont need to use this convenient to send information to the server
    
    Note:
        - the last time I checked, Sanjeev's smartwatch does not follow this convenient 
        - if i am not wrong it does not have a size declaration
    '''
    client_socket.send(b"size-{}".format(len(msg))) # sends size declaration
    while b"send" not in client_socket.recv(32): # waits for "send" message by server. acts as a hang statement
        continue
    client_socket.send(msg) # sends message
    return True