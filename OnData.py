# Begin OnData.py

from AlgorithmImports import *
from shouldBuy import shouldBuy
from shouldSell import shouldSell
import config as c
import variables as v
import json

class OnDataHandler:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def OnData(self, data):
        # Implementation of OnData

    # Runs upon receipt of every bar/candle for the filtered symbols
        try:
            # Log warm-up progress every 10 iterations
            if self.algorithm.IsWarmingUp:
                pass
                    
            else:               
                for symbol in self.algorithm.ActiveSecurities.Keys:
                    if symbol in data:                        
                        bar = data[symbol]
                        if bar is not None and isinstance(bar, (TradeBar, QuoteBar)):

                            # Check if the indicators for the symbol are ready
                            indicators = v.indicators.get(symbol, None)
                            if indicators is not None:
                                all_ready = all(indicator.IsReady for indicator in indicators.values())
                                if all_ready:
                                    self.plotIndicators(self, symbol, indicators)

                                    # Debug logging
                                    if self.algorithm.Time.hour == 16 and self.Time.minute == 0:                                        
                                        for indicator_name, indicator in indicators.items():
                                            self.algorithm.Debug(f"End of day status: {indicator_name} for {symbol} = {indicator.Current.Value}")

                                else:
                                    for indicator_name, indicator in indicators.items():
                                        if not indicator.IsReady:
                                            self.algorithm.Debug(f"{self.algorithm.Time} - {indicator_name} not ready for {symbol}. Skipping OnData slice...")
                                            continue

                                v.symbol_sector[symbol] = self.algorithm.Securities[symbol].Fundamentals.AssetClassification.MorningstarSectorCode
                                v.current_price[symbol] = data[symbol].Price
                                v.current_close_price[symbol] = data[symbol].Close
                            
                                # Check for Buy condition
                                should_buy, order_tag = shouldBuy(self.algorithm, symbol, data)
                                if should_buy:
                                    v.latest_order_ticket[symbol] = self.algorithm.LimitOrder(symbol, round(v.position_size_share_qty_to_buy[symbol]), v.buy_limit_price[symbol], order_tag)
                                    v.open_order_tickets[symbol] = v.latest_order_ticket[symbol]

                                # Check for Sell condition
                                should_sell, order_tag = shouldSell(self.algorithm, symbol, data)
                                if self.algorithm.Portfolio[symbol].Invested and not should_buy and should_sell:
                                    
                                    shares_qty_held = self.algorithm.Portfolio[symbol].Quantity
                                        # Get the total shares held for this symbol.
                                    
                                    if v.take_profit_max_price[symbol] == v.take_profit_percent_price[symbol]:
                                        shares_qty_to_sell = round(shares_qty_held * c.sell_parameter_take_profit_percent) 
                                        v.latest_order_ticket[symbol] = self.algorithm.LimitOrder(symbol, -round(shares_qty_to_sell), v.take_profit_max_price[symbol], order_tag)
                                            # In case the price target is the Fixed Take Profit %, only sell half.
                                        v.open_order_tickets[symbol]  = v.latest_order_ticket[symbol]
                                    else:
                                        v.latest_order_ticket[symbol] = self.algorithm.LimitOrder(symbol, -round(shares_qty_held), v.take_profit_max_price[symbol], order_tag)
                                        v.open_order_tickets[symbol]  = v.latest_order_ticket[symbol]
                                            # Otherwise, sell the entire position.   

                                if should_buy or should_sell:
                                    if symbol in v.latest_order_ticket and v.latest_order_ticket is not None:
                                        debug_message = {
                                            "Type": v.latest_order_ticket[symbol].OrderDirection,
                                            "ID": v.latest_order_ticket[symbol].OrderId,
                                            "Symbol": str(v.latest_order_ticket[symbol].Symbol),
                                            "Quantity": v.latest_order_ticket[symbol].Quantity,
                                            "Status": v.latest_order_ticket[symbol].Status,
                                            "Price": v.latest_order_ticket[symbol].AverageFillPrice,
                                            "Time": str(v.latest_order_ticket[symbol].Time),
                                            "Tag": v.latest_order_ticket[symbol].Tag
                                        }                     
                                        self.algorithm.Debug("ORDER SUBMITTED:")
                                        self.algorithm.Debug(json.dumps(debug_message))

                            else: 
                                self.algorithm.Error(f"{self.algorithm.Time} - {indicator_name} not initialized for {symbol}")

                        else:
                            self.algorithm.Error(f"Received unexpected data type for {symbol}: {type(bar)}. Skipping.")                            

        except Exception as e:
            self.algorithm.Error(f"Error on OnData: {str(e)}")  

    def CancelOldOrders(self):
        try:
            for symbol, order_ticket in v.open_order_tickets.items():
                
                if order_ticket is not None and not order_ticket.OrderClosed:
                    order_time = self.algorithm.Time  # Current algorithm time
                    order_age = (order_time - order_ticket.Time).total_seconds() / 60  # Age in minutes
                    
                    if order_age > c.max_pending_order_age_minutes:
                        order_ticket.Cancel("Order too old")
                        self.algorithm.Debug(f"Order {order_ticket.OrderId} for {symbol} cancelled due to timeout")
                    
                    # Log unfilled orders periodically (e.g., every 15 minutes)
                    elif order_age % 15 == 0:
                        self.algorithm.Debug(f"Order still pending: {order_ticket.Symbol}, Order Age: {order_age} minutes, Canceling in {c.max_submitted_order_minutes - order_age} minutes...")
        
        except Exception as e:
            self.algorithm.Error(f"Error on HandleTradeOutcome: {str(e)}") 
            return False
    
    def plotIndicators(self, symbol, indicators):
    # Create and add series for EMAs on one chart
        ema_chart = f"{symbol} - EMAs"
        self.algorithm.AddChart(Chart(ema_chart))
        self.algorithm.Plot(ema_chart, "EMA Short", indicators["emaShort"].Current.Value)
        self.algorithm.Plot(ema_chart, "EMA Long", indicators["emaLong"].Current.Value)

        # Plot EMA Crossover as Buy Signal (Scatter with Crosses)
        if indicators["emaShort"].Current.Value > indicators["emaLong"].Current.Value and \
        indicators["emaShort"].Previous.Value < indicators["emaLong"].Previous.Value:
            self.algorithm.Plot(ema_chart, "Buy Signal - EMA Crossover", indicators["emaShort"].Current.Value, color=Color.Green, scatterMarkerSymbol=ScatterMarkerSymbol.Cross)

        # Create and add series for MACD on a separate chart
        macd_chart = f"{symbol} - MACD"
        macd_chart_obj = Chart(macd_chart)
        macd_chart_obj.AddSeries(Series("MACD", SeriesType.Line))
        macd_chart_obj.AddSeries(Series("MACD Signal", SeriesType.Line))
        macd_chart_obj.AddSeries(Series("MACD Histogram", SeriesType.Line))
        macd_chart_obj.AddSeries(Series("Buy Signal - MACD Crossover", SeriesType.Scatter, unit="", color=Color.Green, scatterMarkerSymbol=ScatterMarkerSymbol.Cross))
        self.algorithm.AddChart(macd_chart_obj)

        # Plot MACD values
        self.algorithm.Plot(macd_chart, "MACD", indicators["macd"].Current.Value)
        self.algorithm.Plot(macd_chart, "MACD Signal", indicators["macd"].Signal.Current.Value)
        macd_histogram_value = indicators["macd"].Current.Value - indicators["macd"].Signal.Current.Value
        self.algorithm.Plot(macd_chart, "MACD Histogram", macd_histogram_value)

        # Plot MACD Crossover as Buy Signal (Scatter with Crosses)
        if indicators["macd"].Current.Value > indicators["macd"].Signal.Current.Value and \
        indicators["macd"].Previous.Value < indicators["macd"].Signal.Previous.Value:
            self.algorithm.Plot(macd_chart, "Buy Signal", indicators["macd"].Current.Value)

        # Plot RSI and Stochastic on another chart
        rsi_sto_chart = f"{symbol} - RSI & Stochastic (Value)"
        rsi_sto_chart.AddSeries(Series("RSI", SeriesType.Line, unit="%"))
        rsi_sto_chart.AddSeries(Series("Stochastic", SeriesType.Line, unit="%"))
                        
        self.algorithm.Plot(rsi_sto_chart, "RSI", indicators["rsi"].Current.Value)
        self.algorithm.Plot(rsi_sto_chart, "Stochastic", indicators["sto"].Current.Value)

# End OnData.py