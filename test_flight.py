import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from datetime import datetime
from app.scraper.flightio import FlightioScraper
import json

if __name__ == "__main__":
    scraper = FlightioScraper(headless=False)
    
    try:
        nereden = "IST"
        nereye = "DNZ"
        tarih = datetime(2025, 1, 15)
        adults = 2
        children = 1
        
        print(f"=== Uçak Arama: {nereden} → {nereye} ===")
        print(f"Tarih: {tarih.strftime('%Y-%m-%d')}")
        print(f"Yolcular: {adults} yetişkin, {children} çocuk\n")
        
        result = scraper.search_flights(
            nereden=nereden,
            nereye=nereye,
            tarih=tarih,
            adults=adults,
            children=children
        )
        
        print(f"Toplam Uçuş: {result.toplam_ucus}")
        if result.error:
            print(f"Hata: {result.error}\n")
        
        if result.ucusler:
            print("\n=== Bulunan Uçuşlar ===\n")
            for i, flight in enumerate(result.ucusler, 1):
                print(f"Uçuş {i}:")
                print(f"  Havayolu: {flight.havayolu or 'Bilinmiyor'}")
                print(f"  Fiyat: ${flight.toplam_fiyat}")
                print(f"  Kalkış: {flight.kalkis_havaalani} - {flight.kalkis_saati}")
                print(f"  Varış: {flight.varis_havaalani} - {flight.varis_saati}")
                print(f"  Süre: {flight.toplam_sure or 'Bilinmiyor'}")
                print(f"  Aktarma: {flight.aktarma_sayisi}")
                if flight.error:
                    print(f"  Hata: {flight.error}")
                print()
        else:
            print("Uçuş bulunamadı.")
        
        output_data = {
            "nereden": result.nereden,
            "nereye": result.nereye,
            "gidis_tarih": result.gidis_tarih,
            "toplam_ucus": result.toplam_ucus,
            "ucusler": [flight.model_dump() for flight in result.ucusler],
            "error": result.error
        }
        
        print("\n=== JSON Çıktısı ===")
        print(json.dumps(output_data, indent=2, ensure_ascii=False))
        
    except Exception as e:
        print(f"Hata: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        scraper.cleanup()

