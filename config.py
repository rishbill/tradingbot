# Begin config.py

# This module is meant to for setting all the configurables of the algorithm, including enabling/disabling conditions, and setting optimization parameters.

from AlgorithmImports import *
# -----------------------------------------------------
# Algorithm Initialization Parameters
# -----------------------------------------------------
# Built-in QuantConnect method: SetStartDate for historical backtest data.
def SetStartDate(algorithm_instance):
    algorithm_instance.SetStartDate(2023, 10, 1) # Format: YYYY, M, D

# Built-in QuantConnect method: SetEndDate for historical backtest data - defaults to current.
# def SetEndDate(algorithm_instance):
#     algorithm_instance.SetEndDate(2023, 10, 1) # Format: YYYY, M, D
    
# Built-in QuantConnect method: SetCash to the amount the algorithm starts with when backtesting. Cash is also called "Buying Power".
starting_cash = 1000
def SetCash(algorithm_instance):
    algorithm_instance.SetCash(starting_cash)

# Built-in QuantConnect method: SetWarmUp ensures time-based indicator data will be correct.
    # Period should be the max time needed by any of the indicators.
    # Resolution should be the finest level of detail out of all the indicators.
warmup_period = 30
def SetWarmUp(algorithm_instance):
    algorithm_instance.SetWarmUp(warmup_period, Resolution.Daily)

# Built-in QuantConnect method: SetBrokerageModel to TD Ameritrade (they have 0 fees). Better simulates live trading results.
def SetBrokerageModel(algorithm_instance):
    algorithm_instance.SetBrokerageModel(BrokerageName.TradierBrokerage, AccountType.Cash)

max_pending_order_age_minutes = 15 # Expire any pending (un-filled) submitted orders after this time (Only Limit Orders should be affected).

# -----------------------------------------------------
# Stock Filtering Conditions:
# -----------------------------------------------------
stock_filter_condition_min_price = True
    # Minimum Stock Price Filter:
        # What It Does: Excludes stocks priced below a certain threshold.
        # Reasoning: Lower-priced stocks often come with higher volatility and risk, and may not meet certain exchange listing requirements, suggesting less stability.

stock_filter_condition_max_stock_price_portfolio_percent = True
    # Maximum Stock Price as Percentage of Portfolio Filter:
        # What It Does: Limits the maximum price of a stock relative to the total portfolio value.
        # Reasoning: Prevents overexposure to any single stock, ensuring diversification and risk management by avoiding too much allocation in high-priced stocks.

stock_filter_condition_min_pe_ratio = True
    # Minimum P/E Ratio Filter:
        # What It Does: Filters out stocks with a P/E ratio below a certain level.
        # Reasoning: A minimum P/E ratio can help avoid companies with no or negative earnings, targeting firms with at least some level of profitability.

stock_filter_condition_max_pe_ratio = True
    # Maximum P/E Ratio Filter:
        # What It Does: Excludes stocks with a P/E ratio above a certain level.
        # Reasoning: Aims to avoid overvalued stocks that might be priced too high relative to their earnings, reducing exposure to potential market corrections or bubbles.

stock_filter_condition_min_revenue_growth_percent = True
    # Minimum Revenue Growth Percentage Filter:
        # What It Does: Focuses on companies with a minimum threshold of revenue growth.
        # Reasoning: Identifies companies showing signs of growth and financial health, suggesting potential for future profitability and stock price appreciation.

stock_filter_condition_blacklist = False
    # Blacklist Filter:
        # What It Does: Excludes specific stocks or sectors based on predetermined criteria.
        # Reasoning: Allows exclusion of stocks or sectors based on individual or strategic preferences, such as avoiding industries or companies with ethical concerns or poor performance history.

stock_filter_condition_whitelist = False
    # Whitelist Filter:
        # What It Does: Opts for a static, unchanging stock universe instead of dynamic.
        # Reasoning: Allows exclusion of stocks or sectors based on individual or strategic preferences, such as avoiding industries or companies with ethical concerns or poor performance history.

# -----------------------------------------------------
# Stock Filtering Parameters:
    # Control what stocks can be traded on a given trading day, if their conditions are enabled above.
# -----------------------------------------------------
stock_filter_parameter_min_price = 3.00
    # Require stock to be at least this price to limit risk.

stock_filter_parameter_max_stock_price_portfolio_percent = 0.10
    # Limit max stock price to X% of portfolio size for affordability and diversification.

stock_filter_parameter_min_pe_ratio = 0
    # Require stock to have positive Profit to Earnings Ratio.

stock_filter_parameter_max_pe_ratio = 20
    # Require stock to not be overvalued / overbought.
    
stock_filter_parameter_min_revenue_growth_percent = 0
    # Require stock to have positive Revenue Growth for past year.

    # List of stock symbols we don't want to trade due to ethics or other reasons.
