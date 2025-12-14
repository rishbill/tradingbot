# AddUniverse.py

# Universe Settings:
#   "Universe" is the selection of symbols \ stocks OnData will receive Data slices for.
#   In other words, its the collection of stocks to be traded.
#   Universe can be static (un-changing) or dynamic (updated over time based on filters).

from AlgorithmImports import *
import config as c
import variables as v
import numpy as np

class AddUniverseHandler:
    def __init__(self, algorithm):
        self.algorithm = algorithm
    
    def AddUniverse(self):

        # If c.symbol_filter_condition_static_universe == True,
        # create a Static Symbol Universe.
        self.algorithm.Debug(f"Creating Universe...")
        self.algorithm.Debug(f"---- Static Universe (c.symbol_filter_condition_static_universe) = {c.symbol_filter_condition_static_universe}")
        if c.symbol_filter_condition_static_universe == True: 
            for x in c.symbol_filter_parameter_static_universe:
                self.algorithm.AddEquity(x.Symbol, c.finest_resolution)
                self.algorithm.initializeIndicators(x.Symbol)
                self.algorithm.Debug(f"-------- Static Universe Updated: +{x.Symbol}")

        elif not c.symbol_filter_condition_static_universe: 
            # If c.symbol_filter_condition_static_universe not == True,
            # create a Dynamic Symbol Universe.
            
            self.algorithm.Debug(f"---- Extended Market Hours (c.symbol_filter_condition_extended_market_hours) = {c.symbol_filter_condition_extended_market_hours}")
            self.algorithm.UniverseSettings.ExtendedMarketHours = (
                c.symbol_filter_condition_extended_market_hours
            ) # Enable or disable Extended Market Hours for the Universe.

            self.algorithm.Debug(f"---- Finest Resolution (c.finest_resolution) = {c.finest_resolution}")
            self.algorithm.UniverseSettings.Resolution = c.finest_resolution
                # Sets Universe resolution. OnData will run and receive a 
                # data slice once per minute 
                # with data for each symbol in the dynamic universe.

            self.algorithm.AddUniverse(lambda fundamental: self.algorithm.filterAndSortUniverse(fundamental))
                # Run the built-in AddUniverse based on defined filter filterAndSortUniverse.            
    
    def filterAndSortUniverse(self, fundamental: List[Fundamental]) -> List[Symbol]:
        # Filter and sort a dynamic universe based on various criteria
        
        v.max_symbol_price = (
            self.algorithm.Portfolio.TotalPortfolioValue 
            * c.symbol_filter_parameter_max_symbol_price_portfolio_percent
            if c.symbol_filter_condition_max_symbol_price_portfolio_percent 
            else 0.95 * self.algorithm.Portfolio.TotalPortfolioValue
        ) # Set max price of symbols in the universe to what's defined in config.py, 
          # if not then 95%.

        self.algorithm.Debug(f"---- Symbol Price Range --------------------------- ${c.symbol_filter_parameter_min_price} - ${v.max_symbol_price}")
        self.algorithm.Debug(f"---- P/E Ratio Range ------------------------------ {c.symbol_filter_parameter_min_pe_ratio} to {c.symbol_filter_parameter_max_pe_ratio}")
        self.algorithm.Debug(f"---- Min Annual Revenue Growth % ------------------ {c.symbol_filter_parameter_min_revenue_growth_percent}")        
        self.algorithm.Debug(f"---- Extended Market Hours Enabled ---------------- {c.symbol_filter_condition_extended_market_hours}")        

        # Filter symbols by fundamentals
        try:
            filtered_symbols = [
                f for f in fundamental
                if (
                    f.HasFundamentalData
                    and not np.isnan(f.MarketCap) and f.MarketCap > 0
                    and not np.isnan(f.DollarVolume) and f.DollarVolume > 0
                    and f.Price <= v.max_symbol_price
                    and (not c.symbol_filter_condition_blacklist 
                         or f.Symbol not in c.symbol_filter_parameter_blacklist)
                    and (not c.symbol_filter_condition_min_price or 
                         c.symbol_filter_parameter_min_price <= f.Price)
                    and (not c.symbol_filter_condition_min_pe_ratio 
                         or (c.symbol_filter_parameter_min_pe_ratio 
                             < f.ValuationRatios.PERatio 
                             and not np.isnan(f.ValuationRatios.PERatio) 
                             and f.ValuationRatios.PERatio != 0))
                    and (not c.symbol_filter_condition_max_pe_ratio 
                         or (c.symbol_filter_parameter_max_pe_ratio 
                             > f.ValuationRatios.PERatio 
                             and not np.isnan(f.ValuationRatios.PERatio) 
                             and f.ValuationRatios.PERatio != 0))
                    and (not c.symbol_filter_condition_min_revenue_growth_percent 
                         or (c.symbol_filter_parameter_min_revenue_growth_percent 
                             < f.OperationRatios.RevenueGrowth.OneYear 
                             and not np.isnan(f.OperationRatios.RevenueGrowth.OneYear) 
                             and f.OperationRatios.RevenueGrowth.OneYear != 0))
                )
            ]

            # Sort symbols by Dollar Volume: Top 100
            symbols_sorted_by_dollar_volume = sorted(
                filtered_symbols, 
                key=lambda f: f.DollarVolume, 
                reverse=True)[:100]

            # Sort symbols by Price-to-Earnings Ratio: Top 50
            symbols_sorted_by_pe_ratio = sorted(
                symbols_sorted_by_dollar_volume, 
                key=lambda f: f.ValuationRatios.PERatio, 
                reverse=False)[:50]

            # Sort symbols by market cap: Bottom 10
            symbols_sorted_by_market_cap = sorted(
                symbols_sorted_by_pe_ratio, 
                key=lambda f: f.MarketCap, 
                reverse=False)[:10]
            return [f.Symbol for f in symbols_sorted_by_market_cap]
         
        except Exception as e:
            self.algorithm.Error(f"---- Error on filterAndSortUniverse: {str(e)}")

# End AddUniverse.py