# Begin calculateStopLossPrice.py

from AlgorithmImports import *
import config as c
import variables as v

def calculateStopLossPrice(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'): # Confirm this is a valid data point

            indicators = v.indicators[symbol]

            v.stop_loss_atr_price[symbol] = (
                v.current_price[symbol] - (indicators["atr"].Current.Value * c.sell_parameter_stop_loss_price_atr_multiplier) 
                if c.sell_condition_stop_loss_atr_price and indicators["atr"].IsReady else 0
            )                
                # ATR Multiplier-Based Stop Loss Price: Price set by using the Average True Range value, a measure of market volatility, to determine a stop loss level that adjusts with the asset's recent price fluctuations.
        
            v.stop_loss_fibonacci_prices[symbol] = [v.current_price[symbol] * (1 + level) for level in c.sell_parameter_stop_loss_fibonacci_retracement_levels]
            v.stop_loss_fib_atr_price[symbol] = (
                min(v.stop_loss_fibonacci_prices[symbol]) + indicators["atr"].Current.Value 
                if c.sell_condition_stop_loss_fibonacci_atr_price and indicators["atr"].IsReady else 0
            )                
                # Fibonacci levels with ATR: This approach adjusts stop loss levels not only based on historical price patterns (Fibonacci retracements) but also considers recent market volatility (ATR), aiming to provide a more dynamic and context-sensitive stop loss strategy.

            v.stop_loss_trailing_price[symbol] = (
                v.current_price[symbol] * (1 - c.sell_parameter_stop_loss_trailing_percent) 
                if c.sell_condition_stop_loss_trailing_percent else 0
            )
                # Trailing-Based Stop Loss Price: Price to sell share at a determined price when it drops x% from the stock's highest price since purchase.

            v.stop_loss_percent_price[symbol] = (
                v.current_price[symbol] * (1 - c.sell_condition_stop_loss_percent) 
                if c.sell_condition_stop_loss_percent else 0
            )            
                # Percentage-Based Stop Loss Price: Price to sell if position loss hits this fixed %. Good in case ATR or Trailing Stop Loss Prices fail or are to high, to avoid losing too much on the position.

            # Combining methods: Choose the largest of the three for the most highst conservative stop-loss.
            v.stop_loss_max_price[symbol] = max(
                v.stop_loss_percent_price[symbol], 
                v.stop_loss_atr_price[symbol], 
                v.stop_loss_trailing_price[symbol]
            )            
            return v.stop_loss_max_price[symbol]
        
        else:
            return None  # Return None if symbol is not in data or data[symbol] is None
        
    except Exception as e:
        self.Error(f"Error on calculateStopLossPrice for {symbol}: {str(e)}")
        return None  # Return None in case of an exception

# End calculateStopLossPrice.py