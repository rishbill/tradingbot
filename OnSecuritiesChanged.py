# Begin OnSecuritiesChanged.py

from AlgorithmImports import *
import config as c
import variables as v

class OnSecuritiesChangedHandler:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def OnSecuritiesChanged(self, changes):        
        try:
            # Runs when new symbols are added to the dynamic universe  
            # Preview up to 10 symbols that are AddedSecurities and include the current timestamp
            current_timestamp = self.algorithm.Time.strftime("%Y-%m-%d")
            added_symbols_preview = [security.Symbol for security in changes.AddedSecurities[:10]]
            self.algorithm.Debug(f"{current_timestamp} - Universe Updated +{len(changes.AddedSecurities)}: {', '.join(str(symbol) for symbol in added_symbols_preview)}")
            
            for security in changes.AddedSecurities:
                symbol = security.Symbol

                # Initialize indicators for each symbol
                v.indicators[symbol] = {
                    "atrmin": self.algorithm.MIN(symbol, c.buy_parameter_atr_low_period, Resolution.Daily),
                    "atr": self.algorithm.ATR(symbol, c.buy_parameter_atr_periods, MovingAverageType.Wilders, Resolution.Minute),
                    "emaShort": self.algorithm.EMA(symbol, c.buy_parameter_ema_short_periods, Resolution.Minute),
                    "emaLong": self.algorithm.EMA(symbol, c.buy_parameter_ema_long_periods, Resolution.Minute),
                    "macd": self.algorithm.MACD(symbol, fastPeriod=12, slowPeriod=26, signalPeriod=9, resolution=Resolution.Daily),
                    "rsi": self.algorithm.RSI(symbol, c.buy_parameter_rsi_periods, Resolution.Daily),
                    "sto": self.algorithm.STO(symbol, c.buy_parameter_stochastic_rsi_periods, Resolution.Minute)
                }

        except Exception as e:
            self.algorithm.algorithm.Error(f"Error on OnSecuritiesChanged: {str(e)}")

# End OnSecuritiesChanged.py            