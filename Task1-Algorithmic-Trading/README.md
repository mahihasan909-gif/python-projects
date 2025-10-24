# Algorithmic Trading Adventure 🚀

An advanced algorithmic trading system implementing the Golden Cross strategy with a $5000 budget. This project demonstrates class-based design, financial data analysis, and automated trading decisions using Python.

## 🎯 Project Overview

Alex, a budding programmer and finance enthusiast, embarks on an algorithmic trading adventure with a budget of $5000. The mission is to develop a tool that leverages Python to make informed decisions in the stock market using a class-based approach for flexibility.

## ✨ Features

- **Golden Cross Strategy**: Detects bullish trends when 50-day MA crosses above 200-day MA
- **Automated Trading**: Buys on golden cross signals, sells on death cross signals
- **Portfolio Management**: Manages $5000 budget efficiently with maximum share calculations
- **Risk Management**: Force closes positions on the last trading day
- **Performance Analysis**: Calculates profits/losses and compares with buy-and-hold strategy
- **Multi-Stock Testing**: Test strategy across different stocks and time periods

## 📊 Strategy Details

### Golden Cross Strategy
1. **Moving Averages**: Calculates 50-day and 200-day moving averages
2. **Golden Cross**: Buy signal when 50-day MA crosses above 200-day MA
3. **Death Cross**: Sell signal when 50-day MA crosses below 200-day MA
4. **Position Management**: Only one position active at a time
5. **Budget Control**: Maximizes shares within $5000 budget

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Internet connection for downloading stock data

### Installation

1. **Clone or download the project**
   ```bash
   cd Task1-Algorithmic-Trading
   ```

2. **Install required packages**
   ```bash
   pip install -r requirements.txt
   ```

### Quick Start

#### Basic Usage
```python
from trading_bot import AlgorithmicTrader

# Create a trader instance
trader = AlgorithmicTrader("AAPL", "2020-01-01", "2023-12-31", budget=5000)

# Run the complete strategy
results = trader.run_strategy()

# View performance
print(f"Total Return: ${results['total_return']:.2f}")
print(f"Return Percentage: {results['return_percentage']:.2f}%")
```

#### Run Demo with Multiple Stocks
```bash
python demo.py
```

## 📁 Project Structure

```
Task1-Algorithmic-Trading/
├── trading_bot.py          # Main AlgorithmicTrader class
├── demo.py                 # Demo script with multiple examples
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## 🔧 Class Methods

### AlgorithmicTrader Class

```python
class AlgorithmicTrader:
    def __init__(self, symbol, from_date, to_date, budget=5000)
    def download_data()                    # Download historical data
    def clean_data()                       # Remove duplicates, handle NaN
    def calculate_moving_averages()        # Calculate 50-day and 200-day MA
    def execute_trades()                   # Execute golden cross strategy
    def calculate_performance()            # Calculate profits/losses
    def show_trade_history()              # Display all trades
    def run_strategy()                    # Execute complete strategy
```

## 📈 Example Output

```
🚀 Starting Algorithmic Trading Adventure!
Symbol: AAPL | Budget: $5,000.00
Period: 2020-01-01 to 2023-12-31
============================================================

Downloading data for AAPL from 2020-01-01 to 2023-12-31...
Downloaded 1008 data points

Data cleaning complete:
  - Removed 0 duplicate entries
  - Forward filled 0 NaN values
  - Final dataset: 1008 rows

Moving averages calculated:
  - 50-day MA: 959 valid values
  - 200-day MA: 809 valid values
  - Golden crosses detected: 3
  - Death crosses detected: 2

2020-08-18: BUY  44 shares at $114.42 = $5,034.48
  Cash remaining: $-34.48

2022-01-24: SELL 44 shares at $161.62 = $7,111.28
  Cash after sale: $7,076.80

============================================================
TRADING PERFORMANCE SUMMARY
============================================================
Initial Budget:        $5,000.00
Final Value:           $7,076.80
Total Return:          $2,076.80
Return Percentage:     41.54%
Number of Trades:      2

Buy & Hold Comparison:
Buy & Hold Value:      $6,847.23
Buy & Hold Return:     $1,847.23 (36.94%)
Strategy vs Buy&Hold:  $229.57

🎉 Congratulations! Your strategy was profitable!
```

## 🧪 Testing Different Scenarios

### Test Multiple Stocks
```python
stocks = ["AAPL", "MSFT", "GOOGL", "TSLA", "AMZN"]
for symbol in stocks:
    trader = AlgorithmicTrader(symbol, "2020-01-01", "2023-12-31")
    results = trader.run_strategy()
```

### Test Different Time Periods
```python
periods = [
    ("2018-01-01", "2020-12-31", "Pre-COVID"),
    ("2020-01-01", "2022-12-31", "COVID Era"),
    ("2021-01-01", "2023-12-31", "Recent Years")
]
```

## 🎯 Key Features Implemented

✅ **Class-based Design**: Flexible and reusable `AlgorithmicTrader` class  
✅ **Data Download**: Uses `yfinance` for historical market data  
✅ **Data Cleaning**: Handles duplicates and NaN values with forward filling  
✅ **Moving Averages**: Calculates 50-day and 200-day moving averages  
✅ **Golden Cross Detection**: Identifies bullish trend signals  
✅ **Budget Management**: Maximizes shares within $5000 budget constraint  
✅ **Position Management**: Prevents multiple simultaneous positions  
✅ **Force Close**: Automatically closes positions on the last trading day  
✅ **Performance Analysis**: Comprehensive profit/loss calculations  
✅ **Buy & Hold Comparison**: Benchmarks against simple buy-and-hold strategy  

## 📊 Performance Metrics

The system tracks multiple performance indicators:
- **Total Return**: Absolute profit/loss in dollars
- **Return Percentage**: Percentage gain/loss on initial investment
- **Number of Trades**: Total buy/sell transactions executed
- **Buy & Hold Comparison**: Performance vs. simple buy-and-hold
- **Trade History**: Detailed log of all transactions with dates and prices

## ⚠️ Important Notes

1. **Educational Purpose**: This is for learning algorithmic trading concepts
2. **Past Performance**: Historical results don't guarantee future performance
3. **Risk Warning**: Real trading involves significant financial risk
4. **Data Dependencies**: Requires internet connection for stock data
5. **Market Hours**: Uses historical daily closing prices

## 🔮 Future Enhancements

- Add more technical indicators (RSI, MACD, Bollinger Bands)
- Implement stop-loss and take-profit mechanisms
- Add portfolio diversification across multiple stocks
- Include transaction costs and slippage
- Add real-time trading capabilities
- Implement backtesting with different parameters

## 🤝 Contributing

Feel free to fork this project and submit pull requests for improvements!

## 📄 License

This project is for educational purposes. Use at your own risk for any real trading activities.

---

**Happy Trading! 📈💰**