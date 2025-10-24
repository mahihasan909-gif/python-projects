"""
FastAPI application for Samsung Phone Advisor
Unified API endpoint that combines RAG and Multi-Agent System
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
import os
import json

# Import our modules
try:
    from database.database import SamsungPhoneDatabase, SQLitePhoneDatabase
    from src.rag_system import PhoneRAG
    from src.multi_agent_system import MultiAgentSystem
    FULL_AI_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  AI modules not available: {e}")
    print("🔄 Running in simplified mode...")
    FULL_AI_AVAILABLE = False
    
    # Create dummy classes for fallback
    class SQLitePhoneDatabase:
        def __init__(self, db_path="samsung_phones.db"):
            self.db_path = db_path
            self.connection = None
        
        def connect(self):
            return True
            
        def create_tables(self):
            return True
            
        def search_phones(self, query, limit=10):
            return SAMPLE_PHONES[:limit]
            
        def get_all_phones(self, limit=50):
            return SAMPLE_PHONES[:limit]

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Sample phone data for fallback
SAMPLE_PHONES = [
    {
        'id': 1,
        'model_name': 'Samsung Galaxy S23 Ultra',
        'release_date': '2023-02-01',
        'display': '6.8" Dynamic AMOLED 2X, 120Hz',
        'battery': '5000 mAh',
        'camera': '200 MP main, 12 MP ultrawide, 10 MP telephoto (3x), 10 MP telephoto (10x)',
        'ram': '8GB, 12GB',
        'storage': '256GB, 512GB, 1TB',
        'price': '$1199'
    },
    {
        'id': 2,
        'model_name': 'Samsung Galaxy S23',
        'release_date': '2023-02-01',
        'display': '6.1" Dynamic AMOLED 2X, 120Hz',
        'battery': '3900 mAh',
        'camera': '50 MP main, 12 MP ultrawide, 10 MP telephoto (3x)',
        'ram': '8GB',
        'storage': '128GB, 256GB',
        'price': '$799'
    },
    {
        'id': 3,
        'model_name': 'Samsung Galaxy S22 Ultra',
        'release_date': '2022-02-25',
        'display': '6.8" Dynamic AMOLED 2X, 120Hz',
        'battery': '5000 mAh',
        'camera': '108 MP main, 12 MP ultrawide, 10 MP telephoto (3x), 10 MP telephoto (10x)',
        'ram': '8GB, 12GB',
        'storage': '128GB, 256GB, 512GB, 1TB',
        'price': '$1199'
    },
    {
        'id': 4,
        'model_name': 'Samsung Galaxy A54 5G',
        'release_date': '2023-03-24',
        'display': '6.4" Super AMOLED, 120Hz',
        'battery': '5000 mAh',
        'camera': '50 MP main, 12 MP ultrawide, 5 MP macro',
        'ram': '6GB, 8GB',
        'storage': '128GB, 256GB',
        'price': '$449'
    },
    {
        'id': 5,
        'model_name': 'Samsung Galaxy Z Fold5',
        'release_date': '2023-08-11',
        'display': '7.6" Foldable Dynamic AMOLED 2X, 120Hz',
        'battery': '4400 mAh',
        'camera': '50 MP main, 12 MP ultrawide, 10 MP telephoto (3x)',
        'ram': '12GB',
        'storage': '256GB, 512GB, 1TB',
        'price': '$1799'
    }
]

# Initialize FastAPI app
app = FastAPI(
    title="Samsung Phone Advisor API",
    description="Unified API for Samsung phone specifications, reviews, and recommendations using RAG and Multi-Agent System",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response models
class QueryRequest(BaseModel):
    question: str
    use_rag: Optional[bool] = True
    use_multi_agent: Optional[bool] = True

class QueryResponse(BaseModel):
    answer: str
    confidence: Optional[float] = None
    phones_found: int
    response_type: str
    recommendations: Optional[List[str]] = None
    success: bool

class PhoneSpecs(BaseModel):
    model_name: str
    release_date: Optional[str] = None
    display: Optional[str] = None
    battery: Optional[str] = None
    camera: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    price: Optional[str] = None

# Global variables for database and systems
database = None
rag_system = None
multi_agent_system = None

def get_database():
    """Dependency to get database instance."""
    global database
    if database is None:
        # Try PostgreSQL first, fall back to SQLite
        try:
            database = SamsungPhoneDatabase()
            if not database.connect():
                raise Exception("PostgreSQL connection failed")
            logger.info("Using PostgreSQL database")
        except:
            # Use SQLite as fallback
            db_path = os.path.join(os.path.dirname(__file__), "database", "samsung_phones.db")
            database = SQLitePhoneDatabase(db_path)
            if not database.connect():
                raise Exception("Failed to connect to any database")
            logger.info("Using SQLite database (fallback)")
            
        # Ensure tables exist
        database.create_tables()
    
    return database

def get_rag_system(db=Depends(get_database)):
    """Dependency to get RAG system instance."""
    global rag_system
    if not FULL_AI_AVAILABLE:
        return None
        
    if rag_system is None:
        try:
            rag_system = PhoneRAG(db)
            logger.info("RAG system initialized")
        except Exception as e:
            logger.warning(f"RAG system initialization failed: {e}")
            rag_system = None
    
    return rag_system

def get_multi_agent_system(db=Depends(get_database)):
    """Dependency to get Multi-Agent system instance."""
    global multi_agent_system
    if not FULL_AI_AVAILABLE:
        return None
        
    if multi_agent_system is None:
        multi_agent_system = MultiAgentSystem(db)
        logger.info("Multi-Agent system initialized")
    
    return multi_agent_system

def simple_response_generator(query: str, phones: List[Dict]) -> str:
    """Enhanced response generator for detailed phone information."""
    if not phones:
        return "I couldn't find any Samsung phones matching your query. Try asking about Galaxy S23, S22, A54, or Z Fold5."
    
    query_lower = query.lower()
    
    # Handle camera-related queries
    if 'camera' in query_lower or 'photo' in query_lower:
        response = "📸 **Samsung Phones with Excellent Cameras:**\n\n"
        for phone in phones[:3]:
            response += f"**{phone['model_name']}** - {phone['price']}\n"
            response += f"Camera: {phone['camera']}\n"
            if 'S23 Ultra' in phone['model_name'] or 'S24' in phone['model_name']:
                response += "⭐ **Top Choice for Photography** - 200MP main camera with exceptional zoom\n"
            elif 'A54' in phone['model_name']:
                response += "💰 **Best Value** - Great cameras for the price point\n"
            response += f"Display: {phone['display']}\n\n"
        
        response += "🎯 **Recommendation:** For professional photography, choose Galaxy S23 Ultra. For great value, go with Galaxy A54 5G."
        return response
    
    # Handle comparison queries
    elif 'compare' in query_lower and len(phones) >= 2:
        phone1, phone2 = phones[0], phones[1]
        return f"""📱 **Detailed Comparison: {phone1['model_name']} vs {phone2['model_name']}**

