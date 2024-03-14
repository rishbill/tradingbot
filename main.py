# QuantConnect Knowledge Base
# https://www.quantconnect.com/docs/v2/writing-algorithms
# Stocks = Symbols = Securities

from AlgorithmImports import *
from TradingLogic import *
import numpy as np
import config

class CodysAdvancedStrategy(QCAlgorithm):
    def Initialize(self):
    # Main function for class
        # Debug parameters from config.py
        self.Debug("Initializing basic variables...")
        config.SetStartDate(self)
        config.SetCash(self)
        config.SetWarmUp(self)
        self.Debug("---- Successfully initialized basic parameters:")
        self.Debug(f"------- Initial Capital -------------------------- ${self.Portfolio.Cash}")
        self.Debug(f"------- Start Date ------------------------------- {self.StartDate}")
        self.Debug(f"------- End Date --------------------------------- {self.EndDate}")
        self.Debug(f"------- Warm Up ---------------------------------- 100 Days")
        self.Debug("Initializing Indicator Variables...")
        self.Debug("---- Successfully Initialized Indicator Variables: config.ema_short, config.ema_long, config.atr, config.stochastic_rsi")
        self.Debug("Initializing News and Sentiment Variables...")
        self.Debug("---- Successfully Initialized News and Sentiment Variables: config.news_feed")
        self.Debug("Initializing Trading Variables...")
        self.Debug("---- Successfully Initialized Trading Variables: ")
        self.Debug(f"------- Max Portfolio At Risk --------------------- {config.max_portfolio_at_risk * 100}%")
        self.Debug(f"------- Max Portfolio % Per Trade ----------------- {config.max_percent_per_trade * 100}%")
        self.Debug(f"------- Fixed Take Profit % ----------------------- {config.max_percent_per_trade * 100}%")
        self.Debug(f"------- Fixed Take Profit % Gain ------------------ {config.fixed_take_profit_percent_gain * 100}%")
        self.Debug(f"------- Fixed Take Profit % To Sell --------------- {config.fixed_take_profit_percent_to_sell * 100}%")
        self.Debug(f"------- Fixed Stop Loss % ------------------------- {config.fixed_stop_loss_percent * 100}%")
        self.Debug(f"------- Stop Loss ATR Multiplier ------------------ {config.stop_loss_atr_multiplier}")
        self.Debug(f"------- Trailing Stop Loss % ---------------------- {config.trailing_stop_loss_percent * 100}%")

        # Portfolio Summary
        try:
            self.Debug("Portfolio Summary:")
            # Portfolio Value
            portfolio_value = self.Portfolio.TotalPortfolioValue
            self.Debug(f"---- Portfolio Value ----------------------------- ${portfolio_value}")
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
            self.Error(f"---- Error on PortfolioSummary: {str(e)}")

        # Universe Filtering
        self.max_stock_price = self.Portfolio.TotalPortfolioValue * config.max_stock_price_percent # Limit max stock price to X% of portfolio size, for affordability
        self.Debug("Initializing Universe filter variables...")
        self.Debug("---- Successfully set Universe selection variables:")
        self.Debug(f"------- Stock Price Range ------------------------- ${config.min_stock_price} - ${self.max_stock_price}")
        self.Debug(f"------- P/E Ratio Range --------------------------- {config.min_pe_ratio} to {config.max_pe_ratio}")
        self.Debug(f"------- Min Revenue Growth ------------------------ {config.min_revenue_growth}")
        try:
            self.Debug(f"Filtering Universe...")
            self.UniverseSettings.Resolution = Resolution.Minute
            self.AddUniverse(self.UniverseFilter)  # Get the stocks for today's potential trades
        except Exception as e:
            self.Error(f"---- Error filtering Universe: {str(e)}")                    

    def UniverseFilter(self, fundamental: List[Fundamental]) -> List[Symbol]:
    # Returns a filtered list of stocks    
        try:
            filtered = [f for f in fundamental if f.HasFundamentalData and config.min_stock_price <= f.Price < self.max_stock_price and f.ValuationRatios.PERatio > config.min_pe_ratio and f.ValuationRatios.PERatio < config.max_pe_ratio and f.OperationRatios.RevenueGrowth.OneYear > config.min_revenue_growth and not np.isnan(f.ValuationRatios.PERatio) and not np.isnan(f.OperationRatios.RevenueGrowth.OneYear) and not np.isnan(f.DollarVolume) and not np.isnan(f.MarketCap) and f.ValuationRatios.PERatio != 0 and f.OperationRatios.RevenueGrowth.OneYear != 0 and f.DollarVolume != 0 and f.MarketCap != 0]
            sortedByDollarVolume = sorted(filtered, key=lambda f: f.DollarVolume, reverse=True)[:10]
            sortedByPeRatio = sorted(sortedByDollarVolume, key=lambda f: f.ValuationRatios.PERatio, reverse=False)[:10]
            if config.warmup_counter >= config.warmup_period + 1:
                self.Debug("---- Successfully filtered Universe")
                try:
                    self.filteredSymbolsDetails = [(f.Symbol, f.Price, f.DollarVolume, f.ValuationRatios.PERatio, f.OperationRatios.RevenueGrowth.OneYear, f.MarketCap, f.AssetClassification.MorningstarSectorCode, f.AssetClassification.MorningstarIndustryCode, f.CompanyReference.ShortName) for f in sortedByPeRatio]
                except Exception as e:
                    self.Debug(f"Error accessing fundamentals data: {str(e)}")
            else:
                self.Debug(f"Warming Up... ({config.warmup_counter} \ 100 Days)")
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
                if self.Portfolio[symbol].Invested and self.GetSectorForStock(symbol) == sector: # If the portfolio is invested in this stock, and the sector for this stock matches the sector being checked
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
                if symbol not in config.stockSymbols:
                    config.stockSymbols.append(symbol)
                config.numberOfStocks = len(config.stockSymbols)    
                # Create and register indicators for each added symbol
                config.ema_short[symbol] = self.EMA(symbol, config.ema_short_periods, Resolution.Minute)
                config.ema_long[symbol] = self.EMA(symbol, config.ema_long_periods, Resolution.Minute)
                config.atr[symbol] = self.ATR(symbol, config.atr_periods, MovingAverageType.Wilders, Resolution.Minute)
                # Create and register the Stochastic RSI indicator for this symbol
                config.stochastic_rsi[symbol] = self.STO(symbol, config.stochastic_rsi_periods, Resolution.Minute)  # Create Stochastic RSI
                self.RegisterIndicator(symbol, config.stochastic_rsi[symbol], Resolution.Minute)
                # config.news_feed[symbol] = self.AddData(TiingoNews, symbol)
            for security in changes.RemovedSecurities:
                symbol = security.Symbol
                if symbol in config.stockSymbols:
                    config.stockSymbols.remove(symbol)
                # Remove indicators for removed symbols
                if symbol in config.ema_short: del config.ema_short[symbol]
                if symbol in config.ema_long: del config.ema_long[symbol]
                if symbol in config.atr: del config.atr[symbol]
                if symbol in config.stochastic_rsi: del config.stochastic_rsi[symbol]
                if symbol in config.news_feed: self.RemoveSecurity(symbol)
        except Exception as e:
            self.Error(f"Error on OnSecuritiesChanged: {str(e)}")

    def OnData(self, data):
    # Runs upon receipt of every bar/candle for the filtered stocks
        current_day = self.Time.day
        if self.IsWarmingUp:
            if config.last_increment_day != current_day:
                config.warmup_counter += 1
                config.last_increment_day = current_day     
        else:               
            for symbol in config.stockSymbols:
                if not data.ContainsKey(symbol):
                    # Skip this symbol if it's not present in the current Slice
                    continue
                try:
                    # # Check if news for the symbol is present
                    # news_data = data.Get(TiingoNews, symbol)
                    # if news_data:
                    #     for article in news_data.Values:
                    #         # Log news articles and sentiment
                    #         self.Debug(f"News for {symbol}: Title - {article.Title}, Sentiment - {article.Sentiment}")
                    # Check for Buy condition
                    if ShouldBuy(self, symbol, data):
                        limit_price_to_buy = data[symbol].Close * config.buy_limit_order_percent
                        fraction_of_portfolio = 1 / config.numberOfStocks
                        total_cash_to_spend = self.Portfolio.Cash * fraction_of_portfolio
                        quantity_to_buy = total_cash_to_spend / limit_price_to_buy
                        quantity_to_buy = max(1, round(quantity_to_buy))  # Ensure at least one unit is bought
                        config.ticket = self.LimitOrder(symbol, quantity_to_buy, limit_price_to_buy)
                        config.open_order_tickets[symbol] = config.ticket
                    # Update trailing take profit level for each invested symbol
                    if self.Portfolio[symbol].Invested:
                        # Calculate the value at risk for this position
                        current_price = data[symbol].Price
                        if symbol not in config.trailing_take_profit_price:
                            config.trailing_take_profit_price[symbol] = current_price * (1 + config.trailing_take_profit_percent)
                        else:
                            # Update the trailing take profit if the price moves up
                            if current_price > config.trailing_take_profit_price[symbol] / (1 + config.trailing_take_profit_percent):
                                config.trailing_take_profit_price[symbol] = current_price * (1 + config.trailing_take_profit_percent)
                    # Check for Sell condition
                    if self.Portfolio[symbol].Invested and ShouldSell(self, symbol, data):
                        holdings = self.Portfolio[symbol].Quantity
                        config.ticket = self.MarketOrder(symbol, -holdings * config.fixed_take_profit_percent_to_sell)
                        config.open_order_tickets[symbol] = config.ticket
                except Exception as e:
                    self.Debug(f"Error on OnData: {str(e)}")  
            self.CancelOldOrders()                

    def HandleTradeOutcome(self, orderEvent):
        try:    
            # Assume orderEvent has the necessary information about the trade outcome
            profit = self.CalculateProfit(orderEvent)
            if profit > 0:
                config.win_count += 1
                config.total_profit += profit
            else:
                config.loss_count += 1
                config.total_loss += abs(profit)
            self.UpdateWinProbabilityAndRatio()
        except Exception as e:
            self.Debug(f"Error on HandleTradeOutcome: {str(e)}") 
            return False            

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
            total_trades = config.win_count + config.loss_count
            if total_trades > 0:
                win_probability = config.win_count / total_trades
                win_loss_ratio = config.total_profit / config.total_loss if config.total_loss != 0 else float('inf')  # 'inf' if no losses
                # Calculate Kelly Criterion
                kelly_criterion = win_probability - ((1 - win_probability) / (win_loss_ratio if win_loss_ratio != 0 else float('inf')))
                self.Debug(f"Updated Win Probability: {win_probability:.2f}, Win/Loss Ratio: {win_loss_ratio:.2f}, Kelly Criterion: {kelly_criterion:.2f}")
            else:
                self.Debug("No trades have been made yet to calculate win probability, ratio, and Kelly Criterion.")
        except Exception as e:
            self.Error(f"Error on UpdateWinProbabilityAndRatio: {str(e)}")

    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status == OrderStatus.Filled:
            # Log the order details
            self.Debug(f"Order Event: {orderEvent.Symbol} - {orderEvent.OrderId} - {orderEvent.Direction} - Quantity: {orderEvent.FillQuantity} at Price: ${orderEvent.FillPrice}")
            self.HandleTradeOutcome(orderEvent)
            if orderEvent.Direction == OrderDirection.Buy:
                # Set trailing stop price after a buy order is filled
                new_trailing_stop_price = orderEvent.FillPrice * (1 - config.trailing_stop_loss_percent)
                config.trailing_stop_price[orderEvent.Symbol] = new_trailing_stop_price
                self.Debug(f"New trailing stop set for {orderEvent.Symbol}: {new_trailing_stop_price}")
            elif orderEvent.Direction == OrderDirection.Sell:
                # Optional: Add any specific actions or logs for sell orders
                self.Debug(f"Sold {orderEvent.Symbol} - Quantity: {orderEvent.FillQuantity} at Price: ${orderEvent.FillPrice}")

    def CancelOldOrders(self):
        for symbol, config.ticket in config.open_order_tickets.items():
            if config.ticket is not None and not config.ticket.OrderClosed:
                order_time = self.Time  # Current algorithm time
                order_age = (order_time - config.ticket.Time).total_seconds() / 60  # Age in minutes
                if order_age > config.max_submitted_order_minutes:
                    config.ticket.Cancel("Order too old")
                    self.Debug(f"Order {config.ticket.OrderId} for {symbol} cancelled due to timeout")
                # Log unfilled orders periodically (e.g., every 15 minutes)
                elif order_age % 15 == 0:
                    self.Debug(f"Order still pending: {config.ticket.Symbol}, Order Age: {order_age} minutes")

    def OnWarmupFinished(self):
        self.Debug(f"Warmup Finished. Universe includes {len(self.filteredSymbolsDetails)} symbols.")
        for symbol, price, dollar_volume, pe_ratio, revenue_growth, market_cap, sector, industry, ShortName in self.filteredSymbolsDetails:
            self.Debug(f"-------- {symbol}, Price: ${price}, Dollar Volume: ${dollar_volume}, P/E Ratio:{pe_ratio}, Revenue Growth: {revenue_growth}%, MarketCap: {market_cap}, Sector: {sector}, Industry: {industry} - {ShortName}")
