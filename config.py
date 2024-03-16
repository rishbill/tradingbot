# Begin config.py
# This module is meant to for setting all the configurables of the algorithm, including parameters, variables, and enabling/disabling conditions.

from AlgorithmImports import *

# Buy Conditions - Enable\Disable:
    # Set each condition to True or False to control which conditions the algorithm should consider before placing a Buy trade

buy_condition_atr_breakout_level_reached = False
# ATR Breakout Level:
    # What It Is: Uses the Average True Range (ATR) to determine a volatility-based price level above the current price. The ATR measures market volatility by calculating the average range between high and low prices.
    # What It Tells You: It suggests that the price has moved significantly from its recent range, indicating a potential start of a new trend or continuation of an existing trend with strong momentum.
    # Speed & Sensitivity: The ATR is responsive to market volatility but does not indicate price direction; hence, the breakout level is used as a threshold to gauge significant price moves.
    # How It's Calculated: The breakout level is typically set by adding a multiple of the ATR to the current or recent closing price. A buy signal is generated when the price exceeds this calculated breakout level.

buy_condition_ema_crossover = True
# EMA (Exponential Moving Average) Crossover:
    # What It Is: This involves two EMAs of different lengths (like short-term and long-term EMAs).
    # What It Tells You: A crossover of these EMAs indicates potential trend changes. For instance, a short-term EMA crossing above a long-term EMA suggests a bullish trend.
    # Speed & Sensitivity: The EMA crossover is sensitive to recent price movements, especially with shorter timeframes, and can provide earlier signals than the MACD.
    # How It's Calculated: By comparing the values of two EMAs (e.g., a 50-day and a 200-day EMA). A crossover event occurs when these two lines intersect, with the short-term EMA moving above or below the long-term EMA.

buy_condition_ema_distance_widening = False
# EMA Distance Widening:
    # What It Is: This compares the difference between two EMAs (e.g., short and long-term) now and in the past.
    # What It Tells You: Widening distance indicates an increasing difference in trends identified by the two EMAs, potentially signaling a strengthening trend.
    # Speed & Sensitivity: It combines the characteristics of both EMAs, giving a nuanced view of trend momentum.
    # How It's Calculated: By measuring the difference between the short-term and long-term EMAs at two different points in time. If the more recent difference is larger, it suggests the distance is widening.

buy_condition_macd_cross_above_signal = False
# MACD (Moving Average Convergence Divergence):
    # What It Is: The MACD involves two lines: the MACD line (difference between two EMAs) and the signal line (an EMA of the MACD line).
    # What It Tells You: It shows both trend direction (upward or downward) and momentum (strengthening or weakening). A bullish signal occurs when the MACD line crosses above the signal line.
    # Speed & Sensitivity: It's a bit slower and smoother compared to some other indicators, providing a broader view of the market trend.
    # How It's Calculated: By subtracting the 26-period EMA from the 12-period EMA (forming the MACD line) and then plotting a 9-period EMA of the MACD line (signal line). A bullish signal is indicated when the MACD line crosses above the signal line.

buy_condition_risk_reward = False
# Risk-Reward Ratio:
    # What It Is: The ratio compares the potential gain (reward) of a trade to its potential loss (risk).
    # What It Tells You: A higher ratio indicates a more favorable trade, where the potential gain outweighs the potential loss. A common benchmark is a ratio of at least 2:1 (twice as much reward as risk).
    # Speed & Sensitivity: This ratio is a strategic measure, not directly sensitive to rapid market movements, but crucial for evaluating the overall feasibility and soundness of a trade.
    # How It's Calculated:
        # Risk: Calculated as the difference between the current price and the stop-loss price (the lower price at which you'd sell to limit losses). 
        # Reward: Determined by the difference between the current price and the take-profit price (the higher price at which you'd sell to realize gains).