📸 **Camera Performance:**
• {phone1['model_name']}: {phone1['camera']}
• {phone2['model_name']}: {phone2['camera']}

📺 **Display Quality:**
• {phone1['model_name']}: {phone1['display']}
• {phone2['model_name']}: {phone2['display']}

🔋 **Battery Life:**
• {phone1['model_name']}: {phone1['battery']}
• {phone2['model_name']}: {phone2['battery']}

💰 **Pricing:**
• {phone1['model_name']}: {phone1['price']}
• {phone2['model_name']}: {phone2['price']}

🎯 **Bottom Line:** The {phone1['model_name']} offers premium features and better camera performance, while the {phone2['model_name']} provides excellent value for money. Choose based on your budget and photography needs."""

    # Handle gaming/performance queries
    elif 'gaming' in query_lower or 'performance' in query_lower:
        response = "🎮 **Best Samsung Phones for Gaming:**\n\n"
        for phone in phones[:2]:
            response += f"**{phone['model_name']}** - {phone['price']}\n"
            response += f"RAM: {phone['ram']}\n"
            response += f"Display: {phone['display']} (smooth 120Hz for gaming)\n"
            if 'Ultra' in phone['model_name']:
                response += "⚡ **Gaming Beast** - Flagship processor, maximum RAM\n"
            response += "\n"
        
        response += "🎯 **Gaming Verdict:** All Samsung flagships offer excellent gaming with 120Hz displays and powerful processors."
        return response
    
    # Handle budget/best value queries
    elif 'budget' in query_lower or 'cheap' in query_lower or 'affordable' in query_lower:
        response = "💰 **Best Value Samsung Phones:**\n\n"
        # Sort by price (assuming lower price = better value)
        affordable_phones = [p for p in phones if '$' in str(p.get('price', '')) and int(p['price'].replace('$', '').replace(',', '')) < 600]
        
        if affordable_phones:
            for phone in affordable_phones[:2]:
                response += f"**{phone['model_name']}** - {phone['price']}\n"
                response += f"Camera: {phone['camera']}\n"
                response += f"Display: {phone['display']}\n"
                response += "✅ **Great Value** - Premium features at mid-range price\n\n"
        else:
            phone = phones[0]
            response += f"**{phone['model_name']}** - {phone['price']}\n"
            response += f"Camera: {phone['camera']}\n"
            response += f"Display: {phone['display']}\n\n"
        
        response += "🎯 **Value Recommendation:** Galaxy A54 5G offers the best balance of features and price."
        return response
    
    # General phone information
    else:
        phone = phones[0]
        return f"""📱 **{phone['model_name']} - Complete Overview**

