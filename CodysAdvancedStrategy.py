# QuantConnect Knowledge Base
# https://www.quantconnect.com/docs/v2/writing-algorithms

from AlgorithmImports import *

class CodysAdvancedStrategy(QCAlgorithm):
    def Initialize(self):
        # Basic variables
        try:
            self.Debug("Initializing basic variables...")
            self.SetStartDate(2024, 1, 1)  # Set Start Date
            # self.SetEndDate(2024, 1, 1)  # Set End Date -- Default is present
            self.SetCash(1000)  # Set Strategy Starting Capital
            self.total_portfolio_value = self.Portfolio.TotalPortfolioValue
            self.Debug("---- Successfully initialized basic parameters:")
            self.Debug(f"------- Initial Capital -------------------------- ${self.Portfolio.Cash}")
            self.Debug(f"------- Start Date ------------------------------- {self.StartDate}")
            self.Debug(f"------- End Date --------------------------------- {self.EndDate}")
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
                self.Error("-------- No invested stocks in portfolio")

            else:
                self.Debug("---- Portfolio Summary:")
                for sector, count in stock_counts_per_sector.items():
                    sector_value = self.CalculateSectorPortfolioValue(sector)
                    percentage_of_portfolio = (sector_value / portfolio_value) * 100
                    self.Debug(f"------- Sector: {sector}, Count: {count}, Value: ${sector_value}, % of Portfolio: {percentage_of_portfolio:.2f}%")

        except Exception as e:
            self.Error(f"---- Error in PortfolioSummary: {str(e)}")

        # # Trading indicators and variables
        # try:    
        #     self.Debug("Initializing Trading indicators and variables...")
        #     # Indicators
        #     self.emaShort = {}
        #     self.emaLong = {}
        #     self.atr = {}
        #     self.stochRsi = {}

        #     # News and Sentiment
        #     self.news_feed = {}

        #     # P/L Calculations
        #     self.win_count = 0
        #     self.loss_count = 0
        #     self.total_profit = 0
        #     self.total_loss = 0

        #     # Orders
        #     self.trailingStopLoss = 0.05  # 5% trailing stop
        #     self.trailingStopPrice = {}

        #     self.Debug("----Successfully initialized trading variables")

        # except Exception as e:
        #     self.Error(f"Error initializing Trading variables: {str(e)}")        

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
            self.Debug(f"------- Max stock price -------------------------- ${self.max_stock_price}")
            self.Debug(f"------- Min stock price -------------------------- ${self.min_stock_price}")
            self.Debug(f"------- P/E ratio range -------------------------- {self.min_pe_ratio} to {self.max_pe_ratio}")
            self.Debug(f"------- Min revenue growth ----------------------- {self.min_revenue_growth}")
            # self.Debug(f"------- Min total portfolio stocks --------------- {self.min_total_portfolio_stocks}")
            # self.Debug(f"------- Min portfolio sectors -------------------- {self.min_portfolio_sectors}")
            # self.Debug(f"------- Max exposure per biggest sector ---------- {self.max_portfolio_exposure_per_biggest_sector * 100}%")
            # self.Debug(f"------- Min stocks per biggest sector ------------ {self.min_portfolio_stocks_per_biggest_sector}")
            # self.Debug(f"------- Max invested percentage ------------------ {self.max_portfolio_invested * 100}%")
        except Exception as e:
            self.Error(f"---- Error setting Universe selection variables: {str(e)}")

        try:
            self.Debug("Filtering Universe...")
            self.UniverseSettings.Resolution = Resolution.Daily
            self.AddUniverse(self.UniverseFilter)  # Get the stocks for today's potential trades
        except Exception as e:
            self.Error(f"---- Error filtering Universe: {str(e)}")                    

    def UniverseFilter(self, fundamental: List[Fundamental]) -> List[Symbol]:
        try:
            self.Debug(f"---- Fundamental Universe Filter:")
            self.Debug(f"------- HasFundamentalData ------ True")
            self.Debug(f"------- Min Stock Price --------- ${self.min_stock_price}")
            self.Debug(f"------- Max Stock Price --------- ${self.max_stock_price}")
                
            filtered = [f for f in fundamental if f.HasFundamentalData and self.min_stock_price <= f.Price < self.max_stock_price and f.ValuationRatios.PERatio > self.min_pe_ratio and f.ValuationRatios.PERatio < self.max_pe_ratio and f.OperationRatios.RevenueGrowth.OneYear > self.min_revenue_growth and not np.isnan(f.ValuationRatios.PERatio)]
            sortedByDollarVolume = sorted(filtered, key=lambda f: f.DollarVolume, reverse=True)[:100]
            sortedByPeRatio = sorted(sortedByDollarVolume, key=lambda f: f.ValuationRatios.PERatio, reverse=False)[:100]
            # Return the list of coarse-filtered stocks which have passed through filters
            self.Debug("---- Successfully filtered Universe")
            return [f.Symbol for f in sortedByPeRatio]
        except Exception as e:
            self.Error(f"---- Error on UniverseFilter: {str(e)}")        

    def CalculateStockCountsPerSector(self):
    # Gets a list of stock counts for each sector
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
        # Gets the sector associated with a provided stock (symbol)
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
    # This function runs whenever the list of stocks in our filtered Universe changes    
        self.Debug(f"Universe has changed. Number of symbols: {len(changes.AddedSecurities)}")

        # Loop through each universe in the Universe Manager
        for universe in self.UniverseManager.Values:
            # Loop through each security in the current universe
            for security in universe.Members.Values:
                self.Debug(f"----Symbol: {security.Symbol}")

        # Debug added and removed securities
        for security in changes.AddedSecurities:
            self.Debug(f"Added: {security.Symbol}")
        for security in changes.RemovedSecurities:
            self.Debug(f"Removed: {security.Symbol}")

        # Adjust indicators and news feed for added and removed securities
        try: 
            for security in changes.AddedSecurities:
                symbol = security.Symbol
                self.emaShort[symbol] = self.EMA(symbol, 9, Resolution.Minute)
                self.emaLong[symbol] = self.EMA(symbol, 21, Resolution.Minute)
                self.atr[symbol] = self.ATR(symbol, 14, MovingAverageType.Wilders, Resolution.Minute)
                self.RegisterIndicator(symbol, self.stochRsi, Resolution.Minute)            
                self.news_feed[symbol] = self.AddData(TiingoNews, symbol)

            for security in changes.RemovedSecurities:
                symbol = security.Symbol
                if symbol in self.emaShort: del self.emaShort[symbol]
                if symbol in self.emaLong: del self.emaLong[symbol]
                if symbol in self.atr: del self.atr[symbol]
                if symbol in self.news_feed: self.RemoveSecurity(symbol)
        except Exception as e:
            self.SetRunTimeError(f"Error on OnSecuritiesChanged: {str(e)}")                        


    # def OnData(self, data):
    # # Runs upon receipt of every bar/candle for the filtered stocks
    #     try:
    #         self.UpdateSectorExposure()
            
    #         total_atr_inverse = sum(1 / self.atr[s].Current.Value for s in self.stockSymbols if s in self.atr)
            
    #         # Implement your intraday trading logic here
    #         for symbol in self.stockSymbols:
    #             # Check if news for the symbol is present
    #             news_data = data.Get(TiingoNews, symbol)
    #             if news_data:
    #                 for article in news_data.Values:
    #                     # Log news articles and sentiment
    #                     self.Debug(f"News for {symbol}: Title - {article.Title}, Sentiment - {article.Sentiment}")
    #             if self.ShouldInvest(symbol, data):
    #                 volatility = self.atr[symbol].Current.Value
    #                 positionSize = self.CalculatePositionSize(volatility)
    #                 self.SetHoldings(symbol, positionSize)
    #                 risk = self.CalculateRisk(symbol, data)
    #                 reward = self.CalculateReward(symbol, data)
    #                 if reward > 0 and risk > 0 and (reward / risk) >= 2:  # Ensuring neither risk nor reward is zero
    #                     self.EnterTrade(symbol, data, risk)

    #             if symbol in self.trailingStopPrice:
    #                 if data[symbol].Close < self.trailingStopPrice[symbol]:
    #                     self.Liquidate(symbol)
    #                 else:
    #                     self.trailingStopPrice[symbol] = max(self.trailingStopPrice[symbol], data[symbol].Close * (1 - self.trailingStopLoss))

    #             # Trading logic with advanced order types
    #             if not self.Portfolio[symbol].Invested and self.IsUptrend(symbol):
    #                 limitPrice = data[symbol].Close * 0.99  # e.g., 1% below current close
    #                 quantity = self.CalculateOrderQuantity(symbol, 1 / self.numberOfStocks)
    #                 self.LimitOrder(symbol, quantity, limitPrice)
    #             elif self.Portfolio[symbol].Invested:
    #                 if self.ShouldSell(symbol, data):
    #                     # Stop-Limit order example
    #                     stopPrice = data[symbol].Close * 0.9  # 10% stop loss
    #                     limitPrice = stopPrice * 0.98  # 2% below stop price
    #                     quantity = self.Portfolio[symbol].Quantity
    #                     self.StopLimitOrder(symbol, -quantity, stopPrice, limitPrice)
    #     except Exception as e:
    #         self.Debug(f"Error on OnData: {str(e)}")                        

    # def IsUptrend(self, symbol):
    #     try: 
    #         # EMA analysis
    #         short_ema_current = self.emaShort[symbol].Current.Value
    #         long_ema_current = self.emaLong[symbol].Current.Value
    #         short_ema_previous = self.emaShort[symbol].Previous.Value
    #         long_ema_previous = self.emaLong[symbol].Previous.Value

    #         is_ema_crossover = short_ema_current > long_ema_current
    #         is_short_ema_rising = short_ema_current > short_ema_previous
    #         is_ema_distance_widening = (short_ema_current - long_ema_current) > (short_ema_previous - long_ema_previous)
            
    #         # RSI Analysis
    #         rsi_value = self.RSI(symbol, 14, Resolution.Minute).Current.Value
    #         is_rsi_bullish = rsi_value > 50
    #         is_stoch_rsi_bullish = self.stochRsi.IsReady and self.stochRsi.StochRsi > 0.5  # Example condition

    #         # MACD Analysis
    #         macd = self.MACD(symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily, Field.Close)
    #         is_macd_bullish = macd.Current.Value > macd.Signal.Current.Value

    #         return is_ema_crossover and is_ema_distance_widening and is_stoch_rsi_bullish and is_rsi_bullish and is_macd_bullish
    #     except Exception as e:
    #         self.Debug(f"Error on IsUptrend: {str(e)}")                        

    # def EnterTrade(self, symbol, data, risk):
    #     # Enter the trade
    #     # Size the position based on the risk
    #     self.SetHoldings(symbol, self.CalculatePositionSize(risk))
    #     # Set up exit criteria (e.g., stop-loss orders, take-profit orders)

    # def CalculateRisk(self, symbol, data):
    #     # Assuming you have a method to calculate stop-loss level
    #     stopLossLevel = self.CalculateStopLossLevel(symbol, data)
    #     currentPrice = data[symbol].Price
    #     risk = currentPrice - stopLossLevel  # For a long position
    #     return risk

    # def CalculateReward(self, symbol, data):
    #     # Assuming you have a method to calculate take-profit level
    #     takeProfitLevel = self.CalculateTakeProfitLevel(symbol, data)
    #     currentPrice = data[symbol].Price
    #     reward = takeProfitLevel - currentPrice  # For a long position
    #     return reward

    # def ShouldBuy(self, symbol, data):
    #     # Implement your buying logic
    #     return shouldBuy

    # def ShouldSell(self, symbol, data):
    #     currentPrice = data[symbol].Price
    #     investedPrice = self.Portfolio[symbol].AveragePrice
    #     profit = (currentPrice - investedPrice) / investedPrice

    #     # Check for 10% stop loss or 500% profit target
    #     if profit <= -0.10:
    #         return True
    #     elif profit >= 5.00:
    #         self.SellHalfPosition(symbol)  # Custom method to sell half position
    #         return False  # Keep the rest of the position
    #     return False

    # def SellHalfPosition(self, symbol):
    #     # Sell half the position of the specified symbol
    #     holdings = self.Portfolio[symbol].Quantity
    #     self.MarketOrder(symbol, -holdings / 2)

    # def OnOrderEvent(self, orderEvent):
    #     if orderEvent.Status == OrderStatus.Filled:
    #         self.HandleTradeOutcome(orderEvent)
    #         if orderEvent.Direction == OrderDirection.Buy:
    #             self.trailingStopPrice[orderEvent.Symbol] = orderEvent.FillPrice * (1 - self.trailingStopLoss)

    # def HandleTradeOutcome(self, orderEvent):
    #     # Assume orderEvent has the necessary information about the trade outcome
    #     profit = self.CalculateProfit(orderEvent)
    #     if profit > 0:
    #         self.win_count += 1
    #         self.total_profit += profit
    #     else:
    #         self.loss_count += 1
    #         self.total_loss += abs(profit)

    #     self.UpdateWinProbabilityAndRatio()

    # def CalculateProfit(self, orderEvent):
    #     # Implement logic to calculate profit from the orderEvent
    #     return profit

    # def CalculatePortfolioHeat(self, data):
    #     totalHeat = 0
    #     for symbol in self.ActiveSecurities.Keys:
    #         if self.Portfolio[symbol].Invested:
    #             positionSize = self.Portfolio[symbol].Quantity * self.Securities[symbol].Price
    #             riskPerTrade = positionSize - self.CalculateStopLossValue(symbol, data)
    #             totalHeat += max(0, riskPerTrade)  # Add only positive risk values
    #     return totalHeat / self.Portfolio.TotalPortfolioValue

    # def CalculateStopLossValue(self, symbol, data):
    #     # Assuming a stop-loss method to calculate the value at which a stop-loss would be hit
    #     # This could be a fixed percentage below the current price or based on ATR, etc.
    #     # Example: Fixed percentage
    #     stopLossPercentage = 0.1  # 10% stop loss
    #     currentPrice = data[symbol].Price
    #     stopLossValue = currentPrice * (1 - stopLossPercentage)
    #     return self.Portfolio[symbol].Quantity * stopLossValue

    # def UpdateWinProbabilityAndRatio(self):
    #     if self.win_count + self.loss_count > 0:
    #         win_probability = self.win_count / (self.win_count + self.loss_count)
    #         win_loss_ratio = self.total_profit / self.total_loss if self.total_loss != 0 else 0

    #         # Now, you can use win_probability and win_loss_ratio to calculate your Kelly Criterion

    # def RebalancePortfolio(self):
    #     # Check for portfolio drawdown and rebalance if needed
    #     currentPortfolioValue = self.Portfolio.TotalPortfolioValue
    #     if currentPortfolioValue < self.highestPortfolioValue * (1 - self.MaxPortfolioDrawdown):
    #         self.Liquidate()  # Exit all positions
    #     else:
    #         self.highestPortfolioValue = max(self.highestPortfolioValue, currentPortfolioValue)

    # def CalculateStopLossLevel(self, symbol, data):
    #     # Implement your logic to calculate the stop-loss level
    #     return stopLossLevel

    # def CalculateTakeProfitLevel(self, symbol, data):
    #     # Implement your logic to calculate the take-profit level
    #     return takeProfitLevel

    # def CalculatePositionSize(self, risk):
    #     # Calculate the position size based on the risk and your total portfolio value
    #     # Example: Risk 1% of portfolio per trade
    #     riskCapital = self.Portfolio.TotalPortfolioValue * 0.01
    #     positionSize = riskCapital / risk
    #     return min(positionSize, 1)  # Ensure not to exceed 100% allocation
