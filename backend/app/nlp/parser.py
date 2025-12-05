from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import re
from app.nlp.gemini_client import GeminiClient


class QueryParser:
    """Parse natural language queries for bus trip searches"""
    
    def __init__(self, gemini_client: Optional[GeminiClient] = None):
        self.gemini_client = gemini_client
    
    def parse(self, query: str) -> Dict[str, Any]:
        """Parse user query to extract search parameters"""
        if self.gemini_client:
            return self.gemini_client.parse_query(query)
        
        return self._simple_parse(query)
    
    def _simple_parse(self, query: str) -> Dict[str, Any]:
        """Simple regex-based parsing fallback"""
        query_lower = query.lower()
        
        nereden = None
        nereye = None
        tarih = None
        saat = None
        firma = None
        
        if "istanbul" in query_lower or "esenler" in query_lower:
            nereden = "İSTANBUL-AVRUPA(ESENLER)"
        elif "ankara" in query_lower:
            nereden = "ANKARA"
        elif "izmir" in query_lower:
            nereden = "İZMİR"
        
        if "denizli" in query_lower:
            nereye = "DENİZLİ"
        elif "ankara" in query_lower and nereden != "ANKARA":
            nereye = "ANKARA"
        elif "izmir" in query_lower and nereden != "İZMİR":
            nereye = "İZMİR"
        
        if "yarın" in query_lower or "tomorrow" in query_lower:
            tarih = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        elif "bugün" in query_lower or "today" in query_lower:
            tarih = datetime.now().strftime("%Y-%m-%d")
        else:
            date_match = re.search(r'(\d{1,2})[./-](\d{1,2})[./-](\d{4})', query)
            if date_match:
                day, month, year = date_match.groups()
                tarih = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        time_match = re.search(r'(\d{1,2}):?(\d{2})?', query)
        if time_match:
            hour = time_match.group(1)
            minute = time_match.group(2) or "00"
            saat = f"{hour.zfill(2)}:{minute}"
        
        return {
            "nereden": nereden,
            "nereye": nereye,
            "tarih": tarih,
            "saat": saat,
            "firma": firma
        }

