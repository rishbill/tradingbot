from AlgorithmImports import *
import config as c
import variables as v
import json

def shouldSell(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'): # Confirm this is a valid data point
            
            # Obtain the Stop Loss and Take Profit price targets used.
            is_sell_condition_stop_loss_atr_price = v.stop_loss_atr_price[symbol] == v.take_profit_max_price[symbol]
            is_sell_condition_stop_loss_fibonacci_atr_price = v.stop_loss_fib_atr_price[symbol] == v.take_profit_max_price[symbol]
            is_sell_condition_stop_loss_percent = v.stop_loss_percent_price[symbol] = v.take_profit_max_price[symbol]
            is_sell_condition_stop_loss_trailing_percent = v.stop_loss_trailing_price[symbol] = v.take_profit_max_price[symbol]
            is_sell_condition_take_profit_atr_price = v.take_profit_atr_price[symbol] = v.take_profit_max_price[symbol]
            is_sell_condition_take_profit_fibonacci_atr_price = v.take_profit_fib_atr_price[symbol] = v.take_profit_max_price[symbol]
            is_sell_condition_take_profit_percent = v.take_profit_percent_price[symbol] = v.take_profit_max_price[symbol]
            is_sell_condition_take_profit_trailing_percent = v.take_profit_trailing_price[symbol] = v.take_profit_max_price[symbol]

            # Price Target Condition
            is_sell_condition_price_target_met = v.current_price[symbol] >= v.take_profit_max_price[symbol] or v.current_price[symbol] <= v.stop_loss_max_price[symbol]
            
            # Technical Indicators
            is_sell_condition_macd_cross_below_signal = v.macd.Current.Value < v.macd.Signal.Current.Value if c.sell_condition_macd_cross_below_signal else True
            is_sell_condition_rsi_weak = v.rsi[symbol].Current.Value > c.sell_parameter_rsi_max_threshold if c.sell_condition_rsi_weak else True

            condition_details = {
                "Conditions": {
                    "SellPriceTargetMet": is_sell_condition_price_target_met,
                    "StopLossATRPriceUsed": is_sell_condition_stop_loss_atr_price,
                    "StopLossFibATRPriceUsed": is_sell_condition_stop_loss_fibonacci_atr_price,
                    "StopLossPercentPriceUsed": is_sell_condition_stop_loss_percent,
                    "StopLossTrailingPriceUsed": is_sell_condition_stop_loss_trailing_percent,
                    "TakeProfitATRPriceUsed": is_sell_condition_take_profit_atr_price,
                    "TakeProfitFibATRPriceUsed": is_sell_condition_take_profit_fibonacci_atr_price,
                    "TakeProfitPercentPriceUsed": is_sell_condition_take_profit_percent,
                    "TakeProfitTrailingPriceUsed": is_sell_condition_take_profit_trailing_percent,
                    "MACDCrossBelowSignal": is_sell_condition_macd_cross_below_signal,
                    "RSIWeak": is_sell_condition_rsi_weak
                },
                "UnderlyingValues": {
                    "CurrentPrice": v.current_price[symbol],
                    "TakeProfitPrice": v.take_profit_max_price[symbol],
                    "StopLossPrice": v.stop_loss_max_price[symbol],
                    "ShortEMA": v.short_ema,
                    "LongEMA": v.long_ema,
                    "ATR": v.atr[symbol],
                    "MACDValue": v.macd.Current.Value,
                    "MACDSignal": v.macd.Signal.Current.Value,
                    "RSI": v.rsi
                },
                "Parameters": {
                    "SellConditionStopLossATRPriceEnabled": is_sell_condition_stop_loss_atr_price, 
                    "SellConditionStopLossFibATRPriceEnabled": is_sell_condition_stop_loss_fibonacci_atr_price,
                    "SellConditionStopLossPercentPriceEnabled": is_sell_condition_stop_loss_percent,
                    "SellConditionStopLossTrailingPriceEnabled": is_sell_condition_stop_loss_trailing_percent,
                    "SellConditionTakeProfitATRPriceEnabled": is_sell_condition_take_profit_atr_price,
                    "SellConditionTakeProfitFibATRPriceEnabled": is_sell_condition_take_profit_fibonacci_atr_price,
                    "SellConditionTakeProfitPercentPriceEnabled": is_sell_condition_take_profit_percent,
                    "SellConditionTakeProfitTrailingPriceEnabled": is_sell_condition_take_profit_trailing_percent,
                    "SellConditionRSIMinThreshold": c.sell_parameter_rsi_max_threshold
                }
            }

            order_tag = json.dumps(condition_details)

            # Conditions
            if (
                is_sell_condition_price_target_met
                and is_sell_condition_macd_cross_below_signal
                and is_sell_condition_rsi_weak
            ):
                return True, order_tag
            
            else:
                return False, None

        else:
            self.Error(f"Error on shouldSell: {str(e)}")
            return False, None  # Return None if symbol is not in data or data[symbol] is None
        
    except Exception as e:
        self.Error(f"Error on shouldSell: {str(e)}")
        return False
