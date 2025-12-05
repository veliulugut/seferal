from typing import List
from app.models.trip import Trip


class TripMerger:
    """Merge and deduplicate trips from multiple sources"""
    
    @staticmethod
    def merge(trips_list: List[List[Trip]]) -> List[Trip]:
        """Merge multiple trip lists into one"""
        all_trips = []
        for trips in trips_list:
            all_trips.extend(trips)
        return all_trips
    
    @staticmethod
    def deduplicate(trips: List[Trip]) -> List[Trip]:
        """Remove duplicate trips based on sefer_takip_no, time, and company"""
        seen = set()
        unique_trips = []
        
        for trip in trips:
            key = (
                trip.sefer_takip_no,
                trip.kalkis_saati,
                trip.firma
            )
            
            if key not in seen:
                seen.add(key)
                unique_trips.append(trip)
        
        return unique_trips
    
    @staticmethod
    def merge_and_deduplicate(trips_list: List[List[Trip]]) -> List[Trip]:
        """Merge and deduplicate trips"""
        merged = TripMerger.merge(trips_list)
        return TripMerger.deduplicate(merged)

