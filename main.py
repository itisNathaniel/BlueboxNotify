import time
import machine, neopixel
from umqtt import MQTTClient
import ubinascii
import network

# LED Config
lamp = neopixel.NeoPixel(machine.Pin(4), 12)
roof = neopixel.NeoPixel(machine.Pin(14), 12)

# MQTT Config
CLIENT_ID = ubinascii.hexlify(machine.unique_id())
TOPIC = "tardis"

interiorColour = (110,110,110);

##### Lamp Config
# lamp flash method
def lampFlash(colour):
    color = tuple(colour)
    for i in range(2):
        for i in range(3):
            lamp[6] = colour
            #lamp[5] = colour
            #lamp[7] = colour
            lamp.write()
            time.sleep_ms(1000)
        for i in range(80):
            lamp.fill((0,0,0))
            lamp.write()
        time.sleep_ms(1000)

# interior colour global change method
def interiorChangeGlobal(colour):
    color = tuple(colour)
    global interiorColour
    interiorColour = colour
    interiorChange(colour)

def fault():
    for i in range(1):
        for j in range(1):
            lampFlash((255,0,152))
            lampFlash((255,0,0))

# interior colour change method
def interiorChange(colour):
    color = tuple(colour)
    roofn = roof.n
    # set roof default colour
    for j in range(roofn):
        roof[j] = colour
    roof.write()

# change for a notification
def notification(notifColour):
    notifColour = tuple(notifColour)
    roofn = roof.n
    lampn = lamp.n

    # set roof to notifColour
    for j in range(roofn):
        roof[j] = notifColour
        roof.write()

    # lamp (fade in/out)
    lampFlash(notifColour)

    # clear lamp
    for i in range(lampn):
        lamp[i] = (0, 0, 0)
    lamp.write()

    # inside (cycle)
    for j in range(3):
        for i in range(roofn):
            roof[i] = (0,0,0)
            roof.write()
        for i in range(roofn):
            print("%2")
            if (i % 2 == 0):
                roof[i] = notifColour
                roof.write()
            time.sleep_ms(80)
        print("set to zero")
        for i in range(roofn):
            roof[i] = (0,0,0)
            roof.write()
        print("!=")
        for i in range(roofn):
            if (i % 2 != 0):
                roof[i] = notifColour
                roof.write()

    # for i in range(2 * roofn):
    #     for j in range(roofn):
    #         roof[j] = (0,0,0)
    #     roof[i % roofn] = notifColour
    #     roof.write()
    #     time.sleep_ms(80)

    # set roof to notifColour
    print("set roof")
    for j in range(roofn):
        roof[j] = notifColour
        roof.write()
    time.sleep_ms(6000)

    for i in range(roofn):
        roof[i] = interiorColour
        roof.write()


## MQTT Config

def sub_cb(tardis, msg):
    print((TOPIC, msg))
    msg = msg.decode("utf-8")
    if msg.startswith( 'lamp' ):
        lamp = msg[4:]
        lamp = tuple(map(int, lamp.split(',')))
        print(lamp)
        lampFlash(lamp)
    elif msg.startswith( 'interior' ):
        interior = msg[8:]
        interior = tuple(map(int, interior.split(',')))
        print(interior)
        interiorChangeGlobal(interior)
    elif msg.startswith( 'notify' ):
        interior = msg[6:]
        interior = tuple(map(int, interior.split(',')))
        print(interior)
        notification(interior)

def runMQTT(server=SERVER):
    while True:
        # Server based data
        port = 8883
        user = "USERNAME-REDACTED"
        password = "PASSWORD-REDACTED"
        keepalive = 1
        ssl = True

        c = MQTTClient(CLIENT_ID, SERVER, 1883, user, password,0, False)
        # Subscribed messages will be delivered to this callback
        c.set_callback(sub_cb)
        try:
            ap_if.active(False)
            c.connect()
            c.subscribe(TOPIC)
            print("Connected to %s, subscribed to %s topic" % (server, TOPIC))
            interiorChangeGlobal(interiorColour)
            lampFlash(interiorColour)

            try:
                while 1:
                    ap_if.active(True)
                    c.wait_msg()
            finally:
                c.disconnect()

        except OSError as e:
            fault()
            print("fault - server not found :(")
            time.sleep(120)


print("Give ourselves some time to connect to the internet...")


station = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)
print(station.ifconfig())
runMQTT("DOMAIN-REDACTED")
