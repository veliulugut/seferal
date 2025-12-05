from typing import List, Dict, Optional
from datetime import datetime
from app.scraper.base import BaseScraper
from app.models.trip import Trip, SearchResponse
from app.scraper.sarikiz import SarikizScraper
from app.scraper.uludag import UludagScraper
from app.scraper.anadolu import AnadoluScraper


class ScraperManager:
    """Manages multiple bus company scrapers"""
    
    _scrapers: Dict[str, BaseScraper] = {}
    
    def __init__(self):
        self._scrapers = {
            "sarikiz": SarikizScraper,
            "uludag": UludagScraper,
            "anadolu": AnadoluScraper,
        }
    
    def get_scraper(self, company: str, headless: bool = False) -> Optional[BaseScraper]:
        """Get scraper instance for a company"""
        scraper_class = self._scrapers.get(company.lower())
        if scraper_class:
            return scraper_class(headless=headless)
        return None
    
    def get_available_companies(self) -> List[str]:
        """Get list of available company names"""
        return list(self._scrapers.keys())
    
    def search_all(self, nereden: str, nereye: str, tarih: datetime, companies: Optional[List[str]] = None) -> SearchResponse:
        """
        Search trips from all or specified companies
        
        Args:
            nereden: Origin city
            nereye: Destination city
            tarih: datetime object
            companies: List of company names to search (None = all)
        
        Returns:
            SearchResponse with all trips
        """
        if companies is None:
            companies = self.get_available_companies()
        
        all_trips = []
        errors = []
        
        for company in companies:
            scraper = self.get_scraper(company, headless=False)
            if not scraper:
                errors.append(f"Unknown company: {company}")
                continue

            try:
                trips = scraper.search_trips(nereden, nereye, tarih)
                all_trips.extend(trips)
            except Exception as e:
                errors.append(f"{company}: {str(e)}")
            finally:
                if scraper:
                    scraper.cleanup()
        
        return SearchResponse(
            nereden=nereden,
            nereye=nereye,
            tarih=tarih.strftime("%Y-%m-%d"),
            toplam_sefer=len(all_trips),
            seferler=all_trips,
            error="; ".join(errors) if errors else None
        )

