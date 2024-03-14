from AlgorithmImports import *
import config

def ShouldBuy(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'):            
        
            short_ema_current = config.ema_short[symbol].Current.Value
            long_ema_current = config.ema_long[symbol].Current.Value
            short_ema_previous = config.ema_short[symbol].Previous.Value
            long_ema_previous = config.ema_long[symbol].Previous.Value
            rsi_value = self.RSI(symbol, config.rsi_periods, Resolution.Daily).Current.Value
            macd = self.MACD(symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily, Field.Close)
            risk_per_share = CalculateRisk(self, symbol, data)
            reward = CalculateReward(self, symbol, data)

            # EMA Crossover
            if config.enable_ema_crossover:
                is_ema_crossover = short_ema_current > long_ema_current
            else:
                is_ema_crossover = True
            
            # Short EMA Rising
            if config.enable_short_ema_rising:
                is_short_ema_rising = short_ema_current > short_ema_previous
            else:
                is_short_ema_rising = True

            # EMA Distance Widening   
            if config.enable_ema_distance_widening:
                is_ema_distance_widening = (short_ema_current - long_ema_current) > (short_ema_previous - long_ema_previous)
            else:
                is_ema_distance_widening = True

            # RSI Bullish
            if config.enable_rsi_bullish:
                is_rsi_bullish = rsi_value > config.rsi_min_threshold
            else:
                is_rsi_bullish = True

            # Stochastic RSI Bullish
            if config.enable_rsi_bullish:
                is_stochastic_rsi_bullish = config.stochastic_rsi[symbol].IsReady and config.stochastic_rsi[symbol].Current.Value > config.stochastic_rsi_min_threshold
            else:
                is_stochastic_rsi_bullish = True
            
            # MACD Bullish
            if config.enable_macd_bullish:
                is_macd_bullish = macd.Current.Value > macd.Signal.Current.Value
            else:
                is_macd_bullish = True

            # Risk/Reward Analysis
            if config.enable_risk_reward:
                if reward is None or risk_per_share is None:
                    return False  # Can't proceed if risk or reward can't be calculated
                is_acceptable_risk_reward = reward > 0 and risk_per_share > 0 and (reward / risk_per_share) >= 2
            else:
                is_acceptable_risk_reward = True

            # Calculate position size based on risk
            position_size = CalculatePositionSize(self, risk_per_share)
            if position_size == 0:
                return False  # Skip trade if position size is 0

            # Calculate potential value at risk for this trade
            limit_price_to_buy = data[symbol].Close * config.buy_limit_order_percent
            potential_quantity = min(position_size, self.Portfolio.Cash / limit_price_to_buy)
            potential_value_at_risk = CalculateStopLossEquityAmount(self, symbol, data) * potential_quantity

            if self.Portfolio.Cash < potential_value_at_risk:
                return False  # Skip trade if not enough cash
            else: 
                if potential_value_at_risk >= config.max_percent_per_trade * self.Portfolio.TotalPortfolioValue:
                    return False  # Skip trade if it exceeds max percent per trade

            # Check if all indicators are met
            return is_short_ema_rising and is_ema_crossover and is_ema_distance_widening and is_stochastic_rsi_bullish and is_rsi_bullish and is_macd_bullish and is_acceptable_risk_reward
        else:
            return None  # Return None if symbol is not in data or data[symbol] is None
    
    except Exception as e:
        self.Debug(f"Error on ShouldBuy: {str(e)}") 
        return False
                    
def ShouldSell(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'):            
            current_price = data[symbol].Price
            stop_loss_price = CalculateStopLossPrice(self, symbol, data)
            take_profit_price = CalculateTakeProfitPrice(self, symbol, data)
            # Check for Take Profit condition
            if current_price >= take_profit_price:
                self.Debug(f"Take Profit Triggered for {symbol}: Current Price: {current_price}, Target: {take_profit_price}")
                return True
            # Check for Stop Loss condition
            if current_price <= stop_loss_price:
                self.Debug(f"Stop Loss Triggered for {symbol}: Current Price: {current_price}, Target: {stop_loss_price}")
                return True
            return False
        else:
            return None  # Return None if symbol is not in data or data[symbol] is None
    except Exception as e:
        self.Debug(f"Error on ShouldSell: {str(e)}")
        return False

def CalculateRisk(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'):            
            stopLossLevel = CalculateStopLossPrice(self, symbol, data)
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
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'):            
            take_profit_level = CalculateTakeProfitPrice(self, symbol, data)
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
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'):            
            stop_loss_level = CalculateStopLossPrice(self, symbol, data)
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
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'):            
            # Percentage-based stop loss
            current_price = data[symbol].Price
            stop_loss_level_percent = current_price * (1 - config.fixed_stop_loss_percent)
            # ATR-based stop loss
            atr_value = config.atr[symbol].Current.Value if symbol in config.atr else 0
            stop_loss_level_atr = current_price - (atr_value * config.stop_loss_atr_multiplier)
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
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'):            
            current_price = data[symbol].Price
            # Fixed take profit level based on a percentage
            fixed_take_profit_level = current_price * (1 + config.fixed_take_profit_percent)
            # Fibonacci levels with ATR
            atr_value = config.atr[symbol].Current.Value if symbol in config.atr else 0
            fibonacci_levels = [0.236, 0.382, 0.618]  # Example Fibonacci levels
            fibonacci_take_profit_levels = [current_price * (1 + level) for level in fibonacci_levels]
            fib_atr_take_profit_level = min(fibonacci_take_profit_levels) + atr_value
            # Use the trailing take profit level updated in OnData
            trailing_take_profit_level = config.trailing_take_profit_price.get(symbol, current_price * (1 + config.trailing_take_profit_percent))
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
        riskCapital = self.Portfolio.TotalPortfolioValue * config.max_percent_per_trade
        positionSize = riskCapital / risk
        return min(positionSize, config.max_portfolio_at_risk)  # Ensure not to exceed 90% allocation
    except Exception as e:
        self.Debug(f"Error on CalculatePositionSize: {str(e)}")
        return None  # Return None in case of an exception        
