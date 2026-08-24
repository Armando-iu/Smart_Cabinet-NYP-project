import network
import time

print("connecting")

def conn_wifi(WIFI_SSID , WIFI_PASS):
    sta_if = network.WLAN(network.STA_IF)# make a WLAN network interface that connects to wifis APs
    sta_if.active(True) # activate the station interface
    while sta_if.isconnected() != True:# continously try to connect to wifi 
        all_wifi = sta_if.scan()                             # Scan for available access points(AP)
        print("all wifi: {}".format(all_wifi))
        for wifi in all_wifi:  
            if WIFI_SSID in wifi[0]: # check if all surrounding wifi that has an ssid of WIFI_SSID
                print("no")
                print("bssid {} , channel: {} , RSSI: {} , security: {} , hidden: {}".format(wifi[1] , wifi[2] , wifi[3] , wifi[4] , wifi[5]))
                sta_if.connect(WIFI_SSID, WIFI_PASS) # Connect to an AP
        time.sleep(0.1)