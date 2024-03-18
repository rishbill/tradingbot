from AlgorithmImports import *
import config as c
import variables as v
import calculateStopLossPrice
import calculateTakeProfitPrice
import json

def shouldBuy(self, symbol, data):
    try:
        if symbol in data and data[symbol] is not None and hasattr(data[symbol], 'Price'): # Confirm this is a valid data point

            # Risk/Reward Analysis
            v.take_profit_max_price[symbol] = calculateTakeProfitPrice(self, symbol, data)
                # Calculate optimal Take Profit share price for this buy. 
            
            v.stop_loss_max_price[symbol] = calculateStopLossPrice(self, symbol, data)
                # Calculate optimal Stop Loss share price for this buy.

            v.max_profit_reward_per_share[symbol] = v.take_profit_max_price[symbol] - v.current_price[symbol]
                # Calculate max potential profit per share for this buy.

            v.max_loss_risk_per_share[symbol] = v.current_price[symbol] - v.stop_loss_max_price[symbol]
                # Calculate max potential loss per share for this buy.

            if (
                v.max_loss_risk_per_share[symbol] is None 
                or v.max_loss_risk_per_share[symbol] <= 0 
                or v.max_profit_reward_per_share[symbol] is None 
                or v.max_profit_reward_per_share[symbol] <= 0
            ):    
                self.Error(f"Risk/Reward per share is non-positive or invalid (max_loss_risk_per_share: {str(v.max_loss_risk_per_share[symbol])}, max_profit_reward_per_share: {str(v.max_profit_reward_per_share[symbol])}). Skipping position size calculation.")                
                return False
                # Throw error if risk/reward calculation problem.
            
            # Position Size Analysis
            v.buy_limit_price[symbol] = v.current_close_price[symbol] * c.buy_parameter_limit_order_percent
                # Calulate desired limit price for this buy.

            position_size_cash_available_share_qty = self.Portfolio.Cash / v.buy_limit_price[symbol]
                # Calculate potential position size for this buy based on available cash - Simplest method, always enabled.

            position_size_kelly_criterion_share_qty = ( self.Portfolio.Cash * v.kelly_criterion ) / v.max_loss_risk_per_share[symbol] if c.buy_condition_kelly_criterion_position_size else 0
                # Uses the win probability and win/loss ratio to determine the optimal fraction of capital to be used for each trade

            position_size_max_portfolio_percent_per_trade_share_qty = (self.Portfolio.TotalPortfolioValue * c.buy_parameter_max_portfolio_percent_per_trade) / v.max_loss_risk_per_share[symbol] if c.buy_condition_max_portfolio_percent_per_trade else 0
                # Calculate potential position size for this buy based on max portfolio percent of a single trade.
            
            position_size_max_total_portfolio_invested_percent_share_qty = (self.Portfolio.TotalPortfolioValue * c.buy_parameter_max_total_portfolio_invested_percent) / v.max_loss_risk_per_share[symbol] if c.buy_condition_max_total_portfolio_invested_percent else 0
                # Calculate potential position size for this buy based on percent of total invested portfolio value.

            v.position_size_share_qty_to_buy[symbol] = min(position_size_max_portfolio_percent_per_trade_share_qty, position_size_max_total_portfolio_invested_percent_share_qty, position_size_cash_available_share_qty, position_size_kelly_criterion_share_qty)
                # Use the lesser of the 4 potential position sizes.
                        
            max_loss_risk_per_trade = v.max_loss_risk_per_share[symbol] * v.position_size_share_qty_to_buy[symbol]
                # Calculate max potential loss for this trade.

            # Check if the symbol's sector is the max sector and if its percentage is less than the parameter
            is_buy_condition_max_sector_invested_percent = v.symbol_sector[symbol] == v.biggest_portfolio_sector and v.portfolio_percent_per_sector[v.biggest_portfolio_sector] < c.buy_parameter_max_sector_invested_percent if v.biggest_portfolio_sector and c.buy_condition_max_sector_invested_percent else True

            # Technical Analysis
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
            is_buy_condition_max_sector_invested_percent = v.portfolio_percent_per_sector[symbol] < c.buy_parameter_max_sector_invested_percent if c.buy_condition_max_sector_invested_percent else True
            is_buy_condition_pdt_rule = len(v.day_trade_dates) >= 3 and self.Portfolio.Cash < 25000 if c.buy_condition_pdt_rule else True
            is_buy_condition_lost_it_all = self.Portfolio.TotalPortfolioValue < c.buy_parameter_lost_it_all if c.buy_condition_lost_it_all else True

            condition_details = {
                "Conditions": {
                    "ATRBreakoutLevelReached": is_buy_condition_atr_breakout_level_reached,
                    "EMACrossover": is_buy_condition_ema_crossover,
                    "EMADistanceWidening": is_buy_condition_ema_distance_widening,
                    "MACDCrossAboveSignal": is_buy_condition_macd_cross_above_signal,
                    "RewardRiskRatio": is_buy_condition_reward_risk_ratio,
                    "RSIStrong": is_buy_condition_rsi_strong,
                    "ShortEMARising": is_buy_condition_short_ema_rising,
                    "StochasticRSIStrong": is_buy_condition_stochastic_rsi_strong,
                    "MaxTotalPortfolioInvestedPercent": is_buy_condition_max_total_portfolio_invested_percent,
                    "MaxPortfolioPercentPerTrade": is_buy_condition_max_portfolio_percent_per_trade,
                    "MinStocksInvested": is_buy_condition_min_stocks_invested,
                    "MaxSectorInvestedPercent": is_buy_condition_max_sector_invested_percent,
                    "PDTRule": is_buy_condition_pdt_rule,
                    "LostItAll": is_buy_condition_lost_it_all
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
                    "RSI": v.rsi,
                    "StochasticRSI": v.stochastic_rsi
                },
                "Parameters": {
                    "LimitOrderPercent": c.buy_parameter_limit_order_percent,
                    "ATRBreakoutMultiplier": c.buy_parameter_atr_breakout_level_multiplier,
                    "MaxPortfolioPercentPerTrade": c.buy_parameter_max_portfolio_percent_per_trade,
                    "MaxTotalPortfolioInvestedPercent": c.buy_parameter_max_total_portfolio_invested_percent,
                    "RSIMinThreshold": c.buy_parameter_rsi_min_threshold,
                    "StochasticRSIMinThreshold": c.buy_parameter_stochastic_rsi_min_threshold,
                    "RewardRiskRatio": c.buy_parameter_reward_risk_ratio
                }
            }

            order_tag = json.dumps(condition_details)

            # For a Buy to occur, all conditions must be True if they are enabled.
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
                return True, order_tag

            else:
                return False, None
        else:
            self.Error(f"Error on shouldBuy: {str(e)}") 
            return False, None  # Return None if symbol is not in data or data[symbol] is None
    
    except Exception as e:
        self.Error(f"Error on shouldBuy: {str(e)}") 
        return False
