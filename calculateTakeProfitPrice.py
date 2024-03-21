# Begin calculateTakeProfitPrice.py

from AlgorithmImports import *
import config as c
import variables as v

def calculateTakeProfitPrice(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'): # Confirm this is a valid data point
            
            indicators = v.indicators[symbol]

            v.take_profit_atr_price[symbol] = (
                v.current_price[symbol] - (indicators["atr"].Current.Value * c.sell_parameter_take_profit_price_atr_multiplier) 
                if c.sell_condition_take_profit_atr_price and indicators["atr"].IsReady else 0
            )
                # ATR Multiplier-Based take profit Price: Price set by using the Average True Range value, a measure of market volatility, to determine a take profit level that adjusts with the asset's recent price fluctuations.

            v.take_profit_fib_atr_price[symbol] = (
                min(v.take_profit_fibonacci_prices[symbol]) + indicators["atr"].Current.Value 
                if c.sell_condition_take_profit_fibonacci_atr_price and indicators["atr"].IsReady else 0
            )
                # Fibonacci levels with ATR: This approach adjusts take profit levels not only based on historical price patterns (Fibonacci retracements) but also considers recent market volatility (ATR), aiming to provide a more dynamic and context-sensitive take profit strategy.

            v.take_profit_trailing_price[symbol] = (
                v.current_price[symbol] * (1 + c.sell_parameter_take_profit_trailing_percent) 
                if c.sell_condition_take_profit_trailing_percent else 0
            )
                # Trailing-Based Take Profit Price: Price to sell share at a determined price when it drops x% from the stock's highest price since purchase.

            v.take_profit_percent_price[symbol] = (
                v.current_price[symbol] * (1 + c.sell_parameter_take_profit_percent) 
                if c.sell_condition_take_profit_percent else 0
            )
                # Percentage-Based Take Profit Price: Price to sell if position loss hits this fixed %. Good in case ATR or Trailing take profit Prices fail or are to high, to avoid losing too much on the position.

            # Combine methods: Choose the most conservative (highest) take-profit price
            v.take_profit_max_price[symbol] = max(
                v.take_profit_percent_price[symbol], 
                v.take_profit_fib_atr_price[symbol], 
                v.take_profit_trailing_price[symbol]
            )

            return v.take_profit_max_price[symbol]

        else:
            return None  # Return None if symbol is not in data or data[symbol] is None
                                                    
    except Exception as e:
        self.Error(f"Error in calculateTakeProfitPrice for {symbol}: {str(e)}")
        return None  # Return None in case of an exception

# End calculateTakeProfitPrice.py