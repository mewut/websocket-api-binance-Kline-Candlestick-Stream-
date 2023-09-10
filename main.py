import websocket
import json
import pandas
import numpy
from binance.client import Client


# Binance API client
api_key = 'your_api_key'
api_secret = 'your_api_secret'
client = Client(api_key, api_secret)

symbol = 'BTCUSDT'
interval = Client.KLINE_INTERVAL_5MINUTE

price_changes = []
gains = []
losses = []
average_gain = 0
average_loss = 0
RSI = 0

def calculate_RSI(price_change):
    global gains, losses, average_gain, average_loss, RSI

    # Вычисление прироста и потери 
    gain = max(0, price_change)
    loss = abs(min(0, price_change))

    # Добавление прироста и потери в список
    gains.append(gain)
    losses.append(loss)

    # Рассчет средних прироста и потери
    if len(gains) >= 14:
        if len(gains) == 14:
            average_gain = sum(gains) / 14
            average_loss = sum(losses) / 14
        else:
            average_gain = ((average_gain * 13) + gain) / 14
            average_loss = ((average_loss * 13) + loss) / 14

        # Рассчет relative strength и RSI
        relative_strength = average_gain / average_loss
        RSI = 100 - (100 / (1 + relative_strength))

        print(f"RSI: {RSI}")

def on_message(ws, message):
    global price_changes

    # парсим в JSON
    data = json.loads(message)

    # Получаем данные из свечек
    candlestick = data['k']
    close_price = float(candlestick['c'])
    open_price = float(candlestick['o'])
    high_price = float(candlestick['h'])
    low_price = float(candlestick['l'])

    # Считаем изменение цены
    if len(price_changes) > 0:
        price_change = close_price - price_changes[-1]
        calculate_RSI(price_change)

    # Сюда добавляем цену закрытия в список price_changes 
    price_changes.append(close_price)

    # Выводим данные из свечей
    print(f"Open: {open_price}, High: {high_price}, Low: {low_price}, Close: {close_price}")

def run():
    # подключаемся через вебсокет 
    stream_name = f"{symbol.lower()}@kline_{interval}"
    wss = f"wss://stream.binance.com:9443/ws/{stream_name}"
    ws = websocket.WebSocketApp(wss, on_message=on_message)

    ws.run_forever()

if __name__ == '__main__':
    run()
