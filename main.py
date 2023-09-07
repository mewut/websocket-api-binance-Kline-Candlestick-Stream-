import websocket


# НЕ РАБОТАЕТ. Но я хочу сохранить это в коммите

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

    # Если достигнута длина 14 для расчета среднего прироста и средней потери
    if len(gains) >= 14:
        # Если это первое значение, инициализируем суммы прироста и потери
        if len(gains) == 14:
            average_gain = sum(gains) / 14
            average_loss = sum(losses) / 14
        else:
            # Расчет среднего прироста и средней потери с использованием экспоненциального скользящего среднего
            average_gain = ((average_gain * 13) + gain) / 14
            average_loss = ((average_loss * 13) + loss) / 14

        # Расчет relative_strength
        relative_strength = average_gain / average_loss

        # Расчет RSI по формуел
        RSI = 100 - (100 / (1 + relative_strength))

    print(f"RSI: {RSI}")


def on_message(_wsa, data):
    # Извлечение цены закрытия из полученных данных
    close_price = float(data['k']['c'])

    # Вычисление изменения цены 
    if len(price_changes) > 0:
        price_change = close_price - price_changes[-1]
        calculate_RSI(price_change)

    # Добавление текущей цены закрытия в список
    price_changes.append(close_price)


def run():
    print('hi')

    stream_name = 'btcusdt@kline_5m' # Пятиминутные свечи из доков Stream Name: <symbol>@kline_<interval>
    wss = 'wss://stream.binance.com:9443/ws/%s' % stream_name
    wsa = websocket.WebSocketApp(wss, on_message=on_message)
    wsa.run_forever()


if __name__ == '__main__':
    run()
