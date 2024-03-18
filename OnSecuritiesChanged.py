# Begin OnSecuritiesChanged.py

from AlgorithmImports import *
import config as c
import variables as v

class OnSecuritiesChangedHandler:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def OnSecuritiesChanged(self, changes):
        # Runs when new symbols are added to the dynamic universe  
        # Preview up to 10 symbols that are AddedSecurities and include the current timestamp
        current_timestamp = self.algorithm.Time.strftime("%Y-%m-%d")
        added_symbols_preview = [security.Symbol for security in changes.AddedSecurities[:10]]
        self.algorithm.Debug(f"{current_timestamp} - Universe Updated +{len(changes.AddedSecurities)}: {', '.join(str(symbol) for symbol in added_symbols_preview)}")
        try: 
            for security in changes.AddedSecurities:
                symbol = security.Symbol
                if symbol not in v.active_stock_symbols:
                    v.active_stock_symbols.append(symbol)
                v.count_active_stock_symbols = len(v.active_stock_symbols)

                # Create and register indicators for each added symbol
                v.ema_short_data[symbol] = self.algorithm.EMA(symbol, c.buy_parameter_ema_short_periods, Resolution.Minute)
                v.ema_long_data[symbol] = self.algorithm.EMA(symbol, c.buy_parameter_ema_long_periods, Resolution.Minute)
                v.atr_data[symbol] = self.algorithm.ATR(symbol, c.buy_parameter_atr_periods, MovingAverageType.Wilders, Resolution.Minute)
                v.rsi_data[symbol] = self.algorithm.RSI(symbol, c.buy_parameter_rsi_periods, Resolution.Daily)
                v.stochastic_rsi_data[symbol] = self.algorithm.STO(symbol, c.buy_parameter_stochastic_rsi_periods, Resolution.Minute)
                v.macd_data[symbol] = self.algorithm.MACD(symbol, 12, 26, 9, MovingAverageType.Exponential, Resolution.Daily, Field.Close)

            for security in changes.RemovedSecurities:
                symbol = security.Symbol
                if symbol in v.active_stock_symbols:
                    v.active_stock_symbols.remove(symbol)

                # Remove indicators for removed symbols
                if symbol in v.ema_short_data: del v.ema_short_data[symbol]
                if symbol in v.ema_long_data: del v.ema_long_data[symbol]
                if symbol in v.atr_data: del v.atr_data[symbol]
                if symbol in v.rsi_data: del v.rsi_data[symbol]
                if symbol in v.stochastic_rsi_data: del v.stochastic_rsi_data[symbol]
                if symbol in v.macd_data: del v.macd_data[symbol]

        except Exception as e:
            self.algorithm.Error(f"Error on OnSecuritiesChanged: {str(e)}")

# End OnSecuritiesChanged.py            