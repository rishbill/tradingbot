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
            
        except Exception as e:
            self.algorithm.Error(f"Error on OnSecuritiesChanged: {str(e)}")

# End OnSecuritiesChanged.py            