buy_condition_rsi_strong = False
# Relative Strength Index (RSI):
    # What It Is: RSI measures the magnitude of recent price changes to evaluate overbought or oversold conditions.
    # What It Tells You: An RSI reading above a certain threshold (like 70) indicates a strong upward price movement (potentially overbought), while below a threshold (like 30) suggests a strong downward movement (potentially oversold).
    # Speed & Sensitivity: It's moderately responsive, providing insights into the overall strength of the current price trend.
    # How It's Calculated: By analyzing the average gains and average losses over a specified period (commonly 14 days) to produce a value between 0 and 100. This value indicates if a stock is potentially overbought (above 70) or oversold (below 30).

buy_condition_short_ema_rising = False
# Short-Term EMA Rising:
    # What It Is: This checks if the current value of a short-term EMA is higher than its previous value.
    # What It Tells You: A rising short-term EMA suggests increasing short-term momentum or an emerging uptrend.
    # Speed & Sensitivity: It's a quick indicator, reacting to recent price changes, making it useful for identifying early trend shifts.
    # How It's Calculated: By comparing the current value of a short-term EMA (e.g., 20-day EMA) with its previous value. If the current value is higher, the short-term EMA is considered to be rising.

buy_condition_stochastic_rsi_strong = False
# Stochastic RSI:
    # What It Is: This is an indicator of an indicator, measuring the RSI's level relative to its high-low range over a set period.
    # What It Tells You: It identifies overbought or oversold conditions more sensitively than the standard RSI.
    # Speed & Sensitivity: It's highly sensitive and reacts quickly to price movements, making it useful for spotting short-term trend reversals.
    # How It's Calculated: By taking the RSI value and plotting it on a scale of 0 to 100, considering its high and low values over a specific period. It's a measure of the RSI's relative level to its range.

# Buy Conditions - Technical Indicator Parameters:
    # Control what values the algorithm uses for optimal performance tuning
buy_parameter_atr_periods = 14 # Determines the period over which the Average True Range (ATR) is calculated. The 14-period ATR is a common choice for gauging market volatility.
buy_parameter_ema_short_periods = 9 # The number of periods used to calculate the short-term Exponential Moving Average. A smaller number like 9 provides a more responsive EMA.
buy_parameter_ema_long_periods = 14 # Used for computing the long-term Exponential Moving Average. A larger number like 14 offers a slower, more stable EMA.
buy_parameter_rsi_periods = 14 # Specifies the number of periods (days, hours, etc.) over which the RSI is calculated. Commonly set to 14 for standard RSI analysis.
buy_parameter_rsi_min_threshold = 50 # The minimum threshold for RSI to be considered bullish. Above 50 can suggest upward momentum.
buy_parameter_stochastic_rsi_periods = 14 # Defines the period for calculating the Stochastic RSI. Often set to 14, similar to the standard RSI.
buy_parameter_stochastic_rsi_min_threshold = 0.5 # The lower bound for Stochastic RSI to be seen as bullish. A value above 0.5 (in a range from 0 to 1) typically indicates increasing momentum.

# Sell Conditions - Enable\Disable:
    # Set each condition to True or False to control which conditions the algorithm should consider before placing a Buy trade
    # Price Targets
sell_condition_take_profit_percent = True
sell_condition_trailing_take_profit = True
sell_condition_atr_take_profit = True
sell_condition_fibonacci_take_profit = True
sell_condition_fixed_stop_loss = True
sell_condition_trailing_stop_loss = True
sell_condition_atr_stop_loss = True
    # Technical Indicators
sell_condition_macd_cross_below_signal = False
sell_condition_rsi_weak = False

# Sell Conditions - Technical Indicator Parameters:
    # Control what values the algorithm uses for optimal performance tuning
