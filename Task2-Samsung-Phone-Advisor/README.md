# Samsung Phone Advisor 📱🤖

An intelligent Samsung smartphone advisory system that combines **RAG (Retrieval-Augmented Generation)** and **Multi-Agent Architecture** to provide comprehensive phone recommendations, specifications, and comparisons through natural language queries.

## 🎯 Project Overview

This project builds a smart assistant for a tech review platform that helps users make informed decisions when buying Samsung smartphones. Users can ask natural language questions and receive both detailed specifications and intelligent recommendations powered by AI.

## ✨ Key Features

### 🔄 Unified RAG + Multi-Agent System
- **RAG Module**: Retrieves structured specifications from PostgreSQL
- **Multi-Agent System**: 
  - **Data Extractor Agent**: Pulls relevant phone data based on queries
  - **Review Generator Agent**: Creates comparative analysis and recommendations
- **FastAPI Integration**: Single endpoint for all query types

### 🗃️ Data Management
- **Web Scraper**: Collects Samsung phone data from GSMArena (20-30 models)
- **PostgreSQL Database**: Stores comprehensive phone specifications
- **SQLite Fallback**: Local development database option

### 🧠 Intelligent Query Processing
- Natural language understanding
- Automatic intent detection (specs, comparison, price, camera, battery)
- Context-aware responses
- Confidence scoring

## 🏗️ System Architecture

```
User Query → FastAPI → RAG System → Database
                  ↓
            Multi-Agent System
                  ↓
      [Data Extractor Agent] → [Review Generator Agent]
                  ↓
            Unified Response
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- PostgreSQL (optional, SQLite fallback available)
- Internet connection for web scraping

### Installation

1. **Navigate to project directory**
   ```bash
   cd Task2-Samsung-Phone-Advisor
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables** (optional for PostgreSQL)
   ```bash
   # Create .env file
   DB_HOST=localhost
   DB_NAME=samsung_phones
   DB_USER=postgres
   DB_PASSWORD=your_password
   DB_PORT=5432
   ```

4. **Initialize database and load data**
   ```bash
   python database/database.py
   python src/scraper.py
   ```

5. **Start the API server**
   ```bash
   python api.py
   ```

## 🎮 Usage Examples

### 📡 API Endpoints

#### Main Query Endpoint
```bash
POST /ask
Content-Type: application/json

{
  "question": "Compare Samsung Galaxy S23 Ultra and S22 Ultra"
}
```

**Response:**
```json
{
  "answer": "Comparing Samsung Galaxy S23 Ultra and S22 Ultra:\n\n**Camera Performance:**\n• Galaxy S23 Ultra: 200 MP main, 12 MP ultrawide, 10 MP telephoto (3x), 10 MP telephoto (10x)\n• Galaxy S22 Ultra: 108 MP main, 12 MP ultrawide, 10 MP telephoto (3x), 10 MP telephoto (10x)\nThe Galaxy S23 Ultra has a significantly better main camera sensor.\n\n**Battery Life:**\n• Galaxy S23 Ultra: 5000 mAh\n• Galaxy S22 Ultra: 5000 mAh\nBoth phones have similar battery capacity.",
  "confidence": 0.8,
  "phones_found": 2,
  "response_type": "multi_agent",
  "recommendations": [
    "For photography enthusiasts, the Galaxy S23 Ultra offers excellent camera performance"
  ],
  "success": true
}
```

#### Other Endpoints
```bash
GET /phones                          # Get all phones
GET /phones/search?q=S23            # Search phones
POST /phones/compare                 # Compare specific phones
GET /phones/{phone_name}             # Get phone details
GET /health                          # Health check
GET /docs                           # API documentation
```

### 🗣️ Natural Language Queries

**Specifications:**
- "What are the specs of Samsung Galaxy S23 Ultra?"
- "Tell me about Galaxy A54 features"

**Comparisons:**
- "Compare Galaxy S23 Ultra and S22 Ultra for photography"
- "S23 vs S22 differences"

**Price-based:**
- "Which Samsung phone has the best battery under $1000?"
- "Budget Samsung phones under $500"

**Feature-focused:**
- "Best Samsung camera phone"
- "Samsung phones with longest battery life"

## 📁 Project Structure

```
Task2-Samsung-Phone-Advisor/
├── api.py                           # FastAPI application
├── requirements.txt                 # Dependencies
├── README.md                        # This file
├── database/
│   ├── database.py                  # Database operations
│   └── samsung_phones.db           # SQLite database (auto-generated)
└── src/
    ├── scraper.py                   # Web scraper for GSMArena
    ├── rag_system.py               # RAG implementation
    └── multi_agent_system.py       # Multi-agent architecture
```

## 🤖 Multi-Agent System Details

### Data Extractor Agent
```python
class DataExtractorAgent:
    # Strategies:
    - specific_models    # Search for named phones
    - comparison        # Get multiple phones for comparison
    - price_range       # Filter by price criteria
    - general          # Keyword-based search
```

