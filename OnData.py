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
            current_day = self.algorithm.Time.day
            if self.algorithm.IsWarmingUp:
                if v.last_increment_day != current_day:
                    v.warmup_counter += 1
                    v.last_increment_day = current_day
                # Skip doing anything if algorithm is still warming up.
                    
            else:               
                for symbol in v.active_stock_symbols:
                    if not data.ContainsKey(symbol):
                        # Skip this symbol if it's not present in the current OnData Slice.
                        continue

                    # Update Variables for this symbol.
                    v.current_price = data[symbol].Price
                    v.current_close_price = data[symbol].Close
                    v.symbol_history[symbol] = self.algorithm.History(["SPY"], 30, Resolution.Daily)
                    v.lowest_price_30_days[symbol] = min([bar.Low for bar in v.symbol_history[symbol]])
                    v.symbol_sector[symbol] = symbol.AssetClassification.MorningstarSectorCode

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

                    # Check for Buy condition
                    should_buy, order_tag = shouldBuy(self, symbol, data)
                    if should_buy:
                        v.latest_order_ticket = self.algorithm.LimitOrder(symbol, round(v.position_size_share_qty_to_buy[symbol]), v.buy_limit_price[symbol], order_tag)
                        v.open_order_tickets.append(v.latest_order_ticket)
                        debug_message = (
                            f"BUY Order Submitted: ID={v.latest_order_ticket.OrderId}, Symbol={v.latest_order_ticket.Symbol}, "
                            f"Quantity={v.latest_order_ticket.Quantity}, Status={v.latest_order_ticket.Status}, "
                            f"Price={v.latest_order_ticket.AverageFillPrice}, Time={v.latest_order_ticket.Time}, Tag={v.latest_order_ticket.Tag}"
                        )

                    # Check for Sell condition
                    should_sell, order_tag = shouldSell(self, symbol, data)
                    if self.algorithm.Portfolio[symbol].Invested and not should_buy and should_sell:
                        
                        shares_qty_held = self.algorithm.Portfolio[symbol].Quantity
                            # Get the total shares held for this symbol.
                        
                        if v.take_profit_max_price[symbol] == v.take_profit_percent_price[symbol]:
                            shares_qty_to_sell = round(shares_qty_held * c.sell_parameter_take_profit_percent) 
                            v.latest_order_ticket = self.algorithm.LimitOrder(symbol, -round(shares_qty_to_sell), v.take_profit_max_price[symbol], order_tag)
                                # In case the price target is the Fixed Take Profit %, only sell half.
                            v.open_order_tickets.append(v.latest_order_ticket)
                            debug_message = (
                                f"SELL Order Submitted: ID={v.latest_order_ticket.OrderId}, Symbol={v.latest_order_ticket.Symbol}, "
                                f"Quantity={v.latest_order_ticket.Quantity}, Status={v.latest_order_ticket.Status}, "
                                f"Price={v.latest_order_ticket.AverageFillPrice}, Time={v.latest_order_ticket.Time}, Tag={v.latest_order_ticket.Tag}"
                            )                    
                        else:
                            v.latest_order_ticket = self.algorithm.LimitOrder(symbol, -round(shares_qty_held), v.take_profit_max_price[symbol], order_tag)
                            v.open_order_tickets.append(v.latest_order_ticket)
                                # Otherwise, sell the entire position.
                            debug_message = (
                                f"SELL Order Submitted: ID={v.latest_order_ticket.OrderId}, Symbol={v.latest_order_ticket.Symbol}, "
                                f"Quantity={v.latest_order_ticket.Quantity}, Status={v.latest_order_ticket.Status}, "
                                f"Price={v.latest_order_ticket.AverageFillPrice}, Time={v.latest_order_ticket.Time}, Tag={v.latest_order_ticket.Tag}"
                            )      

                    if should_buy or should_sell:
                        if v.latest_order_ticket is not None:
                            self.algorithm.Debug(debug_message)

        except Exception as e:
            self.algorithm.Debug(f"Error on OnData: {str(e)}")  

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