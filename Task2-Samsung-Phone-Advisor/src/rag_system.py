"""
RAG (Retrieval-Augmented Generation) Module
Handles retrieval of phone specifications and context for question answering
"""

import numpy as np
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
from typing import List, Dict, Any, Optional
import logging
import re

logger = logging.getLogger(__name__)


class PhoneRAG:
    """RAG system for Samsung phone specifications."""
    
    def __init__(self, database, model_name='all-MiniLM-L6-v2'):
        """
        Initialize RAG system.
        
        Args:
            database: Database instance (PostgreSQL or SQLite)
            model_name: Sentence transformer model name
        """
        self.database = database
        self.model = SentenceTransformer(model_name)
        self.phone_embeddings = None
        self.phone_texts = None
        self.phone_data = None
        
    def prepare_phone_texts(self, phones_data: List[Dict]) -> List[str]:
        """Convert phone data to searchable text."""
        texts = []
        
        for phone in phones_data:
            # Create comprehensive text representation
            text_parts = [
                f"Model: {phone.get('model_name', '')}",
                f"Display: {phone.get('display', 'N/A')}",
                f"Battery: {phone.get('battery', 'N/A')}",
                f"Camera: {phone.get('camera', 'N/A')}",
                f"RAM: {phone.get('ram', 'N/A')}",
                f"Storage: {phone.get('storage', 'N/A')}",
                f"Price: {phone.get('price', 'N/A')}",
                f"Release Date: {phone.get('release_date', 'N/A')}"
            ]
            
            # Add additional specs if available
            if phone.get('additional_specs'):
                if isinstance(phone['additional_specs'], str):
                    import json
                    try:
                        additional = json.loads(phone['additional_specs'])
                        for key, value in additional.items():
                            if value:
                                text_parts.append(f"{key}: {value}")
                    except:
                        pass
            
            full_text = " | ".join(text_parts)
            texts.append(full_text)
            
        return texts
    
    def build_embeddings(self):
        """Build embeddings for all phones in the database."""
        try:
            # Get all phones from database
            self.phone_data = self.database.get_all_phones(limit=100)
            
            if not self.phone_data:
                logger.warning("No phone data found in database")
                return False
            
            # Convert to searchable texts
            self.phone_texts = self.prepare_phone_texts(self.phone_data)
            
            # Generate embeddings
            logger.info(f"Generating embeddings for {len(self.phone_texts)} phones...")
            self.phone_embeddings = self.model.encode(self.phone_texts)
            
            logger.info("Embeddings built successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error building embeddings: {e}")
            return False
    
    def retrieve_relevant_phones(self, query: str, top_k: int = 5) -> List[Dict]:
        """
        Retrieve most relevant phones for a given query.
        
        Args:
            query: User query
            top_k: Number of top results to return
            
        Returns:
            List of relevant phone data with similarity scores
        """
        if self.phone_embeddings is None or self.phone_data is None:
            if not self.build_embeddings():
                return []
        
        try:
            # Generate query embedding
            query_embedding = self.model.encode([query])
            
            # Calculate similarities
            similarities = cosine_similarity(query_embedding, self.phone_embeddings)[0]
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            # Prepare results
            results = []
            for idx in top_indices:
                if similarities[idx] > 0.1:  # Minimum similarity threshold
                    phone_data = self.phone_data[idx].copy()
                    phone_data['similarity_score'] = float(similarities[idx])
                    phone_data['matched_text'] = self.phone_texts[idx]
                    results.append(phone_data)
            
            return results
            
        except Exception as e:
            logger.error(f"Error retrieving relevant phones: {e}")
            return []
    
    def extract_phone_specs(self, query: str) -> Dict[str, Any]:
        """
        Extract specific phone specifications based on query.
        
        Args:
            query: User query about phone specs
            
        Returns:
            Dictionary with extracted specifications
        """
        # Get relevant phones
        relevant_phones = self.retrieve_relevant_phones(query, top_k=3)
        
        if not relevant_phones:
            return {'error': 'No relevant phones found'}
        
        # Extract specific information based on query type
        query_lower = query.lower()
        result = {'query': query, 'phones': relevant_phones}
        
        # Identify query intent
        if any(word in query_lower for word in ['spec', 'specification', 'detail']):
            result['intent'] = 'specifications'
            result['response_type'] = 'detailed_specs'
        elif any(word in query_lower for word in ['compare', 'vs', 'versus', 'difference']):
            result['intent'] = 'comparison'
            result['response_type'] = 'comparison'
        elif any(word in query_lower for word in ['price', 'cost', 'budget', 'cheap', 'expensive']):
            result['intent'] = 'price_inquiry'
            result['response_type'] = 'price_focused'
        elif any(word in query_lower for word in ['camera', 'photo', 'photography']):
            result['intent'] = 'camera_focused'
            result['response_type'] = 'camera_specs'
        elif any(word in query_lower for word in ['battery', 'power', 'life']):
            result['intent'] = 'battery_focused'
            result['response_type'] = 'battery_specs'
        else:
            result['intent'] = 'general'
            result['response_type'] = 'general_info'
        
        return result
    
    def format_phone_response(self, phone_data: Dict) -> str:
        """Format phone data into readable response."""
        response_parts = []
        
        # Basic info
        response_parts.append(f"**{phone_data.get('model_name', 'Unknown Model')}**")
        
        if phone_data.get('price'):
            response_parts.append(f"Price: {phone_data['price']}")
        
        if phone_data.get('display'):
            response_parts.append(f"Display: {phone_data['display']}")
        
        if phone_data.get('camera'):
            response_parts.append(f"Camera: {phone_data['camera']}")
        
        if phone_data.get('battery'):
            response_parts.append(f"Battery: {phone_data['battery']}")
        
        if phone_data.get('ram'):
            response_parts.append(f"RAM: {phone_data['ram']}")
        
        if phone_data.get('storage'):
            response_parts.append(f"Storage: {phone_data['storage']}")
        
        return "\n".join(response_parts)
    
    def answer_query(self, query: str) -> Dict[str, Any]:
        """
        Generate comprehensive answer for user query.
        
        Args:
            query: User question
            
        Returns:
            Structured response with answer and metadata
        """
        try:
            # Extract relevant information
            spec_data = self.extract_phone_specs(query)
            
            if 'error' in spec_data:
                return {
                    'answer': "I couldn't find any relevant Samsung phones for your query. Please try rephrasing your question.",
                    'confidence': 0.0,
                    'phones_found': 0
                }
            
            relevant_phones = spec_data['phones']
            response_type = spec_data['response_type']
            
            # Generate response based on type
            if response_type == 'comparison' and len(relevant_phones) >= 2:
                answer = self._generate_comparison_response(relevant_phones[:2])
            elif response_type == 'price_focused':
                answer = self._generate_price_response(relevant_phones)
            elif response_type == 'camera_specs':
                answer = self._generate_camera_response(relevant_phones)
            elif response_type == 'battery_specs':
                answer = self._generate_battery_response(relevant_phones)
            else:
                answer = self._generate_general_response(relevant_phones)
            
            return {
                'answer': answer,
                'confidence': relevant_phones[0]['similarity_score'] if relevant_phones else 0.0,
                'phones_found': len(relevant_phones),
                'intent': spec_data['intent'],
                'response_type': response_type
            }
            
        except Exception as e:
            logger.error(f"Error answering query: {e}")
            return {
                'answer': "I encountered an error while processing your query. Please try again.",
                'confidence': 0.0,
                'phones_found': 0
            }
    
    def _generate_comparison_response(self, phones: List[Dict]) -> str:
        """Generate comparison response for two phones."""
        if len(phones) < 2:
            return self._generate_general_response(phones)
        
        phone1, phone2 = phones[0], phones[1]
        
        response = f"**Comparison: {phone1['model_name']} vs {phone2['model_name']}**\n\n"
        
        # Compare key specs
        comparisons = [
            ('Display', 'display'),
            ('Camera', 'camera'),
            ('Battery', 'battery'),
            ('RAM', 'ram'),
            ('Storage', 'storage'),
            ('Price', 'price')
        ]
        
        for label, key in comparisons:
            val1 = phone1.get(key, 'N/A')
            val2 = phone2.get(key, 'N/A')
            response += f"**{label}:**\n- {phone1['model_name']}: {val1}\n- {phone2['model_name']}: {val2}\n\n"
        
        return response
    
    def _generate_price_response(self, phones: List[Dict]) -> str:
        """Generate price-focused response."""
        if not phones:
            return "No phones found with pricing information."
        
        response = "**Samsung Phones - Price Information:**\n\n"
        
        for phone in phones[:3]:
            price = phone.get('price', 'Price not available')
            response += f"**{phone['model_name']}**\n"
            response += f"Price: {price}\n"
            if phone.get('display'):
                response += f"Display: {phone['display']}\n"
            if phone.get('camera'):
                response += f"Camera: {phone['camera']}\n"
            response += "\n"
        
        return response
    
    def _generate_camera_response(self, phones: List[Dict]) -> str:
        """Generate camera-focused response."""
        response = "**Samsung Phones - Camera Information:**\n\n"
        
        for phone in phones[:3]:
            response += f"**{phone['model_name']}**\n"
            response += f"Camera: {phone.get('camera', 'Camera specs not available')}\n"
            if phone.get('price'):
                response += f"Price: {phone['price']}\n"
            response += "\n"
        
        return response
    
    def _generate_battery_response(self, phones: List[Dict]) -> str:
        """Generate battery-focused response."""
        response = "**Samsung Phones - Battery Information:**\n\n"
        
        for phone in phones[:3]:
            response += f"**{phone['model_name']}**\n"
            response += f"Battery: {phone.get('battery', 'Battery info not available')}\n"
            if phone.get('display'):
                response += f"Display: {phone['display']}\n"
            if phone.get('price'):
                response += f"Price: {phone['price']}\n"
            response += "\n"
        
        return response
    
    def _generate_general_response(self, phones: List[Dict]) -> str:
        """Generate general response."""
        if not phones:
            return "No relevant Samsung phones found."
        
        phone = phones[0]  # Use most relevant phone
        
        response = self.format_phone_response(phone)
        
        # Add additional phones if available
        if len(phones) > 1:
            response += f"\n\n**Other relevant options:**\n"
            for other_phone in phones[1:3]:
                response += f"• {other_phone['model_name']}"
                if other_phone.get('price'):
                    response += f" - {other_phone['price']}"
                response += "\n"
        
        return response


if __name__ == "__main__":
    # Test the RAG system
    from database.database import SQLitePhoneDatabase
    
    print("Testing RAG system...")
    
    # Use SQLite for testing
    db = SQLitePhoneDatabase("../database/samsung_phones.db")
    if not db.connect():
        print("Failed to connect to database")
        exit(1)
    
    # Initialize RAG system
    rag = PhoneRAG(db)
    
    # Test queries
    test_queries = [
        "What are the specs of Samsung Galaxy S23 Ultra?",
        "Compare Galaxy S23 Ultra and S22 Ultra",
        "Which Samsung phone has the best camera?",
        "Samsung phones under $800"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        result = rag.answer_query(query)
        print(f"Answer: {result['answer']}")
        print(f"Confidence: {result['confidence']:.2f}")
        print(f"Phones found: {result['phones_found']}")
        print("=" * 50)