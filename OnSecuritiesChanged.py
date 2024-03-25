# Begin OnSecuritiesChanged.py
from AlgorithmImports import *
import config as c
import variables as v
from datetime import timedelta

class OnSecuritiesChangedHandler:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def OnSecuritiesChanged(self, changes):
    # Runs whenever a symbol is added to the static or dynamic Universe.

        try:
            for security in changes.AddedSecurities:
                symbol = security.Symbol
                if symbol not in v.indicators:
                    self.initializeIndicators(symbol)
                    for indicator_key, indicator in v.indicators[symbol].items():
                        self.registerConsolidator(symbol, c.finest_resolution, indicator, self.updateIndicator, indicator_key)

            for security in changes.RemovedSecurities:
                symbol = security.Symbol
                self.removeConsolidators(symbol)

        except Exception as e:
            self.algorithm.Error(f"Error on OnSecuritiesChanged: {str(e)}")

    def updateIndicator(self, bar, indicator, indicator_key):
        try:
            if bar is not None:
                try: 
                    # Determine if the indicator expects IndicatorDataPoint or TradeBar
                    if isinstance(indicator, IndicatorBase[IndicatorDataPoint]):
                        # Create an IndicatorDataPoint for these indicators
                        dataPoint = IndicatorDataPoint(bar.EndTime, bar.Close)
                        indicator.Update(dataPoint)
                    else:
                        indicator.Update(bar)
                except Exception as e:
                    self.algorithm.Error(f"Error on OnSecuritiesChanged: {str(e)}")

                if self.algorithm.IsWarmingUp:
                    if indicator_key not in v.indicator_warmup_counter:
                        v.indicator_warmup_counter[indicator_key] = 0
                    v.indicator_warmup_counter[indicator_key] += 1
                    self.algorithm.Debug(f"{bar.EndTime} - {bar.Symbol} - Warming up IndicatorDataPoint {indicator_key}: {indicator.Current.Value} - Received {v.indicator_warmup_counter[indicator_key]} / {c.warmup_period} data points...")
                else:
                    v.indicator_warmup_counter[indicator_key] += 1
                    self.algorithm.Debug(f"{bar.EndTime} - {bar.Symbol} - Updated IndicatorDataPoint {indicator_key}: {indicator.Current.Value} - Received {v.indicator_warmup_counter[indicator_key]} / {c.warmup_period} data points")
                                            
            else:
                self.algorithm.Debug(f"Skipping {indicator_key} update for {bar.Symbol} at {bar.EndTime} due to missing data.")
        
        except Exception as e:
            self.algorithm.Error(f"Error on OnSecuritiesChanged: {str(e)}")
            
    def initializeIndicators(self, symbol):
        # Initialize indicators
        self.algorithm.Debug(f"Initializing indicators for {symbol}...")
        atr = AverageTrueRange(c.buy_parameter_atr_periods, MovingAverageType.Wilders)
        emaShort = ExponentialMovingAverage(c.buy_parameter_ema_short_periods)
        emaLong = ExponentialMovingAverage(c.buy_parameter_ema_long_periods)
        macd = MovingAverageConvergenceDivergence(12, 26, 9, MovingAverageType.Wilders)
        rsi = RelativeStrengthIndex(c.buy_parameter_rsi_periods)
        sto = Stochastic(14, 3, 3)

        # Store indicators
        v.indicators[symbol] = {
            'atr': atr,
            'emaShort': emaShort,
            'emaLong': emaLong,
            'macd': macd,
            'rsi': rsi,
            'sto': sto
        }

    def registerConsolidator(self, symbol, resolution, indicator, updateMethod, indicator_key):
        consolidator = self.algorithm.ResolveConsolidator(symbol, resolution)
        consolidator.DataConsolidated += lambda sender, bar: updateMethod(bar, indicator, indicator_key)
        self.algorithm.SubscriptionManager.AddConsolidator(symbol, consolidator)
        if symbol not in v.consolidators:
            v.consolidators[symbol] = []
        v.consolidators[symbol].append(consolidator)

    def removeConsolidators(self, symbol):
        if symbol in v.consolidators:
            for consolidator in v.consolidators[symbol]:
                self.algorithm.SubscriptionManager.RemoveConsolidator(symbol, consolidator)
            del v.consolidators[symbol]

# End OnSecuritiesChanged.py