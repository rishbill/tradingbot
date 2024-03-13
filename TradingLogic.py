from AlgorithmImports import *

def ShouldBuy(self, symbol, data):
    try:
        # EMA analysis
        short_ema_current = self.ema_short[symbol].Current.Value
        long_ema_current = self.ema_long[symbol].Current.Value
        short_ema_previous = self.ema_short[symbol].Previous.Value
        long_ema_previous = self.ema_long[symbol].Previous.Value
        is_ema_crossover = short_ema_current > long_ema_current
        is_short_ema_rising = short_ema_current > short_ema_previous
        is_ema_distance_widening = (short_ema_current - long_ema_current) > (short_ema_previous - long_ema_previous)
        
        # RSI Analysis
        rsi_value = self.RSI(symbol, self.rsi_periods, Resolution.Daily).Current.Value
        is_rsi_bullish = rsi_value > self.rsi_min_threshold
        is_stochastic_rsi_bullish = self.stochastic_rsi[symbol].IsReady and self.stochastic_rsi[symbol].stochastic_rsi > 0.5
        
        # MACD Analysis
        macd = self.MACD(symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily, Field.Close)
        is_macd_bullish = macd.Current.Value > macd.Signal.Current.Value
        
        # Risk/Reward Analysis
        risk_per_share = self.CalculateRisk(symbol, data)
        reward = self.CalculateReward(symbol, data)
        if reward is None or risk_per_share is None:
            return False  # Can't proceed if risk or reward can't be calculated
        is_acceptable_risk_reward = reward > 0 and risk_per_share > 0 and (reward / risk_per_share) >= 2

        # Calculate position size based on risk
        position_size = self.CalculatePositionSize(risk_per_share)
        if position_size == 0:
            return False  # Skip trade if position size is too small

        # Calculate potential value at risk for this trade
        limit_price_to_buy = data[symbol].Close * self.buy_limit_order_percent
        potential_quantity = min(position_size, self.Portfolio.Cash / limit_price_to_buy)
        potential_value_at_risk = self.CalculateStopLossEquityAmount(symbol, data) * potential_quantity

        # Check if potential value at risk exceeds the threshold
        if potential_value_at_risk > self.max_percent_per_trade * self.Portfolio.TotalPortfolioValue:
            return False  # Skip trade if it exceeds max percent per trade

        # Check if all indicators are met
        return is_short_ema_rising and is_ema_crossover and is_ema_distance_widening and is_stochastic_rsi_bullish and is_rsi_bullish and is_macd_bullish and is_acceptable_risk_reward
    except Exception as e:
        self.Debug(f"Error on ShouldBuy: {str(e)}") 
        return False
                    
def ShouldSell(self, symbol, data):
    try:
        current_price = data[symbol].Price
        stop_loss_price = self.CalculateStopLossPrice(symbol, data)
        take_profit_price = self.CalculateTakeProfitPrice(symbol, data)

        # Check for Take Profit condition
        if current_price >= take_profit_price:
            self.Debug(f"Take Profit Triggered for {symbol}: Current Price: {current_price}, Target: {take_profit_price}")
            return True

        # Check for Stop Loss condition
        if current_price <= stop_loss_price:
            self.Debug(f"Stop Loss Triggered for {symbol}: Current Price: {current_price}, Target: {stop_loss_price}")
            return True

        return False
    except Exception as e:
        self.Debug(f"Error on ShouldSell: {str(e)}")
        return False

def CalculateRisk(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None:
            stopLossLevel = self.CalculateStopLossPrice(symbol, data)
            currentPrice = data[symbol].Price
            risk = currentPrice - stopLossLevel  # For a long position
            return risk
        else:
            return None  # Return None if symbol is not in data or data[symbol] is None
    except Exception as e:
        self.Debug(f"Error on CalculateRisk for {symbol}: {str(e)}")
        return None        

def CalculateReward(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None:
            take_profit_level = self.CalculateTakeProfitPrice(symbol, data)
            current_price = data[symbol].Price
            reward = take_profit_level - current_price
            return reward
        else:
            return None  # Return None if symbol is not in data or data[symbol] is None            
    except Exception as e:
        self.Debug(f"Error on CalculateReward for {symbol}: {str(e)}")
        return None

def CalculateStopLossEquityAmount(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None:            
            stop_loss_level = self.CalculateStopLossPrice(symbol, data)
            current_price = data[symbol].Price
            # The value at risk is the difference between the current price and the stop-loss level, multiplied by the quantity
            value_at_risk = (current_price - stop_loss_level) * self.Portfolio[symbol].Quantity
            return value_at_risk
        else:
            return None  # Return None if symbol is not in data or data[symbol] is None                        
    except Exception as e:
        self.Debug(f"Error on CalculateStopLossEquityAmount for {symbol}: {str(e)}")
        return None  # Return None in case of an exception

def CalculateStopLossPrice(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None:            
            # Percentage-based stop loss
            current_price = data[symbol].Price
            stop_loss_level_percent = current_price * (1 - self.fixed_stop_loss_percent)
            # ATR-based stop loss
            atr_value = self.atr[symbol].Current.Value if symbol in self.atr else 0
            stop_loss_level_atr = current_price - (atr_value * self.stop_loss_atr_multiplier)
            # Combining methods: Choose the larger of the two for more conservative stop-loss
            combined_stop_loss_level = max(stop_loss_level_percent, stop_loss_level_atr)
            return combined_stop_loss_level
        else:
            return None  # Return None if symbol is not in data or data[symbol] is None                                    
    except Exception as e:
        self.Debug(f"Error on CalculateStopLossPrice for {symbol}: {str(e)}")
        return None  # Return None in case of an exception

def CalculateTakeProfitPrice(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None:            
            current_price = data[symbol].Price
            # Fixed take profit level based on a percentage
            fixed_take_profit_level = current_price * (1 + self.fixed_take_profit_percent)
            # Fibonacci levels with ATR
            atr_value = self.atr[symbol].Current.Value if symbol in self.atr else 0
            fibonacci_levels = [0.236, 0.382, 0.618]  # Example Fibonacci levels
            fibonacci_take_profit_levels = [current_price * (1 + level) for level in fibonacci_levels]
            fib_atr_take_profit_level = min(fibonacci_take_profit_levels) + atr_value
            # Use the trailing take profit level updated in OnData
            trailing_take_profit_level = self.trailing_take_profit_price.get(symbol, current_price * (1 + self.trailing_take_profit_percent))
            # Combine methods: Choose the most conservative (highest) take-profit level
            combined_take_profit_level = max(fixed_take_profit_level, fib_atr_take_profit_level, trailing_take_profit_level)
            return combined_take_profit_level
        else:
            return None  # Return None if symbol is not in data or data[symbol] is None                                                
    except Exception as e:
        self.Debug(f"Error in CalculateTakeProfitPrice for {symbol}: {str(e)}")
        return None  # Return None in case of an exception

def CalculatePositionSize(self, risk):
    try:
        # Calculate the position size based on the risk and your total portfolio value
        riskCapital = self.Portfolio.TotalPortfolioValue * self.max_percent_per_trade
        positionSize = riskCapital / risk
        return min(positionSize, self.max_portfolio_at_risk)  # Ensure not to exceed 90% allocation
    except Exception as e:
        self.Debug(f"Error on CalculatePositionSize: {str(e)}")
        return None  # Return None in case of an exception        
