"""
Multi-Agent System for Samsung Phone Advisor
Implements specialized agents for different aspects of phone analysis
"""

import logging
from typing import Dict, List, Any, Optional
from abc import ABC, abstractmethod
import json

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        
    @abstractmethod
    def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process a query and return results."""
        pass


class DataExtractorAgent(BaseAgent):
    """Agent responsible for extracting relevant phone data from database."""
    
    def __init__(self, database):
        super().__init__(
            name="Data Extractor",
            description="Extracts relevant phone data based on user queries"
        )
        self.database = database
        
    def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant phone data based on query."""
        try:
            # Analyze query to determine search strategy
            extracted_data = {
                'agent': self.name,
                'query': query,
                'phones': [],
                'search_strategy': 'general'
            }
            
            query_lower = query.lower()
            
            # Detect specific phone models
            phones_mentioned = self._extract_phone_names(query)
            
            if phones_mentioned:
                # Search for specific phones
                extracted_data['search_strategy'] = 'specific_models'
                for phone_name in phones_mentioned:
                    phone_data = self.database.get_phone_by_name(phone_name)
                    if phone_data:
                        extracted_data['phones'].append(phone_data)
                        
            elif 'compare' in query_lower or 'vs' in query_lower:
                # Comparison query - get multiple phones
                extracted_data['search_strategy'] = 'comparison'
                search_results = self.database.search_phones(
                    self._extract_search_terms(query), 
                    limit=5
                )
                extracted_data['phones'] = search_results
                
            elif any(word in query_lower for word in ['under', 'below', 'budget', 'cheap']):
                # Price-based query
                extracted_data['search_strategy'] = 'price_range'
                price_limit = self._extract_price_limit(query)
                if price_limit:
                    phones = self.database.get_phones_by_price_range(0, price_limit)
                    extracted_data['phones'] = phones
                    extracted_data['price_limit'] = price_limit
                else:
                    # Fallback to general search
                    extracted_data['phones'] = self.database.search_phones(
                        self._extract_search_terms(query), 
                        limit=5
                    )
                    
            else:
                # General search
                search_terms = self._extract_search_terms(query)
                extracted_data['phones'] = self.database.search_phones(search_terms, limit=5)
            
            extracted_data['phones_found'] = len(extracted_data['phones'])
            
            logger.info(f"Data Extractor found {extracted_data['phones_found']} phones "
                       f"using {extracted_data['search_strategy']} strategy")
            
            return extracted_data
            
        except Exception as e:
            logger.error(f"Error in Data Extractor Agent: {e}")
            return {
                'agent': self.name,
                'error': str(e),
                'phones': [],
                'phones_found': 0
            }
    
    def _extract_phone_names(self, query: str) -> List[str]:
        """Extract Samsung phone model names from query."""
        phone_patterns = [
            r'galaxy\s+s\d+\s*ultra?',
            r'galaxy\s+s\d+\s*\+?',
            r'galaxy\s+note\s*\d+',
            r'galaxy\s+a\d+',
            r'galaxy\s+z\s*fold\d*',
            r'galaxy\s+z\s*flip\d*',
            r's\d+\s*ultra?',
            r's\d+\s*\+?',
            r'note\s*\d+'
        ]
        
        import re
        found_phones = []
        query_lower = query.lower()
        
        for pattern in phone_patterns:
            matches = re.findall(pattern, query_lower)
            for match in matches:
                # Clean up the match
                clean_match = re.sub(r'\s+', ' ', match.strip())
                if clean_match not in found_phones:
                    found_phones.append(clean_match)
        
        return found_phones
    
    def _extract_search_terms(self, query: str) -> str:
        """Extract search terms from query."""
        # Remove common stop words and focus on key terms
        stop_words = {'the', 'is', 'at', 'which', 'on', 'what', 'are', 'best', 'good', 'phone'}
        
        import re
        words = re.findall(r'\b\w+\b', query.lower())
        search_terms = [word for word in words if word not in stop_words and len(word) > 2]
        
        return ' '.join(search_terms[:5])  # Limit to 5 most relevant terms
    
    def _extract_price_limit(self, query: str) -> Optional[int]:
        """Extract price limit from query."""
        import re
        
        # Look for price patterns
        price_patterns = [
            r'\$(\d+)',
            r'(\d+)\s*dollars?',
            r'under\s+(\d+)',
            r'below\s+(\d+)',
            r'(\d+)\s*bucks?'
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, query.lower())
            if match:
                return int(match.group(1))
        
        return None


