# Begin variables.py
# This module stores dynamic, non-configurable variables used across the algorithm.

import collections

# Algorithm Initialization
day_trade_counter = 0  # Counts day trades
day_trade_dates = collections.deque(maxlen=5)  # Dates of last 5 day trades
last_increment_day = None  # Last day warmup counter was incremented
warmup_counter = 0  # Tracks warmup progress
daily_transactions = {}  # Track daily buys and sells for each security
current_date = {}

# Technical Indicators
     # Stores technical indicator data. Updates with each OnSecuritiesChanged and OnData slice.
atr_data = {}
ema_long_data = {}
ema_short_data = {}
macd_data = {}
rsi_data = {}
stochastic_rsi_data = {}

    # Stores technical indicator data. Updates with each stock in OnData.
current_price = {} 
current_close_price = {}
atr = {}
short_ema = {}
short_ema_previous = {}
long_ema = {}
long_ema_previous = {}
rsi = {}
stochastic_rsi = {}
macd = {}

# Buy Conditions
buy_limit_price = {} # Updated with each OnData slice through shouldBuy.

# Sell Conditions
max_loss_risk_per_share = {}
max_profit_reward_per_share = {}
stop_loss_atr_price = {}
stop_loss_fib_atr_price = {}
stop_loss_fibonacci_prices = []
stop_loss_max_price = {}
stop_loss_percent_price = {}
stop_loss_trailing_price = {}
take_profit_atr_price = {}
take_profit_fib_atr_price = {}
take_profit_fibonacci_prices = []
take_profit_max_price = {}
take_profit_percent_price = {}
take_profit_trailing_price = {}

# Stocks
active_stock_symbols = []  # Stocks in filtered universe
count_active_stock_symbols = 0
unique_portfolio_stocks = set()
sector_allocation = {}
unique_portfolio_sectors = set()
symbol_history = {}
lowest_price_30_days = {}
sector_portfolio_value = {}
stock_counts_per_sector = {}
symbol_sector = {}
portfolio_percent_per_sector = {}
biggest_portfolio_sector = {}
max_stock_price = 0

# Orders
order_ticket = None
open_order_tickets = {}
position_size_share_qty_to_buy = 0
latest_order_ticket = {}

# Profit/Loss Sell Results
average_buy_price = {}
trade_win_count = 0
trade_loss_count = 0
total_profit = 0
total_loss = 0
kelly_criterion = 0
win_probability = 0
win_loss_ratio = 0

# End variables.py