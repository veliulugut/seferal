from typing import Dict, Any, Optional
from datetime import datetime
from app.scraper.manager import ScraperManager
from app.models.trip import SearchResponse
from app.logic.filters import TripFilter
from app.logic.ranking import TripRanker
from app.utils.date import parse_date
from app.utils.location import validate_route


class BusTool:
    """MCP tool for bus trip searches"""
    
    def __init__(self):
        self.manager = ScraperManager()
    
    def search(self, 
               nereden: str, 
               nereye: str, 
               tarih: str,
               companies: Optional[list] = None,
               min_time: Optional[str] = None,
               max_time: Optional[str] = None,
               max_price: Optional[float] = None,
               min_seats: int = 1,
               sort_by: str = "time") -> Dict[str, Any]:
        """Search for bus trips"""
        
        is_valid, error = validate_route(nereden, nereye)
        if not is_valid:
            return {"error": error}
        
        date_obj = parse_date(tarih)
        if not date_obj:
            return {"error": f"Geçersiz tarih formatı: {tarih}"}
        
        result = self.manager.search_all(
            nereden=nereden,
            nereye=nereye,
            tarih=date_obj,
            companies=companies
        )
        
        trips = result.seferler
        
        trips = TripFilter.filter_errors(trips)
        trips = TripFilter.filter_by_time(trips, min_time, max_time)
        trips = TripFilter.filter_by_price(trips, max_price)
        trips = TripFilter.filter_by_available_seats(trips, min_seats)
        
        if sort_by == "price":
            trips = TripRanker.rank_by_price(trips, ascending=True)
        elif sort_by == "seats":
            trips = TripRanker.rank_by_available_seats(trips, descending=True)
        else:
            trips = TripRanker.rank_by_departure_time(trips, ascending=True)
        
        return {
            "nereden": result.nereden,
            "nereye": result.nereye,
            "tarih": result.tarih,
            "toplam_sefer": len(trips),
            "seferler": [trip.model_dump() for trip in trips],
            "error": result.error
        }

