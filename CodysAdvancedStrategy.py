# QuantConnect Knowledge Base
# https://www.quantconnect.com/docs/v2/writing-algorithms
# Stocks = Symbols = Securities

from AlgorithmImports import *

class CodysAdvancedStrategy(QCAlgorithm):
    def Initialize(self):
    # Main function for class
        # Basic variables
        try:
            self.Debug("Initializing basic variables...")
            self.SetStartDate(2024, 1, 1) # Set Start Date
            # self.SetEndDate(2024, 12, 1) # Set End Date -- Default is present
            self.SetCash(1000) # Set Strategy Starting Capital
            self.SetWarmUp(100, Resolution.Daily) # Set Warm Up period for accurate indicator calculations
            self.warm_up_counter = 0 # Increments for each warm day, to check warmup progress
            self.last_increment_day = None # Used to calculate warm_up_counter
            self.Debug("---- Successfully initialized basic parameters:")
            self.Debug(f"------- Initial Capital -------------------------- ${self.Portfolio.Cash}")
            self.Debug(f"------- Start Date ------------------------------- {self.StartDate}")
            self.Debug(f"------- End Date --------------------------------- {self.EndDate}")
            self.Debug(f"------- Warm Up ---------------------------------- 100 Days")
        except Exception as e:
            self.Error(f"---- Error initializing basic variables: {str(e)}")

        # Portfolio Summary
        try:
            self.Debug("Portfolio Summary:")
            # Portfolio Value
            portfolio_value = self.Portfolio.TotalPortfolioValue
            self.Debug(f"---- Portfolio Value ----------------------------- ${portfolio_value}")
            # Stock counts and percentages per sector
            stock_counts_per_sector = self.CalculateStockCountsPerSector()
            total_invested_stocks = sum(stock_counts_per_sector.values())
            if total_invested_stocks == 0:
                self.Debug("-------- No invested stocks in portfolio")
            else:
                self.Debug("---- Portfolio Summary:")
                for sector, count in stock_counts_per_sector.items():
                    sector_value = self.CalculateSectorPortfolioValue(sector)
                    percentage_of_portfolio = (sector_value / portfolio_value) * 100
                    self.Debug(f"------- Sector: {sector}, Count: {count}, Value: ${sector_value}, % of Portfolio: {percentage_of_portfolio:.2f}%")
        except Exception as e:
            self.Error(f"---- Error in PortfolioSummary: {str(e)}")

        try:
            # Indicator Variables
            # These are set per each OnData function that runs with each bar/candle/slice
            self.Debug("Initializing Indicator Variables...")
            self.rsi_min_threshold = 50
            self.rsi_periods = 14
            self.stochastic_rsi = {}
            self.stochastic_rsi_periods = 14
            self.ema_short_periods = 9
            self.ema_long_periods = 14
            self.ema_short = {}
            self.ema_long = {}
            self.atr = {}
            self.atr_periods = 14
            self.Debug("---- Successfully Initialized Indicator Variables: self.ema_short, self.ema_long, self.atr, self.stochastic_rsi")

            # News and Sentiment Variables
            self.Debug("Initializing News and Sentiment Variables...")
            self.news_feed = {}
            self.Debug("---- Successfully Initialized News and Sentiment Variables: self.news_feed")

            # Trading Parameters
            self.Debug("Initializing Trading Variables...")
            self.max_portfolio_at_risk = 0.90 # Max % of portfolio invested
            self.max_percent_per_trade = 0.15 # Max % of portfolio to spend on a single trade
            self.fixed_take_profit_percent_gain = 5.00 # Sell a fixed portion if over this % profit
            self.fixed_take_profit_percent_to_sell = 0.25 # The portion % to sell if fixed_take_profit_percent_gain is reached
            self.trailing_take_profit_percent = 0.05 # Takes profit based on % of current price
            self.trailing_take_profit_price = {} # Calculated after each trade
            self.fixed_stop_loss_percent = 0.20 # Max loss % for a held share, in case trailing stop loss fails            
            self.trailing_stop_loss_percent = 0.05 # Sell a fixed portion if over this % loss
            self.stop_loss_atr_multiplier = 2 # Modifies the ATR for increased aggressiveness / risk before triggering stop loss 
            self.buy_limit_order_percent = 0.99 # Bid buy orders at 99% the ask, to get the extra deal
            self.max_submitted_order_minutes = 15 # Expire any pending submitted orders after this time
            self.trailing_stop_price = {} # Calculated after each trade 
            self.stockSymbols = [] # Holds the stocks in the dynamically filtered Universe
            self.numberOfStocks = 0  # Number of stocks in stockSymbols

            self.Debug("---- Successfully Initialized Trading Variables: ")
            self.Debug(f"------- Max Portfolio At Risk --------------------- {self.max_portfolio_at_risk * 100}%")
            self.Debug(f"------- Max Percent Per Trade --------------------- {self.max_percent_per_trade * 100}%")
            self.Debug(f"------- Fixed Stop Loss Percent ------------------- {self.fixed_stop_loss_percent * 100}%")
            self.Debug(f"------- Fixed Take Profit Percent Gain ------------ {self.fixed_take_profit_percent_gain}%")
            self.Debug(f"------- Fixed Take Profit Percent To Sell --------- {self.fixed_take_profit_percent_to_sell * 100}%")
            self.Debug(f"------- Stop Loss ATR Multiplier ------------------ {self.stop_loss_atr_multiplier}")
            self.Debug(f"------- Trailing Stop Loss Percent ---------------- {self.trailing_stop_loss_percent * 100}%")

            # Profit/Loss Variables
            # Calculated after each trade via functions HandleTradeOutcome and UpdateWinProbabilityAndRatio
            self.win_count = 0
            self.loss_count = 0
            self.total_profit = 0
            self.total_loss = 0            

        except Exception as e:
            self.Error(f"Error Initializing Variables: {str(e)}")        

        # Universe Filtering
        try:
            self.Debug("Initializing Universe filter variables...")
            # Fundamentals criteria
            self.max_stock_price = self.Portfolio.TotalPortfolioValue * 0.10 # Limit max stock price to X% of portfolio size, for affordability
            self.min_stock_price = 1.00 # Require the min stock price to limit risk
            self.min_pe_ratio = 0 # Require stock to have positive earnings
            self.max_pe_ratio = 20 # Require stock to not be overvalued
            self.min_revenue_growth = 0 # Require stock to have positive Revenue Growth
            # # Portfolio diversification criteria
            # self.min_total_portfolio_stocks = 5 # Require at least 5 stocks for whole portfolio 
            # self.min_portfolio_sectors = 3 # Require at least 3 sectors for whole portfolio            
            # self.max_portfolio_exposure_per_biggest_sector = 0.65 # Require biggest portfolio sector to be < 65% of whole portfolio value
            # self.min_portfolio_stocks_per_biggest_sector = 5 # Require at least 5 stocks in biggest sector
            # self.max_portfolio_invested = 0.9 # Maximum total portfolio value invested in stocks 
            self.Debug("---- Successfully set Universe selection variables:")
            self.Debug(f"------- Stock Price Range ------------------------- ${self.min_stock_price} - ${self.max_stock_price}")
            self.Debug(f"------- P/E Ratio Range --------------------------- {self.min_pe_ratio} to {self.max_pe_ratio}")
            self.Debug(f"------- Min Revenue Growth ------------------------ {self.min_revenue_growth}")
            # self.Debug(f"------- Min total portfolio stocks -------------- {self.min_total_portfolio_stocks}")
            # self.Debug(f"------- Min portfolio sectors ------------------- {self.min_portfolio_sectors}")
            # self.Debug(f"------- Max exposure per biggest sector --------- {self.max_portfolio_exposure_per_biggest_sector * 100}%")
            # self.Debug(f"------- Min stocks per biggest sector ----------- {self.min_portfolio_stocks_per_biggest_sector}")
            # self.Debug(f"------- Max invested percentage ----------------- {self.max_portfolio_invested * 100}%")
        except Exception as e:
            self.Error(f"---- Error setting Universe selection variables: {str(e)}")

        try:
            self.Debug(f"Filtering Universe...")
            self.UniverseSettings.Resolution = Resolution.Minute
            self.AddUniverse(self.UniverseFilter)  # Get the stocks for today's potential trades
        except Exception as e:
            self.Error(f"---- Error filtering Universe: {str(e)}")                    

    def UniverseFilter(self, fundamental: List[Fundamental]) -> List[Symbol]:
    # Returns a filtered list of stocks    
        try:
            filtered = [f for f in fundamental if f.HasFundamentalData and self.min_stock_price <= f.Price < self.max_stock_price and f.ValuationRatios.PERatio > self.min_pe_ratio and f.ValuationRatios.PERatio < self.max_pe_ratio and f.OperationRatios.RevenueGrowth.OneYear > self.min_revenue_growth and not np.isnan(f.ValuationRatios.PERatio) and not np.isnan(f.OperationRatios.RevenueGrowth.OneYear) and not np.isnan(f.DollarVolume) and not np.isnan(f.MarketCap)]
            sortedByDollarVolume = sorted(filtered, key=lambda f: f.DollarVolume, reverse=True)[:100]
            sortedByPeRatio = sorted(sortedByDollarVolume, key=lambda f: f.ValuationRatios.PERatio, reverse=False)[:100]
            # Return the list of coarse-filtered stocks which have passed through filters
            if self.warm_up_counter >= 100:
                self.Debug("---- Successfully filtered Universe")
                for f in sortedByPeRatio:
                    try:
                        self.Debug(f"-------- {f.Symbol}, Price: ${f.Price}, Dollar Volume: ${f.DollarVolume}, P/E Ratio:{f.ValuationRatios.PERatio}, Revenue Growth: {f.OperationRatios.RevenueGrowth.OneYear}, MarketCap: {f.MarketCap}, Sector: {f.AssetClassification.MorningstarSectorCode}")
                    except Exception as e:
                        self.Debug(f"Error accessing fundamentals data for {f.Symbol}: {str(e)}")
            else:
                self.Debug(f"Warming Up... ({self.warm_up_counter}\100 Days )")
            return [f.Symbol for f in sortedByPeRatio]
        except Exception as e:
            self.Error(f"---- Error on UniverseFilter: {str(e)}")        

    def CalculateStockCountsPerSector(self):
    # Returns a list of stock counts for each sector in the current portfolio
        try:
            stock_counts_per_sector = {} # Initialize list variable
            for symbol in self.Portfolio.Keys: # Iterate over all stocks in portfolio
                if self.Portfolio[symbol].Invested: # If the portfolio is invested in this stock
                    sector = self.GetSectorForStock(symbol) # Get the sector for this stock
                    if sector: # If sector was returned
                        stock_counts_per_sector[sector] = stock_counts_per_sector.get(sector, 0) + 1 # Increment the number of stocks for this sector 
            return stock_counts_per_sector # Return the  list of stock counts per sector
        except Exception as e:
            self.Error(f"Error on CalculateStockCountsPerSector: {str(e)}")        

    def GetSectorForStock(self, stock):
    # Returns the sector associated with the provided stock
        try:
            self.Debug(f"----Checking sector for {stock}")
            if stock.HasFundamentalData:  # Check if fundamental data is available
                self.Debug(f"------- Symbol {stock} has fundamental data")
                sector = stock.AssetClassification.MorningstarSectorCode  # Get the sector code
                return sector if sector is not None else "Unknown"  # Return the sector or 'Unknown' if not found
            else: 
                self.Error(f"------- Symbol {stock} does not have fundamental data")
                return "Not Available"  # Return 'Not Available' if no fundamental data
        except Exception as e:
            self.Error(f"Error on GetSectorForStock for {stock.Symbol}: {str(e)}")
            return "Error"

    def GetDistinctSectorsFromPortfolio(self):
    # Gets the number of sectors in the portfolio
        try:
            distinct_sectors_from_portfolio = set() # Initialize distinct list variable
            for symbol in self.Portfolio.Keys: # Iterate over all stocks in portfolio
                if self.Portfolio[symbol].Invested: # If the portfolio is invested in this stock
                    sector = self.GetSectorForStock(symbol) # Get the sector for this stock
                    distinct_sectors_from_portfolio.add(sector) # Add sector to the distinct list
            return distinct_sectors_from_portfolio # Return the final list of distinct portfolio sectors
        except Exception as e:
            self.Error(f"Error on GetDistinctSectorsFromPortfolio: {str(e)}")        

    def CalculateSectorPortfolioValue(self, sector):
    # Gets the total portfolio value for a provided sector 
        try:    
            sector_value = 0 # Initialize integer variable 
            for symbol in self.Portfolio.Keys: # Iterate over all stocks in portfolio
                if self.Portfolio[symbol].Invested and self.GetSector(symbol) == sector: # If the portfolio is invested in this stock, and the sector for this stock matches the sector being checked
                    sector_value += self.Portfolio[symbol].HoldingsValue # Adds the value of portfolio holdings for this stock to the sector_value
            return sector_value # Returns the total portfolio value for the provided sector
        except Exception as e:
            self.Error(f"Error on CalculateSectorPortfolioValue: {str(e)}")        

    def OnSecuritiesChanged(self, changes):
    # Runs when new symbols  
        self.Debug(f"---- Universe Updated. Symbols Count: {len(changes.AddedSecurities)}")
        # Adjust indicators and news feed for added and removed securities
        try: 
            for security in changes.AddedSecurities:
                symbol = security.Symbol
                if symbol not in self.stockSymbols:
                    self.stockSymbols.append(symbol)
                self.numberOfStocks = len(self.stockSymbols)    
                # Create and register indicators for each added symbol
                self.ema_short[symbol] = self.EMA(symbol, self.ema_short_periods, Resolution.Minute)
                self.ema_long[symbol] = self.EMA(symbol, self.ema_long_periods, Resolution.Minute)
                self.atr[symbol] = self.ATR(symbol, self.atr_periods, MovingAverageType.Wilders, Resolution.Minute)
                # Create and register the Stochastic RSI indicator for this symbol
                self.stochastic_rsi[symbol] = self.STO(symbol, self.stochastic_rsi_periods, Resolution.Minute)  # Create Stochastic RSI
                self.RegisterIndicator(symbol, self.stochastic_rsi[symbol], Resolution.Minute)
                self.news_feed[symbol] = self.AddData(TiingoNews, symbol)
            for security in changes.RemovedSecurities:
                symbol = security.Symbol
                if symbol in self.stockSymbols:
                    self.stockSymbols.remove(symbol)
                # Remove indicators for removed symbols
                if symbol in self.ema_short: del self.ema_short[symbol]
                if symbol in self.ema_long: del self.ema_long[symbol]
                if symbol in self.atr: del self.atr[symbol]
                if symbol in self.stochastic_rsi: del self.stochastic_rsi[symbol]
                if symbol in self.news_feed: self.RemoveSecurity(symbol)
        except Exception as e:
            self.Error(f"Error on OnSecuritiesChanged: {str(e)}")

    def OnData(self, data):
    # Runs upon receipt of every bar/candle for the filtered stocks
        current_day = self.Time.day
        if self.IsWarmingUp:
            if self.last_increment_day != current_day:
                self.warm_up_counter += 1
                self.last_increment_day = current_day            
            for symbol in self.stockSymbols:
                try:
                    # # Check if news for the symbol is present
                    # news_data = data.Get(TiingoNews, symbol)
                    # if news_data:
                    #     for article in news_data.Values:
                    #         # Log news articles and sentiment
                    #         self.Debug(f"News for {symbol}: Title - {article.Title}, Sentiment - {article.Sentiment}")
                    # Check for Buy condition
                    if self.ShouldBuy(symbol, data):
                        limit_price_to_buy = data[symbol].Close * self.buy_limit_order_percent
                        fraction_of_portfolio = 1 / self.numberOfStocks
                        # Direct calculation of the order quantity
                        total_cash_to_spend = self.Portfolio.Cash * fraction_of_portfolio
                        quantity_to_buy = total_cash_to_spend / limit_price_to_buy
                        quantity_to_buy = max(1, round(quantity_to_buy))  # Ensure at least one unit is bought
                        self.LimitOrder(symbol, quantity_to_buy, limit_price_to_buy)
                    # Update trailing take profit level for each invested symbol
                    if self.Portfolio[symbol].Invested:
                        current_price = data[symbol].Price
                        if symbol not in self.trailing_take_profit_price:
                            self.trailing_take_profit_price[symbol] = current_price * (1 + self.initial_trailing_take_profit_percent)
                        else:
                            # Update the trailing take profit if the price moves up
                            if current_price > self.trailing_take_profit_price[symbol] / (1 + self.initial_trailing_take_profit_percent):
                                self.trailing_take_profit_price[symbol] = current_price * (1 + self.initial_trailing_take_profit_percent)
                    # Check for Sell condition
                    if self.Portfolio[symbol].Invested and self.ShouldSell(symbol, data):
                        holdings = self.Portfolio[symbol].Quantity
                        self.MarketOrder(symbol, -holdings * self.fixed_take_profit_percent_to_sell)
                except Exception as e:
                    self.Debug(f"Error on OnData: {str(e)}")                        

    def ShouldBuy(self, symbol, data):
        try:
            # EMA analysis
            short_ema_current = self.ema_short[symbol].Current.Value
            long_ema_current = self.ema_long[symbol].Current.Value
            short_ema_previous = self.ema_short[symbol].Previous.Value
            long_ema_previous = self.ema_long[symbol].Previous.Value
            is_ema_crossover = short_ema_current > long_ema_current
            is_short_ema_rising = short_ema_current > short_ema_previous
            is_ema_distance_widening = (short_ema_current - long_ema_current) > (short_ema_previous - long_ema_previous)
            # RSI Analysis
            rsi_value = self.RSI(symbol, self.rsi_periods, Resolution.Daily).Current.Value
            is_rsi_bullish = rsi_value > self.rsi_min_threshold
            is_stochastic_rsi_bullish = self.stochastic_rsi[symbol].IsReady and self.stochastic_rsi[symbol].stochastic_rsi > 0.5
            # MACD Analysis
            macd = self.MACD(symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily, Field.Close)
            is_macd_bullish = macd.Current.Value > macd.Signal.Current.Value
            # Risk/Reward Analysis
            risk = self.CalculateRisk(symbol, data)
            reward = self.CalculateReward(symbol, data)
            if reward is None or risk is None:
                return False  # Cannot proceed if risk or reward cannot be calculated
            is_acceptable_risk_reward = reward > 0 and risk > 0 and (reward / risk) >= 2
            # Check if all conditions are met
            return is_short_ema_rising and is_ema_crossover and is_ema_distance_widening and is_stochastic_rsi_bullish and is_rsi_bullish and is_macd_bullish and is_acceptable_risk_reward
        except Exception as e:
            self.Debug(f"Error on ShouldBuy: {str(e)}") 
            return False
                     
    def ShouldSell(self, symbol, data):
        current_price = data[symbol].Price
        invested_price = self.Portfolio[symbol].AveragePrice
        profit = (current_price - invested_price) / invested_price
        # Check for Take Profit condition
        if profit >= self.fixed_take_profit_percent_gain:
            self.Debug(f"Take Profit Triggered for {symbol}: Current Price: {current_price}, Invested Price: {invested_price}, Profit: {profit}")
            return True
        # Check for Stop Loss condition
        current_trailing_stop = self.trailing_stop_price.get(symbol, 0)
        new_trailing_stop = current_price * (1 - self.trailing_stop_loss_percent)
        if new_trailing_stop > current_trailing_stop:
            self.trailing_stop_price[symbol] = new_trailing_stop
            self.Debug(f"Updated Trailing Stop for {symbol}: New Trailing Stop: {new_trailing_stop}, Current Price: {current_price}")
        if current_price <= self.trailing_stop_price.get(symbol, float('inf')):
            self.Debug(f"Stop Loss Triggered for {symbol}: Current Price: {current_price}, Trailing Stop: {self.trailing_stop_price[symbol]}")
            return True
        return False

    def CalculateRisk(self, symbol, data):
        try:
            stopLossLevel = self.CalculateStopLossPrice(symbol, data)
            currentPrice = data[symbol].Price
            risk = currentPrice - stopLossLevel  # For a long position
            return risk
        except Exception as e:
            self.Debug(f"Error in CalculateRisk for {symbol}: {str(e)}")
            return None        

    def CalculateReward(self, symbol, data):
        try:
            take_profit_level = self.CalculateTakeProfitLevel(symbol, data)
            current_price = data[symbol].Price
            reward = take_profit_level - current_price
            return reward
        except Exception as e:
            self.Debug(f"Error in CalculateReward for {symbol}: {str(e)}")
            return None

    def CalculateStopLossEquityAmount(self, symbol, data):
        try:
            stop_loss_level = self.CalculateStopLossPrice(symbol, data)
            current_price = data[symbol].Price
            # The value at risk is the difference between the current price and the stop-loss level, multiplied by the quantity
            value_at_risk = (current_price - stop_loss_level) * self.Portfolio[symbol].Quantity
            return value_at_risk
        except Exception as e:
            self.Debug(f"Error in CalculateStopLossEquityAmount for {symbol}: {str(e)}")
            return None  # Return None in case of an exception

    def CalculateStopLossPrice(self, symbol, data):
        try:
            # Percentage-based stop loss
            current_price = data[symbol].Price
            stop_loss_level_percent = current_price * (1 - self.fixed_stop_loss_percent)
            # ATR-based stop loss
            atr_value = self.atr[symbol].Current.Value if symbol in self.atr else 0
            stop_loss_level_atr = current_price - (atr_value * self.stop_loss_atr_multiplier)
            # Combining methods: Choose the larger of the two for more conservative stop-loss
            combined_stop_loss_level = max(stop_loss_level_percent, stop_loss_level_atr)
            return combined_stop_loss_level
        except Exception as e:
            self.Debug(f"Error in CalculateStopLossPrice for {symbol}: {str(e)}")
            return None  # Return None in case of an exception

    def CalculateTakeProfitLevel(self, symbol, data):
        try:
            current_price = data[symbol].Price
            # Fixed take profit level based on a percentage
            fixed_take_profit_level = current_price * (1 + self.fixed_take_profit_percent)
            # Fibonacci levels with ATR
            atr_value = self.atr[symbol].Current.Value if symbol in self.atr else 0
            fibonacci_levels = [0.236, 0.382, 0.618]  # Example Fibonacci levels
            fibonacci_take_profit_levels = [current_price * (1 + level) for level in fibonacci_levels]
            fib_atr_take_profit_level = min(fibonacci_take_profit_levels) + atr_value
            # Dynamic trailing take profit (needs separate logic for updating it continuously)
            # Assuming you have a method to update this value regularly
            trailing_take_profit_level = self.GetUpdatedTrailingTakeProfit(symbol, current_price)
            # Combine methods: Choose the most conservative (highest) take-profit level
            combined_take_profit_level = max(fixed_take_profit_level, fib_atr_take_profit_level, trailing_take_profit_level)
            return combined_take_profit_level
        except Exception as e:
            self.Debug(f"Error in CalculateTakeProfitLevel for {symbol}: {str(e)}")
            return None  # Return None in case of an exception

    def CalculatePositionSize(self, risk):
        try:
            # Calculate the position size based on the risk and your total portfolio value
            riskCapital = self.Portfolio.TotalPortfolioValue * self.max_percent_per_trade
            positionSize = riskCapital / risk
            return min(positionSize, self.max_portfolio_at_risk)  # Ensure not to exceed 90% allocation
        except Exception as e:
            self.Debug(f"Error in CalculatePositionSize: {str(e)}")
            return None  # Return None in case of an exception        

    def HandleTradeOutcome(self, orderEvent):
        # Assume orderEvent has the necessary information about the trade outcome
        profit = self.CalculateProfit(orderEvent)
        if profit > 0:
            self.win_count += 1
            self.total_profit += profit
        else:
            self.loss_count += 1
            self.total_loss += abs(profit)
        self.UpdateWinProbabilityAndRatio()

    def CalculateProfit(self, orderEvent):
        # Extract relevant information from the orderEvent
        fillPrice = orderEvent.FillPrice
        quantityFilled = orderEvent.FillQuantity
        orderDirection = orderEvent.Direction
        # Calculate profit based on the order direction (buy or sell)
        if orderDirection == OrderDirection.Buy:
            # If it's a buy order, profit is negative (cost)
            return -1 * fillPrice * quantityFilled
        elif orderDirection == OrderDirection.Sell:
            # If it's a sell order, profit is positive (revenue)
            return fillPrice * quantityFilled
        else:
            # Handle other order types if needed
            return 0  # No profit for other order types

    def UpdateWinProbabilityAndRatio(self):
        try:
            total_trades = self.win_count + self.loss_count
            if total_trades > 0:
                win_probability = self.win_count / total_trades
                win_loss_ratio = self.total_profit / self.total_loss if self.total_loss != 0 else float('inf')  # 'inf' if no losses
                # Calculate Kelly Criterion
                kelly_criterion = win_probability - ((1 - win_probability) / (win_loss_ratio if win_loss_ratio != 0 else float('inf')))
                self.Debug(f"Updated Win Probability: {win_probability:.2f}, Win/Loss Ratio: {win_loss_ratio:.2f}, Kelly Criterion: {kelly_criterion:.2f}")
            else:
                self.Debug("No trades have been made yet to calculate win probability, ratio, and Kelly Criterion.")
        except Exception as e:
            self.Error(f"Error in UpdateWinProbabilityAndRatio: {str(e)}")

    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status == OrderStatus.Filled:
            # Log the order details
            self.Debug(f"Order Event: {orderEvent.Symbol} - {orderEvent.OrderId} - {orderEvent.Direction} - Quantity: {orderEvent.FillQuantity} at Price: ${orderEvent.FillPrice}")

            self.HandleTradeOutcome(orderEvent)

            if orderEvent.Direction == OrderDirection.Buy:
                # Set trailing stop price after a buy order is filled
                new_trailing_stop_price = orderEvent.FillPrice * (1 - self.trailing_stop_loss_percent)
                self.trailing_stop_price[orderEvent.Symbol] = new_trailing_stop_price
                self.Debug(f"New trailing stop set for {orderEvent.Symbol}: {new_trailing_stop_price}")

            elif orderEvent.Direction == OrderDirection.Sell:
                # Optional: Add any specific actions or logs for sell orders
                self.Debug(f"Sold {orderEvent.Symbol} - Quantity: {orderEvent.FillQuantity} at Price: ${orderEvent.FillPrice}")
        
        # Check for orders that are still open (not filled)
        elif orderEvent.Status == OrderStatus.Submitted:
            order_time = self.Time  # Current time
            order_age = (order_time - orderEvent.OrderTime).total_seconds() / 60  # Age in minutes

            # Cancel orders that are older than a set threshold (e.g., 30 minutes)
            if order_age > self.max_submitted_order_minutes:
                self.CancelOrder(orderEvent.OrderId)
                self.Debug(f"Order Cancelled due to timeout: {orderEvent.Symbol}, Order Age: {order_age} minutes")

            # Log unfilled orders periodically (e.g., every 15 minutes)
            elif order_age % 15 == 0:
                self.Debug(f"Order still pending: {orderEvent.Symbol}, Order Age: {order_age} minutes")

    def OnWarmupFinished(self):
        self.Debug(f"Warm-up completed. Universe includes {len(self.stockSymbols)} symbols.")
        for symbol in self.stockSymbols:
            self.Debug(f"Symbol: {symbol}")
