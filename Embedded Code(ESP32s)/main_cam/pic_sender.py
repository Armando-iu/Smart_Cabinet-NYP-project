from main_cam import wifi
from main_cam import sock
import camera
# import _thread #for some reason it messes with the camera

# paramaters to pass in
WIFI_SSID = "TP-Link_66EC"
WIFI_PASS = "34252857"
SERVER_IP = '192.168.0.101'
SERVER_PORT = 5001
#

def pic_taking():
    ''' 
        - will continually try to take picture. 
        - if it takes a picture it will leave the function 
    '''
    while True:
        try:
            camera.init(0, format=camera.JPEG) # fb location means frame buffer location. You would have to initialise every time you would want to take a picture
            pic_in_bytes = camera.capture()
            print(len(pic_in_bytes))
            size = len(pic_in_bytes)
            return pic_in_bytes , size
        except Exception as e:
            print("error")
        finally:
            camera.deinit() # de initialise after every picture
                      
wifi.conn_wifi(WIFI_SSID , WIFI_PASS) #to connect to wifi
print("done wifi")
client_socket = sock._init(SERVER_IP , SERVER_PORT , "img") #to connect to server and initialise sender id as "img"

while True:
    req_server = client_socket.recv(35) # listens for request from server
    print("requested")
    if req_server == b"img":
        pic , size = pic_taking() 

        # saves the picture locally on the esp32 cam. Mainly used for debugging 
        file = open("stuff.jpg" , "w")
        file.write(pic)
        file.close()

        sock.send_b_msg(client_socket , pic) # sends size declaration and picture