stock_filter_parameter_blacklist = [
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
    # List of stock symbols to use for a static universe instead of dynamic.
stock_filter_parameter_whitelist = [
    "TSLA",  # Tesla
]

# -----------------------------------------------------
# Buy Conditions - Enable\Disable:
    # Set each condition to True or False to control which conditions the algorithm should consider before placing a Buy trade.
# -----------------------------------------------------
    # Price Targets:
buy_condition_limit_order_percent = True 
    # Submit buy orders at x% the asking price, to get the extra deal.

    # Technical Indicators
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
        # How It's Calculated: By subtracting the 26-period EMA from the 12-period EMA (forming the MACD line) and then plotting a 9-period EMA of the MACD line (signal line).

buy_condition_reward_risk_ratio = True
    # Reward-Risk Ratio:
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

# -----------------------------------------------------
    # Diversification Conditions - Enable\Disable:
# -----------------------------------------------------
buy_condition_limit_order_percent = True
    # Attempt to place Buy orders at a discounted limit price instead of market price.

buy_condition_max_portfolio_percent_per_trade = True
    # Max % of portfolio to spend on a single trade.

buy_condition_max_total_portfolio_invested_percent = True
    # Max % of total portfolio value to be invested.

buy_condition_min_stocks_invested = True
    # Min unique stocks that must be in the portfolio.

buy_condition_max_sector_invested_percent = True
    # Maximum portfolio percent for a single sector.

buy_condition_pdt_rule = True
    # Follow the Pattern Day Trader law to restrict trades if 4 day trades are made in a 5 business day period on a margin account under $25,000. 

buy_condition_lost_it_all = True
    # Block Buys if the total portfolio value < $X - This is bad and means the algo failed completely.

buy_condition_min_cash = True
    # Block Buys if portfolio cash aka "Buying Power" < $X

# -----------------------------------------------------
# Buy Conditions Parameters:
    # Control what values the algorithm uses for buy signals, if their conditions are enabled above.
# -----------------------------------------------------
    # Price Targets:
buy_parameter_limit_order_percent = 0.98
    # Submit buy orders at x% the asking price, to get the extra deal.

    # Technical Indicators
buy_parameter_atr_breakout_level_multiplier = 1.5
    # Determines how far above the current price the breakout level should be set.

buy_parameter_atr_low_period = 30

buy_parameter_atr_periods = 14
    # Determines the period over which the Average True Range (ATR) is calculated. The 14-period ATR is a common choice for gauging market volatility.

buy_parameter_ema_short_periods = 9
    # The number of periods used to calculate the short-term Exponential Moving Average. A smaller number like 9 provides a more responsive EMA.

buy_parameter_ema_long_periods = 14
    # Used for computing the long-term Exponential Moving Average. A larger number like 14 offers a slower, more stable EMA.

buy_parameter_reward_risk_ratio = 2
    # This ratio ensures that the potential reward of a trade is at least twice the potential risk, aligning with a conservative risk management strategy and aiming for trades where the potential gains significantly outweigh the losses.

buy_parameter_rsi_periods = 14
    # Specifies the number of periods (days, hours, etc.) over which the RSI is calculated. Commonly set to 14 for standard RSI analysis.

buy_parameter_rsi_min_threshold = 50
    # The minimum threshold for RSI to be considered bullish. Above 50 can suggest upward momentum.

buy_parameter_stochastic_rsi_periods = 14
    # Defines the period for calculating the Stochastic RSI. Often set to 14, similar to the standard RSI.

buy_parameter_stochastic_rsi_min_threshold = 0.5
    # The lower bound for Stochastic RSI to be seen as bullish. A value above 0.5 (in a range from 0 to 1) typically indicates increasing momentum.
    
    # Diversification \ Position Sizing Parameters:
buy_condition_kelly_criterion_position_size = True
    # Uses the win probability and win/loss ratio to determine the optimal fraction of capital to be used for each trade

buy_condition_limit_order_percent = True
    # Attempt to place Buy orders at a discounted limit price instead of market price.

buy_parameter_max_total_portfolio_invested_percent = 0.95
    # Max % of total portfolio value to be invested.

buy_parameter_max_portfolio_percent_per_trade = 0.50
    # Max % of portfolio to spend on a single trade.

buy_parameter_min_stocks_invested = 5
    # Min unique stocks that must be in the portfolio.

buy_parameter_max_sector_invested_percent = 0.65
    # Maximum portfolio percent for a single sector.

buy_parameter_lost_it_all = 50
    # Minimum portfolio value to Buy.

# -----------------------------------------------------
# Sell Conditions - Enable\Disable:
    # Set each condition to True or False to control which conditions the algorithm should consider before placing a Sell trade.
# -----------------------------------------------------
    
    # Price Targets:
sell_condition_stop_loss_atr_price = True
    # An ATR Multiplier-based Stop Loss Price is set by using the Average True Range value, a measure of market volatility, to determine a stop loss level that adjusts with the asset's recent price fluctuations. 

sell_condition_stop_loss_fibonacci_atr_price = True
    # A Fibonacci Retracement-Based Stop Loss Price is established using key Fibonacci levels as potential targets for exiting a position, based on the assumption that price may reverse after reaching these historically significant proportions of a prior move.

sell_condition_stop_loss_percent = True
    # Stop Loss %: Sell if position loss hits this fixed %. Good in case ATR or Trailing Stop Loss Prices fail or are too high, to avoid losing too much on the position.

sell_condition_stop_loss_trailing_percent = True
    # Trailing Stop %: Sell share at a determined price when it drops x% from the stock's highest price since purchase.

sell_condition_take_profit_atr_price = True
    # An ATR Multiplier-based Stop Loss Price is set by using the Average True Range value, a measure of market volatility, to determine a stop loss level that adjusts with the asset's recent price fluctuations. 

sell_condition_take_profit_fibonacci_atr_price = True
    # A Fibonacci Retracement-Based Take Profit Price is established using key Fibonacci levels as potential targets for exiting a position, based on the assumption that price may reverse after reaching these historically significant proportions of a prior move.

sell_condition_take_profit_percent = True
    # Take Profit Percent: Good for locking in profit when a "feel-good" profit level is reached i.e. "I at least want to beat SPY". Can be dynamically calculated by % of current price or profit.

sell_condition_take_profit_trailing_percent = True
    # Trailing Stop %: Sell share at a determined price when it drops x% from the stock's highest price since purchase.

    # Technical Indicators:
sell_condition_macd_cross_below_signal = False
    # MACD (Moving Average Convergence Divergence):
        # What It Is: The MACD involves two lines: the MACD line (difference between two EMAs) and the signal line (an EMA of the MACD line).
        # What It Tells You: It shows both trend direction (upward or downward) and momentum (strengthening or weakening). A bearish signal occurs when the MACD line crosses below the signal line.
        # Speed & Sensitivity: It's a bit slower and smoother compared to some other indicators, providing a broader view of the market trend.
        # How It's Calculated: By subtracting the 26-period EMA from the 12-period EMA (forming the MACD line) and then plotting a 9-period EMA of the MACD line (signal line).

sell_condition_rsi_weak = False
    # Relative Strength Index (RSI):
        # What It Is: RSI measures the magnitude of recent price changes to evaluate overbought or oversold conditions.
        # What It Tells You: An RSI reading above a certain threshold (like 70) indicates a strong upward price movement (potentially overbought), while below a threshold (like 30) suggests a strong downward movement (potentially oversold).
        # Speed & Sensitivity: It's moderately responsive, providing insights into the overall strength of the current price trend.
        # How It's Calculated: By analyzing the average gains and average losses over a specified period (commonly 14 days) to produce a value between 0 and 100. This value indicates if a stock is potentially overbought (above 70) or oversold (below 30).

# -----------------------------------------------------
# Sell Conditions - Parameters:
    # Control what values the algorithm uses for sell signals, if their conditions are enabled above.
# -----------------------------------------------------
    # Price Targets:
sell_parameter_stop_loss_fibonacci_retracement_levels = [0.236, 0.382, 0.618] 
    # Fibonacci retracement levels to determine potential stop prices. These levels are based on the Fibonacci sequence, a well-known series in mathematics, and are commonly used in technical analysis as indicators of potential reversal points in an asset's price. Traders often observe these specific ratios (23.6%, 38.2%, 61.8%) for signs of price support or resistance

sell_parameter_stop_loss_percent = 0.20 
    # Max loss % for a held share, in case ATR-based or trailing stop loss fails or are both too high.

sell_parameter_stop_loss_price_atr_multiplier = 2 
    # Modifies the ATR for increased aggressiveness / risk before triggering stop loss.

sell_parameter_stop_loss_trailing_percent = 0.10 
    # Sell share when it drops x% from the stock's highest price since purchase. "Highest" price could be a new peak (profit), or the original purchase price (loss).

sell_parameter_take_profit_fibonacci_retracement_levels = [0.236, 0.382, 0.618] 
    # Fibonacci retracement levels to determine potential stop prices. These levels are based on the Fibonacci sequence, a well-known series in mathematics, and are commonly used in technical analysis as indicators of potential reversal points in an asset's price. Traders often observe these specific ratios (23.6%, 38.2%, 61.8%) for signs of price support or resistance

sell_parameter_take_profit_percent = 0.20 
    # Sell a portion of shares if over this % profit (SPY average is 8%).

sell_parameter_take_profit_percent_to_sell = 0.50 
    # The portion % to sell if fixed_take_profit_percent_gain is reached.

sell_parameter_take_profit_price_atr_multiplier = 2
    # Modifies the ATR for increased aggressiveness / risk before triggering take profit.

sell_parameter_take_profit_trailing_percent = 0.10
    # Sell share when it drops x% from the stock's highest price since purchase. "Highest" price could be a new peak (profit), or the original purchase price (loss).

    # Technical Indicators:
sell_parameter_atr_periods = 14 
    # Determines the period over which the Average True Range (ATR) is calculated. The 14-period ATR is a common choice for gauging market volatility.

sell_parameter_rsi_max_threshold = 30
        # The max threshold for RSI to be considered bearish. Below 30 can suggest downward momentum.

sell_parameter_rsi_periods = 14
    # Specifies the number of periods (days, hours, etc.) over which the RSI is calculated. Commonly set to 14 for standard RSI analysis.

# End config.py