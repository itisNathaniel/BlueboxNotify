# handle wifi
def do_connect():
    import network
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected():
        print('connecting to network...')
        sta_if.active(True)
        print('Attempting to connect to NET1-REDACTED:')
        sta_if.connect('NET1-REDACTED', '')
        print('Attempting to connect to NET2-REDACTED:')
        sta_if.connect('NET2-REDACTED', '')
        while not sta_if.isconnected():
            pass
    print('network config:', sta_if.ifconfig())

do_connect();
