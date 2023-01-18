import logging
import requests
import pandas as pd
import time
import yfinance as yf

logging.basicConfig(level=logging.INFO)

stock_symbols = ['GOOG', 'MSFT', 'BTC-USD', 'ETH-USD', 'ADA-USD']

def get_finance_data(stock_symbol):
    logging.info(f'Getting data from Yahoo Finance for stock {stock_symbol}')

    google = yf.Ticker(stock_symbol)        
    df = google.history(period='1d', interval="1m")[['Low']]
    if (df.size > 0):
        logging.info(f'Data found. Last value dated on {df.index[-1]}')
        return df
    else:
        logging.info(f'No data found for stock symbol: {stock_symbol}')
        return None

def get_last_price(stock_symbol):
    price_data = get_finance_data(stock_symbol)

    if price_data is not None:
        last_element = price_data.tail(1)
        last_row = last_element.iloc[0]
        
        return last_row['Low']
    else:
        return None

while True:

  prices = {}

  for stock_symbol in stock_symbols:
    
    price = get_last_price(stock_symbol)
    logging.info(f'Price of stock is {price}')
    if price is not None:
      prices[stock_symbol] = price

    time.sleep(0.2)  # sleep a bit to not query too fast

  payload = []
  payload.append('# TYPE stock_price gauge')
  for symbol, price in prices.items():
    payload.append('stock_price{sym="%s"} %f' % (symbol, price))

  try:
    requests.delete('http://prometheus-pushgateway:9091/metrics/job/stocks-data')
  except IOError as e:
    logging.exception('Could not delete stock data', e)
    continue

  try:
    requests.post(
      'http://prometheus-pushgateway:9091/metrics/job/stocks-data',
      data='\n'.join(payload) + '\n')
  except IOError as e:
    logging.exception(f'Could not push price of {stock_symbol}', e)

  time.sleep(30)
