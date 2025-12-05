from typing import Optional, Tuple


CITY_ALIASES = {
    "istanbul": ["istanbul", "esenler", "alibeyköy", "dudullu", "harem"],
    "ankara": ["ankara"],
    "izmir": ["izmir"],
    "denizli": ["denizli"],
    "antalya": ["antalya"],
    "bursa": ["bursa"],
    "eskisehir": ["eskisehir", "eskişehir"],
}


def normalize_city(city: str) -> str:
    """Normalize city name"""
    city_lower = city.lower().strip()
    
    for normalized, aliases in CITY_ALIASES.items():
        if city_lower in aliases:
            return normalized.title()
    
    return city.strip()


def match_city(city: str, city_list: list) -> Optional[str]:
    """Match city name against a list of cities (case-insensitive partial match)"""
    city_lower = city.lower().strip()
    
    for c in city_list:
        c_lower = c.lower()
        if city_lower == c_lower or city_lower in c_lower or c_lower in city_lower:
            return c
    
    return None


def validate_route(nereden: str, nereye: str) -> Tuple[bool, Optional[str]]:
    """Validate if route is valid (origin and destination should be different)"""
    if not nereden or not nereye:
        return False, "Kalkış ve varış şehirleri belirtilmelidir"
    
    if nereden.lower() == nereye.lower():
        return False, "Kalkış ve varış şehirleri aynı olamaz"
    
    return True, None

