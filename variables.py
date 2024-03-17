# Begin variables.py
# This module is used for storing NON-CONFIGURABLE variables. These are dynamically populated, calculated, or updated throughout the algorithm across modules.
import collections

warmup_counter = 0 # Increments for each warmup day, to check warmup progress
last_increment_day = None # Used to calculate warmup_counter
day_trade_dates = collections.deque(maxlen=5)  # Stores dates of last 5 day trades
day_trade_counter = 0

# Technical Indicators
rsi_data = {}
stochastic_rsi_data = {} # Updated during main.OnSecuritiesChange and 
ema_short_data = {}
ema_long_data = {}
atr_data = {}
macd_data = {}
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
buy_limit_price = {}

# Sell Conditions - 
take_profit_percent_price = {} # Updated after each trade
trailing_stop_price = {} # Updated after each trade 
stop_loss_percent_price = {}
atr_stop_loss_price = {}
max_stop_loss_price = {}
trailing_take_profit_price = {}
fibonacci_stop_loss_prices = []
fib_atr_stop_loss_price = {}
fibonacci_take_profit_prices = []
fib_atr_take_profit_price = {}
max_take_profit_price = {}
max_profit_reward_per_share = {}
max_loss_risk_per_share = {}

# Stocks
active_stock_symbols = [] # Holds the stocks in the dynamically filtered Universe
count_active_stock_symbols = 0  # Number of stocks in active_stock_symbols
unique_portfolio_stocks = set()
sector_allocation = {}
unique_portfolio_stocks = set()
symbol_history = {}
lowest_price_30_days = {}

# Orders        
order_ticket = None
open_order_tickets = {}

# Profit/Loss (P/L) Sell Results
win_count = 0
loss_count = 0
total_profit = 0
total_loss = 0            

# End variables.py