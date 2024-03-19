# Begin OnData.py

from AlgorithmImports import *
from shouldBuy import shouldBuy
from shouldSell import shouldSell
import config as c
import variables as v

class OnDataHandler:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def OnData(self, data):
        # Implementation of OnData

    # Runs upon receipt of every bar/candle for the filtered stocks
        try:
            # Log warm-up progress every 10 iterations
            current_day = self.algorithm.Time.day
            if self.algorithm.IsWarmingUp:
                if v.last_increment_day != current_day:
                    v.warmup_counter += 1
                    v.last_increment_day = current_day
                    if v.warmup_counter % 10 == 0:
                        self.algorithm.Debug(f"Warming Up... ({v.warmup_counter} \ {c.warmup_period} Days)")
                    
            else:               
                for symbol in self.algorithm.ActiveSecurities.Keys:
                    if symbol in data:                        
                        bar = data[symbol]
                        if bar is not None and isinstance(bar, (TradeBar, QuoteBar)):
                            # Process the bar data
                            # Update Variables for this symbol.
                            v.current_price[symbol] = data[symbol].Price
                            v.current_close_price[symbol] = data[symbol].Close
                            
                            try:
                                v.symbol_history[symbol] = self.algorithm.History(symbol, 30, Resolution.Daily)
                                history_bars = v.symbol_history[symbol]
                                if isinstance(history_bars, list):
                                    # Assuming the list contains TradeBar or QuoteBar objects
                                    v.lowest_price_30_days[symbol] = min([bar.Low for bar in history_bars])
                                else:
                                    self.algorithm.Error(f"Unexpected data type for {symbol} history: {type(history_bars)}")
                            except Exception as e:
                                self.algorithm.Error(f"Error retrieving history for {symbol}: {str(e)}")  

                            v.symbol_sector[symbol] = self.algorithm.Securities[symbol].Fundamentals.AssetClassification.MorningstarSectorCode
                            
                            if symbol in v.atr_data and v.atr_data[symbol].IsReady:
                                v.atr[symbol] = v.atr_data[symbol].Current.Value

                            if symbol in v.ema_short_data and v.ema_short_data[symbol].IsReady:
                                v.short_ema[symbol] = v.ema_short_data[symbol].Current.Value
                                v.short_ema_previous[symbol] = v.ema_short_data[symbol].Previous.Value

                            if symbol in v.ema_long_data and v.ema_long_data[symbol].IsReady:
                                v.long_ema[symbol] = v.ema_long_data[symbol].Current.Value
                                v.long_ema_previous[symbol] = v.ema_long_data[symbol].Previous.Value

                            if symbol in v.rsi_data and v.rsi_data[symbol].IsReady:
                                v.rsi[symbol] = v.rsi_data[symbol].Current.Value

                            if symbol in v.stochastic_rsi_data and v.stochastic_rsi_data[symbol].IsReady:
                                v.stochastic_rsi[symbol] = v.stochastic_rsi_data[symbol].Current.Value

                            if symbol in v.macd_data and v.macd_data[symbol].IsReady:
                                v.macd[symbol] = v.macd_data[symbol].Current.Value

                            # Check for Buy condition
                            should_buy, order_tag = shouldBuy(self, symbol, data)
                            if should_buy:
                                v.latest_order_ticket[symbol] = self.algorithm.LimitOrder(symbol, round(v.position_size_share_qty_to_buy[symbol]), v.buy_limit_price[symbol], order_tag)
                                v.open_order_tickets[symbol] = v.latest_order_ticket[symbol]
                            debug_message = (
                                f"BUY Order Submitted: ID={v.latest_order_ticket[symbol].OrderId}, Symbol={v.latest_order_ticket[symbol].Symbol}, "
                                f"Quantity={v.latest_order_ticket[symbol].Quantity}, Status={v.latest_order_ticket[symbol].Status}, "
                                f"Price={v.latest_order_ticket[symbol].AverageFillPrice}, Time={v.latest_order_ticket[symbol].Time}, Tag={v.latest_order_ticket[symbol].Tag}"
                            )

                            # Check for Sell condition
                            should_sell, order_tag = shouldSell(self, symbol, data)
                            if self.algorithm.Portfolio[symbol].Invested and not should_buy and should_sell:
                                
                                shares_qty_held = self.algorithm.Portfolio[symbol].Quantity
                                    # Get the total shares held for this symbol.
                                
                                if v.take_profit_max_price[symbol] == v.take_profit_percent_price[symbol]:
                                    shares_qty_to_sell = round(shares_qty_held * c.sell_parameter_take_profit_percent) 
                                    v.latest_order_ticket[symbol] = self.algorithm.LimitOrder(symbol, -round(shares_qty_to_sell), v.take_profit_max_price[symbol], order_tag)
                                        # In case the price target is the Fixed Take Profit %, only sell half.
                                    v.open_order_tickets[symbol]  = v.latest_order_ticket[symbol]
                                    debug_message = (
                                        f"SELL Order Submitted: ID={v.latest_order_ticket[symbol].OrderId}, Symbol={v.latest_order_ticket[symbol].Symbol}, "
                                        f"Quantity={v.latest_order_ticket[symbol].Quantity}, Status={v.latest_order_ticket[symbol].Status}, "
                                        f"Price={v.latest_order_ticket[symbol].AverageFillPrice}, Time={v.latest_order_ticket[symbol].Time}, Tag={v.latest_order_ticket[symbol].Tag}"
                                    )                    
                                else:
                                    v.latest_order_ticket[symbol] = self.algorithm.LimitOrder(symbol, -round(shares_qty_held), v.take_profit_max_price[symbol], order_tag)
                                    v.open_order_tickets[symbol]  = v.latest_order_ticket[symbol]
                                        # Otherwise, sell the entire position.
                                    debug_message = (
                                        f"SELL Order Submitted: ID={v.latest_order_ticket[symbol].OrderId}, Symbol={v.latest_order_ticket[symbol].Symbol}, "
                                        f"Quantity={v.latest_order_ticket[symbol].Quantity}, Status={v.latest_order_ticket[symbol].Status}, "
                                        f"Price={v.latest_order_ticket[symbol].AverageFillPrice}, Time={v.latest_order_ticket[symbol].Time}, Tag={v.latest_order_ticket[symbol].Tag}"
                                    )      

                            if should_buy or should_sell:
                                if v.latest_order_ticket is not None:
                                    self.algorithm.Debug(debug_message)

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

# End OnData.py