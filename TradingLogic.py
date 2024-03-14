# Begin TradingLogic.py
from AlgorithmImports import *
import config

def ShouldBuy(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'):

            # Extract indicator values
            short_ema_current = config.ema_short[symbol].Current.Value
            long_ema_current = config.ema_long[symbol].Current.Value
            short_ema_previous = config.ema_short[symbol].Previous.Value
            long_ema_previous = config.ema_long[symbol].Previous.Value
            rsi_value = self.RSI(symbol, config.rsi_periods, Resolution.Daily).Current.Value
            macd = self.MACD(symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily, Field.Close)

            # Risk/Reward Analysis
            risk_per_share = CalculateRisk(self, symbol, data)
            reward = CalculateReward(self, symbol, data)
            if risk_per_share is None or reward is None:
                return False  # Can't proceed if risk or reward can't be calculated
            is_acceptable_risk_reward = (reward / risk_per_share) >= 2 if config.enable_risk_reward else True

            # Decision variables
            is_ema_crossover = short_ema_current > long_ema_current if config.enable_ema_crossover else True
            is_short_ema_rising = short_ema_current > short_ema_previous if config.enable_short_ema_rising else True
            is_ema_distance_widening = (short_ema_current - long_ema_current) > (short_ema_previous - long_ema_previous) if config.enable_ema_distance_widening else True
            is_rsi_bullish = rsi_value > config.rsi_min_threshold if config.enable_rsi_bullish else True
            is_stochastic_rsi_bullish = config.stochastic_rsi[symbol].IsReady and config.stochastic_rsi[symbol].Current.Value > config.stochastic_rsi_min_threshold if config.enable_stochastic_rsi_bullish else True
            is_macd_bullish = macd.Current.Value > macd.Signal.Current.Value if config.enable_macd_bullish else True

            # Calculate potential value at risk
            position_size = CalculatePositionSize(self, risk_per_share)
            if position_size == 0:
                return False  # Skip trade if position size is 0
            limit_price_to_buy = data[symbol].Close * config.buy_limit_order_percent
            potential_quantity = min(position_size, self.Portfolio.Cash / limit_price_to_buy)
            potential_value_at_risk = CalculateStopLossEquityAmount(self, symbol, data) * potential_quantity

            # Decision logic
            if is_short_ema_rising and is_ema_crossover and is_ema_distance_widening and is_stochastic_rsi_bullish and is_rsi_bullish and is_macd_bullish and is_acceptable_risk_reward:
                for symbol, holding in self.Portfolio.items():
                    if holding.Invested:
                        config.unique_portfolio_stocks.add(symbol)
                # current_sector = self.Fundamentals[symbol].AssetClassification.MorningstarSectorCode                        
                if self.Portfolio.Cash < potential_value_at_risk:
                    self.Debug(f"Buy Decision: False for {symbol}. Reason: Insufficient cash. Cash Available: {self.Portfolio.Cash}, Value at Risk: {potential_value_at_risk}")
                    return False
                elif potential_value_at_risk >= config.max_percent_per_trade * self.Portfolio.TotalPortfolioValue:
                    self.Debug(f"Buy Decision: False for {symbol}. Reason: Exceeds max percent per trade. Value at Risk: {potential_value_at_risk}, Max Percent Per Trade: {config.max_percent_per_trade * self.Portfolio.TotalPortfolioValue}")
                    return False
                elif self.Portfolio[symbol].Invested and len(config.unique_portfolio_stocks) < config.min_stocks_invested:
                    self.Debug(f"Buy Decision: False for {symbol}. Reason: Portfolio needs more diversification (currently only {len(config.unique_portfolio_stocks)} unique stocks).")
                    return False
                # elif current_sector in config.sector_allocation:
                #     sector_percent = config.sector_allocation[current_sector] / self.Portfolio.TotalPortfolioValue
                #     if sector_percent > config.max_sector_invested_percent:
                #         self.Debug(f"Buy Decision: False for {symbol}. Reason: Sector limit exceeded (Sector: {current_sector}, Allocation: {sector_percent:.2%}).")
                #         return False
                else:
                    # Output detailed conditions and values
                    self.Debug(f"Buy Decision: True for {symbol}. Condition Details:")
                    self.Debug(f"---- EMA Crossover: {is_ema_crossover} (Short EMA: {short_ema_current} > Long EMA: {long_ema_current})")
                    self.Debug(f"---- Short EMA Rising: {is_short_ema_rising} (Current Short EMA: {short_ema_current} > Previous Short EMA: {short_ema_previous})")
                    self.Debug(f"---- EMA Distance Widening: {is_ema_distance_widening} (Current Diff: {short_ema_current - long_ema_current}, Previous Diff: {short_ema_previous - long_ema_previous})")
                    self.Debug(f"---- RSI Bullish: {is_rsi_bullish} (Value: {rsi_value} > {config.rsi_min_threshold})")
                    self.Debug(f"---- Stochastic RSI Bullish: {is_stochastic_rsi_bullish} (Value: {config.stochastic_rsi[symbol].Current.Value} > {config.stochastic_rsi_min_threshold})")
                    self.Debug(f"---- MACD Bullish: {is_macd_bullish} (MACD: {macd.Current.Value} > Signal: {macd.Signal.Current.Value})")

            else:
                return False
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

# End TradingLogic.py