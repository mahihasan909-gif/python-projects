"""
Samsung Phone Advisor - Web Scraper Module
Scrapes Samsung phone data from GSMArena
"""

import requests
from bs4 import BeautifulSoup
import time
import pandas as pd
import re
from urllib.parse import urljoin, urlparse
from dataclasses import dataclass
from typing import List, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PhoneData:
    """Data class for Samsung phone specifications."""
    model_name: str
    release_date: Optional[str] = None
    display: Optional[str] = None
    battery: Optional[str] = None
    camera: Optional[str] = None
    ram: Optional[str] = None
    storage: Optional[str] = None
    price: Optional[str] = None
    url: Optional[str] = None
    additional_specs: Optional[dict] = None


class GSMArenaSeamScraper:
    """Scraper for Samsung phones from GSMArena."""
    
    def __init__(self):
        self.base_url = "https://www.gsmarena.com"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.phones_data = []
    
    def get_samsung_phone_list(self, max_phones=30):
        """Get list of Samsung phones from GSMArena."""
        samsung_url = f"{self.base_url}/samsung-phones-9.php"
        
        try:
            response = self.session.get(samsung_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            phone_links = []
            
            # Find phone listings
            phone_elements = soup.find_all('div', class_='makers')
            if phone_elements:
                for phone_div in phone_elements:
                    links = phone_div.find_all('a')
                    for link in links:
                        if len(phone_links) >= max_phones:
                            break
                        phone_url = urljoin(self.base_url, link.get('href'))
                        phone_name = link.find('strong')
                        if phone_name:
                            phone_links.append({
                                'name': phone_name.text.strip(),
                                'url': phone_url
                            })
                    if len(phone_links) >= max_phones:
                        break
            
            logger.info(f"Found {len(phone_links)} Samsung phones")
            return phone_links[:max_phones]
            
        except Exception as e:
            logger.error(f"Error getting Samsung phone list: {e}")
            return []
    
    def scrape_phone_details(self, phone_url, phone_name):
        """Scrape detailed specifications for a specific phone."""
        try:
            response = self.session.get(phone_url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            phone_data = PhoneData(model_name=phone_name, url=phone_url)
            
            # Extract specifications
            spec_tables = soup.find_all('table', cellspacing='0')
            
            for table in spec_tables:
                rows = table.find_all('tr')
                for row in rows:
                    cells = row.find_all(['td', 'th'])
                    if len(cells) >= 2:
                        spec_name = cells[0].get_text(strip=True).lower()
                        spec_value = cells[1].get_text(strip=True)
                        
                        # Map specifications to our data structure
                        if 'display' in spec_name or 'screen' in spec_name:
                            if not phone_data.display:
                                phone_data.display = spec_value
                        elif 'battery' in spec_name:
                            phone_data.battery = spec_value
                        elif 'camera' in spec_name and 'main' in spec_name:
                            phone_data.camera = spec_value
                        elif 'memory' in spec_name or 'ram' in spec_name:
                            if 'gb' in spec_value.lower():
                                phone_data.ram = spec_value
                        elif 'storage' in spec_name or ('internal' in spec_name and 'gb' in spec_value.lower()):
                            phone_data.storage = spec_value
                        elif 'announced' in spec_name or 'release' in spec_name:
                            phone_data.release_date = spec_value
            
            # Try to extract price (often not available on GSMArena)
            price_elem = soup.find('span', class_='price-tag')
            if price_elem:
                phone_data.price = price_elem.get_text(strip=True)
            
            # Add some fallback data extraction
            if not phone_data.display:
                display_elem = soup.find('td', {'data-spec': 'displaysize'})
                if display_elem:
                    phone_data.display = display_elem.get_text(strip=True)
            
            return phone_data
            
        except Exception as e:
            logger.error(f"Error scraping {phone_name}: {e}")
            return PhoneData(model_name=phone_name, url=phone_url)
    
    def scrape_all_phones(self, max_phones=30):
        """Scrape all Samsung phones."""
        phone_links = self.get_samsung_phone_list(max_phones)
        
        logger.info(f"Starting to scrape {len(phone_links)} phones...")
        
        for i, phone_info in enumerate(phone_links, 1):
            logger.info(f"Scraping {i}/{len(phone_links)}: {phone_info['name']}")
            
            phone_data = self.scrape_phone_details(phone_info['url'], phone_info['name'])
            self.phones_data.append(phone_data)
            
            # Be respectful to the server
            time.sleep(1)
        
        logger.info(f"Completed scraping {len(self.phones_data)} phones")
        return self.phones_data
    
    def save_to_csv(self, filename="samsung_phones_data.csv"):
        """Save scraped data to CSV."""
        if not self.phones_data:
            logger.warning("No phone data to save")
            return
        
        df_data = []
        for phone in self.phones_data:
            df_data.append({
                'model_name': phone.model_name,
                'release_date': phone.release_date,
                'display': phone.display,
                'battery': phone.battery,
                'camera': phone.camera,
                'ram': phone.ram,
                'storage': phone.storage,
                'price': phone.price,
                'url': phone.url
            })
        
        df = pd.DataFrame(df_data)
        df.to_csv(filename, index=False)
        logger.info(f"Data saved to {filename}")
        return df


# Sample phone data for testing (in case scraping fails)
def get_sample_samsung_data():
    """Return sample Samsung phone data for testing."""
    sample_data = [
        {
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
            'model_name': 'Samsung Galaxy Z Fold5',
            'release_date': '2023-08-11',
            'display': '7.6" Foldable Dynamic AMOLED 2X, 120Hz',
            'battery': '4400 mAh',
            'camera': '50 MP main, 12 MP ultrawide, 10 MP telephoto (3x)',
            'ram': '12GB',
            'storage': '256GB, 512GB, 1TB',
            'price': '$1799'
        },
        # Add more sample data...
    ]
    
    # Add more phones to reach ~30 models
    additional_phones = [
        'Galaxy S21 Ultra', 'Galaxy S21', 'Galaxy S21+', 'Galaxy Note 20 Ultra',
        'Galaxy A73 5G', 'Galaxy A53 5G', 'Galaxy A33 5G', 'Galaxy A23',
        'Galaxy Z Flip5', 'Galaxy Z Flip4', 'Galaxy S20 Ultra', 'Galaxy S20',
        'Galaxy Note 10+', 'Galaxy A14', 'Galaxy A04s', 'Galaxy M54 5G',
        'Galaxy F54 5G', 'Galaxy M34 5G', 'Galaxy A34 5G', 'Galaxy A24',
        'Galaxy A14 5G', 'Galaxy A04', 'Galaxy M14 5G', 'Galaxy F14 5G',
        'Galaxy A13', 'Galaxy M13', 'Galaxy A03', 'Galaxy M53 5G'
    ]
    
    for i, phone_name in enumerate(additional_phones[:25]):  # Fill to ~30 total
        sample_data.append({
            'model_name': f'Samsung {phone_name}',
            'release_date': '2022-01-01',
            'display': f'{6.0 + (i % 3) * 0.2:.1f}" AMOLED',
            'battery': f'{3000 + (i % 5) * 500} mAh',
            'camera': f'{48 + (i % 4) * 16} MP main',
            'ram': f'{4 + (i % 3) * 2}GB',
            'storage': f'{64 + (i % 4) * 64}GB',
            'price': f'${300 + i * 25}'
        })
    
    return sample_data


if __name__ == "__main__":
    # Test the scraper
    scraper = GSMArenaSeamScraper()
    
    print("Starting Samsung phone data collection...")
    print("Note: If scraping fails, sample data will be used for testing.")
    
    try:
        # Try to scrape real data
        phones = scraper.scrape_all_phones(max_phones=10)  # Start with 10 for testing
        df = scraper.save_to_csv("database/samsung_phones_scraped.csv")
        print(f"Successfully scraped {len(phones)} phones")
        
    except Exception as e:
        print(f"Scraping failed: {e}")
        print("Using sample data instead...")
        
        # Use sample data
        sample_data = get_sample_samsung_data()
        df = pd.DataFrame(sample_data)
        df.to_csv("database/samsung_phones_sample.csv", index=False)
        print(f"Created sample dataset with {len(sample_data)} phones")
    
    # Display first few entries
    print("\nFirst 5 phone entries:")
    print(df.head() if 'df' in locals() else pd.DataFrame(sample_data).head())