import threading
import websocket
import json
import time
import hmac
import hashlib


BINANCE_API_KEY = 'your_api_key'
BINANCE_API_SECRET = b'your_api_secret'
BINANCE_SYMBOL = 'btcusdt'
BINANCE_INTERVAL = '5m'

BITFINEX_API_KEY = 'your_api_key'
BITFINEX_API_SECRET = b'your_api_secret'
BITFINEX_SYMBOL = 'tBTCUSD'
BITFINEX_TIMEFRAME = '1m'


binance_price_changes = []
binance_gains = []
binance_losses = []
binance_average_gain = 0
binance_average_loss = 0
binance_RSI = 0

bitfinex_price_changes = []
bitfinex_VWAP = 0


def binance_calculate_RSI(price_change):
    global binance_gains, binance_losses, binance_average_gain, binance_average_loss, binance_RSI

    # Вычисление прироста и потери
    gain = max(0, price_change)
    loss = abs(min(0, price_change))

    # Добавление прироста и потери в список
    binance_gains.append(gain)
    binance_losses.append(loss)

    # Рассчет средних прироста и потери
    if len(binance_gains) >= 14:
        if len(binance_gains) == 14:
            binance_average_gain = sum(binance_gains) / 14
            binance_average_loss = sum(binance_losses) / 14
        else:
            binance_average_gain = ((binance_average_gain * 13) + gain) / 14
            binance_average_loss = ((binance_average_loss * 13) + loss) / 14

        # Рассчет relative strength и RSI
        relative_strength = binance_average_gain / binance_average_loss
        binance_RSI = 100 - (100 / (1 + relative_strength))

        print(f"Binance: RSI: {binance_RSI}")

def binance_on_message(ws, message):
    data = json.loads(message)

    # Проверка на свечку
    if 'k' in data:
        candle = data['k']
        close_price = float(candle['c'])

        # Смотрим изменение цены
        if len(binance_price_changes) > 0:
            price_change = close_price - binance_price_changes[-1]
            binance_calculate_RSI(price_change)

        # Сюда добавляем цену закрытия в список price_changes
        binance_price_changes.append(close_price)

def binance_run():
    # Подключаемся через вебсокет 
    stream_name = f"{BINANCE_SYMBOL}@kline_{BINANCE_INTERVAL}"
    wss = f"wss://stream.binance.com:9443/ws/{stream_name}"
    ws = websocket.WebSocketApp(wss, on_message=binance_on_message)

    ws.run_forever()

def on_open(ws):
    # Подписываемся на канал свечей
    ws.send(json.dumps({
        "event": "subscribe",
        "channel": "candles",
        "key": "trade:1m:tBTCUSD"
    }))

def on_message(ws, message):
    # Обрабатываем сообщение
    print(message)

def on_error(ws, error):
    # Обрабатываем ошибку
    print(error)

def on_close(ws):
    # Обрабатываем закрытие соединения
    print("Connection closed")

def bitfinex_on_message(ws, message):
    data = json.loads(message)

    # Проверка на свечку
    if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
        candle = data[1]
        close_price = float(candle[2])

        # Рассчет VWAP
        total_volume = 0
        volume_weighted_sum = 0

        for data_point in data:
            if isinstance(data_point, list):
                volume = float(data_point[5])
                price = float(data_point[2])
                volume_weighted_sum += price * volume
                total_volume += volume

        vwap = volume_weighted_sum / total_volume

        # Выводим VWAP
        print(f"Bitfinex: Close price: {close_price}, VWAP: {vwap}")

def bitfinex_run():
    # Подключаемся через вебсокет 
    wss = f"wss://api.bitfinex.com/ws/2"
    ws = websocket.WebSocketApp(wss, on_open=on_open, on_message=bitfinex_on_message)

    ws.run_forever()

if __name__ == '__main__':
    # Запускаем Binance 
    binance_thread = threading.Thread(target=binance_run)
    binance_thread.start()

    # И запускаем Bitfinex  
    bitfinex_thread = threading.Thread(target=bitfinex_run)
    bitfinex_thread.start()