class ReviewGeneratorAgent(BaseAgent):
    """Agent responsible for generating natural language reviews and recommendations."""
    
    def __init__(self):
        super().__init__(
            name="Review Generator",
            description="Generates comparative analysis and recommendations in natural language"
        )
        
    def process(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate natural language review and recommendations."""
        try:
            phones_data = context.get('phones', [])
            search_strategy = context.get('search_strategy', 'general')
            
            result = {
                'agent': self.name,
                'query': query,
                'review': '',
                'recommendations': [],
                'strategy_used': search_strategy
            }
            
            if not phones_data:
                result['review'] = "I couldn't find any Samsung phones matching your criteria. Please try rephrasing your question."
                return result
            
            # Generate review based on search strategy
            if search_strategy == 'comparison':
                result['review'] = self._generate_comparison_review(phones_data, query)
            elif search_strategy == 'price_range':
                result['review'] = self._generate_price_review(phones_data, query, context.get('price_limit'))
            elif search_strategy == 'specific_models':
                result['review'] = self._generate_specific_model_review(phones_data, query)
            else:
                result['review'] = self._generate_general_review(phones_data, query)
            
            # Generate recommendations
            result['recommendations'] = self._generate_recommendations(phones_data, query)
            
            return result
            
        except Exception as e:
            logger.error(f"Error in Review Generator Agent: {e}")
            return {
                'agent': self.name,
                'error': str(e),
                'review': 'Sorry, I encountered an error while generating the review.',
                'recommendations': []
            }
    
    def _generate_comparison_review(self, phones: List[Dict], query: str) -> str:
        """Generate comparison review for multiple phones."""
        if len(phones) < 2:
            return self._generate_general_review(phones, query)
        
        phone1, phone2 = phones[0], phones[1]
        
        review = f"Comparing {phone1['model_name']} and {phone2['model_name']}:\n\n"
        
        # Camera comparison
        if phone1.get('camera') and phone2.get('camera'):
            review += "**Camera Performance:**\n"
            review += f"• {phone1['model_name']}: {phone1['camera']}\n"
            review += f"• {phone2['model_name']}: {phone2['camera']}\n"
            
            if '200' in phone1.get('camera', '') and '108' in phone2.get('camera', ''):
                review += f"The {phone1['model_name']} has a significantly better main camera sensor.\n\n"
            elif '108' in phone1.get('camera', '') and '50' in phone2.get('camera', ''):
                review += f"The {phone1['model_name']} offers superior camera resolution.\n\n"
            else:
                review += "Both phones offer competitive camera systems.\n\n"
        
        # Battery comparison
        if phone1.get('battery') and phone2.get('battery'):
            review += "**Battery Life:**\n"
            review += f"• {phone1['model_name']}: {phone1['battery']}\n"
            review += f"• {phone2['model_name']}: {phone2['battery']}\n"
            
            battery1 = self._extract_number(phone1.get('battery', ''))
            battery2 = self._extract_number(phone2.get('battery', ''))
            
            if battery1 and battery2:
                if battery1 > battery2:
                    review += f"The {phone1['model_name']} offers better battery capacity.\n\n"
                elif battery2 > battery1:
                    review += f"The {phone2['model_name']} provides longer battery life.\n\n"
                else:
                    review += "Both phones have similar battery capacity.\n\n"
        
        # Display comparison
        if phone1.get('display') and phone2.get('display'):
            review += "**Display Quality:**\n"
            review += f"• {phone1['model_name']}: {phone1['display']}\n"
            review += f"• {phone2['model_name']}: {phone2['display']}\n\n"
        
        return review
    
    def _generate_price_review(self, phones: List[Dict], query: str, price_limit: Optional[int]) -> str:
        """Generate price-focused review."""
        review = f"Samsung phones under ${price_limit}:\n\n" if price_limit else "Samsung phones by price:\n\n"
        
        # Sort by price if available
        phones_with_price = [p for p in phones if p.get('price')]
        
        for phone in phones_with_price[:3]:
            review += f"**{phone['model_name']}** - {phone['price']}\n"
            
            # Highlight key features
            if phone.get('camera'):
                review += f"• Camera: {phone['camera']}\n"
            if phone.get('battery'):
                review += f"• Battery: {phone['battery']}\n"
            if phone.get('display'):
                review += f"• Display: {phone['display']}\n"
            
            # Value assessment
            price_num = self._extract_number(phone.get('price', ''))
            if price_num:
                if price_num < 500:
                    review += "• Excellent value for budget-conscious users\n"
                elif price_num < 800:
                    review += "• Good balance of features and price\n"
                else:
                    review += "• Premium device with flagship features\n"
            
            review += "\n"
        
        return review
    
    def _generate_specific_model_review(self, phones: List[Dict], query: str) -> str:
        """Generate review for specific phone models."""
        if not phones:
            return "The specified Samsung phone model was not found in our database."
        
        phone = phones[0]
        review = f"**{phone['model_name']} Specifications:**\n\n"
        
        # Detailed specs
        specs = [
            ('Display', 'display'),
            ('Camera System', 'camera'),
            ('Battery', 'battery'),
            ('RAM', 'ram'),
            ('Storage', 'storage'),
            ('Price', 'price'),
            ('Release Date', 'release_date')
        ]
        
        for label, key in specs:
            value = phone.get(key)
            if value:
                review += f"**{label}:** {value}\n"
        
        # Add analysis
        review += "\n**Analysis:**\n"
        
        if 'ultra' in phone['model_name'].lower():
            review += "This is a flagship model with premium features and performance.\n"
        elif any(series in phone['model_name'].lower() for series in ['a5', 'a7', 'a3']):
            review += "This is a mid-range device offering good value for money.\n"
        elif 'fold' in phone['model_name'].lower() or 'flip' in phone['model_name'].lower():
            review += "This is an innovative foldable device with unique form factor.\n"
        
        return review
    
    def _generate_general_review(self, phones: List[Dict], query: str) -> str:
        """Generate general review."""
        if not phones:
            return "No Samsung phones found matching your criteria."
        
        query_lower = query.lower()
        
        if 'camera' in query_lower or 'photo' in query_lower:
            return self._generate_camera_focused_review(phones)
        elif 'battery' in query_lower:
            return self._generate_battery_focused_review(phones)
        elif 'gaming' in query_lower or 'performance' in query_lower:
            return self._generate_performance_review(phones)
        else:
            return self._generate_overview_review(phones)
    
    def _generate_camera_focused_review(self, phones: List[Dict]) -> str:
        """Generate camera-focused review."""
        review = "**Samsung Phones for Photography:**\n\n"
        
        for phone in phones[:3]:
            review += f"**{phone['model_name']}**\n"
            if phone.get('camera'):
                review += f"Camera: {phone['camera']}\n"
                
                # Camera analysis
                if '200' in phone.get('camera', ''):
                    review += "• Exceptional 200MP main sensor for ultra-detailed photos\n"
                elif '108' in phone.get('camera', ''):
                    review += "• High-resolution 108MP sensor for detailed shots\n"
                elif '50' in phone.get('camera', ''):
                    review += "• Reliable 50MP main camera for everyday photography\n"
                
                if 'ultrawide' in phone.get('camera', '').lower():
                    review += "• Ultrawide lens for landscape and group photos\n"
                if 'telephoto' in phone.get('camera', '').lower():
                    review += "• Telephoto lens for zoom photography\n"
            
            if phone.get('price'):
                review += f"Price: {phone['price']}\n"
            
            review += "\n"
        
        return review
    
    def _generate_battery_focused_review(self, phones: List[Dict]) -> str:
        """Generate battery-focused review."""
        review = "**Samsung Phones for Long Battery Life:**\n\n"
        
        for phone in phones[:3]:
            review += f"**{phone['model_name']}**\n"
            if phone.get('battery'):
                review += f"Battery: {phone['battery']}\n"
                
                battery_capacity = self._extract_number(phone.get('battery', ''))
                if battery_capacity:
                    if battery_capacity >= 5000:
                        review += "• Excellent battery life for all-day usage\n"
                    elif battery_capacity >= 4000:
                        review += "• Good battery life for regular usage\n"
                    else:
                        review += "• Moderate battery life, suitable for light usage\n"
            
            if phone.get('display'):
                review += f"Display: {phone['display']}\n"
            
            if phone.get('price'):
                review += f"Price: {phone['price']}\n"
            
            review += "\n"
        
        return review
    
    def _generate_performance_review(self, phones: List[Dict]) -> str:
        """Generate performance-focused review."""
        review = "**Samsung Phones for Performance:**\n\n"
        
        for phone in phones[:3]:
            review += f"**{phone['model_name']}**\n"
            
            if phone.get('ram'):
                review += f"RAM: {phone['ram']}\n"
                
                ram_size = self._extract_number(phone.get('ram', ''))
                if ram_size:
                    if ram_size >= 12:
                        review += "• Excellent for multitasking and gaming\n"
                    elif ram_size >= 8:
                        review += "• Good for most apps and moderate gaming\n"
                    else:
                        review += "• Suitable for basic usage\n"
            
            if phone.get('storage'):
                review += f"Storage: {phone['storage']}\n"
            
            if 'ultra' in phone['model_name'].lower():
                review += "• Flagship performance with top-tier processor\n"
            
            if phone.get('price'):
                review += f"Price: {phone['price']}\n"
            
            review += "\n"
        
        return review
    
    def _generate_overview_review(self, phones: List[Dict]) -> str:
        """Generate general overview review."""
        review = "**Samsung Phone Overview:**\n\n"
        
        top_phone = phones[0]
        review += f"**Top Recommendation: {top_phone['model_name']}**\n"
        
        if top_phone.get('price'):
            review += f"Price: {top_phone['price']}\n"
        if top_phone.get('display'):
            review += f"Display: {top_phone['display']}\n"
        if top_phone.get('camera'):
            review += f"Camera: {top_phone['camera']}\n"
        if top_phone.get('battery'):
            review += f"Battery: {top_phone['battery']}\n"
        
        if len(phones) > 1:
            review += f"\n**Other Options:**\n"
            for phone in phones[1:3]:
                review += f"• {phone['model_name']}"
                if phone.get('price'):
                    review += f" - {phone['price']}"
                review += "\n"
        
        return review
    
    def _generate_recommendations(self, phones: List[Dict], query: str) -> List[str]:
        """Generate specific recommendations."""
        recommendations = []
        
        query_lower = query.lower()
        
        if phones:
            top_phone = phones[0]
            
            if 'budget' in query_lower or 'cheap' in query_lower:
                recommendations.append(f"For budget-conscious buyers, consider the {top_phone['model_name']}")
            elif 'photography' in query_lower or 'camera' in query_lower:
                recommendations.append(f"For photography enthusiasts, the {top_phone['model_name']} offers excellent camera performance")
            elif 'gaming' in query_lower or 'performance' in query_lower:
                recommendations.append(f"For gaming and performance, the {top_phone['model_name']} provides flagship-level power")
            else:
                recommendations.append(f"The {top_phone['model_name']} is an excellent choice for your needs")
            
            # Add specific feature recommendations
            if len(phones) > 1:
                if any('fold' in p['model_name'].lower() for p in phones):
                    recommendations.append("Consider a foldable model for innovative design and productivity")
                
                if any(self._extract_number(p.get('battery', '')) >= 5000 for p in phones):
                    battery_phone = next(p for p in phones if self._extract_number(p.get('battery', '')) >= 5000)
                    recommendations.append(f"For all-day battery life, choose the {battery_phone['model_name']}")
        
        return recommendations
    
    def _extract_number(self, text: str) -> Optional[int]:
        """Extract first number from text."""
        import re
        if not text:
            return None
        match = re.search(r'(\d+)', text)
        return int(match.group(1)) if match else None


class MultiAgentSystem:
    """Coordinator for multiple agents."""
    
    def __init__(self, database):
        self.database = database
        self.agents = {
            'data_extractor': DataExtractorAgent(database),
            'review_generator': ReviewGeneratorAgent()
        }
        
    def process_query(self, query: str) -> Dict[str, Any]:
        """Process query through multiple agents."""
        try:
            logger.info(f"Processing query through multi-agent system: {query}")
            
            # Step 1: Extract relevant data
            data_result = self.agents['data_extractor'].process(query, {})
            
            # Step 2: Generate review and recommendations
            review_result = self.agents['review_generator'].process(query, data_result)
            
            # Combine results
            final_result = {
                'query': query,
                'data_extraction': data_result,
                'review_generation': review_result,
                'phones_found': data_result.get('phones_found', 0),
                'success': True
            }
            
            return final_result
            
        except Exception as e:
            logger.error(f"Error in multi-agent system: {e}")
            return {
                'query': query,
                'error': str(e),
                'success': False
            }


if __name__ == "__main__":
    # Test the multi-agent system
    from database.database import SQLitePhoneDatabase
    
    print("Testing Multi-Agent System...")
    
    # Use SQLite for testing
    db = SQLitePhoneDatabase("../database/samsung_phones.db")
    if not db.connect():
        print("Failed to connect to database")
        exit(1)
    
    # Initialize multi-agent system
    mas = MultiAgentSystem(db)
    
    # Test queries
    test_queries = [
        "Compare Galaxy S23 Ultra and S22 Ultra",
        "Best Samsung phone for photography",
        "Samsung phones under $800",
        "Galaxy S23 Ultra specifications"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        result = mas.process_query(query)
        
        if result['success']:
            print(f"Review: {result['review_generation']['review']}")
            if result['review_generation']['recommendations']:
                print(f"Recommendations: {result['review_generation']['recommendations']}")
        else:
            print(f"Error: {result['error']}")
        
        print("=" * 50)