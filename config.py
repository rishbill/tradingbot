# Begin config.py
from AlgorithmImports import *

# Enable/Disable Trading Conditions
# ShouldBuy
enable_ema_crossover = True
enable_short_ema_rising = False
enable_ema_distance_widening = False
enable_rsi_bullish = False
enable_stochastic_rsi_bullish = False
enable_macd_bullish = False
enable_risk_reward = False

# Trading Parameters
warmup_period = 100
starting_cash = 1000
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
trailing_stop_loss_percent = 0.05 # Sell if loss hits this %
stop_loss_atr_multiplier = 2 # Modifies the ATR for increased aggressiveness / risk before triggering stop loss 
buy_limit_order_percent = 0.99 # Bid buy orders at 99% the ask, to get the extra deal
max_submitted_order_minutes = 15 # Expire any pending submitted orders after this time
min_stock_price = 1.00 # Require the min stock price to limit risk
min_pe_ratio = 0 # Require stock to have positive earnings
max_pe_ratio = 20 # Require stock to not be overvalued
min_revenue_growth = 0 # Require stock to have positive Revenue Growth
max_stock_price_percent = 0.10
min_stocks_invested = 5
max_sector_invested_percent = 0.65

def SetStartDate(algorithm_instance):
    algorithm_instance.SetStartDate(2023, 10, 1) # Set Start Date for backtest data. End Date defaults to current.
def SetCash(algorithm_instance):
    algorithm_instance.SetCash(starting_cash)     
def SetWarmUp(algorithm_instance):
    algorithm_instance.SetWarmUp(warmup_period, Resolution.Daily)

blacklist_stocks = [
    "CMCSA",  # Comcast Corporation
    "VZ",     # Verizon Communications Inc.
    "NSRGY",  # Nestlé S.A.
    "BAC",    # Bank of America Corporation
    "SIVB",   # Silicon Valley Bank
    "SBNY",   # Signature Bank
    "FRC",    # First Republic Bank
    "CS",     # Credit Suisse Group AG
    "BTI",    # British American Tobacco p.l.c.
    "NWG",    # NatWest Group plc
    "ILMN",   # Illumina, Inc.
    "STX",    # Seagate Technology plc
    "GS",     # Goldman Sachs Group, Inc.
    "DB",     # Deutsche Bank AG
    "TMUS",   # T-Mobile US, Inc.
    "AMZN"    # Amazon.com, Inc.
]

# Initializing variables
warmup_counter = 0 # Increments for each warm day, to check warmup progress
last_increment_day = None # Used to calculate warmup_counter
filtered_symbol_details = []

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
ticket = None
open_order_tickets = {}
unique_portfolio_stocks = set()
sector_allocation = {}

# Profit/Loss Variables
# Calculated dynamically after each trade via functions main.HandleTradeOutcome and main.UpdateWinProbabilityAndRatio
win_count = 0
loss_count = 0
total_profit = 0
total_loss = 0            

# End config.py