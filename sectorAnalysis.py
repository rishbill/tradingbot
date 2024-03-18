from AlgorithmImports import *
import config as c
import variables as v

class sectorAnalysis:
# Functions for getting sector info
    
    def getUniquePortfolioSectors(self):
    # Gets the number of sectors in the portfolio.
        try:
            for symbol in self.Portfolio.Keys: # Iterate over all stocks in portfolio
                if self.Portfolio[symbol].Invested: # If the portfolio is invested in this stock
                    v.symbol_sector[symbol] = symbol.AssetClassification.MorningstarSectorCode # Get the sector for this stock
                    v.unique_portfolio_sectors.add(v.symbol_sector[symbol]) # Add sector to the distinct list
            return v.unique_portfolio_sectors # Return the final list of distinct portfolio sectors
        except Exception as e:
            self.Error(f"Error on getUniquePortfolioSectors: {str(e)}")
            return

    def calculatePortfolioValueForSector (self, sector):
    # Gets the total portfolio value for a provided sector 
        try:    
            for symbol in self.Portfolio.Keys: # Iterate over all stocks in portfolio
                if self.Portfolio[symbol].Invested and symbol.AssetClassification.MorningstarSectorCode == sector: # If the portfolio is invested in this stock, and the sector for this stock matches the sector being checked
                    v.sector_portfolio_value[sector] += self.Portfolio[symbol].HoldingsValue # Adds the value of portfolio holdings for this stock to the v.sector_portfolio_value[sector]
            return v.sector_portfolio_value[sector] # Returns the total portfolio value for the provided sector
        except Exception as e:
            self.Error(f"Error on calculatePortfolioValueForSector : {str(e)}")
            return   

    def calculateStockCountsPerSector(self):
    # Returns a list of stock counts for each sector in the current portfolio.
        try:
            for symbol in self.Portfolio.Keys: # Iterate over all stocks in portfolio
                if self.Portfolio[symbol].Invested: # If the portfolio is invested in this stock
                    v.symbol_sector[symbol] = symbol.AssetClassification.MorningstarSectorCode # Get the sector for this stock
                    if v.symbol_sector[symbol]: # If sector was returned
                        v.stock_counts_per_sector[v.symbol_sector[symbol]] = v.stock_counts_per_sector.get(v.symbol_sector[symbol], 0) + 1 # Increment the number of stocks for this sector 
            return v.stock_counts_per_sector # Return the  list of stock counts per sector
        except Exception as e:
            self.Error(f"Error on calculateStockCountsPerSector: {str(e)}")
            return
