from typing import List
from app.models.trip import Trip


class TripRanker:
    """Rank trips by various criteria"""
    
    @staticmethod
    def rank_by_price(trips: List[Trip], ascending: bool = True) -> List[Trip]:
        """Rank trips by price"""
        def get_price(trip: Trip) -> float:
            if not trip.fiyat:
                return float('inf') if ascending else float('-inf')
            try:
                return float(trip.fiyat.replace("TL", "").replace(",", ".").strip())
            except:
                return float('inf') if ascending else float('-inf')
        
        return sorted(trips, key=get_price, reverse=not ascending)
    
    @staticmethod
    def rank_by_departure_time(trips: List[Trip], ascending: bool = True) -> List[Trip]:
        """Rank trips by departure time"""
        def get_time(trip: Trip) -> str:
            return trip.kalkis_saati or ("99:99" if ascending else "00:00")
        
        return sorted(trips, key=get_time, reverse=not ascending)
    
    @staticmethod
    def rank_by_available_seats(trips: List[Trip], descending: bool = True) -> List[Trip]:
        """Rank trips by number of available seats"""
        def get_seats(trip: Trip) -> int:
            if trip.koltuk_plani:
                return trip.koltuk_plani.bos
            return 0
        
        return sorted(trips, key=get_seats, reverse=descending)
    
    @staticmethod
    def rank_by_score(trips: List[Trip], 
                      price_weight: float = 0.4,
                      time_weight: float = 0.3,
                      seats_weight: float = 0.3) -> List[Trip]:
        """Rank trips by composite score"""
        def calculate_score(trip: Trip) -> float:
            score = 0.0
            
            if trip.fiyat:
                try:
                    price = float(trip.fiyat.replace("TL", "").replace(",", ".").strip())
                    normalized_price = 1.0 / (1.0 + price / 1000.0)
                    score += normalized_price * price_weight
                except:
                    pass
            
            if trip.kalkis_saati:
                try:
                    hour, minute = map(int, trip.kalkis_saati.split(":"))
                    time_score = 1.0 - abs(hour - 12) / 12.0
                    score += time_score * time_weight
                except:
                    pass
            
            if trip.koltuk_plani:
                seats_score = min(trip.koltuk_plani.bos / 50.0, 1.0)
                score += seats_score * seats_weight
            
            return score
        
        return sorted(trips, key=calculate_score, reverse=True)

