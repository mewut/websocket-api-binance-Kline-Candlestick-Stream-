import websocket


def on_message(_wsa, data):
    print(data, '\n\n')

def run():
    print('hi')

    stream_name = 'btcusdt@depth'
    wss = 'wss://stream.binance.com:9443/ws/%s' % stream_name
    wsa = websocket.WebSocketApp(wss, on_message=on_message)
    wsa.run_forever()

if __name__ == '__main__':
    run()
