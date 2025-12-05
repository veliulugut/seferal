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


class UludagScraper(BaseScraper):
    """Uludağ Turizm scraper"""
    
    # HTML'den çıkarılan şehir listeleri
    NEREDEN_SEHIRLER = {
        "AKYAKA", "ALACATI", "ALAŞEHİR", "AYVALIK (ÇARŞI)", "BURSA (GÖRÜKLE FAKÜLTE)", "ÇANAKKALE",
        "ÇANDARLI", "ÇEŞME 1", "DALAMAN", "EDİRNE", "FETHİYE", "GÖCEK", "HAVSA", "KAYNARCA HAREKET NOKTASI",
        "KORKUTELİ", "KÜTAHYA", "KÖYCEĞİZ", "ORTACA", "POLATLI", "SİLİVRİ", "URLA", "UZUNKÖPRÜ",
        "BALIKESİR (OTOGAR)", "BURSA", "ANKARA", "B.T.T", "EDREMİT (OTOGAR)", "AKÇAY", "AFYON", "AKHİSAR",
        "ALANYA", "ALTINOLUK (ÇARŞI)", "ALTINOLUK (OTOGAR)", "ALTINOVA", "ALİAĞA", "ANTALYA", "AYDIN",
        "AYVALIK (OTOGAR)", "BABAESKİ", "BALIKESİR(T.T.M)", "BLK ATATÜRK PARK KÖPRÜ ALTI", "BODRUM",
        "BOZÜYÜK", "BUCAK", "BURDUR", "BURHANİYE (OTOGAR)", "BİGA", "ÇAN", "ÇANAKKALE DÖRTYOL EĞİTİM FAK.",
        "ÇARDAK", "EZİNE", "ÇORLU", "BALIKESİR(YONCA)", "ÇİNE", "DENİZLİ", "DİKİLİ", "DİNAR", "ERDEK",
        "ESKİŞEHİR", "GEBZE", "GEMLİK", "GÜRE", "GÖMEÇ", "GÖNEN", "HAVRAN", "ISPARTA", "İVRİNDİ", "İNEGÖL",
        "İSTANBUL(ALİBEYKÖY)", "İSTANBUL(ESENLER)", "KARACABEY", "KEŞAN", "KIRKLARELİ", "KUŞADASI",
        "KÜÇÜKKUYU", "İSTANBUL(DUDULLU)", "LAPSEKİ", "LÜLEBURGAZ", "M.KEMALPAŞA", "MALKARA", "MANAVGAT",
        "MANİSA", "MARMARİS", "MUĞLA", "MİLAS", "DİDİM", "NAZİLLİ", "İZMİR", "ORHANGAZİ", "SALİHLERALTI",
        "SALİHLİ", "SARIMSAKLI (OTGR)", "SELÇUK", "BANDIRMA (OTOGAR)", "SERİK", "SUSURLUK", "SÖKE",
        "TEKİRDAĞ", "TURGUTLU", "TURGUTREİS", "UŞAK", "BANDIRMA (ÇARŞI)", "BANDIRMA (İDO)", "YALOVA", "YATAĞAN"
    }
    
    NEREYE_SEHIRLER = {
        "AKÇAY", "AKHİSAR", "ALACATI", "ALAŞEHİR", "ALTINOLUK (OTOGAR)", "ALTINOVA", "ANTALYA", "AYDIN",
        "AYVALIK (OTOGAR)", "BABAESKİ", "BALIKESİR (OTOGAR)", "BALIKESİR(T.T.M)", "BANDIRMA (OTOGAR)",
        "BODRUM", "BURHANİYE (OTOGAR)", "BURSA", "BURSA (GÖRÜKLE FAKÜLTE)", "ÇANAKKALE",
        "ÇANAKKALE DÖRTYOL EĞİTİM FAK.", "ÇEŞME 1", "ÇORLU", "DALAMAN", "DENİZLİ", "EDREMİT (OTOGAR)",
        "ERDEK", "EZİNE", "FETHİYE", "GEBZE", "GÖMEÇ", "HAVRAN", "İVRİNDİ", "İZMİR", "KIRKLARELİ",
        "KUŞADASI", "KÜÇÜKKUYU", "KÖYCEĞİZ", "LÜLEBURGAZ", "M.KEMALPAŞA", "MANİSA", "MARMARİS", "MUĞLA",
        "MİLAS", "ORTACA", "SALİHLİ", "SARIMSAKLI (OTGR)", "SUSURLUK", "SÖKE", "TEKİRDAĞ", "TURGUTLU",
        "URLA", "YATAĞAN"
    }
    
    @property
    def company_name(self) -> str:
        return "Pamukkale Turizm"
    
    @property
    def supported_cities(self) -> Tuple[set, set]:
        return self.NEREDEN_SEHIRLER, self.NEREYE_SEHIRLER
    
    @classmethod
    def is_valid_route(cls, nereden: str, nereye: str) -> Tuple[bool, str]:
        # Normalize city names for comparison (case-insensitive)
        nereden_upper = nereden.upper().strip()
        nereye_upper = nereye.upper().strip()
        
        nereden_found = any(city.upper() == nereden_upper or nereden_upper in city.upper() or city.upper() in nereden_upper 
                           for city in cls.NEREDEN_SEHIRLER)
        nereye_found = any(city.upper() == nereye_upper or nereye_upper in city.upper() or city.upper() in nereye_upper 
                          for city in cls.NEREYE_SEHIRLER)
        
        if not nereden_found:
            return False, f"'{nereden}' şehri Pamukkale Turizm'in hizmet verdiği kalkış şehirleri arasında değil."
        if not nereye_found:
            return False, f"'{nereye}' şehri Pamukkale Turizm'in hizmet verdiği varış şehirleri arasında değil."
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
        self.driver.get("https://balikesiruludag.com.tr/otobus-bileti/Bilet.php")
        sleep(0.5)
    
    def _select_date(self, tarih: datetime):
        """Select date in DD/MM/YYYY format"""
        day = tarih.day
        month = tarih.month
        year = tarih.year
        
        date_str = f"{day:02d}/{month:02d}/{year}"
        
        self.wait.until(EC.presence_of_element_located((By.ID, "Tarih")))
        
        # Clear and set date value
        date_input = self.driver.find_element(By.ID, "Tarih")
        self.driver.execute_script(f"""
            var input = document.getElementById('Tarih');
            input.value = '{date_str}';
            if (input.onchange) input.onchange();
            if (input.onblur) input.onblur();
        """)
        sleep(0.3)
    
    def _select_cities(self, nereden: str, nereye: str):
        """Select origin and destination cities"""
        self.wait.until(EC.presence_of_element_located((By.ID, "Kalkis")))
        
        # Select origin city
        kalkis_select = Select(self.driver.find_element(By.ID, "Kalkis"))
        kalkis_found = False
        
        for option in kalkis_select.options:
            option_text = option.text.strip()
            if option_text == nereden or option_text.startswith(nereden):
                kalkis_select.select_by_visible_text(option_text)
                kalkis_found = True
                break
        
        if not kalkis_found:
            # Try to find by partial match
            for option in kalkis_select.options:
                option_text = option.text.strip()
                if nereden.upper() in option_text.upper() or option_text.upper() in nereden.upper():
                    kalkis_select.select_by_visible_text(option_text)
                    kalkis_found = True
                    break
        
        if not kalkis_found:
            raise Exception(f"Kalkış şehri '{nereden}' bulunamadı")
        
        sleep(0.3)
        
        # Wait for destination select to be populated
        self.wait.until(EC.presence_of_element_located((By.ID, "Varis")))
        sleep(0.5)  # Wait for options to load
        
        # Select destination city
        varis_select = Select(self.driver.find_element(By.ID, "Varis"))
        varis_found = False
        
        for option in varis_select.options:
            option_text = option.text.strip()
            if option_text == nereye or option_text.startswith(nereye):
                varis_select.select_by_visible_text(option_text)
                varis_found = True
                break
        
        if not varis_found:
            # Try to find by partial match
            for option in varis_select.options:
                option_text = option.text.strip()
                if nereye.upper() in option_text.upper() or option_text.upper() in nereye.upper():
                    varis_select.select_by_visible_text(option_text)
                    varis_found = True
                    break
        
        if not varis_found:
            raise Exception(f"Varış şehri '{nereye}' bulunamadı")
        
        sleep(0.3)
    
    def _extract_trips_from_page(self) -> List[Trip]:
        """Extract trips from current page"""
        try:
            # Wait for trips table to load
            self.wait.until(EC.presence_of_element_located((By.ID, "divSefer")))
            sleep(0.5)
            
            # Find all trip rows
            trip_rows = self.driver.find_elements(By.CSS_SELECTOR, "#divSefer table tbody tr[id^='Sef']")
            
            if not trip_rows:
                return []
            
            trips = []
            
            for row in trip_rows:
                try:
                    # Get trip ID from row id (e.g., "Sef602949" -> "602949")
                    row_id = row.get_attribute("id")
                    sefer_id = row_id.replace("Sef", "") if row_id else None
                    
                    # Extract trip information with safe element finding
                    kalkis_saati = None
                    try:
                        kalkis_saati_elem = row.find_element(By.CSS_SELECTOR, "td.s_tarih font b")
                        kalkis_saati = kalkis_saati_elem.text.strip() if kalkis_saati_elem else None
                    except:
                        try:
                            kalkis_saati_elem = row.find_element(By.CSS_SELECTOR, "td.s_tarih")
                            kalkis_saati = kalkis_saati_elem.text.strip() if kalkis_saati_elem else None
                        except:
                            pass
                    
                    model = None
                    try:
                        model_elem = row.find_element(By.CSS_SELECTOR, "td.s_model font")
                        model = model_elem.text.strip() if model_elem else None
                    except:
                        try:
                            model_elem = row.find_element(By.CSS_SELECTOR, "td.s_model")
                            model = model_elem.text.strip() if model_elem else None
                        except:
                            pass
                    
                    fiyat = None
                    try:
                        fiyat_elem = row.find_element(By.CSS_SELECTOR, "td.s_if font")
                        fiyat = fiyat_elem.text.strip() if fiyat_elem else None
                    except:
                        try:
                            fiyat_elem = row.find_element(By.CSS_SELECTOR, "td.s_if")
                            fiyat = fiyat_elem.text.strip() if fiyat_elem else None
                        except:
                            pass
                    
                    aciklama = None
                    try:
                        aciklama_elem = row.find_element(By.CSS_SELECTOR, "td.s_aciklama")
                        aciklama = aciklama_elem.text.strip() if aciklama_elem else None
                    except:
                        pass
                    
                    trip = Trip(
                        sefer_takip_no=sefer_id,
                        kalkis_saati=kalkis_saati,
                        otobus_tipi=model,
                        fiyat=fiyat,
                        sefer_tipi=aciklama
                    )
                    
                    # Click on the trip to load seat plan
                    try:
                        # Try to click on the trip row using JavaScript SeferSec function
                        # The onclick attribute contains: SeferSec('602949','white','Gidis','1')
                        self.driver.execute_script(f"""
                            if (typeof SeferSec === 'function') {{
                                SeferSec('{sefer_id}', 'white', 'Gidis', '1');
                            }}
                        """)
                        sleep(1)
                        
                        # Wait for seat plan to load
                        try:
                            self.wait.until(EC.presence_of_element_located((By.ID, "divKoltuk")))
                        except:
                            # Try alternative: wait for koltuk table
                            self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#divKoltuk table.table-koltuk")))
                        sleep(0.5)
                        
                        # Extract seat plan
                        seats = self.driver.execute_script("""
                            var seats = [];
                            var koltukTable = document.querySelector('#divKoltuk table.table-koltuk');
                            if (!koltukTable) return seats;
                            
                            var koltukCells = koltukTable.querySelectorAll('td[id^="Kol"]');
                            
                            for (var i = 0; i < koltukCells.length; i++) {
                                var cell = koltukCells[i];
                                var cellId = cell.getAttribute('id');
                                var koltukNo = null;
                                var durum = 'bos';
                                var musait = true;
                                var cinsiyetKisitlamasi = null;
                                var koltukTipi = 'tekli';
                                
                                // Extract seat number from id (e.g., "Kol602956*01" -> "01")
                                if (cellId) {
                                    var parts = cellId.split('*');
                                    if (parts.length > 1) {
                                        koltukNo = parts[1];
                                    }
                                }
                                
                                // Try to get seat number from text content (b tag)
                                if (!koltukNo) {
                                    var bTag = cell.querySelector('b');
                                    if (bTag) {
                                        koltukNo = bTag.textContent.trim();
                                    }
                                }
                                
                                if (!koltukNo) continue;
                                
                                // Determine seat status
                                var classList = cell.classList;
                                var hasCheckbox = cell.querySelector('input[type="checkbox"]') !== null;
                                var label = cell.querySelector('label');
                                var isDisabled = cell.style.cursor === 'not-allowed' || 
                                                (label && label.style.cursor === 'not-allowed') ||
                                                cell.classList.contains('dolu');
                                
                                // Check if seat is occupied (has gender icon but no checkbox)
                                var hasGenderIcon = cell.querySelector('img[src*="bay.png"], img[src*="bayan.png"]') !== null;
                                
                                if (isDisabled || (!hasCheckbox && hasGenderIcon)) {
                                    durum = 'dolu';
                                    musait = false;
                                } else if (hasCheckbox && !isDisabled) {
                                    durum = 'bos';
                                    musait = true;
                                } else {
                                    durum = 'bos';
                                    musait = true;
                                }
                                
                                // Check for gender restriction (bay/bayan icons)
                                var img = cell.querySelector('img');
                                if (img) {
                                    var imgSrc = img.getAttribute('src') || '';
                                    if (imgSrc.includes('bay.png') || imgSrc.includes('1bay.png')) {
                                        cinsiyetKisitlamasi = 'bay';
                                    } else if (imgSrc.includes('bayan.png') || imgSrc.includes('1bayan.png')) {
                                        cinsiyetKisitlamasi = 'bayan';
                                    }
                                }
                                
                                // Determine seat type (check if it's a pair) and get pair seat number
                                var pairSeatNo = null;
                                var checkbox = cell.querySelector('input[type="checkbox"]');
                                if (checkbox) {
                                    var onclickAttr = checkbox.getAttribute('onclick') || '';
                                    // Extract the last parameter from onclick
                                    // Format: KoltukSec('602950*23','3400','2000','Gidis','BiletEkle','','24');
                                    // If last parameter is a seat number (not '00' or empty), it's a pair seat
                                    var params = onclickAttr.split(',');
                                    if (params.length >= 7) {
                                        var lastParam = params[params.length - 1].trim();
                                        // Remove closing parenthesis and quotes
                                        lastParam = lastParam.replace(/[);'\"]/g, '');
                                        // Check if it's a valid seat number (not '00' or empty)
                                        if (lastParam && lastParam !== '00' && !isNaN(parseInt(lastParam))) {
                                            koltukTipi = 'ciftli';
                                            pairSeatNo = lastParam;
                                        }
                                    }
                                }
                                
                                seats.push({
                                    koltuk_no: koltukNo,
                                    durum: durum,
                                    musait: musait,
                                    cinsiyet_kisitlamasi: cinsiyetKisitlamasi,
                                    koltuk_tipi: koltukTipi,
                                    pair_seat_no: pairSeatNo
                                });
                            }
                            
                            // Second pass: For pair seats, check the pair seat's gender restriction
                            for (var i = 0; i < seats.length; i++) {
                                var seat = seats[i];
                                // If seat is empty, pair type, and has a pair seat number
                                if (seat.durum === 'bos' && seat.koltuk_tipi === 'ciftli' && seat.pair_seat_no) {
                                    // Find the pair seat (compare as both string and number to handle padding)
                                    var pairSeatNoStr = String(seat.pair_seat_no);
                                    var pairSeatNoNum = parseInt(seat.pair_seat_no);
                                    for (var j = 0; j < seats.length; j++) {
                                        var otherSeatNoStr = String(seats[j].koltuk_no);
                                        var otherSeatNoNum = parseInt(seats[j].koltuk_no);
                                        // Match by string or number (to handle "04" vs "4")
                                        if (otherSeatNoStr === pairSeatNoStr || otherSeatNoNum === pairSeatNoNum) {
                                            var pairSeat = seats[j];
                                            // If pair seat is occupied and has gender restriction, apply it to this seat too
                                            if (pairSeat.durum === 'dolu' && pairSeat.cinsiyet_kisitlamasi) {
                                                seat.cinsiyet_kisitlamasi = pairSeat.cinsiyet_kisitlamasi;
                                            }
                                            break;
                                        }
                                    }
                                }
                            }
                            
                            return seats;
                        """)
                        
                        bos_koltuklar = [s for s in seats if s['durum'] == 'bos']
                        dolu_koltuklar = [s for s in seats if s['durum'] == 'dolu']
                        
                        bos_koltuklar_sorted = sorted(bos_koltuklar, key=lambda x: int(x.get('koltuk_no', 0)))
                        
                        bos_koltuklar_list = []
                        for koltuk in bos_koltuklar_sorted:
                            koltuk_dict = {
                                'koltuk_no': koltuk['koltuk_no'],
                                'koltuk_tipi': koltuk.get('koltuk_tipi', 'tekli')
                            }
                            # Add gender restriction if exists (for both single and pair seats)
                            if koltuk.get('cinsiyet_kisitlamasi'):
                                koltuk_dict['cinsiyet_kisitlamasi'] = koltuk['cinsiyet_kisitlamasi']
                            bos_koltuklar_list.append(koltuk_dict)
                        
                        trip.koltuk_plani = SeatPlan(
                            toplam_koltuk=len(seats),
                            bos=len(bos_koltuklar),
                            dolu=len(dolu_koltuklar),
                            bos_koltuklar=bos_koltuklar_list
                        )
                        
                    except Exception as e:
                        trip.error = f"Koltuk planı yüklenemedi: {str(e)}"
                    
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
            
            # Click "Sefer Listele" button
            sefer_listele_button = self.wait.until(EC.element_to_be_clickable((By.ID, "seferListele")))
            self.driver.execute_script("arguments[0].click();", sefer_listele_button)
            sleep(1)
            
            # Wait for trips to load
            self.wait.until(EC.presence_of_element_located((By.ID, "divSefer")))
            sleep(0.5)
            
            return self._extract_trips_from_page()
        except Exception as e:
            return [Trip(error=str(e))]
    
    def cleanup(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
