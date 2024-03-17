from AlgorithmImports import *
import config as c
import variables as v

def calculateStopLossPrice(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'): # Confirm this is a valid data point

            v.atr_stop_loss_price[symbol] = v.current_price[symbol] - (v.atr[symbol] * c.sell_parameter_atr_stop_loss_price_multiplier) if c.sell_condition_atr_stop_loss_price else 0
                # ATR Multiplier-Based Stop Loss Price: Price set by using the Average True Range value, a measure of market volatility, to determine a stop loss level that adjusts with the asset's recent price fluctuations.
        
            v.fibonacci_stop_loss_prices[symbol] = [v.current_price[symbol] * (1 + level) for level in c.sell_parameter_stop_fibonacci_retracement_levels]
            v.fib_atr_stop_loss_price[symbol] = min(v.fibonacci_stop_loss_prices[symbol]) + v.atr[symbol] if c.sell_condition_fibonacci_atr_stop_price else 0
                # Fibonacci levels with ATR: This approach adjusts stop loss levels not only based on historical price patterns (Fibonacci retracements) but also considers recent market volatility (ATR), aiming to provide a more dynamic and context-sensitive stop loss strategy.
            
            v.trailing_stop_price[symbol] = v.current_price[symbol] * (1 - c.sell_parameter_trailing_stop_percent)
                # Trailing-Based Stop Loss Price: Price to sell share at a determined price when it drops x% from the stock's highest price since purchase.
            
            v.stop_loss_percent_price = v.current_price[symbol] * (1 - c.sell_parameter_stop_loss_percent)
                # Percentage-Based Stop Loss Price: Price to sell if position loss hits this fixed %. Good in case ATR or Trailing Stop Loss Prices fail or are to high, to avoid losing too much on the position.

            # Combining methods: Choose the largest of the three for the most highst conservative stop-loss.
            v.max_stop_loss_price[symbol] = max(v.stop_loss_percent_price[symbol], v.atr_stop_loss_price[symbol], v.trailing_stop_price[symbol])
            return v.max_stop_loss_price[symbol]
        
        else:
            return None  # Return None if symbol is not in data or data[symbol] is None
        
    except Exception as e:
        self.Error(f"Error on calculateStopLossPrice for {symbol}: {str(e)}")
        return None  # Return None in case of an exception
