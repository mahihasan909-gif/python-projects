"""
Algorithmic Trading Adventure - Golden Cross Strategy
Author: Alex's Trading Bot
Budget: $5000

This module implements a class-based algorithmic trading strategy using the golden cross
method to identify bullish trends and make informed trading decisions.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')


class AlgorithmicTrader:
    """
    A class to implement algorithmic trading strategy using golden cross signals.
    
    The golden cross occurs when the 50-day moving average crosses above the 200-day
    moving average, signaling a potential bullish trend.
    """
    
    def __init__(self, symbol, from_date, to_date, budget=5000):
        """
        Initialize the trading strategy.
        
        Args:
            symbol (str): Stock symbol (e.g., "AAPL")
            from_date (str): Start date in format "YYYY-MM-DD"
            to_date (str): End date in format "YYYY-MM-DD"
            budget (float): Trading budget in dollars (default: $5000)
        """
        self.symbol = symbol
        self.from_date = from_date
        self.to_date = to_date
        self.budget = budget
        self.initial_budget = budget
        self.data = None
        self.position = 0  # Number of shares held
        self.position_open = False
        self.trades = []  # Track all trades
        self.current_cash = budget
        
    def download_data(self):
        """Download historical stock data using yfinance."""
        try:
            print(f"Downloading data for {self.symbol} from {self.from_date} to {self.to_date}...")
            ticker = yf.Ticker(self.symbol)
            self.data = ticker.history(start=self.from_date, end=self.to_date)
            
            if self.data.empty:
                raise ValueError(f"No data found for symbol {self.symbol}")
                
            print(f"Downloaded {len(self.data)} data points")
            return True
            
        except Exception as e:
            print(f"Error downloading data: {e}")
            return False
    
    def clean_data(self):
        """Clean data by removing duplicates and handling NaN values."""
        if self.data is None:
            print("No data to clean. Please download data first.")
            return False
            
        # Remove duplicates
        initial_length = len(self.data)
        self.data = self.data.drop_duplicates()
        duplicates_removed = initial_length - len(self.data)
        
        # Forward fill NaN values
        nan_count = self.data.isnull().sum().sum()
        self.data = self.data.fillna(method='ffill')
        
        print(f"Data cleaning complete:")
        print(f"  - Removed {duplicates_removed} duplicate entries")
        print(f"  - Forward filled {nan_count} NaN values")
        print(f"  - Final dataset: {len(self.data)} rows")
        
        return True
    
    def calculate_moving_averages(self):
        """Calculate 50-day and 200-day moving averages."""
        if self.data is None:
            print("No data available. Please download data first.")
            return False
            
        self.data['MA_50'] = self.data['Close'].rolling(window=50).mean()
        self.data['MA_200'] = self.data['Close'].rolling(window=200).mean()
        
        # Identify golden cross signals
        self.data['Golden_Cross'] = (self.data['MA_50'] > self.data['MA_200']) & \
                                   (self.data['MA_50'].shift(1) <= self.data['MA_200'].shift(1))
        
        # Identify death cross signals (when to sell)
        self.data['Death_Cross'] = (self.data['MA_50'] < self.data['MA_200']) & \
                                  (self.data['MA_50'].shift(1) >= self.data['MA_200'].shift(1))
        
        print("Moving averages calculated:")
        print(f"  - 50-day MA: {self.data['MA_50'].notna().sum()} valid values")
        print(f"  - 200-day MA: {self.data['MA_200'].notna().sum()} valid values")
        print(f"  - Golden crosses detected: {self.data['Golden_Cross'].sum()}")
        print(f"  - Death crosses detected: {self.data['Death_Cross'].sum()}")
        
        return True
    
    def execute_trades(self):
        """Execute trading strategy based on golden cross and death cross signals."""
        if self.data is None:
            print("No data available for trading.")
            return False
            
        print(f"\nStarting trading simulation with ${self.budget:,.2f}")
        print("-" * 60)
        
        for index, row in self.data.iterrows():
            current_price = row['Close']
            
            # Skip if we don't have moving averages yet
            if pd.isna(row['MA_50']) or pd.isna(row['MA_200']):
                continue
            
            # Golden Cross - Buy Signal
            if row['Golden_Cross'] and not self.position_open and self.current_cash > 0:
                shares_to_buy = int(self.current_cash / current_price)
                if shares_to_buy > 0:
                    cost = shares_to_buy * current_price
                    self.position = shares_to_buy
                    self.current_cash -= cost
                    self.position_open = True
                    
                    trade = {
                        'date': index,
                        'action': 'BUY',
                        'shares': shares_to_buy,
                        'price': current_price,
                        'total': cost,
                        'cash_remaining': self.current_cash
                    }
                    self.trades.append(trade)
                    
                    print(f"{index.strftime('%Y-%m-%d')}: BUY  {shares_to_buy:,} shares at ${current_price:.2f} = ${cost:,.2f}")
                    print(f"  Cash remaining: ${self.current_cash:,.2f}")
            
            # Death Cross - Sell Signal
            elif row['Death_Cross'] and self.position_open:
                revenue = self.position * current_price
                self.current_cash += revenue
                
                trade = {
                    'date': index,
                    'action': 'SELL',
                    'shares': self.position,
                    'price': current_price,
                    'total': revenue,
                    'cash_remaining': self.current_cash
                }
                self.trades.append(trade)
                
                print(f"{index.strftime('%Y-%m-%d')}: SELL {self.position:,} shares at ${current_price:.2f} = ${revenue:,.2f}")
                print(f"  Cash after sale: ${self.current_cash:,.2f}")
                
                self.position = 0
                self.position_open = False
        
        # Force close position on last day if still open
        if self.position_open:
            last_date = self.data.index[-1]
            last_price = self.data.iloc[-1]['Close']
            revenue = self.position * last_price
            self.current_cash += revenue
            
            trade = {
                'date': last_date,
                'action': 'FORCE_SELL',
                'shares': self.position,
                'price': last_price,
                'total': revenue,
                'cash_remaining': self.current_cash
            }
            self.trades.append(trade)
            
            print(f"\n{last_date.strftime('%Y-%m-%d')}: FORCE SELL {self.position:,} shares at ${last_price:.2f} = ${revenue:,.2f}")
            print(f"  Final cash: ${self.current_cash:,.2f}")
            
            self.position = 0
            self.position_open = False
        
        return True
    
    def calculate_performance(self):
        """Calculate and display trading performance metrics."""
        if not self.trades:
            print("No trades executed.")
            return
        
        final_value = self.current_cash
        total_return = final_value - self.initial_budget
        return_percentage = (total_return / self.initial_budget) * 100
        
        # Buy and hold comparison
        start_price = self.data.iloc[0]['Close']
        end_price = self.data.iloc[-1]['Close']
        buy_hold_shares = self.initial_budget / start_price
        buy_hold_value = buy_hold_shares * end_price
        buy_hold_return = buy_hold_value - self.initial_budget
        buy_hold_percentage = (buy_hold_return / self.initial_budget) * 100
        
        print("\n" + "=" * 60)
        print("TRADING PERFORMANCE SUMMARY")
        print("=" * 60)
        print(f"Initial Budget:        ${self.initial_budget:,.2f}")
        print(f"Final Value:           ${final_value:,.2f}")
        print(f"Total Return:          ${total_return:,.2f}")
        print(f"Return Percentage:     {return_percentage:.2f}%")
        print(f"Number of Trades:      {len(self.trades)}")
        
        print(f"\nBuy & Hold Comparison:")
        print(f"Buy & Hold Value:      ${buy_hold_value:,.2f}")
        print(f"Buy & Hold Return:     ${buy_hold_return:,.2f} ({buy_hold_percentage:.2f}%)")
        
        strategy_vs_buy_hold = total_return - buy_hold_return
        print(f"Strategy vs Buy&Hold:  ${strategy_vs_buy_hold:,.2f}")
        
        if total_return > 0:
            print(f"\n🎉 Congratulations! Your strategy was profitable!")
        else:
            print(f"\n📉 Your strategy resulted in a loss. Consider refining the approach.")
            
        return {
            'initial_budget': self.initial_budget,
            'final_value': final_value,
            'total_return': total_return,
            'return_percentage': return_percentage,
            'trades_count': len(self.trades),
            'buy_hold_return': buy_hold_return,
            'buy_hold_percentage': buy_hold_percentage
        }
    
    def show_trade_history(self):
        """Display detailed trade history."""
        if not self.trades:
            print("No trades to display.")
            return
            
        print("\n" + "=" * 80)
        print("DETAILED TRADE HISTORY")
        print("=" * 80)
        print(f"{'Date':<12} {'Action':<10} {'Shares':<8} {'Price':<10} {'Total':<12} {'Cash Left':<12}")
        print("-" * 80)
        
        for trade in self.trades:
            print(f"{trade['date'].strftime('%Y-%m-%d'):<12} "
                  f"{trade['action']:<10} "
                  f"{trade['shares']:,<8} "
                  f"${trade['price']:<9.2f} "
                  f"${trade['total']:,<11.2f} "
                  f"${trade['cash_remaining']:,<11.2f}")
    
    def run_strategy(self):
        """Run the complete algorithmic trading strategy."""
        print("🚀 Starting Algorithmic Trading Adventure!")
        print(f"Symbol: {self.symbol} | Budget: ${self.budget:,.2f}")
        print(f"Period: {self.from_date} to {self.to_date}")
        print("=" * 60)
        
        # Step 1: Download data
        if not self.download_data():
            return False
        
        # Step 2: Clean data
        if not self.clean_data():
            return False
        
        # Step 3: Calculate moving averages
        if not self.calculate_moving_averages():
            return False
        
        # Step 4: Execute trading strategy
        if not self.execute_trades():
            return False
        
        # Step 5: Show results
        self.show_trade_history()
        performance = self.calculate_performance()
        
        return performance


# Example usage and testing
if __name__ == "__main__":
    # Alex's trading adventure with Apple stock
    trader = AlgorithmicTrader("AAPL", "2018-01-01", "2023-12-31", budget=5000)
    
    # Run the complete strategy
    results = trader.run_strategy()
    
    # You can also test with other stocks
    print("\n" + "="*60)
    print("Testing with Microsoft (MSFT)")
    print("="*60)
    
    msft_trader = AlgorithmicTrader("MSFT", "2020-01-01", "2023-12-31", budget=5000)
    msft_results = msft_trader.run_strategy()