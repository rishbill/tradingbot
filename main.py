# Begin main.py
# QuantConnect Knowledge Base
# https://www.quantconnect.com/docs/v2/writing-algorithms
# Stocks = Symbols = Securities

from AlgorithmImports import *
from TradingLogic import *
import numpy as np
import config
import collections

class CodysAdvancedStrategy(QCAlgorithm):
    def Initialize(self):
    # Main function for class

        # Initialize Variables
        config.SetStartDate(self)
        config.SetCash(self)
        config.SetWarmUp(self)
        config.SetBrokerageModel(self)       
        portfolio_value = self.Portfolio.TotalPortfolioValue
        stock_counts_per_sector = self.CalculateStockCountsPerSector()
        total_invested_stocks = sum(stock_counts_per_sector.values())
        self.warmup_counter = 0 # Increments for each warmup day, to check warmup progress
        self.last_increment_day = None # Used to calculate warmup_counter
        self.day_trade_dates = collections.deque(maxlen=5)  # Stores dates of last 5 day trades
        self.day_trade_counter = 0

        # Technical Indicators
        self.stochastic_rsi = {} # See config.py
        self.ema_short = {}
        self.ema_long = {}
        self.atr = {}

        # Sell Conditions
        self.trailing_take_profit_price = {} # Updated after each trade
        self.trailing_stop_loss_price = {} # Updated after each trade 

        # Stocks
        self.active_stock_symbols = [] # Holds the stocks in the dynamically filtered Universe
        self.count_active_stock_symbols = 0  # Number of stocks in active_stock_symbols
        self.unique_portfolio_stocks = set()
        self.sector_allocation = {}

        # Orders        
        self.order_ticket = None
        self.open_order_tickets = {}

        # Profit/Loss (P/L) Sell Results
        self.win_count = 0
        self.loss_count = 0
        self.total_profit = 0
        self.total_loss = 0            

        # Debug Values from config.py
        self.Debug("Basic parameters:")
        self.Debug(f"---- Initial Capital -------------------------- ${self.Portfolio.Cash}")
        self.Debug(f"---- Start Date ------------------------------- {self.StartDate}")
        self.Debug(f"---- End Date --------------------------------- {self.EndDate}")
        self.Debug(f"---- Warm Up ---------------------------------- {config.warmup_period} Days")
        self.Debug("Indicator Variables:")
        self.Debug("---- Initialized Indicator Variables: self.ema_short, self.ema_long, self.atr, self.stochastic_rsi")
        self.Debug("News and Sentiment Variables:")
        self.Debug("---- Initialized News and Sentiment Variables: config.news_feed")
        self.Debug("Trading Variables:")
        self.Debug(f"---- Max Portfolio At Risk --------------------- {config.max_portfolio_invested_percent * 100}%")
        self.Debug(f"---- Max Portfolio % Per Trade ----------------- {config.max_trade_portfolio_percent * 100}%")
        self.Debug(f"---- Fixed Take Profit % ----------------------- {config.fixed_take_profit_percent * 100}%")
        self.Debug(f"---- Fixed Take Profit % Gain ------------------ {config.fixed_take_profit_percent_gain * 100}%")
        self.Debug(f"---- Fixed Take Profit % To Sell --------------- {config.fixed_take_profit_percent_to_sell * 100}%")
        self.Debug(f"---- Fixed Stop Loss % ------------------------- {config.fixed_stop_loss_percent * 100}%")
        self.Debug(f"---- Stop Loss ATR Multiplier ------------------ {config.stop_loss_atr_multiplier}")
        self.Debug(f"---- Trailing Stop Loss % ---------------------- {config.trailing_stop_loss_percent * 100}%")  
        self.Debug("Portfolio Summary:")
        self.Debug(f"---- Portfolio Value ----------------------------- ${portfolio_value}")
        if total_invested_stocks == 0:
            self.Debug("---- No invested stocks in portfolio")
        else:
            for sector, count in stock_counts_per_sector.items():
                sector_portfolio_value = self.CalculateSectorPortfolioValue(sector)
                percentage_of_portfolio = (sector_portfolio_value / portfolio_value) * 100
                self.Debug(f"---- Sector: {sector}, Count: {count}, Value: ${sector_portfolio_value}, % of Portfolio: {percentage_of_portfolio:.2f}%")

        # Universe Filtering
        self.max_stock_price = self.Portfolio.TotalPortfolioValue * config.max_stock_price_portfolio_percent # Limit max stock price to X% of portfolio size, for affordability
        self.Debug("Universe filter variables:")
        self.Debug(f"------- Stock Price Range ------------------------- ${config.min_stock_price} - ${self.max_stock_price}")
        self.Debug(f"------- P/E Ratio Range --------------------------- {config.min_pe_ratio} to {config.max_pe_ratio}")
        self.Debug(f"------- Min Revenue Growth ------------------------ {config.min_revenue_growth_percent}")
        try:
            self.Debug(f"Filtering Universe...")
            self.UniverseSettings.Resolution = Resolution.Minute
            self.AddUniverse(self.UniverseFilter)  # Get the stocks for today's potential trades
        except Exception as e:
            self.Error(f"---- Error filtering Universe: {str(e)}")                    

    def UniverseFilter(self, fundamental: List[Fundamental]) -> List[Symbol]:
    # Returns a filtered list of stocks,  dynamically re-filtered daily   
        try:
            filtered = [f for f in fundamental if f.HasFundamentalData and config.min_stock_price <= f.Price < self.max_stock_price and f.ValuationRatios.PERatio > config.min_pe_ratio and f.ValuationRatios.PERatio < config.max_pe_ratio and f.OperationRatios.RevenueGrowth.OneYear > config.min_revenue_growth_percent and not np.isnan(f.ValuationRatios.PERatio) and not np.isnan(f.OperationRatios.RevenueGrowth.OneYear) and not np.isnan(f.DollarVolume) and not np.isnan(f.MarketCap) and f.ValuationRatios.PERatio != 0 and f.OperationRatios.RevenueGrowth.OneYear != 0 and f.DollarVolume != 0 and f.MarketCap != 0]
            sortedByDollarVolume = sorted(filtered, key=lambda f: f.DollarVolume, reverse=True)[:10]
            sortedByPeRatio = sorted(sortedByDollarVolume, key=lambda f: f.ValuationRatios.PERatio, reverse=False)[:10]
            
            if self.warmup_counter >= config.warmup_period + 1:
                try:
                    self.filteredSymbolsDetails = [(f.Symbol, f.Price, f.DollarVolume, f.ValuationRatios.PERatio, f.OperationRatios.RevenueGrowth.OneYear, f.MarketCap, f.AssetClassification.MorningstarSectorCode, f.AssetClassification.MorningstarIndustryCode, f.CompanyReference.ShortName) for f in sortedByPeRatio]
                except Exception as e:
                    self.Debug(f"Error accessing fundamentals data: {str(e)}")
            else:
                self.Debug(f"Warming Up... ({self.warmup_counter} \ 100 Days)")
            return [f.Symbol for f in sortedByPeRatio]
        except Exception as e:
            self.Error(f"---- Error on UniverseFilter: {str(e)}")        

    def CalculateStockCountsPerSector(self):
    # Returns a list of stock counts for each sector in the current portfolio
        try:
            stock_counts_per_sector = {} # Initialize list variable
            for symbol in self.Portfolio.Keys: # Iterate over all stocks in portfolio
                if self.Portfolio[symbol].Invested: # If the portfolio is invested in this stock
                    sector = config.GetSectorForStock(symbol) # Get the sector for this stock
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
                return "Fundamental data Not Available"  # Return 'Not Available' if no fundamental data
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
            sector_portfolio_value = 0 # Initialize integer variable 
            for symbol in self.Portfolio.Keys: # Iterate over all stocks in portfolio
                if self.Portfolio[symbol].Invested and self.GetSectorForStock(symbol) == sector: # If the portfolio is invested in this stock, and the sector for this stock matches the sector being checked
                    sector_portfolio_value += self.Portfolio[symbol].HoldingsValue # Adds the value of portfolio holdings for this stock to the sector_portfolio_value
            return sector_portfolio_value # Returns the total portfolio value for the provided sector
        except Exception as e:
            self.Error(f"Error on CalculateSectorPortfolioValue: {str(e)}")        

    def OnSecuritiesChanged(self, changes):
    # Runs when new symbols  
        # Preview up to 10 symbols that are AddedSecurities and include the current timestamp
        current_timestamp = self.Time.strftime("%Y-%m-%d")
        added_symbols_preview = [security.Symbol for security in changes.AddedSecurities[:10]]
        self.Debug(f"{current_timestamp} - Universe Updated +{len(changes.AddedSecurities)}: {', '.join(str(symbol) for symbol in added_symbols_preview)}")
        # Adjust indicators and news feed for added and removed securities
        try: 
            for security in changes.AddedSecurities:
                symbol = security.Symbol
                if symbol not in self.active_stock_symbols:
                    self.active_stock_symbols.append(symbol)
                config.numberOfStocks = len(self.active_stock_symbols)    
                # Create and register indicators for each added symbol
                self.ema_short[symbol] = self.EMA(symbol, self.ema_short_periods, Resolution.Minute)
                self.ema_long[symbol] = self.EMA(symbol, self.ema_long_periods, Resolution.Minute)
                self.atr[symbol] = self.ATR(symbol, self.atr_periods, MovingAverageType.Wilders, Resolution.Minute)
                # Create and register the Stochastic RSI indicator for this symbol
                self.stochastic_rsi[symbol] = self.STO(symbol, self.stochastic_rsi_periods, Resolution.Minute)  # Create Stochastic RSI
                self.RegisterIndicator(symbol, self.stochastic_rsi[symbol], Resolution.Minute)
            for security in changes.RemovedSecurities:
                symbol = security.Symbol
                if symbol in self.active_stock_symbols:
                    self.active_stock_symbols.remove(symbol)
                # Remove indicators for removed symbols
                if symbol in self.ema_short: del self.ema_short[symbol]
                if symbol in self.ema_long: del self.ema_long[symbol]
                if symbol in self.atr: del self.atr[symbol]
                if symbol in self.stochastic_rsi: del self.stochastic_rsi[symbol]
                if symbol in config.news_feed: self.RemoveSecurity(symbol)
        except Exception as e:
            self.Error(f"Error on OnSecuritiesChanged: {str(e)}")

    def OnData(self, data):
    # Runs upon receipt of every bar/candle for the filtered stocks
        current_day = self.Time.day
        if self.IsWarmingUp:
            if self.last_increment_day != current_day:
                self.warmup_counter += 1
                self.last_increment_day = current_day     
        else:               
            for symbol in self.active_stock_symbols:
                if not data.ContainsKey(symbol):
                    # Skip this symbol if it's not present in the current Slice
                    continue
                try:
                    if ShouldBuy(self, symbol, data):
                        limit_price_to_buy = data[symbol].Close * config.buy_limit_order_percent
                        fraction_of_portfolio = 1 / config.numberOfStocks
                        total_cash_to_spend = self.Portfolio.Cash * fraction_of_portfolio
                        quantity_to_buy = total_cash_to_spend / limit_price_to_buy
                        quantity_to_buy = max(1, round(quantity_to_buy))  # Ensure at least one unit is bought
                        self.order_ticket = self.LimitOrder(symbol, quantity_to_buy, limit_price_to_buy)
                        self.open_order_tickets[symbol] = self.order_ticket
                    # Update new trailing take profit price for each invested symbol
                    if self.Portfolio[symbol].Invested:
                        # Calculate the value at risk for this position
                        current_price = data[symbol].Price
                        if symbol not in self.trailing_take_profit_price:
                            self.trailing_take_profit_price[symbol] = current_price * (1 + config.trailing_take_profit_percent)
                        else:
                            # Update the trailing take profit if the price moves up
                            if current_price > self.trailing_take_profit_price[symbol] / (1 + config.trailing_take_profit_percent):
                                self.trailing_take_profit_price[symbol] = current_price * (1 + config.trailing_take_profit_percent)
                        if symbol not in self.trailing_stop_loss_price:
                            # Initialize trailing stop loss price if it doesn't exist
                            self.trailing_stop_loss_price[symbol] = current_price * (1 - config.trailing_stop_loss_percent)
                        else:
                            # Update the trailing stop loss if the price moves up
                            if current_price > self.trailing_stop_loss_price[symbol]:
                                self.trailing_stop_loss_price[symbol] = current_price * (1 - config.trailing_stop_loss_percent)
                    # Check for Sell condition
                    if self.Portfolio[symbol].Invested and ShouldSell(self, symbol, data):
                        holdings = self.Portfolio[symbol].Quantity
                        self.order_ticket = self.MarketOrder(symbol, -holdings * config.fixed_take_profit_percent_to_sell)
                        self.open_order_tickets[symbol] = self.order_ticket
                except Exception as e:
                    self.Debug(f"Error on OnData: {str(e)}")  
            self.CancelOldOrders()

    def OnOrderEvent(self, orderEvent):
        symbol = orderEvent.Symbol
        fill_price = orderEvent.FillPrice
        fill_qty = orderEvent.FillQuantity
        current_date = self.Time.date()

        # Day trade tracking
        order_type = 'buy' if orderEvent.Direction == OrderDirection.Buy else 'sell'
        if symbol not in config.day_trades:
            config.day_trades[symbol] = {'buy': False, 'sell': False, 'date': None}

        if config.day_trades[symbol]['date'] == current_date:
            # Check for day trade (buy and sell on the same day)
            if (order_type == 'sell' and config.day_trades[symbol]['buy']) or (order_type == 'buy' and config.day_trades[symbol]['sell']):
                self.day_trade_dates.append(current_date)
                self.day_trade_counter += 1
                self.Debug(f"Day Trade Detected for {symbol} on {current_date}. Total Day Trades in last 5 days: {len(self.day_trade_dates)}")
                # Reset the day trade flags for this stock
                config.day_trades[symbol] = {'buy': False, 'sell': False, 'date': None}
        else:
            # Record this trade action
            config.day_trades[symbol][order_type] = True
            config.day_trades[symbol]['date'] = current_date

        self.unique_portfolio_stocks.clear()

        if orderEvent.Status == OrderStatus.Submitted:
            self.Debug(f"Order Submitted: {symbol} - ID: {orderEvent.OrderId} - Qty: {fill_qty} * ${fill_price} = ${fill_qty * fill_price}")

        # Add all currently invested stocks to the unique_portfolio_stocks
        self.unique_portfolio_stocks = {s for s, holding in self.Portfolio.items() if holding.Invested}
        self.Debug(f"Updated unique portfolio stocks: {self.unique_portfolio_stocks}")

        if orderEvent.Status == OrderStatus.Filled:
            if orderEvent.Direction == OrderDirection.Buy:
                self.Debug(f"---- BUY Order Filled: {symbol} - ID: {orderEvent.OrderId} - Qty: {fill_qty} * ${fill_price} = ${fill_qty * fill_price}")
                self.HandleTradeOutcome(orderEvent)
                new_trailing_stop_loss_price = fill_price * (1 - config.trailing_stop_loss_percent)
                self.trailing_stop_loss_price[symbol] = new_trailing_stop_loss_price
                new_trailing_take_profit_price = fill_price * (1 + config.trailing_take_profit_percent)
                self.trailing_take_profit_price[symbol] = new_trailing_take_profit_price

                fixed_take_profit_price = fill_price * (1 + config.fixed_take_profit_percent)
                self.Debug(f"-------- Fixed Take Profit: {symbol} @ ${fixed_take_profit_price} (Fill Price: ${fill_price} * (1 + {config.fixed_take_profit_percent}))")
                self.Debug(f"-------- Trailing Take Profit: {symbol} @ ${new_trailing_take_profit_price} (Fill Price: ${fill_price} * (1 + {config.trailing_take_profit_percent}))")

                fixed_stop_loss_price = fill_price * (1 - config.fixed_stop_loss_percent)
                self.Debug(f"-------- Fixed Stop Loss: {symbol} @ ${fixed_stop_loss_price} (Fill Price: ${fill_price} * (1 - {config.fixed_stop_loss_percent}))")
                self.Debug(f"-------- Trailing Stop Loss: {symbol} @ ${new_trailing_stop_loss_price} (Fill Price: ${fill_price} * (1 - {config.trailing_stop_loss_percent}))")

            elif orderEvent.Direction == OrderDirection.Sell:
                self.Debug(f"---- SELL Order Filled: {symbol} - ID: {orderEvent.OrderId} - Qty: {fill_qty} * ${fill_price} = ${fill_qty * fill_price}")
                # Retrieve existing trailing stop and take profit prices if any
                existing_trailing_stop = self.trailing_stop_loss_price.get(symbol, None)
                if existing_trailing_stop:
                    self.Debug(f"-------- Trailing Stop Loss: {symbol} @ ${existing_trailing_stop}")

                existing_trailing_take_profit = self.trailing_take_profit_price.get(symbol, None)
                if existing_trailing_take_profit:
                    self.Debug(f"-------- Trailing Take Profit: {symbol} @ ${existing_trailing_take_profit}")

    def CancelOldOrders(self):
        try:
            for symbol, self.order_ticket in self.open_order_tickets.items():
                if self.order_ticket is not None and not self.order_ticket.OrderClosed:
                    order_time = self.Time  # Current algorithm time
                    order_age = (order_time - self.order_ticket.Time).total_seconds() / 60  # Age in minutes
                    if order_age > config.max_submitted_order_minutes:
                        self.order_ticket.Cancel("Order too old")
                        self.Debug(f"Order {self.order_ticket.OrderId} for {symbol} cancelled due to timeout")
                    # Log unfilled orders periodically (e.g., every 15 minutes)
                    elif order_age % 15 == 0:
                        self.Debug(f"Order still pending: {self.order_ticket.Symbol}, Order Age: {order_age} minutes, Canceling in {config.max_submitted_order_minutes - order_age} minutes...")
        except Exception as e:
            self.Error(f"Error on HandleTradeOutcome: {str(e)}") 
            return False

    def HandleTradeOutcome(self, orderEvent):
        try:    
            # Handling sell orders to calculate profit or loss
            if orderEvent.Direction == OrderDirection.Sell:
                # Retrieve the average buy price for the stock
                average_buy_price = self.Portfolio[orderEvent.Symbol].AveragePrice
                # Calculate profit or loss
                profit = (orderEvent.FillPrice - average_buy_price) * orderEvent.FillQuantity
                # Update win/loss counts and total profit/loss
                if profit > 0:
                    self.win_count += 1
                    self.total_profit += profit
                else:
                    self.loss_count += 1
                    self.total_loss += abs(profit)
                # Update win probability and ratio after any trade outcome
                self.UpdateWinProbabilityAndRatio()

        except Exception as e:
            self.Error(f"Error on HandleTradeOutcome: {str(e)}") 
            return False
   
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
            self.Error(f"Error on UpdateWinProbabilityAndRatio: {str(e)}")

    def OnWarmupFinished(self):
        self.Debug(f"Warmup Finished. Universe includes {len(self.filteredSymbolsDetails)} symbols.")
        for symbol, price, dollar_volume, pe_ratio, revenue_growth, market_cap, sector, industry, ShortName in self.filteredSymbolsDetails:
            self.Debug(f"-------- {symbol}, Price: ${price}, Dollar Volume: ${dollar_volume}, P/E Ratio:{pe_ratio}, Revenue Growth: {revenue_growth}%, MarketCap: {market_cap}, Sector: {sector}, Industry: {industry} - {ShortName}")

# End main.py