import telebot
import ccxt
import time
import logging

# Инициализация бота
API_TOKEN = '8035373557:AAGn-jF969Jjjxi8gNK4_CtSaNvbZABfPJo'
bot = telebot.TeleBot(API_TOKEN)

# Настройка логгера
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Инициализация бирж
binance = ccxt.binance()
okx = ccxt.okx()
bybit = ccxt.bybit()
bitget = ccxt.bitget()
kucoin = ccxt.kucoin()
bingx = ccxt.bingx()
exmo = ccxt.exmo()

# Параметры для арбитража
MIN_PROFIT = 0.1  # Минимальная прибыль в процентах
COIN_PAIRS = [
    'BTC/USDT',
    'ETH/USDT',
    'RDNT/USDT',
    'LTC/USDT',
    'BNB/USDT'  # Добавили ещё одну популярную монету BNB
]

EXCHANGES = {'binance': binance, 'okx': okx, 'bybit': bybit, 'bitget': bitget, 'kucoin': kucoin, 'bingx': bingx, 'exmo': exmo}

def get_prices(coin_pair):
    """Получение текущих цен по заданной паре,"""
    prices = {}
    for exchange_name, exchange in EXCHANGES.items():
        try:
            ticker_data = exchange.fetch_ticker(coin_pair)
            prices[exchange_name] = ticker_data['last']
        except Exception as e:
            logger.error(f"Ошибка получения цен для {coin_pair} на бирже {exchange_name}: {e}")
    return prices

def calculate_profit(price1, price2):
    """Расчёт разницы цен в процентах"""
    return abs((price1 - price2) / price2 * 100)

def find_arbitrage_opportunities():
    results = []
    for coin_pair in COIN_PAIRS:
        prices = get_prices(coin_pair)
        if len(prices) < 2:  # Нужно минимум две биржи для сравнения
            continue

        exchanges = list(prices.keys())
        for i in range(len(exchanges)):
            for j in range(i + 1, len(exchanges)):
                exchange1 = exchanges[i]
                exchange2 = exchanges[j]
                profit = calculate_profit(prices[exchange1], prices[exchange2])
                if profit > MIN_PROFIT:
                    results.append(f"Вилка между {exchange1.upper()} и {exchange2.upper()} ({coin_pair}): {profit:.2f}%")

    return "\n".join(results) or "Арбитражных возможностей не найдено."

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "Бот запущен. Введите /help для получения инструкций.")

@bot.message_handler(commands=['help'])
def help(message):
    help_text = """
    Команды бота:
    /start - Запустить бот
    /help - Показать эту справку
    /find_arbitrage - Найти арбитражные возможности
    """
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['find_arbitrage'])
def find_arbitrage(message):
    result = find_arbitrage_opportunities()
    bot.reply_to(message, result)

def main():
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as e:
            logger.error(f"Ошибка работы бота: {e}")
            time.sleep(5)

if __name__ == '__main__':
    main()