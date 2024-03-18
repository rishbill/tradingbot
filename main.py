# Begin main.py

# QuantConnect Knowledge Base
# https://www.quantconnect.com/docs/v2/writing-algorithms
# Stocks = Symbols = Securities

from AlgorithmImports import *
from shouldBuy import *
from shouldSell import *
import config as c
from OnData import OnDataHandler
from OnOrderEvent import OnOrderEventHandler
from OnSecuritiesChanged import OnSecuritiesChangedHandler
import numpy as np
from sectorAnalysis import sectorAnalysis

class CodysAdvancedStrategy(QCAlgorithm):
    def Initialize(self):
    # Main function for algorithm

        # Initialize Variables
        c.SetStartDate(self)
        c.SetCash(self)
        c.SetWarmUp(self)
        c.SetBrokerageModel(self)
        self.EnableAutomaticIndicatorWarmUp = True

        self.onDataHandler = OnDataHandler(self)
        self.onOrderEventHandler = OnOrderEventHandler(self)
        self.onSecuritiesChangedHandler = OnSecuritiesChangedHandler(self)
        v.stock_counts_per_sector = sectorAnalysis.calculateStockCountsPerSector()
        total_invested_stocks = sum(v.stock_counts_per_sector.values())

        self.Debug("Basic parameters:")
        self.Debug(f"---- Initial Capital -------------------------- ${self.Portfolio.Cash}")
        self.Debug(f"---- Start Date ------------------------------- {self.StartDate}")
        self.Debug(f"---- End Date --------------------------------- {self.EndDate}")
        self.Debug(f"---- Warm Up ---------------------------------- {c.warmup_period} Days")
        self.Debug("Indicator Variables:")
        self.Debug("---- Initialized Indicator Variables: self.ema_short, self.ema_long, self.atr, self.stochastic_rsi")
        self.Debug("News and Sentiment Variables:")
        self.Debug("---- Initialized News and Sentiment Variables: c.news_feed")
        self.Debug("Portfolio Summary:")
        self.Debug(f"---- Portfolio Value ----------------------------- ${self.Portfolio.TotalPortfolioValue}")

        if total_invested_stocks == 0:
            self.Debug("---- No invested stocks in portfolio")
        else:
            for sector, count in v.stock_counts_per_sector.items():
                sector_portfolio_value = self.CalculateSectorPortfolioValue(sector)
                percentage_of_portfolio = (sector_portfolio_value / self.Portfolio.TotalPortfolioValue)
                self.Debug(f"---- Sector: {sector}, Count: {count}, Value: ${sector_portfolio_value}, % of Portfolio: {percentage_of_portfolio:.2f}%")

        # Set Universe settings
        self.UniverseSettings.Resolution = Resolution.Minute

        # Define UniverseFilter as a closure
        def UniverseFilter(fundamental: List[Fundamental]) -> List[Symbol]:
            return self.SelectSymbols(fundamental)

        # Add Universe
        self.AddUniverse(UniverseFilter)

    def filterUniverseStocks(self, fundamental: List[Fundamental]) -> List[Symbol]:
    # Returns a filtered_stocks list of stocks,  dynamically re-filtered_stocks daily   
        v.max_stock_price = self.Portfolio.TotalPortfolioValue * c.stock_filter_parameter_max_stock_price_portfolio_percent 
            # Limit max stock price to x% of portfolio size, for affordability.
        
        self.Debug("Universe filter variables:")
        self.Debug(f"------- Stock Price Range ------------------------- ${c.stock_filter_parameter_min_price} - ${v.max_stock_price}")
        self.Debug(f"------- P/E Ratio Range --------------------------- {c.stock_filter_parameter_min_pe_ratio} to {c.stock_filter_parameter_max_pe_ratio}")
        self.Debug(f"------- Min Revenue Growth ------------------------ {c.stock_filter_parameter_min_revenue_growth_percent}")
        self.Debug(f"Filtering Universe...")
            
        try:
            # Filtering stocks based on fundamental criteria
            filtered_stocks = [
                f for f in fundamental 
                if f.HasFundamentalData
                and c.stock_filter_parameter_min_price <= f.Price < v.max_stock_price
                and c.stock_filter_parameter_min_pe_ratio < f.ValuationRatios.PERatio < c.stock_filter_parameter_max_pe_ratio
                and f.OperationRatios.RevenueGrowth.OneYear > c.stock_filter_parameter_min_revenue_growth_percent
                and not np.isnan(f.ValuationRatios.PERatio)
                and not np.isnan(f.OperationRatios.RevenueGrowth.OneYear)
                and not np.isnan(f.DollarVolume)
                and not np.isnan(f.MarketCap)
                and f.ValuationRatios.PERatio != 0
                and f.OperationRatios.RevenueGrowth.OneYear != 0
                and f.DollarVolume != 0
                and f.MarketCap != 0
            ]

            # Sorting filtered stocks first by Dollar Volume, then by P/E Ratio
            stocks_sorted_by_dollar_volume = sorted(filtered_stocks, key=lambda f: f.DollarVolume, reverse=True)[:10]
            stocks_sorted_by_pe_ratio = sorted(stocks_sorted_by_dollar_volume, key=lambda f: f.ValuationRatios.PERatio, reverse=False)[:10]
            
            if v.warmup_counter >= c.warmup_period + 1:
                try:
                    v.active_stock_symbols = [(f.Symbol, f.Price, f.DollarVolume, f.ValuationRatios.PERatio, f.OperationRatios.RevenueGrowth.OneYear, f.MarketCap, f.AssetClassification.MorningstarSectorCode, f.AssetClassification.MorningstarIndustryCode, f.CompanyReference.ShortName) for f in stocks_sorted_by_pe_ratio]
                except Exception as e:
                    self.Debug(f"Error accessing fundamentals data: {str(e)}")
            else:
                self.Debug(f"Warming Up... ({v.warmup_counter} \ 100 Days)")
            return [f.Symbol for f in stocks_sorted_by_pe_ratio]
        except Exception as e:
            self.Error(f"---- Error # Universe Filter on UniverseFilter: {str(e)}")        

    def OnData(self, data):
        self.onDataHandler.OnData(data)

    def OnOrderEvent(self, orderEvent):
        self.onOrderEventHandler.OnOrderEvent(orderEvent)

    def OnSecuritiesChanged(self, changes):
        self.onSecuritiesChangedHandler.OnSecuritiesChanged(changes)

    def OnWarmupFinished(self):
        self.Debug(f"Warmup Finished. Universe includes {len(v.active_stock_symbols)} symbols.")
        for symbol, price, dollar_volume, pe_ratio, revenue_growth, market_cap, sector, industry, ShortName in v.active_stock_symbols:
            self.Debug(f"-------- {symbol}, Price: ${price}, Dollar Volume: ${dollar_volume}, P/E Ratio:{pe_ratio}, Revenue Growth: {revenue_growth}%, MarketCap: {market_cap}, Sector: {sector}, Industry: {industry} - {ShortName}")

# End main.py