# Begin main.py

# QuantConnect Knowledge Base
# https://www.quantconnect.com/docs/v2/writing-algorithms
# Symbols = Symbols = Securities

from AlgorithmImports import *
import variables as v
import config as c
from AddUniverse import AddUniverseHandler
from OnSecuritiesChanged import OnSecuritiesChangedHandler
from OnWarmupFinished import OnWarmupFinishedHandler
from OnData import OnDataHandler
from OnOrderEvent import OnOrderEventHandler

class CodysAdvancedStrategy(QCAlgorithm):
    def Initialize(self):
    # Main function for algorithm
        
        c.SetStartDate(self)
            # Set Start Date defined in config.py

        c.SetEndDate(self)
            # Set End Date defined in config.py

        c.SetWarmUp(self)
            # Set Warm Up Period defined in config.py

        c.SetCash(self)
            # Set Cash defined in config.py
        
        c.SetBrokerageModel(self)
            # Set Brokerage Model defined in config.py

        self.SetBenchmark("SPY")
            # Adds a benchamrk chart for performance comparison, commonly SPY        

        self.Settings.FreePortfolioValuePercentage = (
            1 - c.buy_parameter_max_total_portfolio_invested_percent
            if c.buy_condition_max_total_portfolio_invested_percent
            else 0.03
        ) # Set the minimum portfolio value to place trades. If not set use 3%.

        self.AddUniverseHandler = AddUniverseHandler(self)
            # Define the handler for AddUniverse.py

        self.onSecuritiesChangedHandler = OnSecuritiesChangedHandler(self)
            # Define the event handler for OnSecuritiesChanged.py
        
        self.onWarmupFinishedHandler = OnWarmupFinishedHandler(self)
            # Define the event handler for OnSecuritiesChanged.py

        self.onDataHandler = OnDataHandler(self)
            # Define the event handler for OnData.py

        self.onOrderEventHandler = OnOrderEventHandler(self)
            # Define the event handler for OnOrderEvent.py

    # Define the handler for AddUniverse.py
    def AddUniverse(self):
        self.AddUniverseHandler.AddUniverse()

    # Define the event handler for OnSecuritiesChanged.py
    def OnSecuritiesChanged(self, changes):
        self.onSecuritiesChangedHandler.OnSecuritiesChanged(changes)

    # Define the event handler for OnWarmupFinished.py
    def OnWarmupFinished(self):
        self.onWarmupFinishedHandler.OnWarmupFinished()

    # Define the event handler for OnData.py
    def OnData(self, data):
        self.onDataHandler.OnData(data)

    # Define the event handler for OnOrderEvent.py
    def OnOrderEvent(self, orderEvent):
        self.onOrderEventHandler.OnOrderEvent(orderEvent)

    def initializeIndicators(self, symbol):
        self.EnableAutomaticIndicatorWarmUp = True
        # Enable auto warmup for indicators where possible.
        # Most indicators are manually updated with consolidators.

        # Initialize indicators
        self.Debug(f"Initializing indicators for {symbol}...")
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

# End main.py