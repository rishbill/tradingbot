# Begin main.py
# QuantConnect Knowledge Base
# https://www.quantconnect.com/docs/v2/writing-algorithms
# Stocks = Symbols = Securities

from AlgorithmImports import *
from shouldBuy import *
from shouldSell import *
import numpy as np
import config as c
import variables as v
import collections

class CodysAdvancedStrategy(QCAlgorithm):
    def Initialize(self):
    # Main function for class

        # Initialize Variables
        c.SetStartDate(self)
        c.SetCash(self)
        c.SetWarmUp(self)
        self.EnableAutomaticIndicatorWarmUp = True
        c.SetBrokerageModel(self)       
        portfolio_value = self.Portfolio.TotalPortfolioValue
        stock_counts_per_sector = self.CalculateStockCountsPerSector()
        total_invested_stocks = sum(stock_counts_per_sector.values())

        # Universe Filtering
        self.max_stock_price = self.Portfolio.TotalPortfolioValue * c.max_stock_price_portfolio_percent # Limit max stock price to X% of portfolio size, for affordability
        self.Debug("Universe filter variables:")
        self.Debug(f"------- Stock Price Range ------------------------- ${c.min_stock_price} - ${self.max_stock_price}")
        self.Debug(f"------- P/E Ratio Range --------------------------- {c.min_pe_ratio} to {c.max_pe_ratio}")
        self.Debug(f"------- Min Revenue Growth ------------------------ {c.min_revenue_growth_percent}")
        try:
            self.Debug(f"Filtering Universe...")
            self.UniverseSettings.Resolution = Resolution.Minute
            self.AddUniverse(self.UniverseFilter)  # Get the stocks for today's potential trades
        except Exception as e:
            self.Error(f"---- Error filtering Universe: {str(e)}")                    

    def UniverseFilter(self, fundamental: List[Fundamental]) -> List[Symbol]:
    # Returns a filtered list of stocks,  dynamically re-filtered daily   
        try:
            filtered = [f for f in fundamental if f.HasFundamentalData and c.min_stock_price <= f.Price < self.max_stock_price and f.ValuationRatios.PERatio > c.min_pe_ratio and f.ValuationRatios.PERatio < c.max_pe_ratio and f.OperationRatios.RevenueGrowth.OneYear > c.min_revenue_growth_percent and not np.isnan(f.ValuationRatios.PERatio) and not np.isnan(f.OperationRatios.RevenueGrowth.OneYear) and not np.isnan(f.DollarVolume) and not np.isnan(f.MarketCap) and f.ValuationRatios.PERatio != 0 and f.OperationRatios.RevenueGrowth.OneYear != 0 and f.DollarVolume != 0 and f.MarketCap != 0]
            sortedByDollarVolume = sorted(filtered, key=lambda f: f.DollarVolume, reverse=True)[:10]
            sortedByPeRatio = sorted(sortedByDollarVolume, key=lambda f: f.ValuationRatios.PERatio, reverse=False)[:10]
            
            if self.warmup_counter >= c.warmup_period + 1:
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
                    sector = c.GetSectorForStock(symbol) # Get the sector for this stock
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
                    # Update Indicators
                    v.current_price = data[symbol].Price
                    v.current_close_price = data[symbol].Close
                    v.symbol_history[symbol] = self.History(["SPY"], 30, Resolution.Daily)
                    v.lowest_price_30_days[symbol] = v.symbol_history[symbol]['low']

                    if v.atr_data.IsReady:
                        v.atr = v.atr_data[symbol].Current.Value
                    if v.ema_short_data.IsReady:    
                        v.short_ema = v.ema_short_data[symbol].Current.Value
                        v.short_ema_previous = v.ema_short_data[symbol].Previous.Value
                    if v.ema_long_data.IsReady:    
                        v.long_ema = v.ema_long_data[symbol].Current.Value
                        v.long_ema_previous = v.ema_long_data[symbol].Previous.Value
                    if v.rsi_data.IsReady:    
                        v.rsi = v.rsi_data[symbol].Current.Value
                    if v.stochastic_rsi_data.IsReady:    
                        v.stochastic_rsi = v.stochastic_rsi_data[symbol].Current.Value
                    if v.macd_data.IsReady:    
                        v.macd = v.macd_data[symbol].Current.Value

                    if shouldBuy(self, symbol, data):
                        limit_price_to_buy = data[symbol].Close * c.buy_limit_order_percent
                        fraction_of_portfolio = 1 / c.numberOfStocks
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
                            self.trailing_take_profit_price[symbol] = current_price * (1 + c.trailing_take_profit_percent)
                        else:
                            # Update the trailing take profit if the price moves up
                            if current_price > self.trailing_take_profit_price[symbol] / (1 + c.trailing_take_profit_percent):
                                self.trailing_take_profit_price[symbol] = current_price * (1 + c.trailing_take_profit_percent)
                        if symbol not in v.trailing_stop_price:
                            # Initialize trailing stop loss price if it doesn't exist
                            v.trailing_stop_price[symbol] = current_price * (1 - c.sell_parameter_trailing_stop_percent)
                        else:
                            # Update the trailing stop loss if the price moves up
                            if current_price > v.trailing_stop_price[symbol]:
                                v.trailing_stop_price[symbol] = current_price * (1 - c.sell_parameter_trailing_stop_percent)
                    # Check for Sell condition
                    if self.Portfolio[symbol].Invested and shouldSell(self, symbol, data):
                        holdings = self.Portfolio[symbol].Quantity
                        self.order_ticket = self.MarketOrder(symbol, -holdings * c.fixed_take_profit_percent_to_sell)
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
        if symbol not in c.day_trades:
            c.day_trades[symbol] = {'buy': False, 'sell': False, 'date': None}

        if c.day_trades[symbol]['date'] == current_date:
            # Check for day trade (buy and sell on the same day)
            if (order_type == 'sell' and c.day_trades[symbol]['buy']) or (order_type == 'buy' and c.day_trades[symbol]['sell']):
                self.day_trade_dates.append(current_date)
                self.day_trade_counter += 1
                self.Debug(f"Day Trade Detected for {symbol} on {current_date}. Total Day Trades in last 5 days: {len(self.day_trade_dates)}")
                # Reset the day trade flags for this stock
                c.day_trades[symbol] = {'buy': False, 'sell': False, 'date': None}
        else:
            # Record this trade action
            c.day_trades[symbol][order_type] = True
            c.day_trades[symbol]['date'] = current_date


        if orderEvent.Status == OrderStatus.Submitted:
            self.Debug(f"Order Submitted: {symbol} - ID: {orderEvent.OrderId} - Qty: {fill_qty} * ${fill_price} = ${fill_qty * fill_price}")
        
        # Add all currently invested stocks to the unique_portfolio_stocks
        v.unique_portfolio_stocks.clear()        
        v.unique_portfolio_stocks = {s for s, holding in self.Portfolio.items() if holding.Invested}
        self.Debug(f"Updated unique portfolio stocks: {v.unique_portfolio_stocks}")

        if orderEvent.Status == OrderStatus.Filled:
            if orderEvent.Direction == OrderDirection.Buy:
                self.Debug(f"---- BUY Order Filled: {symbol} - ID: {orderEvent.OrderId} - Qty: {fill_qty} * ${fill_price} = ${fill_qty * fill_price}")
                self.HandleTradeOutcome(orderEvent)
                new_trailing_stop_price = fill_price * (1 - c.sell_parameter_trailing_stop_percent)
                v.trailing_stop_price[symbol] = new_trailing_stop_price
                new_trailing_take_profit_price = fill_price * (1 + c.trailing_take_profit_percent)
                self.trailing_take_profit_price[symbol] = new_trailing_take_profit_price

                fixed_take_profit_price = fill_price * (1 + c.fixed_take_profit_percent)
                self.Debug(f"-------- Fixed Take Profit: {symbol} @ ${fixed_take_profit_price} (Fill Price: ${fill_price} * (1 + {c.fixed_take_profit_percent}))")
                self.Debug(f"-------- Trailing Take Profit: {symbol} @ ${new_trailing_take_profit_price} (Fill Price: ${fill_price} * (1 + {c.trailing_take_profit_percent}))")

                fixed_stop_loss_price = fill_price * (1 - c.fixed_stop_loss_percent)
                self.Debug(f"-------- Fixed Stop Loss: {symbol} @ ${fixed_stop_loss_price} (Fill Price: ${fill_price} * (1 - {c.fixed_stop_loss_percent}))")
                self.Debug(f"-------- Trailing Stop Loss: {symbol} @ ${new_trailing_stop_price} (Fill Price: ${fill_price} * (1 - {c.sell_parameter_trailing_stop_percent}))")

            elif orderEvent.Direction == OrderDirection.Sell:
                self.Debug(f"---- SELL Order Filled: {symbol} - ID: {orderEvent.OrderId} - Qty: {fill_qty} * ${fill_price} = ${fill_qty * fill_price}")
                # Retrieve existing trailing stop and take profit prices if any
                existing_trailing_stop = v.trailing_stop_price.get(symbol, None)
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
                    if order_age > c.max_submitted_order_minutes:
                        self.order_ticket.Cancel("Order too old")
                        self.Debug(f"Order {self.order_ticket.OrderId} for {symbol} cancelled due to timeout")
                    # Log unfilled orders periodically (e.g., every 15 minutes)
                    elif order_age % 15 == 0:
                        self.Debug(f"Order still pending: {self.order_ticket.Symbol}, Order Age: {order_age} minutes, Canceling in {c.max_submitted_order_minutes - order_age} minutes...")
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