💰 **Price:** {phone['price']}
📅 **Release Date:** {phone['release_date']}

🔥 **Key Specifications:**
📸 Camera: {phone['camera']}
📺 Display: {phone['display']}
🔋 Battery: {phone['battery']}
💾 RAM: {phone['ram']}
💽 Storage: {phone['storage']}

🎯 **Why Choose This Phone:**
{'⭐ Flagship Performance - Top-tier camera and display technology' if 'Ultra' in phone['model_name'] else '💰 Excellent Value - Great features for the price point'}

💡 **Ask me more:** "Compare with other models" or "Best for photography" or "Gaming performance"

This is an excellent Samsung smartphone with modern features and reliable performance."""

@app.on_event("startup")
async def startup_event():
    """Initialize systems on startup."""
    logger.info("Starting Samsung Phone Advisor API...")
    
    # Initialize database
    db = get_database()
    
    # Load sample data if database is empty
    try:
        phones = db.search_phones("", limit=1)  # Empty query to get any phone
        if not phones:
            logger.info("Database is empty, loading sample data...")
            # Use our SAMPLE_PHONES data instead of scraper
            for phone_data in SAMPLE_PHONES:
                db.insert_phone_data(phone_data)
            
            logger.info(f"Loaded {len(SAMPLE_PHONES)} sample phones")
    except Exception as e:
        logger.error(f"Error loading sample data: {e}")
    
    # Initialize systems
    get_rag_system(db)
    get_multi_agent_system(db)
    
    logger.info("Samsung Phone Advisor API is ready!")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Samsung Phone Advisor API",
        "version": "1.0.0",
        "description": "Unified API for Samsung phone specifications, reviews, and recommendations",
        "endpoints": {
            "/ask": "Main query endpoint",
            "/phones": "Get all phones",
            "/phones/search": "Search phones",
            "/phones/compare": "Compare phones",
            "/health": "Health check"
        }
    }

@app.post("/ask", response_model=QueryResponse)
async def ask_question(
    request: QueryRequest,
    db=Depends(get_database),
    rag=Depends(get_rag_system),
    mas=Depends(get_multi_agent_system)
):
    """
    Main endpoint for asking questions about Samsung phones.
    Combines RAG and Multi-Agent System for comprehensive answers.
    """
    try:
        logger.info(f"Processing query: {request.question}")
        
        answer = ""
        confidence = 0.0
        phones_found = 0
        response_type = "hybrid"
        recommendations = []
        
        # Use Multi-Agent System as primary method
        if request.use_multi_agent and mas and FULL_AI_AVAILABLE:
            mas_result = mas.process_query(request.question)
            
            if mas_result.get('success', False):
                answer = mas_result['review_generation']['review']
                phones_found = mas_result.get('phones_found', 0)
                recommendations = mas_result['review_generation'].get('recommendations', [])
                response_type = "multi_agent"
                confidence = 0.8  # Default confidence for multi-agent
                
                logger.info(f"Multi-Agent System generated response with {phones_found} phones")
        
        # Use RAG system as backup or enhancement
        if request.use_rag and rag and FULL_AI_AVAILABLE and (not answer or phones_found == 0):
            try:
                rag_result = rag.answer_query(request.question)
                
                if rag_result.get('confidence', 0) > 0.1:
                    if not answer:
                        answer = rag_result['answer']
                        confidence = rag_result['confidence']
                        phones_found = rag_result['phones_found']
                        response_type = "rag"
                    else:
                        # Enhance existing answer
                        answer += f"\n\n**Additional Information:**\n{rag_result['answer']}"
                        confidence = max(confidence, rag_result['confidence'])
                        response_type = "hybrid"
                
                logger.info(f"RAG system provided response with confidence {rag_result.get('confidence', 0):.2f}")
            except Exception as e:
                logger.warning(f"RAG system failed: {e}")
        
        # Fallback to simple database search
        if not answer:
            search_results = db.search_phones(request.question, limit=5)
            if search_results:
                answer = simple_response_generator(request.question, search_results)
                phones_found = len(search_results)
                response_type = "simple_search"
                confidence = 0.7
            else:
                # Try broader search if no specific results
                all_phones = db.search_phones("Galaxy", limit=5)
                if all_phones:
                    answer = simple_response_generator(request.question, all_phones)
                    phones_found = len(all_phones)
                    response_type = "simple_search"
                    confidence = 0.5
                else:
                    answer = "I couldn't find any Samsung phones matching your query. Please try rephrasing your question."
                    response_type = "no_results"
                    confidence = 0.0
        
        return QueryResponse(
            answer=answer,
            confidence=confidence,
            phones_found=phones_found,
            response_type=response_type,
            recommendations=recommendations,
            success=True
        )
        
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/phones", response_model=List[PhoneSpecs])
async def get_all_phones(limit: int = 20, db=Depends(get_database)):
    """Get all Samsung phones in the database."""
    try:
        phones = db.get_all_phones(limit=limit)
        return [PhoneSpecs(**phone) for phone in phones]
    except Exception as e:
        logger.error(f"Error getting all phones: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/phones/search")
async def search_phones(q: str, limit: int = 10, db=Depends(get_database)):
    """Search for Samsung phones by query."""
    try:
        results = db.search_phones(q, limit=limit)
        return {
            "query": q,
            "results": results,
            "count": len(results)
        }
    except Exception as e:
        logger.error(f"Error searching phones: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/phones/compare")
async def compare_phones(phone_names: List[str], db=Depends(get_database)):
    """Compare multiple Samsung phones."""
    try:
        if len(phone_names) < 2:
            raise HTTPException(status_code=400, detail="At least 2 phone names required for comparison")
        
        phones = db.compare_phones(phone_names)
        
        if not phones:
            raise HTTPException(status_code=404, detail="No phones found with the given names")
        
        # Generate comparison
        comparison = {
            "phones": phones,
            "comparison_summary": f"Comparing {len(phones)} Samsung phones",
            "details": {}
        }
        
        # Compare key specs
        for spec in ['display', 'camera', 'battery', 'ram', 'storage', 'price']:
            comparison['details'][spec] = {
                phone['model_name']: phone.get(spec, 'N/A') 
                for phone in phones
            }
        
        return comparison
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing phones: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/phones/{phone_name}")
async def get_phone_details(phone_name: str, db=Depends(get_database)):
    """Get detailed specifications for a specific phone."""
    try:
        phone = db.get_phone_by_name(phone_name)
        
        if not phone:
            raise HTTPException(status_code=404, detail=f"Phone '{phone_name}' not found")
        
        return phone
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting phone details: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check(db=Depends(get_database)):
    """Health check endpoint."""
    try:
        # Check database connection
        stats = db.get_database_stats() if hasattr(db, 'get_database_stats') else {}
        
        return {
            "status": "healthy",
            "database": "connected",
            "rag_system": "available" if rag_system else "unavailable",
            "multi_agent_system": "available" if multi_agent_system else "unavailable",
            "database_stats": stats
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }

@app.get("/stats")
async def get_stats(db=Depends(get_database)):
    """Get API and database statistics."""
    try:
        stats = db.get_database_stats() if hasattr(db, 'get_database_stats') else {}
        
        return {
            "api_version": "1.0.0",
            "systems": {
                "database": "connected",
                "rag": "available" if rag_system else "unavailable",
                "multi_agent": "available" if multi_agent_system else "unavailable"
            },
            "database_stats": stats
        }
        
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return {"error": "Endpoint not found", "detail": str(exc)}

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return {"error": "Internal server error", "detail": str(exc)}

if __name__ == "__main__":
    import uvicorn
    
    print("Starting Samsung Phone Advisor API...")
    print("Available endpoints:")
    print("  - POST /ask - Main query endpoint")
    print("  - GET /phones - Get all phones")
    print("  - GET /phones/search?q=query - Search phones")
    print("  - POST /phones/compare - Compare phones")
    print("  - GET /health - Health check")
    print("  - GET /docs - API documentation")
    
    uvicorn.run(
        "api:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        log_level="info"
    )