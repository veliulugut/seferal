from datetime import datetime
from app.scraper.manager import ScraperManager
from app.models.trip import SearchResponse
import json

if __name__ == "__main__":
    manager = ScraperManager()
    
    nereden = "İSTANBUL(Esenler)"
    nereye = "DENİZLİ"
    tarih = datetime(2025, 12, 6)
    companies = ["sarikiz"]
    
    print(f"=== Arama: {nereden} → {nereye} ===")
    print(f"Tarih: {tarih.strftime('%Y-%m-%d')}")
    print(f"Firmalar: {', '.join(companies)}\n")
    
    result = manager.search_all(
        nereden=nereden,
        nereye=nereye,
        tarih=tarih,
        companies=companies
    )
    
    output_data = {
        "tarih": tarih.strftime("%Y-%m-%d"),
        "toplam_sefer": result.toplam_sefer,
        "bos_koltuk_toplam": sum(
            trip.koltuk_plani.bos if trip.koltuk_plani else 0 
            for trip in result.seferler
        ),
        "seferler": [trip.model_dump() for trip in result.seferler]
    }
    
    print(f"{tarih.strftime('%Y-%m-%d')}: {result.toplam_sefer} sefer bulundu")
    print("\n=== JSON Output ===")
    json_output = json.dumps([output_data], ensure_ascii=False, indent=2)
    print(json_output)
