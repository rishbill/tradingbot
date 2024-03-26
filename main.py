# Begin main.py

# QuantConnect Knowledge Base
# https://www.quantconnect.com/docs/v2/writing-algorithms
# Symbols = Symbols = Securities

from AlgorithmImports import *
import variables as v
import config as c
from OnData import OnDataHandler
from OnOrderEvent import OnOrderEventHandler
from OnSecuritiesChanged import OnSecuritiesChangedHandler
import numpy as np

class CodysAdvancedStrategy(QCAlgorithm):
    def Initialize(self):
    # Main function for algorithm
        
        c.SetStartDate(self)
            # Set Start Date defined in config.py

        c.SetEndDate(self)
            # Set End Date defined in config.py

        c.SetCash(self)
            # Set Cash defined in config.py
        
        c.SetBrokerageModel(self)
            # Set Brokerage Model defined in config.py

        self.SetBenchmark("SPY")

        self.Settings.FreePortfolioValuePercentage = (
            1 - c.buy_parameter_max_total_portfolio_invested_percent
            if c.buy_condition_max_total_portfolio_invested_percent
            else 0.03
        ) # Set the minimum portfolio value to place trades. If not set use 3%.

        self.EnableAutomaticIndicatorWarmUp = True
            # Enable auto warmup for indicators where possible.
            # Most indicators are manually updated with consolidators.

        self.onDataHandler = OnDataHandler(self)
            # Define the event handler for OnData.py

        self.onOrderEventHandler = OnOrderEventHandler(self)
            # Define the event handler for OnOrderEvent.py

        self.onSecuritiesChangedHandler = OnSecuritiesChangedHandler(self)
            # Define the event handler for OnSecuritiesChanged.py

        v.max_symbol_price = (
            self.Portfolio.TotalPortfolioValue * c.symbol_filter_parameter_max_symbol_price_portfolio_percent
            if c.symbol_filter_condition_max_symbol_price_portfolio_percent 
            else 0.95 * self.Portfolio.TotalPortfolioValue
        ) # Set max price of symbols in the universe to what's defined in config.py, if not then 95%.

        # Debug messages
        self.Debug("Basic parameters:")
        self.Debug(f"---- Initial Capital ------------------------------ ${self.Portfolio.Cash}")
        self.Debug(f"---- Start Date ----------------------------------- {self.StartDate}")
        self.Debug(f"---- End Date ------------------------------------- {self.EndDate}")
        self.Debug(f"---- Warm Up Period ------------------------------- {c.warmup_period}")
        self.Debug(f"---- Resolution ----------------------------------- {c.finest_resolution}")

        # Universe Settings:
        #   "Universe" is the selection of symbols \ stocks OnData will receive Data slices for.
        #   In other words, its the collection of stocks to be traded.
        #   Universe can be static (un-changing) or dynamic (updated over time based on filters).

        self.UniverseSettings.ExtendedMarketHours = c.symbol_filter_condition_extended_market_hours
            # Enable or disable Extended Market Hours for the Universe.

        if c.symbol_filter_condition_static_universe == True: 
            # If c.symbol_filter_condition_static_universe == True,
            # create a Static Symbol Universe.
            for symbol in c.symbol_filter_parameter_static_universe:
                self.AddEquity(symbol, c.finest_resolution)
                self.initializeIndicators(symbol)
                self.Debug(f"Static Universe Updated: +{symbol}")

        elif not c.symbol_filter_condition_static_universe: 
            # If c.symbol_filter_condition_static_universe not == True,
            # create a Dynamic Symbol Universe.
            
            self.Debug("Universe Filters:")
            self.Debug(f"---- Symbol Price Range --------------------------- ${c.symbol_filter_parameter_min_price} - ${v.max_symbol_price}")
            self.Debug(f"---- P/E Ratio Range ------------------------------ {c.symbol_filter_parameter_min_pe_ratio} to {c.symbol_filter_parameter_max_pe_ratio}")
            self.Debug(f"---- Min Annual Revenue Growth % ------------------ {c.symbol_filter_parameter_min_revenue_growth_percent}")
            self.Debug(f"---- Filtering Universe...")

            self.UniverseSettings.Resolution = c.finest_resolution
                # Sets Universe resolution. OnData will run and receive a data slice once per minute 
                # with data for each symbol in the dynamic universe.

            self.AddUniverse(lambda fundamental: self.filterUniverseSymbols(fundamental))
                # Run the built-in AddUniverse based on defined filter filterUniverseSymbols.            

        c.SetWarmUp(self)
            # Set Warm Up Period defined in config.py

    def filterUniverseSymbols(self, fundamental: List[Fundamental]) -> List[Symbol]:
    # Defining the filter criteria.
        try:
            filtered_symbols = [
                f for f in fundamental
                if (
                    f.HasFundamentalData
                    and not np.isnan(f.MarketCap) and f.MarketCap != 0
                    and not np.isnan(f.DollarVolume) and f.DollarVolume != 0
                    and f.Price < v.max_symbol_price
                    and (not c.symbol_filter_condition_blacklist or f.Symbol not in c.symbol_filter_parameter_blacklist)
                    and (not c.symbol_filter_condition_min_price or c.symbol_filter_parameter_min_price <= f.Price)
                    and (not c.symbol_filter_condition_min_pe_ratio or (c.symbol_filter_parameter_min_pe_ratio < f.ValuationRatios.PERatio and not np.isnan(f.ValuationRatios.PERatio) and f.ValuationRatios.PERatio != 0))
                    and (not c.symbol_filter_condition_max_pe_ratio or (c.symbol_filter_parameter_max_pe_ratio > f.ValuationRatios.PERatio and not np.isnan(f.ValuationRatios.PERatio) and f.ValuationRatios.PERatio != 0))
                    and (not c.symbol_filter_condition_min_revenue_growth_percent or (c.symbol_filter_parameter_min_revenue_growth_percent < f.OperationRatios.RevenueGrowth.OneYear and not np.isnan(f.OperationRatios.RevenueGrowth.OneYear) and f.OperationRatios.RevenueGrowth.OneYear != 0))
                )
            ]

            # Sorting filtered symbols first by Dollar Volume, then by P/E Ratio
            symbols_sorted_by_dollar_volume = sorted(filtered_symbols, key=lambda f: f.DollarVolume, reverse=True)[:10]
            symbols_sorted_by_pe_ratio = sorted(symbols_sorted_by_dollar_volume, key=lambda f: f.ValuationRatios.PERatio, reverse=False)[:10]
            return [f.Symbol for f in symbols_sorted_by_pe_ratio]
         
        except Exception as e:
            self.Error(f"---- Error # Universe Filter on UniverseFilter: {str(e)}")        

    # Define the event handler for OnData.py
    def OnData(self, data):
        self.onDataHandler.OnData(data)

    # Define the event handler for OnOrderEvent.py
    def OnOrderEvent(self, orderEvent):
        self.onOrderEventHandler.OnOrderEvent(orderEvent)

    # Define the event handler for OnSecuritiesChanged.py
    def OnSecuritiesChanged(self, changes):
        self.onSecuritiesChangedHandler.OnSecuritiesChanged(changes)

    def initializeIndicators(self, symbol):
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

    def OnWarmupFinished(self):
        self.Debug(f"-------- Universe filtering and warmup complete. Symbol count: {len(self.ActiveSecurities.Keys)}")
        for symbol in self.ActiveSecurities.Keys:
            # Retrieve the symbol data using the symbol
            symbol_data = self.Securities[symbol].Fundamentals
            
            # Extract the required attributes from the symbol data
            price = symbol_data.Price
            dollar_volume = symbol_data.DollarVolume
            pe_ratio = symbol_data.ValuationRatios.PERatio
            revenue_growth = symbol_data.OperationRatios.RevenueGrowth.OneYear
            market_cap = symbol_data.MarketCap
            sector = symbol_data.AssetClassification.MorningstarSectorCode
            industry = symbol_data.AssetClassification.MorningstarIndustryCode
            short_name = symbol_data.CompanyReference.ShortName
            
            self.Debug(f"-------- {symbol}, Price: ${price}, Dollar Volume: ${dollar_volume}, P/E Ratio:{pe_ratio}, Revenue Growth: {revenue_growth}%, MarketCap: {market_cap}, Sector: {sector}, Industry: {industry} - {short_name}")

# End main.py