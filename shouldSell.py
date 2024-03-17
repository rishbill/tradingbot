from AlgorithmImports import *
import config

def shouldSell(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'):            
            current_price = data[symbol].Price
            take_profit_price = CalculateTakeProfitPrice(self, symbol, data)
            stop_loss_price = CalculateStopLossPrice(self, symbol, data)
            # Pattern Day Trader condition
            if len(config.day_trade_dates) >= 3 and self.Portfolio.Cash < 25000:
                self.Debug(f"Sell Decision: False for {symbol}. Reason: PDT Rule is in effect, and max day trades reached for period. (Day Trades last 5 days: {config.day_trade_counter}, Portfolio Value: {self.Portfolio.TotalPortfolioValue}")
                return False
            # Take Profit condition
            elif current_price >= take_profit_price:
                self.Debug(f"Sell Decision: True for {symbol}. Reason: Take Profit. Current Price: {current_price}, Target: {take_profit_price}")
                return True
            # Stop Loss condition
            elif current_price <= stop_loss_price:
                self.Debug(f"Sell Decision: True for {symbol}. Reason: Stop Loss. Current Price: {current_price}, Target: {stop_loss_price}")
                return True
            return False
        else:
            return None  # Return None if symbol is not in data or data[symbol] is None
    except Exception as e:
        self.Debug(f"Error on shouldSell: {str(e)}")
        return False
