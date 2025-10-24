"""
Demo script to test the Algorithmic Trading Bot with different scenarios
"""

from trading_bot import AlgorithmicTrader


def test_multiple_stocks():
    """Test the trading strategy with multiple stocks."""
    
    stocks_to_test = [
        ("AAPL", "Apple Inc."),
        ("MSFT", "Microsoft Corporation"),
        ("GOOGL", "Alphabet Inc."),
        ("TSLA", "Tesla Inc."),
        ("AMZN", "Amazon.com Inc.")
    ]
    
    results_summary = []
    
    print("🚀 ALGORITHMIC TRADING ADVENTURE - MULTI-STOCK ANALYSIS")
    print("="*80)
    
    for symbol, company_name in stocks_to_test:
        print(f"\n📊 Testing {company_name} ({symbol})")
        print("-" * 50)
        
        try:
            # Create trader instance
            trader = AlgorithmicTrader(symbol, "2020-01-01", "2023-12-31", budget=5000)
            
            # Run strategy
            result = trader.run_strategy()
            
            if result:
                results_summary.append({
                    'symbol': symbol,
                    'company': company_name,
                    'return': result['total_return'],
                    'return_pct': result['return_percentage'],
                    'trades': result['trades_count']
                })
                
        except Exception as e:
            print(f"❌ Error testing {symbol}: {e}")
            continue
    
    # Display summary comparison
    if results_summary:
        print("\n" + "="*80)
        print("📈 PERFORMANCE COMPARISON SUMMARY")
        print("="*80)
        print(f"{'Stock':<8} {'Company':<20} {'Return':<12} {'Return %':<10} {'Trades':<8}")
        print("-"*80)
        
        for result in sorted(results_summary, key=lambda x: x['return_pct'], reverse=True):
            print(f"{result['symbol']:<8} "
                  f"{result['company'][:19]:<20} "
                  f"${result['return']:,.2f}{'':>4} "
                  f"{result['return_pct']:>6.2f}%{'':>4} "
                  f"{result['trades']:>5}")
        
        # Find best performer
        best_stock = max(results_summary, key=lambda x: x['return_pct'])
        print(f"\n🏆 Best Performer: {best_stock['company']} ({best_stock['symbol']}) "
              f"with {best_stock['return_pct']:.2f}% return")


def test_different_time_periods():
    """Test the same stock with different time periods."""
    
    time_periods = [
        ("2018-01-01", "2020-12-31", "Pre-COVID (2018-2020)"),
        ("2020-01-01", "2022-12-31", "COVID Era (2020-2022)"),
        ("2021-01-01", "2023-12-31", "Recent Years (2021-2023)")
    ]
    
    print(f"\n🕐 TIME PERIOD ANALYSIS FOR APPLE (AAPL)")
    print("="*60)
    
    for start_date, end_date, period_name in time_periods:
        print(f"\n📅 {period_name}")
        print("-" * 40)
        
        try:
            trader = AlgorithmicTrader("AAPL", start_date, end_date, budget=5000)
            result = trader.run_strategy()
            
        except Exception as e:
            print(f"❌ Error testing period {period_name}: {e}")


if __name__ == "__main__":
    # Run comprehensive tests
    test_multiple_stocks()
    test_different_time_periods()