### Review Generator Agent
```python
class ReviewGeneratorAgent:
    # Response Types:
    - comparison_review      # Detailed phone comparisons
    - price_review          # Budget-focused recommendations
    - camera_focused_review # Photography-oriented analysis
    - battery_focused_review # Battery life analysis
    - performance_review    # Gaming/performance focus
```

## 🔍 RAG System Features

### Semantic Search
- **Sentence Transformers**: Converts phone data to embeddings
- **Cosine Similarity**: Finds most relevant phones for queries
- **Context Retrieval**: Extracts comprehensive phone information

### Intent Detection
- **Specifications**: Detailed phone specs
- **Comparison**: Side-by-side phone analysis  
- **Price Inquiry**: Budget-focused search
- **Feature Focus**: Camera, battery, performance specific queries

## 📊 Database Schema

```sql
CREATE TABLE samsung_phones (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL UNIQUE,
    release_date VARCHAR(100),
    display TEXT,
    battery VARCHAR(100),
    camera TEXT,
    ram VARCHAR(100),
    storage VARCHAR(200),
    price VARCHAR(100),
    url TEXT,
    additional_specs JSONB,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧪 Testing the System

### Run Individual Components
```bash
# Test database
python database/database.py

# Test scraper
python src/scraper.py

# Test RAG system
python src/rag_system.py

# Test multi-agent system
python src/multi_agent_system.py
```

### API Testing
```bash
# Start server
python api.py

# Test endpoints
curl -X POST "http://127.0.0.1:8000/ask" \
     -H "Content-Type: application/json" \
     -d '{"question": "Best Samsung phone for photography"}'

# View interactive docs
# Open http://127.0.0.1:8000/docs in browser
```

## 🎯 Example Responses

### Specification Query
**Input:** "What are the specs of Samsung Galaxy S23 Ultra?"

**Output:**
```
Samsung Galaxy S23 Ultra Specifications:

Display: 6.8" Dynamic AMOLED 2X, 120Hz
Camera System: 200 MP main, 12 MP ultrawide, 10 MP telephoto (3x), 10 MP telephoto (10x)
Battery: 5000 mAh
RAM: 8GB, 12GB
Storage: 256GB, 512GB, 1TB
Price: $1199
Release Date: 2023-02-01

Analysis:
This is a flagship model with premium features and performance.
```

### Comparison Query
**Input:** "Compare Galaxy S23 Ultra and S22 Ultra for photography"

**Output:**
```
Samsung Phones for Photography:

Galaxy S23 Ultra
Camera: 200 MP main, 12 MP ultrawide, 10 MP telephoto (3x), 10 MP telephoto (10x)
• Exceptional 200MP main sensor for ultra-detailed photos
• Ultrawide lens for landscape and group photos
• Telephoto lens for zoom photography
Price: $1199

Galaxy S22 Ultra  
Camera: 108 MP main, 12 MP ultrawide, 10 MP telephoto (3x), 10 MP telephoto (10x)
• High-resolution 108MP sensor for detailed shots
• Ultrawide lens for landscape and group photos
• Telephoto lens for zoom photography
Price: $1199
```

## 🔧 Configuration Options

### Environment Variables
```bash
# Database Configuration
DB_HOST=localhost
DB_NAME=samsung_phones
DB_USER=postgres
DB_PASSWORD=password
DB_PORT=5432

# API Configuration
API_HOST=127.0.0.1
API_PORT=8000
DEBUG=True
```

### System Settings
```python
# RAG Configuration
SENTENCE_TRANSFORMER_MODEL = 'all-MiniLM-L6-v2'
SIMILARITY_THRESHOLD = 0.1
MAX_RESULTS = 5

# Multi-Agent Configuration
MAX_PHONES_PER_QUERY = 10
CONFIDENCE_THRESHOLD = 0.5
```

## 🚀 Advanced Features

### Custom Agents
```python
# Add new specialized agents
class PriceComparisonAgent(BaseAgent):
    def process(self, query, context):
        # Custom price analysis logic
        pass

# Register with multi-agent system
mas.add_agent('price_comparison', PriceComparisonAgent())
```

### Enhanced RAG
```python
# Custom embeddings
rag.model = SentenceTransformer('your-custom-model')

# Custom similarity functions
def custom_similarity(query_embedding, phone_embeddings):
    # Your similarity logic
    pass
```

## 🔮 Future Enhancements

- **Real-time Price Updates**: Live price monitoring from multiple sources
- **User Preference Learning**: Personalized recommendations based on history
- **Voice Interface**: Speech-to-text query processing
- **Visual Comparison**: Side-by-side phone image comparisons
- **Reviews Integration**: Include user reviews and expert opinions
- **Advanced NLP**: Integration with larger language models (GPT-4, Claude)

## ⚠️ Notes

1. **Web Scraping**: Respects robots.txt and includes delays between requests
2. **Data Accuracy**: Phone specifications may vary; verify with official sources
3. **Rate Limiting**: Consider implementing API rate limiting for production use
4. **Scalability**: PostgreSQL recommended for production deployments

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is for educational and demonstration purposes.

---

**Built with ❤️ using Python, FastAPI, PostgreSQL, and AI** 🚀