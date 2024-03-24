from AlgorithmImports import *
import config as c
import variables as v

class sectorAnalysis:
# Functions for getting sector info
    
    def getUniquePortfolioSectors(self):
    # Gets the number of sectors in the portfolio.
        try:
            for symbol in self.Portfolio.Keys: # Iterate over all symbols in portfolio
                if self.Portfolio[symbol].Invested: # If the portfolio is invested in this symbol
                    v.symbol_sector[symbol] = symbol.AssetClassification.MorningstarSectorCode # Get the sector for this symbol
                    v.unique_portfolio_sectors.add(v.symbol_sector[symbol]) # Add sector to the distinct list
            return v.unique_portfolio_sectors # Return the final list of distinct portfolio sectors
        
        except Exception as e:
            self.Error(f"Error on getUniquePortfolioSectors: {str(e)}")
            return

    def calculatePortfolioValueForSector (self, sector):
    # Gets the total portfolio value for a provided sector 
        try:    
            for symbol in self.Portfolio.Keys: # Iterate over all symbols in portfolio
                if self.Portfolio[symbol].Invested and self.Securities[symbol].Fundamentals.AssetClassification.MorningstarSectorCode == sector: # If the portfolio is invested in this symbol, and the sector for this symbol matches the sector being checked
                    v.sector_portfolio_value[sector] += self.Portfolio[symbol].HoldingsValue # Adds the value of portfolio holdings for this symbol to the v.sector_portfolio_value[sector]
            return v.sector_portfolio_value[sector] # Returns the total portfolio value for the provided sector
        
        except Exception as e:
            self.Error(f"Error on calculatePortfolioValueForSector : {str(e)}")
            return   

    def calculateSymbolCountsPerSector(self):
    # Returns a list of symbol counts for each sector in the current portfolio.
        try:
            for symbol in self.Portfolio.Keys: # Iterate over all symbols in portfolio
                if self.Portfolio[symbol].Invested: # If the portfolio is invested in this symbol
                    v.symbol_sector[symbol] = self.Securities[symbol].Fundamentals.AssetClassification.MorningstarSectorCode # Get the sector for this symbol
                    if v.symbol_sector[symbol]: # If sector was returned
                        v.symbol_counts_per_sector[v.symbol_sector[symbol]] = v.symbol_counts_per_sector.get(v.symbol_sector[symbol], 0) + 1 # Increment the number of symbols for this sector 
            return v.symbol_counts_per_sector # Return the  list of symbol counts per sector
        
        except Exception as e:
            self.Error(f"Error on calculateSymbolCountsPerSector: {str(e)}")
            return