sell_parameter_rsi_periods = 14 # Specifies the number of periods (days, hours, etc.) over which the RSI is calculated. Commonly set to 14 for standard RSI analysis.
sell_parameter_rsi_min_threshold = 50 # The minimum threshold for RSI to be considered bullish. Above 50 can suggest upward momentum.
sell_parameter_stochastic_rsi_periods = 14 # Defines the period for calculating the Stochastic RSI. Often set to 14, similar to the standard RSI.
sell_parameter_stochastic_rsi_min_threshold = 0.5 # The lower bound for Stochastic RSI to be seen as bullish. A value above 0.5 (in a range from 0 to 1) typically indicates increasing momentum.
sell_parameter_ema_short_periods = 9 # The number of periods used to calculate the short-term Exponential Moving Average. A smaller number like 9 provides a more responsive EMA.
sell_parameter_ema_long_periods = 14 # Used for computing the long-term Exponential Moving Average. A larger number like 14 offers a slower, more stable EMA.
sell_parameter_atr_periods = 14 # Determines the period over which the Average True Range (ATR) is calculated. The 14-period ATR is a common choice for gauging market volatility.

# Sell Condition Parameters:
    # Price Targets:
fixed_take_profit_percent = 0.05 # WHAT IS THIS FOR AGAIN / DUPLICATE?
fixed_take_profit_percent_gain = 5.00 # Sell a fixed portion if over this % profit.
fixed_take_profit_percent_to_sell = 0.25 # The portion % to sell if fixed_take_profit_percent_gain is reached
trailing_take_profit_percent = 0.05 # Takes profit based on % of current price
fixed_stop_loss_percent = 0.20 # Max loss % for a held share, in case trailing stop loss fails            
trailing_stop_loss_percent = 0.05 # Sell if loss hits this %
atr_stop_loss_price_multiplier = 2 # Modifies the ATR for increased aggressiveness / risk before triggering stop loss 

# Position Sizing Parameters
max_portfolio_invested_percent = 0.90 # Max % of total portfolio value to be invested.
max_trade_portfolio_percent = 0.15 # Max % of portfolio to spend on a single trade.
buy_limit_order_percent = 0.99 # Submit buy orders at X% the asking price, to get the extra X% deal.
min_stocks_invested = 5 # Min unique stocks that must be in the portfolio.
max_sector_invested_percent = 0.65 # Maximum portfolio percent for a single sector.
max_submitted_order_minutes = 15 # Expire any pending (un-filled) submitted orders after this time (Only Limit Orders should be affected).

# Stock Filtering Parameters
min_stock_price = 3.00 # Require stock to be at least this price to limit risk.
max_stock_price_portfolio_percent = 0.10 # Limit max stock price to X% of portfolio size for affordability.
min_pe_ratio = 0 # Require stock to have positive earnings.
max_pe_ratio = 20 # Require stock to not be overvalued / overbought.
min_revenue_growth_percent = 0 # Require stock to have positive Revenue Growth for past year.
# List of stock symbols we don't want to trade
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
    "GS",     # Goldman Sachs Group, Inc.
    "DB",     # Deutsche Bank AG
    "TMUS",   # T-Mobile US, Inc.
]

# Algorithm Initialization Parameters

# Set Start Date for historical backtest data.
def SetStartDate(algorithm_instance):
    algorithm_instance.SetStartDate(2023, 10, 1) # Format: YYYY, M, D

# Set End Date for historical backtest data - defaults to current.
# def SetEndDate(algorithm_instance):
#     algorithm_instance.SetEndDate(2023, 10, 1) # Format: YYYY, M, D
    
# SetCash to the amount the algorithm starts with when backtesting.
starting_cash = 1000
def SetCash(algorithm_instance):
    algorithm_instance.SetCash(starting_cash)

# SetWarmUp ensures time-based indicator data will be correct.
    # Period should be the max time needed by any of the indicators.
    # Resolution should be the finest level of detail out of all the indicators.
warmup_period = 100
def SetWarmUp(algorithm_instance):
    algorithm_instance.SetWarmUp(warmup_period, Resolution.Daily)

# SetBrokerageModel to TD Ameritrade (they have 0 fees). Better simulates live trading results.
def SetBrokerageModel(algorithm_instance):
    algorithm_instance.SetBrokerageModel(BrokerageName.TDAmeritrade, AccountType.Cash)

# End config.py