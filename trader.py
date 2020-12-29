import keys
import alpaca_trade_api as tradeapi
import threading
import time
import datetime


class baseTrader:
    def __init__(self, APCA_API_BASE_URL, stockUniverse):
        self.alpaca = tradeapi.REST(keys.API_KEY, keys.API_SECRET, APCA_API_BASE_URL, 'v2')
        self.allStocks = self._format_all_stocks(stockUniverse)


    def _cancel_existing_orders(self):
        # First, cancel any existing orders so they don't impact our buying power.
        orders = self.alpaca.list_orders(status="open")
        for order in orders:
          self.alpaca.cancel_order(order.id)


    def _format_all_stocks(self, stockUniverse):
        # Format the allStocks variable for use in the class.
        allStocks = []
        for stock in stockUniverse:
          allStocks.append([stock, 0])
        return allStocks


    def _wait_market_open(self):
        # Wait for market to open.
        print("Waiting for market to open...")
        tAMO = threading.Thread(target=self._wait_market_open_helper())
        tAMO.start()
        tAMO.join()
        print("Market is open.")


    def _wait_market_open_helper(self):
        isOpen = self.alpaca.get_clock().is_open
        while(not isOpen):
          clock = self.alpaca.get_clock()
          openingTime = clock.next_open.replace(tzinfo=datetime.timezone.utc).timestamp()
          currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
          timeToOpen = int((openingTime - currTime) / 60)
          print(str(timeToOpen) + " minutes til market open.")
          time.sleep(60)
          isOpen = self.alpaca.get_clock().is_open


    def get_time_to_close(self):
    # returns in seconds, prints in minutes
      clock = self.alpaca.get_clock()
      closingTime = clock.next_close.replace(tzinfo=datetime.timezone.utc).timestamp()
      currTime = clock.timestamp.replace(tzinfo=datetime.timezone.utc).timestamp()
      self.timeToClose = closingTime - currTime
      print("Time to close (min): ", str(self.timeToClose / float(60)))


    def get_percent_changes(self, duration):
    # Get percent changes of the stock prices over the past 'duration' minutes.
        for i, stock in enumerate(self.allStocks):
          bars = self.alpaca.get_barset(stock[0], 'minute', duration)
          self.allStocks[i][1] = (bars[stock[0]][len(bars[stock[0]]) - 1].c - bars[stock[0]][0].o) / bars[stock[0]][0].o


    def run(self, cancel=True):
        if cancel: 
          self._cancel_existing_orders()
        self._wait_market_open()
        self.get_time_to_close()
        self.get_percent_changes(15)


