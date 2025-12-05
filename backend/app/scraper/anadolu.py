from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from time import sleep
from typing import List, Tuple
from datetime import datetime
from app.scraper.base import BaseScraper
from app.models.trip import Trip, SeatPlan


class AnadoluScraper(BaseScraper):
    """Anadolu Ulaşım scraper"""
    
    NEREDEN_SEHIRLER = {
        "UŞAK", "İZMİR", "İSTANBUL-ANADOLU(DUDULLU)", "İSTANBUL-ANADOLU(HAREM)", 
        "İSTANBUL-AVRUPA (ALİBEYKÖY)", "İSTANBUL-AVRUPA(ESENLER)", "BURSA", "ANKARA", 
        "DENİZLİ", "ANTALYA", "ÇANAKKALE OTOGAR", "ESKİŞEHİR", "AFYON", "SEYDIKEMER", 
        "KÜTAHYA", "AHADKÖY", "AKÇAKOCA", "AKÇAY", "AKHİSAR", "AKKÖY", "AKTUR", 
        "AKYAKA", "ALAÇATI", "ALANYA", "ALAPLI", "ALAŞEHİR", "ALTINOLUK", "ALTINOVA", 
        "ALTINTAŞ", "ALİAĞA", "ALİAĞA (YENİ ŞAKRAN)", "ATÇA", "AYDIN", "AYVALIK", 
        "BABAESKİ", "BAFA", "BALIKESİR", "BANAZ", "BANDIRMA", "BAYIR", "BEKİLLİ", 
        "BERGAMA", "BODRUM", "BOLU", "BOZÜYÜK", "BOZÜYÜK ÖMÜR TESİSİ", "BUCAK", 
        "BUHARKENT", "BULDAN", "BURDUR", "BURHANİYE", "BİGA", "BİLECİK", "ÇAL", 
        "ÇAN", "ÇANAKKALE İSKELE", "ÇANDARLI", "ÇANKIRI", "ÇARDAK", "ÇERKEZKÖY", 
        "ÇEŞME", "ÇORLU", "ÇUBUCAK", "ÇİNE", "ÇİVRİL", "DALAMAN", "DARICA", "DATÇA", 
        "DAVUTLAR", "DAZKIRI", "DEĞİRMENDERE", "DEVREK", "DİDİM", "DİKİLİ", 
        "DİKİLİ ÇATI", "DİNAR", "DÜZCE", "ECEABAT", "EDREMİT", "ERDEK", "ERİKLİ (KEŞAN)", 
        "EZİNE", "EŞEN", "FETHİYE", "FİNİKE", "GEBZE", "GELİBOLU", "GEMLİK", 
        "GERMENCİK", "GEYİKLİ", "GÜLLÜK KAVŞAĞI", "GÜMÜLDÜR", "GÜMÜSSUYU", "GÜNDOĞAN", 
        "GÜNLÜKBAŞI", "GÜRPINAR", "GÜVERCİNLİK", "GÖCEK", "GÖLCÜK", "GÖNEN", "HOCALAR", 
        "HORSUNLU", "ILGAZ", "ILICA", "ISPARTA", "KALE", "KALKAN", "KAPAKLI", 
        "KARAAĞAÇ", "KARABÜK", "KARACABEY", "KARACABEY ÇATRAK", "KARAHALLI", 
        "KARAMÜRSEL", "KASTAMONU", "KAŞ", "KDZ.EREĞLİ", "KECIBORLU (YOL AYRIMI)", 
        "KEMER", "KEMER - MUĞLA", "KEŞAN", "KINIK", "KIRKLARELİ", "KONAKOĞLU OTOYOL MOLA", 
        "KOZLU", "KULA", "KUMLA", "KUMLUCA", "KUYUCAK", "KUŞADASI", "KÜÇÜKKUYU", 
        "KÖYCEĞİZ", "KÖŞK", "LAPSEKİ", "LÜLEBURGAZ", "M.KEMALPAŞA", "MANAVGAT", 
        "MANİSA", "MARMARİS", "MAVİŞEHİR", "MENGEN", "MUDANYA", "MUĞLA", "MİLAS", 
        "MİLAS ÜÇYOL", "NAZİLLİ", "ORHANGAZİ", "ORTACA", "ORTAKLAR", "PAMUKKALE", 
        "PAMUKOVA", "PAMUKÖREN", "PINARBAŞI", "PINARCIK", "POLATLI", "SAFRANBOLU", 
        "SAKARYA(ADAPAZARI)", "SALİHLERALTI DÖRTYOL", "SALİHLİ", "SANDIKLI", "SARAY", 
        "SARAYKÖY", "SARIKEMER", "SARIMSAKLI", "SEFERİHİSAR", "SELÇUK", "SELİMİYE", 
        "SERİK", "SULTANHİSAR", "SİVASLI", "SÖĞÜT", "SÖKE", "TAVAS", "TEKİRDAĞ", 
        "TEKİRDAĞ (YENİCE)", "TEKİRDAĞ(M.EREĞLİSİ)", "TEKİRDAĞ(Y. ÇİFTLİK)", 
        "TURGUTLU", "TURGUTREİS", "TÜRSAN KONAKOGLU TES", "UMURLU", "URLA", 
        "UZUNKÖPRÜ", "VİZE", "YALIKAVAK", "YALOVA", "YATAĞAN", "YATAĞAN (YOL AYRIMI)", 
        "YAVASLAR", "YAYLA (KEŞAN)", "YENİPAZAR (YOL AYRIMI)", "YENİŞAKRAN", 
        "İNCİRLİOVA", "İNEGÖL", "ÜRKMEZ", "İSABEYLİ", "İZMİT(KOCAELI)", "ZONGULDAK", 
        "ÖZDERE"
    }
    
    NEREYE_SEHIRLER = {
        "İSTANBUL-ANADOLU(DUDULLU)", "BURSA", "ANKARA", "İZMİR", "DENİZLİ", 
        "ESKİŞEHİR", "ANTALYA", "İZMİT(KOCAELI)", "KÜTAHYA", "AFYON", 
        "ÇANAKKALE OTOGAR", "UŞAK", "BALIKESİR", "BOLU", "KARABÜK", "SAFRANBOLU", 
        "AKÇAKOCA", "AKÇAY", "AKHİSAR", "AKYAKA", "ALAÇATI", "ALANYA", "ALAPLI", 
        "ALAŞEHİR", "ALİAĞA", "ALTINOLUK", "ALTINOVA", "AYDIN", "AYVALIK", "BANAZ", 
        "BANDIRMA", "BERGAMA", "BİGA", "BİLECİK", "BODRUM", "BOZÜYÜK", 
        "BOZÜYÜK ÖMÜR TESİSLERİ", "BUCAK", "BUHARKENT", "BULDAN", "BURDUR", 
        "BURHANİYE", "ÇANAKKALE İSKELE", "ÇANDARLI", "ÇERKEZKÖY", "ÇEŞME", "ÇİNE", 
        "ÇİVRİL", "ÇORLU", "DALAMAN", "DATÇA", "DİDİM", "DİKİLİ", "DÜZCE", "ECEABAT", 
        "EDREMİT", "ERDEK", "EZİNE", "FETHİYE", "FİNİKE", "GEBZE", "GELİBOLU", 
        "GEYİKLİ", "GÖCEK", "GÖMEÇ", "GÜMÜLDÜR", "ILICA", "ISPARTA", "İNEGÖL", 
        "KALKAN", "KAPAKLI", "KARAAĞAÇ", "KARACABEY", "KARAHALLI", "KASTAMONU", 
        "KAŞ", "KDZ.EREĞLİ", "KEMER", "KIRKLARELİ", "KOLAYLI MOLA Y.", "KOZLU", 
        "KÖYCEĞİZ", "KUMLUCA", "KUŞADASI", "KÜÇÜKKUYU", "LAPSEKİ", "LÜLEBURGAZ", 
        "MANAVGAT", "MANİSA", "MARMARİS", "MİLAS", "MUĞLA", "NAZİLLİ", "ORTACA", 
        "ÖZDERE", "SAKARYA(ADAPAZARI)", "SALİHLERALTI DÖRTYOL", "SALİHLİ", "SANDIKLI", 
        "SARAY", "SARAYKÖY", "SARIMSAKLI", "SEFERİHİSAR", "SELÇUK", "SERİK", 
        "SİVASLI", "SÖKE", "TEKİRDAĞ", "TEKİRDAĞ (YENİCE)", "TURGUTLU", "URLA", 
        "UZUNKÖPRÜ", "ÜRKMEZ", "VİZE", "YATAĞAN", "ZONGULDAK"
    }
    
    @property
    def company_name(self) -> str:
        return "Metro Turizm"
    
    @property
    def supported_cities(self) -> Tuple[set, set]:
        return self.NEREDEN_SEHIRLER, self.NEREYE_SEHIRLER
    
    @classmethod
    def is_valid_route(cls, nereden: str, nereye: str) -> Tuple[bool, str]:
        nereden_upper = nereden.upper().strip()
        nereye_upper = nereye.upper().strip()
        
        nereden_found = any(city.upper() == nereden_upper or nereden_upper in city.upper() or city.upper() in nereden_upper 
                           for city in cls.NEREDEN_SEHIRLER)
        nereye_found = any(city.upper() == nereye_upper or nereye_upper in city.upper() or city.upper() in nereye_upper 
                          for city in cls.NEREYE_SEHIRLER)
        
        if not nereden_found:
            return False, f"'{nereden}' şehri Metro Turizm'in hizmet verdiği kalkış şehirleri arasında değil."
        if not nereye_found:
            return False, f"'{nereye}' şehri Metro Turizm'in hizmet verdiği varış şehirleri arasında değil."
        return True, ""
    
    def __init__(self, headless: bool = True):
        chromedriver_autoinstaller.install()
        options = Options()
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        if headless:
            options.add_argument("--headless")
        self.driver = webdriver.Chrome(options=options)
        stealth(
            self.driver, languages=["en-US", "en"], vendor="Google Inc.", platform="MacIntel",
            webgl_vendor="Intel Inc.", renderer="Intel Iris OpenGL", fix_hairline=True,
        )
        self.wait = WebDriverWait(self.driver, 10)
    
    def _setup(self):
        self.driver.get("https://www.anadolu.com.tr/online-otobus-bileti")
        sleep(0.3)
    
    def _select_date(self, tarih: datetime):
        day = tarih.day
        month = tarih.month
        year = tarih.year
        
        date_str = f"{day:02d}/{month:02d}/{year}"
        
        self.wait.until(EC.presence_of_element_located((By.ID, "SeferTarihi")))
        
        date_input = self.driver.find_element(By.ID, "SeferTarihi")
        self.driver.execute_script(f"""
            var input = document.getElementById('SeferTarihi');
            input.value = '{date_str}';
            if (input.onchange) input.onchange();
            if (input.onblur) input.onblur();
        """)
        sleep(0.2)
    
    def _select_cities(self, nereden: str, nereye: str):
        self.wait.until(EC.presence_of_element_located((By.ID, "Kalkis")))
        
        kalkis_select = Select(self.driver.find_element(By.ID, "Kalkis"))
        kalkis_found = False
        
        for option in kalkis_select.options:
            option_text = option.text.strip()
            if option_text == nereden or option_text.startswith(nereden):
                kalkis_select.select_by_visible_text(option_text)
                kalkis_found = True
                break
        
        if not kalkis_found:
            for option in kalkis_select.options:
                option_text = option.text.strip()
                if nereden.upper() in option_text.upper() or option_text.upper() in nereden.upper():
                    kalkis_select.select_by_visible_text(option_text)
                    kalkis_found = True
                    break
        
        if not kalkis_found:
            raise Exception(f"Kalkış şehri '{nereden}' bulunamadı")
        
        sleep(0.3)
        
        self.wait.until(EC.presence_of_element_located((By.ID, "Varis")))
        sleep(0.4)
        
        varis_select = Select(self.driver.find_element(By.ID, "Varis"))
        varis_found = False
        
        for option in varis_select.options:
            option_text = option.text.strip()
            if option_text == nereye or option_text.startswith(nereye):
                varis_select.select_by_visible_text(option_text)
                varis_found = True
                break
        
        if not varis_found:
            for option in varis_select.options:
                option_text = option.text.strip()
                if nereye.upper() in option_text.upper() or option_text.upper() in nereye.upper():
                    varis_select.select_by_visible_text(option_text)
                    varis_found = True
                    break
        
        if not varis_found:
            raise Exception(f"Varış şehri '{nereye}' bulunamadı")
        
        sleep(0.2)
    
    def _extract_trips_from_page(self) -> List[Trip]:
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "seferliste")))
            sleep(0.5)
            
            last_height = self.driver.execute_script("""
                var container = document.getElementById('seferliste');
                if (!container) return 0;
                return container.scrollHeight;
            """)
            scroll_attempts = 0
            max_scroll_attempts = 10
            
            while scroll_attempts < max_scroll_attempts:
                self.driver.execute_script("""
                    var container = document.getElementById('seferliste');
                    if (container) {
                        container.scrollTop = container.scrollHeight;
                    }
                """)
                sleep(0.5)
                new_height = self.driver.execute_script("""
                    var container = document.getElementById('seferliste');
                    if (!container) return 0;
                    return container.scrollHeight;
                """)
                if new_height == last_height:
                    break
                last_height = new_height
                scroll_attempts += 1
            
            self.driver.execute_script("""
                var container = document.getElementById('seferliste');
                if (container) {
                    container.scrollTop = 0;
                }
            """)
            sleep(0.3)
            
            sefer_items = self.driver.find_elements(By.CSS_SELECTOR, "#seferliste li .booking-item")
            
            if not sefer_items:
                return []
            
            trips = []
            
            for booking_item in sefer_items:
                try:
                    sefer_id = booking_item.get_attribute("data-id")
                    if not sefer_id:
                        continue
                    
                    li_element = booking_item.find_element(By.XPATH, "./ancestor::li")
                    
                    firma_adi = "Anadolu Ulaşım"
                    try:
                        img = booking_item.find_element(By.CSS_SELECTOR, ".booking-item-airline-logo img")
                        alt_txt = img.get_attribute("alt") or ""
                        src_txt = img.get_attribute("src") or ""
                        if "pamukkale" in alt_txt.lower() or "pamukkale" in src_txt.lower():
                            firma_adi = "Pamukkale Turizm"
                        elif "anadolu" in alt_txt.lower() or "anadolu" in src_txt.lower():
                            firma_adi = "Anadolu Ulaşım"
                    except:
                        pass
                    
                    kalkis_saati = None
                    try:
                        kalkis_logo = booking_item.find_element(By.CSS_SELECTOR, ".booking-item-airline-logo h5")
                        kalkis_saati = kalkis_logo.text.strip()
                    except:
                        try:
                            dep_text = booking_item.find_element(By.CLASS_NAME, "booking-item-departure").text
                            if "(" in dep_text:
                                kalkis_saati = dep_text.split("(")[-1].replace(")", "").strip()
                        except:
                            pass
                    
                    fiyat = None
                    try:
                        fiyat_elem = booking_item.find_element(By.CSS_SELECTOR, ".booking-item-price b")
                        fiyat = fiyat_elem.text.strip()
                    except:
                        pass
                    
                    is_full = False
                    try:
                        alert = li_element.find_elements(By.CSS_SELECTOR, ".alert-fiyat")
                        for a in alert:
                            if "Araç Dolu" in a.text:
                                is_full = True
                                break
                    except:
                        pass
                    
                    trip = Trip(
                        sefer_takip_no=sefer_id,
                        kalkis_saati=kalkis_saati,
                        fiyat=fiyat,
                        firma=firma_adi,
                        sefer_tipi="Araç Dolu" if is_full else None
                    )
                    
                    if not is_full:
                        try:
                            detay_id = f"detaykoltuk{sefer_id}"
                            
                            detay_elem = None
                            try:
                                detay_elem = self.driver.find_element(By.ID, detay_id)
                            except:
                                pass
                            
                            if not (detay_elem and detay_elem.is_displayed()):
                                self.driver.execute_script(f"""
                                    var bookingItem = document.querySelector('.booking-item[data-id="{sefer_id}"]');
                                    if (bookingItem) {{
                                        var event = new MouseEvent('click', {{
                                            bubbles: true,
                                            cancelable: true,
                                            view: window
                                        }});
                                        bookingItem.dispatchEvent(event);
                                    }}
                                """)
                                sleep(0.8)
                            
                            seats = self.driver.execute_script(f"""
                                var container = document.getElementById('{detay_id}');
                                if (!container) return [];
                                
                                var seats = [];
                                var cells = container.querySelectorAll('td.koltuk');
                                
                                for (var i = 0; i < cells.length; i++) {{
                                    var cell = cells[i];
                                    var tdspan = cell.querySelector('.tdspan');
                                    if (!tdspan) continue;
                                    
                                    var koltukNo = tdspan.getAttribute('data-koltukno');
                                    
                                    if (!koltukNo) {{
                                        var span = cell.querySelector('.koltukno');
                                        if (span) koltukNo = span.textContent.trim();
                                    }}
                                    
                                    if (!koltukNo) {{
                                        var cellId = cell.getAttribute('id');
                                        if (cellId) {{
                                            var parts = cellId.split('_');
                                            if (parts.length > 1) {{
                                                koltukNo = parts[parts.length - 1];
                                            }}
                                        }}
                                    }}
                                    
                                    if (!koltukNo) continue;
                                    
                                    var durum = 'bos';
                                    var musait = true;
                                    var cinsiyetKisitlamasi = null;
                                    var koltukTipi = 'tekli';
                                    var yanKoltukNo = null;
                                    
                                    if (cell.classList.contains('koltukdolu')) {{
                                        durum = 'dolu';
                                        musait = false;
                                        
                                        var style = cell.getAttribute('style') || '';
                                        if (style.indexOf('ErkekDolu') !== -1 || style.indexOf('Erkek') !== -1) {{
                                            cinsiyetKisitlamasi = 'bay';
                                        }} else if (style.indexOf('BayanDolu') !== -1 || style.indexOf('Bayan') !== -1) {{
                                            cinsiyetKisitlamasi = 'bayan';
                                        }}
                                    }} else if (cell.classList.contains('koltukbos')) {{
                                        durum = 'bos';
                                        musait = true;
                                    }}
                                    
                                    yanKoltukNo = tdspan.getAttribute('data-yankoltuk');
                                    var yanCins = tdspan.getAttribute('data-yancins');
                                    
                                    var row = cell.closest('tr');
                                    var isRightSide = false;
                                    var seatNum = parseInt(koltukNo) || 0;
                                    var corridorIndex = -1;
                                    
                                    if (row) {{
                                        var rowCells = Array.from(row.querySelectorAll('td'));
                                        var cellIndex = rowCells.indexOf(cell);
                                        
                                        for (var j = 0; j < rowCells.length; j++) {{
                                            if (rowCells[j].classList.contains('ortakapi')) {{
                                                corridorIndex = j;
                                                break;
                                            }}
                                        }}
                                        
                                        if (corridorIndex < 0) {{
                                            var table = row.closest('table');
                                            if (table) {{
                                                var allRows = table.querySelectorAll('tr');
                                                for (var r = 0; r < allRows.length; r++) {{
                                                    var testRow = allRows[r];
                                                    var testCells = Array.from(testRow.querySelectorAll('td'));
                                                    for (var c = 0; c < testCells.length; c++) {{
                                                        if (testCells[c].classList.contains('ortakapi')) {{
                                                            corridorIndex = c;
                                                            break;
                                                        }}
                                                    }}
                                                    if (corridorIndex >= 0) break;
                                                }}
                                            }}
                                        }}
                                        
                                        if (corridorIndex >= 0 && cellIndex > corridorIndex) {{
                                            isRightSide = true;
                                        }}
                                    }}
                                    
                                    if (!isRightSide && seatNum >= 21 && seatNum <= 37) {{
                                        isRightSide = true;
                                    }}
                                    
                                    if (isRightSide) {{
                                        koltukTipi = 'tekli';
                                        yanKoltukNo = null;
                                    }} else {{
                                        var alwaysSingleSeats = [1, 4, 7, 10, 13, 16, 19, 20];
                                        
                                        if (alwaysSingleSeats.indexOf(seatNum) !== -1) {{
                                            koltukTipi = 'tekli';
                                            yanKoltukNo = null;
                                        }} else {{
                                            if (yanKoltukNo !== null && yanKoltukNo !== '' && yanKoltukNo !== '00' && yanKoltukNo !== '0') {{
                                                koltukTipi = 'ciftli';
                                                
                                                if (durum === 'bos' && yanCins && yanCins !== '') {{
                                                    if (yanCins === 'E') {{
                                                        cinsiyetKisitlamasi = 'bay';
                                                    }} else if (yanCins === 'B') {{
                                                        cinsiyetKisitlamasi = 'bayan';
                                                    }}
                                                }}
                                            }} else {{
                                                koltukTipi = 'tekli';
                                                yanKoltukNo = null;
                                            }}
                                        }}
                                    }}
                                    
                                    seats.push({{
                                        koltuk_no: koltukNo,
                                        durum: durum,
                                        musait: musait,
                                        cinsiyet_kisitlamasi: cinsiyetKisitlamasi,
                                        koltuk_tipi: koltukTipi,
                                        yan_koltuk_no: yanKoltukNo
                                    }});
                                }}
                                
                                return seats;
                            """)
                            
                            if not isinstance(seats, list):
                                seats = []
                            
                            for i in range(len(seats)):
                                seat = seats[i]
                                if not isinstance(seat, dict):
                                    continue
                                if seat.get('durum') == 'bos' and seat.get('koltuk_tipi') == 'ciftli' and seat.get('yan_koltuk_no'):
                                    yan_koltuk_no = str(seat['yan_koltuk_no'])
                                    for j in range(len(seats)):
                                        if not isinstance(seats[j], dict):
                                            continue
                                        if str(seats[j].get('koltuk_no', '')) == yan_koltuk_no:
                                            pair_seat = seats[j]
                                            if pair_seat.get('durum') == 'dolu' and pair_seat.get('cinsiyet_kisitlamasi'):
                                                seat['cinsiyet_kisitlamasi'] = pair_seat['cinsiyet_kisitlamasi']
                                            break
                            
                            bos_koltuklar = [s for s in seats if isinstance(s, dict) and s.get('durum') == 'bos']
                            dolu_koltuklar = [s for s in seats if isinstance(s, dict) and s.get('durum') == 'dolu']
                            
                            bos_koltuklar_sorted = sorted(bos_koltuklar, key=lambda x: int(x.get('koltuk_no', 0)))
                            
                            bos_koltuklar_list = []
                            for koltuk in bos_koltuklar_sorted:
                                if not isinstance(koltuk, dict) or 'koltuk_no' not in koltuk:
                                    continue
                                koltuk_dict = {
                                    'koltuk_no': koltuk.get('koltuk_no'),
                                    'koltuk_tipi': koltuk.get('koltuk_tipi', 'tekli')
                                }
                                if koltuk.get('cinsiyet_kisitlamasi'):
                                    koltuk_dict['cinsiyet_kisitlamasi'] = koltuk.get('cinsiyet_kisitlamasi')
                                bos_koltuklar_list.append(koltuk_dict)
                            
                            trip.koltuk_plani = SeatPlan(
                                toplam_koltuk=len(seats),
                                bos=len(bos_koltuklar),
                                dolu=len(dolu_koltuklar),
                                bos_koltuklar=bos_koltuklar_list
                            )
                            
                        except Exception as e:
                            trip.error = f"Koltuk planı yüklenemedi: {str(e)}"
                    else:
                        trip.koltuk_plani = SeatPlan(toplam_koltuk=0, bos=0, dolu=0, bos_koltuklar=[])
                    
                    trips.append(trip)
                    
                except Exception as e:
                    trips.append(Trip(error=f"Sefer bilgisi çıkarılamadı: {str(e)}"))
            
            return trips
            
        except Exception as e:
            return [Trip(error=str(e))]
    
    def search_trips(self, nereden: str, nereye: str, tarih: datetime) -> List[Trip]:
        is_valid, error_msg = self.is_valid_route(nereden, nereye)
        if not is_valid:
            return [Trip(error=error_msg)]
        
        try:
            self._setup()
            self._select_cities(nereden, nereye)
            self._select_date(tarih)
            
            self.driver.execute_script("yukleniyor();")
            sleep(1.5)
            
            self.wait.until(EC.presence_of_element_located((By.ID, "seferliste")))
            sleep(0.3)
            
            return self._extract_trips_from_page()
        except Exception as e:
            return [Trip(error=str(e))]
    
    def cleanup(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
