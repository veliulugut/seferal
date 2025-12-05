from datetime import datetime
from app.scraper.manager import ScraperManager
from app.models.trip import SearchResponse
import json

if __name__ == "__main__":
    manager = ScraperManager()
    
    nereden = "İSTANBUL-AVRUPA(ESENLER)"
    nereye = "DENİZLİ"
    tarih = datetime(2025, 12, 8)
    companies = ["anadolu"]
    
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
    
    print(f"\n{tarih.strftime('%Y-%m-%d')}: {result.toplam_sefer} sefer bulundu")
    print(f"Toplam boş koltuk: {output_data['bos_koltuk_toplam']}")
    print("\n=== Sefer Listesi ===")
    for i, trip in enumerate(result.seferler, 1):
        firma = trip.firma or "Bilinmiyor"
        saat = trip.kalkis_saati or "N/A"
        fiyat = trip.fiyat or "N/A"
        bos = trip.koltuk_plani.bos if trip.koltuk_plani else 0
        toplam = trip.koltuk_plani.toplam_koltuk if trip.koltuk_plani else 0
        durum = trip.sefer_tipi or "Normal"
        print(f"{i:2d}. [{firma:20s}] {saat:5s} - {fiyat:>6s} TL - Boş: {bos:2d}/{toplam:2d} - {durum}")
    
    print("\n=== JSON Output ===")
    json_output = json.dumps([output_data], ensure_ascii=False, indent=2)
    print(json_output)
