# Python Projects Collection 🐍

This repository contains two advanced Python projects demonstrating different aspects of programming, data science, and AI development.

## 📁 Projects Overview

### 1. 🚀 Task 1: Algorithmic Trading Adventure
**Location:** `Task1-Algorithmic-Trading/`

An advanced algorithmic trading system implementing the Golden Cross strategy with a $5000 budget.

**Key Features:**
- Golden Cross trading strategy (50-day vs 200-day moving averages)
- Automated buy/sell decisions based on technical indicators
- Portfolio management with budget constraints
- Performance analysis and comparison with buy-and-hold strategy
- Multi-stock and multi-timeframe testing capabilities

**Technologies:** Python, yfinance, pandas, numpy, matplotlib

### 2. 📱 Task 2: Samsung Phone Advisor
**Location:** `Task2-Samsung-Phone-Advisor/`

An intelligent smartphone advisory system using RAG (Retrieval-Augmented Generation) and Multi-Agent Architecture.

**Key Features:**
- Web scraping from GSMArena for Samsung phone data
- PostgreSQL database with comprehensive phone specifications
- RAG system for semantic search and retrieval
- Multi-agent architecture with specialized agents
- FastAPI endpoints for natural language queries
- Intelligent recommendations and comparisons

**Technologies:** Python, FastAPI, PostgreSQL, sentence-transformers, scikit-learn, BeautifulSoup

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (optional)

### Setup Instructions

1. **Navigate to desired project:**
   ```bash
   # For Algorithmic Trading
   cd Task1-Algorithmic-Trading
   
   # For Samsung Phone Advisor
   cd Task2-Samsung-Phone-Advisor
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the project:**
   ```bash
   # Algorithmic Trading
   python trading_bot.py
   # or
   python demo.py
   
   # Samsung Phone Advisor
   python api.py
   ```

## 📊 Project Comparison

| Feature | Trading Bot | Phone Advisor |
|---------|-------------|---------------|
| **Domain** | Finance/Trading | E-commerce/Tech |
| **Data Source** | Yahoo Finance | Web Scraping |
| **AI/ML** | Technical Analysis | RAG + Multi-Agent |
| **Database** | In-memory (pandas) | PostgreSQL/SQLite |
| **API** | Class-based | FastAPI REST |
| **Complexity** | Intermediate | Advanced |
| **Real-time** | Historical Data | Static + Live Query |

## 🎯 Learning Objectives

### Task 1 - Algorithmic Trading
- **Financial Programming**: Working with stock market data
- **Object-Oriented Design**: Class-based trading system architecture
- **Data Analysis**: Moving averages and technical indicators
- **Risk Management**: Budget constraints and position management
- **Performance Measurement**: ROI calculations and benchmarking

### Task 2 - Samsung Phone Advisor  
- **Web Scraping**: Automated data collection from websites
- **Database Design**: Structured data storage and retrieval
- **Natural Language Processing**: Query understanding and intent detection
- **AI Architecture**: RAG systems and multi-agent frameworks
- **API Development**: RESTful services with FastAPI
- **System Integration**: Combining multiple AI components

## 🔧 Technologies Used

### Common Technologies
- **Python 3.8+**: Core programming language
- **pandas**: Data manipulation and analysis
- **numpy**: Numerical computing
- **requests**: HTTP requests for data fetching

### Task 1 Specific
- **yfinance**: Yahoo Finance API for stock data
- **matplotlib/seaborn**: Data visualization
- **datetime**: Time series handling

### Task 2 Specific
- **FastAPI**: Modern web framework for APIs
- **PostgreSQL**: Relational database
- **sentence-transformers**: Semantic embeddings
- **scikit-learn**: Machine learning utilities
- **BeautifulSoup**: HTML parsing for web scraping
- **uvicorn**: ASGI server for FastAPI

## 📈 Performance Examples

### Algorithmic Trading Results
```
Initial Budget: $5,000.00
Final Value: $7,076.80
Total Return: $2,076.80 (41.54%)
Trades Executed: 2
Strategy vs Buy&Hold: +$229.57
```

### Phone Advisor Query Examples
```bash
Query: "Compare Galaxy S23 Ultra and S22 Ultra"
Response: Detailed comparison with camera, battery, display analysis
Confidence: 0.85
Phones Found: 2
```

## 🛠️ Development Setup

### Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install project dependencies
pip install -r requirements.txt
```

### Environment Variables
```bash
# For Samsung Phone Advisor (optional)
DB_HOST=localhost
DB_NAME=samsung_phones
DB_USER=postgres
DB_PASSWORD=your_password
DB_PORT=5432
```

## 🧪 Testing

### Task 1 Testing
```bash
# Run basic trading simulation
python trading_bot.py

# Run comprehensive multi-stock testing
python demo.py

# Test with custom parameters
python -c "
from trading_bot import AlgorithmicTrader
trader = AlgorithmicTrader('MSFT', '2020-01-01', '2023-12-31')
results = trader.run_strategy()
"
```

### Task 2 Testing
```bash
# Test individual components
python database/database.py
python src/scraper.py
python src/rag_system.py
python src/multi_agent_system.py

# Test API endpoints
curl -X POST "http://127.0.0.1:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "Best Samsung phone under $800"}'
```

## 🔮 Future Enhancements

### Algorithmic Trading
- [ ] Multiple trading strategies (RSI, MACD, Bollinger Bands)
- [ ] Real-time trading integration
- [ ] Portfolio diversification
- [ ] Advanced risk management
- [ ] Machine learning predictions

### Samsung Phone Advisor
- [ ] Real-time price monitoring
- [ ] User preference learning
- [ ] Voice interface
- [ ] Visual phone comparisons
- [ ] Advanced LLM integration

## 📚 Documentation

Each project includes comprehensive documentation:
- **README.md**: Detailed project overview and setup instructions
- **Code Comments**: Inline documentation for all major functions
- **API Documentation**: Auto-generated docs at `/docs` for Task 2
- **Example Usage**: Multiple usage examples and test cases

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## ⚠️ Disclaimers

### Trading Bot
- **Educational Purpose Only**: Not financial advice
- **Risk Warning**: Trading involves significant financial risk
- **Past Performance**: Does not guarantee future results

### Phone Advisor
- **Data Accuracy**: Specifications may vary; verify with official sources
- **Web Scraping**: Respects robots.txt and implements delays
- **API Limits**: Consider rate limiting for production use

## 📄 License

These projects are created for educational and demonstration purposes. Use responsibly and at your own risk.

## 📞 Support

For questions or issues:
1. Check the project-specific README files
2. Review the code comments and documentation
3. Test with the provided examples
4. Create an issue if you encounter problems

---

**Happy Coding! 🚀💻**

*Built with ❤️ using Python and modern development practices*