import os
from typing import Optional, Dict, Any
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()


class GeminiClient:
    """Gemini AI client for natural language processing"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    def generate_content(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """Generate content using Gemini"""
        full_prompt = prompt
        if system_prompt:
            full_prompt = f"{system_prompt}\n\n{prompt}"
        
        try:
            response = self.model.generate_content(full_prompt)
            return response.text
        except Exception as e:
            raise Exception(f"Gemini API error: {str(e)}")
    
    def parse_query(self, user_query: str) -> Dict[str, Any]:
        """Parse user query to extract trip search parameters"""
        system_prompt = os.getenv(
            "GEMINI_SYSTEM_PROMPT",
            """Sen bir otobüs seferi arama asistanısın. Kullanıcının doğal dil sorgusundan şu bilgileri çıkar:
- nereden: Kalkış şehri
- nereye: Varış şehri  
- tarih: Tarih (bugün, yarın, veya spesifik tarih)
- saat: İstenen kalkış saati (opsiyonel)
- firma: Firma adı (opsiyonel)

JSON formatında döndür. Örnek:
{
  "nereden": "İstanbul",
  "nereye": "Ankara",
  "tarih": "2025-12-08",
  "saat": null,
  "firma": null
}"""
        )
        
        prompt = f"Kullanıcı sorgusu: {user_query}\n\nJSON formatında çıkarılan bilgileri döndür."
        
        try:
            response = self.generate_content(prompt, system_prompt)
            import json
            return json.loads(response)
        except Exception as e:
            return {
                "nereden": None,
                "nereye": None,
                "tarih": None,
                "saat": None,
                "firma": None,
                "error": str(e)
            }

