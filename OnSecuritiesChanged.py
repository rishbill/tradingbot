# Begin OnSecuritiesChanged.py

from AlgorithmImports import *
import config as c
import variables as v
from datetime import datetime, timedelta

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
                if symbol not in v.consolidators:
                    v.consolidators[symbol] = []
                if symbol not in v.indicators:
                    v.indicators[symbol] = []
                    
                atr = AverageTrueRange(c.buy_parameter_atr_periods, MovingAverageType.Wilders)
                consolidator_ATR = TradeBarConsolidator(timedelta(minutes=1))
                consolidator_ATR.DataConsolidated += lambda sender, bar: atr.Update(bar.EndTime, bar.High, bar.Low, bar.Close)
                self.algorithm.SubscriptionManager.AddConsolidator(symbol, consolidator_ATR)
                v.consolidators[symbol].append(consolidator_ATR)
                v.indicators[symbol].append(atr)

                emaShort = ExponentialMovingAverage(c.buy_parameter_ema_short_periods)
                consolidator_Short = TradeBarConsolidator(timedelta(minutes=1))
                consolidator_Short.DataConsolidated += lambda sender, bar: emaShort.Update(bar.EndTime, bar.Close)
                self.algorithm.SubscriptionManager.AddConsolidator(symbol, consolidator_Short)
                v.consolidators[symbol].append(consolidator_Short)
                v.indicators[symbol].append(emaShort)

                emaLong = ExponentialMovingAverage(c.buy_parameter_ema_long_periods)
                consolidator_Long = TradeBarConsolidator(timedelta(minutes=1))
                consolidator_Long.DataConsolidated += lambda sender, bar: emaLong.Update(bar.EndTime, bar.Close)
                self.algorithm.SubscriptionManager.AddConsolidator(symbol, consolidator_Long)
                v.consolidators[symbol].append(consolidator_Long)
                v.indicators[symbol].append(emaLong)

                macd = MovingAverageConvergenceDivergence(12, 26, 9, MovingAverageType.Wilders)
                consolidator_MACD = TradeBarConsolidator(timedelta(days=1))
                consolidator_MACD.DataConsolidated += lambda sender, bar: macd.Update(bar.EndTime, bar.Close)
                self.algorithm.SubscriptionManager.AddConsolidator(symbol, consolidator_MACD)
                v.consolidators[symbol].append(consolidator_MACD)
                v.indicators[symbol].append(macd)

                rsi = RelativeStrengthIndex(c.buy_parameter_rsi_periods)
                consolidator_RSI = TradeBarConsolidator(timedelta(days=1))
                consolidator_RSI.DataConsolidated += lambda sender, bar: rsi.Update(bar.EndTime, bar.Close)
                self.algorithm.SubscriptionManager.AddConsolidator(symbol, consolidator_RSI)
                v.consolidators[symbol].append(consolidator_RSI)
                v.indicators[symbol].append(rsi)

                sto = Stochastic(14, 3, 3)
                consolidator_STO = TradeBarConsolidator(timedelta(minutes=1))
                consolidator_STO.DataConsolidated += lambda sender, bar: sto.Update(bar.EndTime, bar.High, bar.Low, bar.Close)
                self.algorithm.SubscriptionManager.AddConsolidator(symbol, consolidator_STO)
                v.consolidators[symbol].append(consolidator_STO)
                v.indicators[symbol].append(sto)

            for security in changes.RemovedSecurities:
                symbol = security.Symbol
                if symbol in v.consolidators:
                    for consolidator in v.consolidators[symbol]:
                        self.algorithm.SubscriptionManager.RemoveConsolidator(symbol, consolidator)
                    del v.consolidators[symbol]  # Remove the entry from the dictionary

        except Exception as e:
            self.algorithm.algorithm.Error(f"Error on OnSecuritiesChanged: {str(e)}")


    def getIndicatorHistoryLength(self, indicator_name):
        # Define the history length for each indicator
        if indicator_name == "rsi":
            return c.buy_parameter_rsi_periods
        elif indicator_name == "atr":
            return c.buy_parameter_atr_periods
        elif indicator_name in ["emaShort", "emaLong"]:
            return max(c.buy_parameter_ema_short_periods, c.buy_parameter_ema_long_periods)
        elif indicator_name == "macd":
            return 26  # MACD slow period
        elif indicator_name == "sto":
            return c.buy_parameter_stochastic_rsi_periods
        else:
            return 0

    def getIndicatorResolution(self, indicator_name):
        # Define the resolution for each indicator
        if indicator_name in ["rsi", "macd"]:
            return Resolution.Daily
        else:
            return Resolution.Minute

# End OnSecuritiesChanged.py            