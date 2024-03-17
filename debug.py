from AlgorithmImports import *
import config as c
import variables as v

# Debug Values from c.py
self.Debug("Basic parameters:")
self.Debug(f"---- Initial Capital -------------------------- ${self.Portfolio.Cash}")
self.Debug(f"---- Start Date ------------------------------- {self.StartDate}")
self.Debug(f"---- End Date --------------------------------- {self.EndDate}")
self.Debug(f"---- Warm Up ---------------------------------- {c.warmup_period} Days")
self.Debug("Indicator Variables:")
self.Debug("---- Initialized Indicator Variables: self.ema_short, self.ema_long, self.atr, self.stochastic_rsi")
self.Debug("News and Sentiment Variables:")
self.Debug("---- Initialized News and Sentiment Variables: c.news_feed")
self.Debug("Trading Variables:")
self.Debug(f"---- Max Portfolio At Risk --------------------- {c.max_portfolio_invested_percent * 100}%")
self.Debug(f"---- Max Portfolio % Per Trade ----------------- {c.max_trade_portfolio_percent * 100}%")
self.Debug(f"---- Fixed Take Profit % ----------------------- {c.fixed_take_profit_percent * 100}%")
self.Debug(f"---- Fixed Take Profit % Gain ------------------ {c.fixed_take_profit_percent_gain * 100}%")
self.Debug(f"---- Fixed Take Profit % To Sell --------------- {c.fixed_take_profit_percent_to_sell * 100}%")
self.Debug(f"---- Fixed Stop Loss % ------------------------- {c.fixed_stop_loss_percent * 100}%")
self.Debug(f"---- Stop Loss ATR Multiplier ------------------ {c.stop_loss_atr_multiplier}")
self.Debug(f"---- Trailing Stop Loss % ---------------------- {c.sell_parameter_trailing_stop_percent * 100}%")  
self.Debug("Portfolio Summary:")
self.Debug(f"---- Portfolio Value ----------------------------- ${portfolio_value}")
if total_invested_stocks == 0:
    self.Debug("---- No invested stocks in portfolio")
else:
    for sector, count in stock_counts_per_sector.items():
        sector_portfolio_value = self.CalculateSectorPortfolioValue(sector)
        percentage_of_portfolio = (sector_portfolio_value / portfolio_value) * 100
        self.Debug(f"---- Sector: {sector}, Count: {count}, Value: ${sector_portfolio_value}, % of Portfolio: {percentage_of_portfolio:.2f}%")

