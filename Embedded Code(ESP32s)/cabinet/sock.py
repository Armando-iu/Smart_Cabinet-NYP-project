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
    client_socket.connect((SERVER_IP, SERVER_PORT))
    print("done power socket")

    while True:
        msg = client_socket.recv(35)
        print(msg)
        if b"id" in msg:
            break
    
    id_name = b"new~" + name.encode('utf-8')
    '''
     FYI: i dont identify clients by id_name but i identify based on remote address or peer name(which is from clientsocket.getpeername())
     - but for convinience on coding side, i use id to link it with the remote address(unique address)
         so ex:
            i can link esp32 wroom's id "cab" with "xyz" remote address
            to send info from server I only need to find "cab" to send info to esp32 wroom
                - Hence i can do sending without hard coding remote address on my pc
    '''
    client_socket.send(id_name)  
    print("confirm")
    while b"start" not in client_socket.recv(32): # acts as a hang statement
        continue 
    return client_socket

def send_b_msg(client_socket , msg):
    client_socket.send(b"size-{}".format(len(msg)))
    while b"send" not in client_socket.recv(32): # acts as a hang statement
        continue
    print(f"sending msg {msg}")
    client_socket.send(msg)
    print("finish sending msg")
    return True
