from abc import ABC, abstractmethod
from typing import List, Tuple
from datetime import datetime
from app.models.trip import Trip, SearchRequest


class BaseScraper(ABC):
    """Base scraper interface for all bus company scrapers"""
    
    @property
    @abstractmethod
    def company_name(self) -> str:
        """Return the company name"""
        pass
    
    @property
    @abstractmethod
    def supported_cities(self) -> Tuple[set, set]:
        """Return tuple of (origin_cities, destination_cities)"""
        pass
    
    @abstractmethod
    def is_valid_route(self, nereden: str, nereye: str) -> Tuple[bool, str]:
        """
        Check if the route is valid for this company
        
        Args:
            nereden: Origin city
            nereye: Destination city
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        pass
    
    @abstractmethod
    def search_trips(self, nereden: str, nereye: str, tarih: datetime) -> List[Trip]:
        """
        Search for trips
        
        Args:
            nereden: Origin city
            nereye: Destination city
            tarih: datetime object
        
        Returns:
            List of Trip objects
        """
        pass
    
    def cleanup(self):
        """Cleanup resources (close browser, etc.)"""
        pass

