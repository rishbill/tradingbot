from AlgorithmImports import *
import config as c
import variables as v

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
            c.numberOfStocks = len(self.active_stock_symbols)

            # Create and register indicators for each added symbol
            v.ema_short_data[symbol] = self.EMA(symbol, c.buy_parameter_ema_short_periods, Resolution.Minute)
            v.ema_long_data[symbol] = self.EMA(symbol, c.buy_parameter_ema_long_periods, Resolution.Minute)
            v.atr_data[symbol] = self.ATR(symbol, c.buy_parameter_atr_periods, MovingAverageType.Wilders, Resolution.Minute)
            v.rsi_data[symbol] = self.RSI(symbol, c.buy_parameter_rsi_periods, Resolution.Daily).Current.Value
            v.stochastic_rsi_data[symbol] = self.STO(symbol, c.buy_parameter_stochastic_rsi_periods, Resolution.Minute)
            v.macd_data = self.MACD(symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily, Field.Close)

        for security in changes.RemovedSecurities:
            symbol = security.Symbol
            if symbol in self.active_stock_symbols:
                self.active_stock_symbols.remove(symbol)
            # Remove indicators for removed symbols
            if symbol in v.ema_short_data: del v.ema_short_data[symbol]
            if symbol in v.ema_long_data: del v.ema_long_data[symbol]
            if symbol in v.atr_data: del v.atr_data[symbol]
            if symbol in v.stochastic_rsi_data: del v.stochastic_rsi_data[symbol]

    except Exception as e:
        self.Error(f"Error on OnSecuritiesChanged: {str(e)}")