from AlgorithmImports import *
import config as c
import variables as v
import calculateStopLossPrice
import calculateTakeProfitPrice

def shouldBuy(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'): # Confirm this is a valid data point

            # Risk/Reward Analysis
            v.max_take_profit_price[symbol] = calculateTakeProfitPrice(self, symbol, data)
            v.max_profit_reward_per_share[symbol] = v.max_take_profit_price[symbol] - v.current_price[symbol]

            v.max_stop_loss_price[symbol] = calculateStopLossPrice(self, symbol, data)
            v.max_loss_risk_per_share[symbol] = v.current_price[symbol] - v.max_stop_loss_price[symbol]

            if (
                v.max_loss_risk_per_share[symbol] is None 
                or v.max_loss_risk_per_share[symbol] <= 0 
                or v.max_profit_reward_per_share[symbol] <= 0 
                or v.max_profit_reward_per_share[symbol] <= 0
            ):    
                self.Error(f"Risk per share is non-positive or invalid (max_loss_risk_per_share: {str(v.max_loss_risk_per_share[symbol])}, max_profit_reward_per_share: {str(v.max_profit_reward_per_share[symbol])}). Skipping position size calculation.")                
                return False  # Can't proceed if risk or reward can't be calculated
            
            # Position Size Analysis
            # Calculate the position size based on percent of total portfolio value
            position_size_max_portfolio_percent_per_trade_share_qty = (self.Portfolio.TotalPortfolioValue * c.buy_parameter_max_portfolio_percent_per_trade) / v.max_loss_risk_per_share[symbol]
            # Calculate the position size based on percent of total portfolio value
            position_size_max_total_portfolio_invested_percent_share_qty = (self.Portfolio.TotalPortfolioValue * c.buy_parameter_max_total_portfolio_invested_percent) / v.max_loss_risk_per_share[symbol]
            position_size_share_quantity = min(position_size_max_portfolio_percent_per_trade_share_qty, position_size_max_total_portfolio_invested_percent_share_qty)
            v.buy_limit_price = v.current_close_price * c.buy_parameter_limit_order_percent
            position_size_share_qty_to_buy = min(position_size_share_quantity, self.Portfolio.Cash / v.buy_limit_price)
            max_loss_risk_per_trade = v.max_loss_risk_per_share[symbol] * position_size_share_qty_to_buy

            # Conditions
                # Technical Indicators
            is_buy_condition_atr_breakout_level_reached = v.current_price[symbol] > (v.lowest_price_30_days[symbol] + (v.atr[symbol] * c.buy_parameter_atr_breakout_level_multiplier)) if c.buy_condition_atr_breakout_level_reached else True
            is_buy_condition_ema_crossover = v.short_ema > v.long_ema if c.buy_condition_ema_crossover else True
            is_buy_condition_ema_distance_widening = (v.short_ema - v.long_ema) > (v.short_ema_previous - v.long_ema_previous) if c.buy_condition_ema_distance_widening else True            
            is_buy_condition_macd_cross_above_signal = v.macd.Current.Value > v.macd.Signal.Current.Value if c.buy_condition_macd_cross_above_signal else True
            is_buy_condition_reward_risk_ratio = (v.max_profit_reward_per_share[symbol] / v.max_loss_risk_per_share[symbol]) >= c.buy_parameter_reward_risk_ratio if c.buy_condition_reward_risk_ratio else True
            is_buy_condition_rsi_strong = v.rsi > c.buy_parameter_rsi_min_threshold if c.buy_condition_rsi_strong else True
            is_buy_condition_short_ema_rising = v.short_ema > v.short_ema_previous if c.buy_condition_short_ema_rising else True
            is_buy_condition_stochastic_rsi_strong = v.stochastic_rsi > c.buy_parameter_stochastic_rsi_min_threshold if c.buy_condition_stochastic_rsi_strong else True
                
                # Diversification Parameters
            is_buy_condition_max_total_portfolio_invested_percent = max_loss_risk_per_trade < c.buy_parameter_max_total_portfolio_invested_percent * self.Portfolio.TotalPortfolioValue if c.buy_condition_max_total_portfolio_invested_percent else True
            is_buy_condition_max_portfolio_percent_per_trade = max_loss_risk_per_trade < c.buy_parameter_max_portfolio_percent_per_trade * self.Portfolio.TotalPortfolioValue if c.buy_condition_max_portfolio_percent_per_trade else True
            is_buy_condition_min_stocks_invested = len(v.unique_portfolio_stocks) < c.buy_parameter_min_stocks_invested if c.buy_condition_min_stocks_invested else True
            is_buy_condition_max_sector_invested_percent = False if c.buy_condition_max_sector_invested_percent else True
            # NEEDS WORK sector invested percent
            is_buy_condition_pdt_rule = len(v.day_trade_counter) >= 3 and self.Portfolio.Cash < 25000 if c.buy_condition_pdt_rule else True
            # NEEDS WORK PDT Rule
            is_buy_condition_lost_it_all = self.Portfolio.TotalPortfolioValue < c.buy_parameter_lost_it_all if c.buy_condition_lost_it_all else True

            # For a Buy to occur, all conditions must be True if they are enabled
            if (
                is_buy_condition_atr_breakout_level_reached
                and is_buy_condition_ema_crossover
                and is_buy_condition_ema_distance_widening
                and is_buy_condition_macd_cross_above_signal
                and is_buy_condition_reward_risk_ratio
                and is_buy_condition_rsi_strong
                and is_buy_condition_short_ema_rising
                and is_buy_condition_stochastic_rsi_strong
                and is_buy_condition_max_total_portfolio_invested_percent
                and is_buy_condition_max_portfolio_percent_per_trade
                and is_buy_condition_min_stocks_invested
                and is_buy_condition_max_sector_invested_percent
                and is_buy_condition_pdt_rule
                and is_buy_condition_lost_it_all
            ):    
                return True

            else:
                # Output detailed conditions and values
                self.Debug(f"Buy Decision: True for {symbol}. Condition Details:")
                # NEEDS WORK
        else:
            return None  # Return None if symbol is not in data or data[symbol] is None
    
    except Exception as e:
        self.Error(f"Error on shouldBuy: {str(e)}") 
        return False
