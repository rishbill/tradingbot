# Begin config.py
from AlgorithmImports import *

# Configurable Parameters
def SetStartDate(algorithm_instance):
    algorithm_instance.SetStartDate(2024, 1, 1) # Set Start Date for backtest data
def SetEndDate(algorithm_instance):
    # algorithm_instance.SetEndDate(2024, 1, 1) # Set End Date for backtest data (default today)
    pass
def SetCash(algorithm_instance):
    algorithm_instance.SetCash(1000)     
def SetWarmUp(algorithm_instance):
    algorithm_instance.SetWarmUp(100, Resolution.Daily)

rsi_periods = 14
rsi_min_threshold = 50
stochastic_rsi_periods = 14
stochastic_rsi_min_threshold = 0.5
ema_short_periods = 9
ema_long_periods = 14
atr_periods = 14
max_portfolio_at_risk = 0.90 # Max % of portfolio invested
max_percent_per_trade = 0.15 # Max % of portfolio to spend on a single trade
fixed_take_profit_percent = 0.05 # Sell 
fixed_take_profit_percent_gain = 5.00 # Sell a fixed portion if over this % profit
fixed_take_profit_percent_to_sell = 0.25 # The portion % to sell if fixed_take_profit_percent_gain is reached
trailing_take_profit_percent = 0.05 # Takes profit based on % of current price
fixed_stop_loss_percent = 0.20 # Max loss % for a held share, in case trailing stop loss fails            
trailing_stop_loss_percent = 0.05 # Sell a fixed portion if over this % loss
stop_loss_atr_multiplier = 2 # Modifies the ATR for increased aggressiveness / risk before triggering stop loss 
buy_limit_order_percent = 0.99 # Bid buy orders at 99% the ask, to get the extra deal
max_submitted_order_minutes = 15 # Expire any pending submitted orders after this time
min_stock_price = 1.00 # Require the min stock price to limit risk
min_pe_ratio = 0 # Require stock to have positive earnings
max_pe_ratio = 20 # Require stock to not be overvalued
min_revenue_growth = 0 # Require stock to have positive Revenue Growth
max_stock_price_percent = 0.10

# Initializing variables
warm_up_counter = 0 # Increments for each warm day, to check warmup progress
last_increment_day = None # Used to calculate warm_up_counter

# Indicators
# These are set per each main.OnData function that runs with each bar/candle/slice
stochastic_rsi = {}
ema_short = {}
ema_long = {}
atr = {}

# News and Sentiment
news_feed = {}

# Trading
trailing_take_profit_price = {} # Calculated after each trade
trailing_stop_price = {} # Calculated after each trade 
stockSymbols = [] # Holds the stocks in the dynamically filtered Universe
numberOfStocks = 0  # Number of stocks in stockSymbols

# Profit/Loss Variables
# Calculated dynamically after each trade via functions main.HandleTradeOutcome and main.UpdateWinProbabilityAndRatio
win_count = 0
loss_count = 0
total_profit = 0
total_loss = 0            

# Universe Filtering
max_stock_price = Portfolio.TotalPortfolioValue * max_stock_price_percent # Limit max stock price to X% of portfolio size, for affordability

# End config.py