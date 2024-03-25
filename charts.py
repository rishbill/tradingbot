from datetime import datetime
import json
from AlgorithmImports import *
import variables as v
import config as c

def plotIndicators(self, symbol, indicators):

    # Prepare data dictionary
    data = {
        "EMA Short": indicators["emaShort"].Current.Value,
        "EMA Long": indicators["emaLong"].Current.Value,
        "MACD": indicators["macd"].Current.Value,
        "MACD Signal": indicators["macd"].Signal.Current.Value,
        "MACD Histogram": indicators["macd"].Current.Value - indicators["macd"].Signal.Current.Value,
        "RSI": indicators["rsi"].Current.Value,
        "Stochastic": indicators["sto"].Current.Value,
        "Time": self.Time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Convert data to JSON
    data_json = json.dumps(data)

    # Object Store key
    key = f"{symbol}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Save to Object Store
    if not self.ObjectStore.Save(key, data_json):
        self.Error(f"Failed to save data to Object Store: {key}")

def plotPositionSizes(self, symbol):

    # Calculate position sizes
    cash_available = round(self.Portfolio.Cash / v.buy_limit_price[symbol])
    kelly_criterion = round((self.Portfolio.Cash * v.kelly_criterion) / v.max_loss_risk_per_share[symbol])
    max_portfolio_per_trade = round((self.Portfolio.TotalPortfolioValue * c.buy_parameter_max_portfolio_percent_per_trade) / v.max_loss_risk_per_share[symbol])
    max_total_portfolio = round((self.Portfolio.TotalPortfolioValue * c.buy_parameter_max_total_portfolio_invested_percent) / v.max_loss_risk_per_share[symbol])

    # Prepare data dictionary for position sizes
    position_sizes_data = {
        "Cash Available Shares": cash_available,
        "Kelly Criterion Shares": kelly_criterion,
        "Per Trade Max Shares": max_portfolio_per_trade,
        "Portfolio Max Shares": max_total_portfolio,
        "Time": self.Time.strftime("%Y-%m-%d %H:%M:%S")
    }

    # Convert data to JSON
    position_sizes_data_json = json.dumps(position_sizes_data)

    # Object Store key for position sizes
    position_sizes_key = f"{symbol}-position-sizes-{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    # Save position sizes data to Object Store
    if not self.ObjectStore.Save(position_sizes_key, position_sizes_data_json):
        self.Error(f"Failed to save position sizes data to Object Store: {position_sizes_key}")
