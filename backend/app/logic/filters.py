from typing import List, Optional
from datetime import datetime
from app.models.trip import Trip


class TripFilter:
    """Filter trips based on various criteria"""
    
    @staticmethod
    def filter_by_time(trips: List[Trip], min_time: Optional[str] = None, max_time: Optional[str] = None) -> List[Trip]:
        """Filter trips by departure time"""
        filtered = trips
        
        if min_time:
            filtered = [t for t in filtered if t.kalkis_saati and t.kalkis_saati >= min_time]
        
        if max_time:
            filtered = [t for t in filtered if t.kalkis_saati and t.kalkis_saati <= max_time]
        
        return filtered
    
    @staticmethod
    def filter_by_price(trips: List[Trip], max_price: Optional[float] = None) -> List[Trip]:
        """Filter trips by maximum price"""
        if not max_price:
            return trips
        
        filtered = []
        for trip in trips:
            if trip.fiyat:
                try:
                    price = float(trip.fiyat.replace("TL", "").replace(",", ".").strip())
                    if price <= max_price:
                        filtered.append(trip)
                except:
                    filtered.append(trip)
            else:
                filtered.append(trip)
        
        return filtered
    
    @staticmethod
    def filter_by_available_seats(trips: List[Trip], min_seats: int = 1) -> List[Trip]:
        """Filter trips by minimum available seats"""
        filtered = []
        for trip in trips:
            if trip.koltuk_plani and trip.koltuk_plani.bos >= min_seats:
                filtered.append(trip)
            elif not trip.koltuk_plani:
                filtered.append(trip)
        
        return filtered
    
    @staticmethod
    def filter_by_company(trips: List[Trip], companies: List[str]) -> List[Trip]:
        """Filter trips by company names"""
        if not companies:
            return trips
        
        company_lower = [c.lower() for c in companies]
        filtered = []
        for trip in trips:
            if trip.firma and trip.firma.lower() in company_lower:
                filtered.append(trip)
        
        return filtered
    
    @staticmethod
    def filter_by_seat_type(trips: List[Trip], seat_type: Optional[str] = None) -> List[Trip]:
        """Filter trips by seat type (tekli/ciftli)"""
        if not seat_type:
            return trips
        
        filtered = []
        for trip in trips:
            if trip.koltuk_plani and trip.koltuk_plani.bos_koltuklar:
                has_seat_type = any(
                    koltuk.get('koltuk_tipi') == seat_type 
                    for koltuk in trip.koltuk_plani.bos_koltuklar
                )
                if has_seat_type:
                    filtered.append(trip)
            else:
                filtered.append(trip)
        
        return filtered
    
    @staticmethod
    def filter_errors(trips: List[Trip]) -> List[Trip]:
        """Remove trips with errors"""
        return [t for t in trips if not t.error]

