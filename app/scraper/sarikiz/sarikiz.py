from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from typing import List, Tuple
from datetime import datetime
from app.scraper.base import BaseScraper
from app.models.trip import Trip, SeatPlan


class SarikizScraper(BaseScraper):
    """Sarıkız Turizm scraper"""
    
    NEREDEN_SEHIRLER = {
        "AFYON", "Ahmetli", "Ahmetli2", "Akhisar", "Alanya", "Alaşehir", "ANKARA", "ANTALYA", "AYDIN",
        "Ayvacık", "Ayvalık", "BALIKESİR", "Banaz", "Bergama", "Bodrum", "Buldan", "Burhaniye", "BURSA",
        "ÇANAKKALE", "DENİZLİ", "Dereköy", "Didim", "Edremit", "Eşme", "Ezine", "Gebze", "Güzelyalı",
        "ISPARTA", "İst(Alibeyköy)", "İst.(Dudullu)", "İSTANBUL (Harem)", "İSTANBUL(Esenler)", "İZMİR",
        "Kaynarca(İst)", "Kırkağaç", "Korkuteli", "Kuşadası", "Küçükkuyu", "Lapseki", "Manavgat", "MANİSA",
        "Milas", "Mustafakema", "Polatlı", "Salihli", "Salihli2", "Sarayköy", "Sarıgöl", "Sart", "Serik",
        "Soma", "Söke", "Sultanbeyli", "Susurluk", "Turgutlu", "Ulubey (Uşk)", "UŞAK"
    }
    
    NEREYE_SEHIRLER = {
        "AFYON", "Ahmetli", "Ahmetli2", "Akçay", "Akhisar", "Alanya", "ALTINOLUK", "Altınova (Yol Çatı)",
        "ANKARA", "ANTALYA", "Ayvacık", "Ayvalık", "BALIKESİR", "Banaz", "Bayat (Afy)", "Bergama", "Bodrum",
        "Buldan", "BURDUR", "Burhaniye", "BURSA", "ÇANAKKALE", "DENİZLİ", "Didim", "Dikili (Yol Çatı)",
        "Dinar", "Edremit", "Eşme", "Ezine", "Gebze", "Gömü", "ISPARTA", "İst(Alibeyköy)", "İst.(Dudullu)",
        "İSTANBUL (Harem)", "İSTANBUL(Esenler)", "İZMİR", "Kınık", "Kırkağaç", "Korkuteli", "Kuşadası",
        "Küçükkuyu", "Lapseki", "Manavgat", "MANİSA", "Milas", "Mustafakema", "Polatlı", "Sarayköy", "Sart",
        "Selçuk", "Serik", "Soma", "Söke", "Susurluk", "Turgutlu", "Ulubey (Uşk)", "UŞAK"
    }
    
    @property
    def company_name(self) -> str:
        return "Sarıkız Turizm"
    
    @property
    def supported_cities(self) -> Tuple[set, set]:
        return self.NEREDEN_SEHIRLER, self.NEREYE_SEHIRLER
    
    @classmethod
    def is_valid_route(cls, nereden: str, nereye: str) -> Tuple[bool, str]:
        if nereden not in cls.NEREDEN_SEHIRLER:
            return False, f"'{nereden}' şehri Sarıkız Turizm'in hizmet verdiği kalkış şehirleri arasında değil."
        if nereye not in cls.NEREYE_SEHIRLER:
            return False, f"'{nereye}' şehri Sarıkız Turizm'in hizmet verdiği varış şehirleri arasında değil."
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
        self.driver.get("https://secure.sarikizturizm.com.tr/SeyahatIslem.aspx")
        sleep(0.2)
    
    def _select_date(self, tarih: datetime):
        day = tarih.day
        month = tarih.month
        year = tarih.year
        
        self.wait.until(EC.presence_of_element_located((By.ID, "inputSeferAraTarih")))
        
        self.driver.execute_script(f"""
            var input = jQuery('#inputSeferAraTarih');
            var dateObj = new Date({year}, {month - 1}, {day});
            input.datepicker('setDate', dateObj);
            input.trigger('change');
        """)
        sleep(0.3)
    
    def _select_cities(self, nereden: str, nereye: str):
        self.wait.until(EC.presence_of_element_located((By.ID, "ddlKalkis")))
        
        kalkis_selected = self.driver.execute_script(f"""
            var select = jQuery('#ddlKalkis');
            var options = select.find('option');
            var found = false;
            
            options.each(function() {{
                var text = jQuery(this).text().trim();
                var value = jQuery(this).val();
                
                if (text === '{nereden}' || value === '{nereden}') {{
                    select.val(value).trigger('chosen:updated').trigger('change');
                    found = true;
                    return false;
                }}
            }});
            
            return found;
        """)
        
        if not kalkis_selected:
            raise Exception(f"Kalkış şehri '{nereden}' bulunamadı")
        
        sleep(0.2)
        
        self.wait.until(EC.presence_of_element_located((By.ID, "ddlVaris")))
        
        varis_selected = self.driver.execute_script(f"""
            var select = jQuery('#ddlVaris');
            var options = select.find('option');
            var found = false;
            
            options.each(function() {{
                var text = jQuery(this).text().trim();
                var value = jQuery(this).val();
                
                if (text === '{nereye}' || value === '{nereye}') {{
                    select.val(value).trigger('chosen:updated').trigger('change');
                    found = true;
                    return false;
                }}
            }});
            
            return found;
        """)
        
        if not varis_selected:
            raise Exception(f"Varış şehri '{nereye}' bulunamadı")
        
        sleep(0.2)
    
    def _extract_trips_from_page(self) -> List[Trip]:
        """Extract trips from current page"""
        try:
            self.wait.until(EC.presence_of_element_located((By.ID, "seferAlanlari")))
            self.wait.until(EC.presence_of_element_located((By.ID, "gidisSeferleri")))
            self.wait.until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "#gidisSeferleri .seferler .container.liste")) > 0)
            
            trips_data = self.driver.execute_script("""
                var trips = [];
                var gidisDiv = document.getElementById('gidisSeferleri');
                if (!gidisDiv) return trips;
                
                var seferler = gidisDiv.querySelectorAll('.seferler .container.liste');
                
                for (var i = 0; i < seferler.length; i++) {
                    var sefer = seferler[i];
                    var kalkis = sefer.querySelector('.kalkis-saati .saat .buyuk-yazi');
                    var seferTipi = sefer.querySelector('.sefer-tipi .buyuk-yazi div');
                    var otobus = sefer.querySelector('.otobus-ozellikleri .otobus-tipi');
                    var fiyat = sefer.querySelector('.fiyat-sec .int-fiyat .buyuk-yazi');
                    
                    trips.push({
                        sefer_takip_no: sefer.getAttribute('sefertakipno') || null,
                        kalkis_saati: kalkis ? kalkis.textContent.trim() : null,
                        sefer_tipi: seferTipi ? seferTipi.textContent.trim() : null,
                        otobus_tipi: otobus ? otobus.textContent.trim() : null,
                        fiyat: fiyat ? fiyat.textContent.trim() : null
                    });
                }
                
                return trips;
            """)
            
            trips = []
            seferler = self.driver.find_elements(By.CSS_SELECTOR, "#gidisSeferleri .seferler .container.liste")
            
            for i, trip_data in enumerate(trips_data):
                trip = Trip(
                    sefer_takip_no=trip_data.get('sefer_takip_no'),
                    kalkis_saati=trip_data.get('kalkis_saati'),
                    sefer_tipi=trip_data.get('sefer_tipi'),
                    otobus_tipi=trip_data.get('otobus_tipi'),
                    fiyat=trip_data.get('fiyat')
                )
                
                if i < len(seferler):
                    sefer = seferler[i]
                    try:
                        iptal_button = sefer.find_element(By.CSS_SELECTOR, ".sefer-iptal")
                        if iptal_button.is_displayed():
                            self.driver.execute_script("arguments[0].click();", iptal_button)
                    except:
                        pass
                    
                    try:
                        sec_button = sefer.find_element(By.CSS_SELECTOR, ".sefer-sec")
                        if not sec_button.is_displayed():
                            self.driver.execute_script("arguments[0].style.display = 'block';", sec_button)
                        self.driver.execute_script("arguments[0].click();", sec_button)
                        
                        self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, ".koltuk-plan .koltuklar")))
                        sleep(0.3)
                        
                        self.driver.execute_script("""
                            var koltukPlan = document.querySelector('.koltuk-plan .koltuklar');
                            if (koltukPlan) {
                                koltukPlan.scrollIntoView({block: 'center'});
                            }
                        """)
                        sleep(0.1)
                        
                        for _ in range(8):
                            koltuk_sayisi = self.driver.execute_script("""
                                return document.querySelectorAll('.koltuk-plan .koltuklar .koltuk[no]').length;
                            """)
                            if koltuk_sayisi >= 20:
                                sleep(0.2)
                                break
                            sleep(0.1)
                        
                        seats = self.driver.execute_script("""
                            var seats = [];
                            var koltuklarDiv = document.querySelector('.koltuk-plan .koltuklar');
                            if (!koltuklarDiv) return {seats: [], tumKoltuklar: [], kontrol: {toplamDiv: 0, numaraliDiv: 0}};
                            
                            var koltukSiralari = koltuklarDiv.querySelectorAll('.koltuk-sira');
                            var koltukMap = {};
                            var tumKoltuklar = [];
                            var tumKoltukDivleri = koltuklarDiv.querySelectorAll('.koltuk');
                            var numaraliKoltukDivleri = Array.from(tumKoltukDivleri).filter(function(k) {
                                var no = k.getAttribute('no');
                                var txt = k.textContent.trim();
                                return no || (txt && txt.match(/\\d+/));
                            });
                            
                            for (var siraIdx = 0; siraIdx < koltukSiralari.length; siraIdx++) {
                                var sira = koltukSiralari[siraIdx];
                                var siradakiKoltuklar = Array.from(sira.querySelectorAll('.koltuk'));
                                var siraKoltuklar = [];
                                
                                var siradakiNumaraliKoltuklar = [];
                                for (var j = 0; j < siradakiKoltuklar.length; j++) {
                                    var k = siradakiKoltuklar[j];
                                    var no = k.getAttribute('no');
                                    var txt = k.textContent.trim();
                                    
                                    if (!no && txt) {
                                        var m = txt.match(/\\d+/);
                                        if (m) no = m[0];
                                    }
                                    
                                    if (no) {
                                        siradakiNumaraliKoltuklar.push({element: k, no: parseInt(no), index: j});
                                    }
                                }
                                
                                for (var j = 0; j < siradakiKoltuklar.length; j++) {
                                    var k = siradakiKoltuklar[j];
                                    var no = k.getAttribute('no');
                                    var txt = k.textContent.trim();
                                    var classList = k.classList;
                                    
                                    if (!no && txt) {
                                        var m = txt.match(/\\d+/);
                                        if (m) no = m[0];
                                    }
                                    
                                    if (!no && classList.contains('koltuk-gri') && siradakiNumaraliKoltuklar.length > 0) {
                                        var koltukIndex = j;
                                        for (var n = 0; n < siradakiNumaraliKoltuklar.length; n++) {
                                            var numaraliKoltuk = siradakiNumaraliKoltuklar[n];
                                            var fark = koltukIndex - numaraliKoltuk.index;
                                            if (Math.abs(fark) <= 3) {
                                                var tahminNo = numaraliKoltuk.no - fark;
                                                if (tahminNo > 0 && tahminNo < 100 && !koltukMap[String(tahminNo)]) {
                                                    no = String(tahminNo);
                                                    break;
                                                }
                                            }
                                        }
                                    }
                                    
                                    if (no && !koltukMap[no]) {
                                        koltukMap[no] = true;
                                        
                                        var musait = k.getAttribute('musait');
                                        var durum = 'bos';
                                        var cinsiyetKisitlamasi = null;
                                        
                                        if (classList.contains('koltuk-gri')) {
                                            durum = 'dolu';
                                        } else if (classList.contains('koltuk-mavi')) {
                                            durum = musait === '1' ? 'bos' : 'dolu';
                                            cinsiyetKisitlamasi = 'bay';
                                        } else if (classList.contains('koltuk-pembe')) {
                                            durum = musait === '1' ? 'bos' : 'dolu';
                                            cinsiyetKisitlamasi = 'bayan';
                                        } else if (classList.contains('koltuk-beyaz')) {
                                            durum = musait === '1' ? 'bos' : 'dolu';
                                        } else {
                                            durum = musait === '1' ? 'bos' : (musait === '0' ? 'dolu' : 'bos');
                                        }
                                        
                                        siraKoltuklar.push({
                                            element: k,
                                            no: no,
                                            durum: durum,
                                            cinsiyetKisitlamasi: cinsiyetKisitlamasi,
                                            originalIndex: j,
                                            siraIdx: siraIdx
                                        });
                                    }
                                }
                                
                                for (var i = 0; i < siraKoltuklar.length; i++) {
                                    tumKoltuklar.push(siraKoltuklar[i]);
                                }
                            }
                            
                            for (var i = 0; i < tumKoltuklar.length; i++) {
                                tumKoltuklar[i].koltukTipi = 'tekli';
                            }
                            
                            for (var siraIdx = 0; siraIdx < koltukSiralari.length; siraIdx++) {
                                var sira = koltukSiralari[siraIdx];
                                var siradakiKoltuklar = Array.from(sira.querySelectorAll('.koltuk[no]'));
                                
                                for (var i = 0; i < siradakiKoltuklar.length; i++) {
                                    var koltuk = siradakiKoltuklar[i];
                                    var no = parseInt(koltuk.getAttribute('no')) || 0;
                                    var koltukObj = null;
                                    
                                    for (var j = 0; j < tumKoltuklar.length; j++) {
                                        if (parseInt(tumKoltuklar[j].no) === no) {
                                            koltukObj = tumKoltuklar[j];
                                            break;
                                        }
                                    }
                                    
                                    if (!koltukObj) continue;
                                    
                                    var koltukNo = parseInt(koltukObj.no) || 0;
                                    var currentIndex = koltukObj.originalIndex;
                                    var currentSira = koltukObj.siraIdx;
                                    
                                    for (var j = 0; j < tumKoltuklar.length; j++) {
                                        if (j === i || tumKoltuklar[j].koltukTipi === 'ciftli') continue;
                                        
                                        var otherNo = parseInt(tumKoltuklar[j].no) || 0;
                                        var otherIndex = tumKoltuklar[j].originalIndex;
                                        var otherSira = tumKoltuklar[j].siraIdx;
                                        
                                        var numaraFarki = Math.abs(koltukNo - otherNo);
                                        var indexFarki = Math.abs(currentIndex - otherIndex);
                                        var siraFarki = Math.abs(currentSira - otherSira);
                                        
                                        if (numaraFarki === 1) {
                                            if ((siraFarki === 0 && indexFarki === 1) || 
                                                (siraFarki === 1 && indexFarki === 0)) {
                                                koltukObj.koltukTipi = 'ciftli';
                                                tumKoltuklar[j].koltukTipi = 'ciftli';
                                                break;
                                            }
                                        }
                                    }
                                }
                            }
                            
                            for (var i = 0; i < tumKoltuklar.length; i++) {
                                var k = tumKoltuklar[i].element;
                                var koltukNo = tumKoltuklar[i].no;
                                var musait = k.getAttribute('musait');
                                
                                seats.push({
                                    koltuk_no: koltukNo,
                                    durum: tumKoltuklar[i].durum,
                                    musait: musait === '1',
                                    koltuk_tipi: tumKoltuklar[i].koltukTipi,
                                    cinsiyet_kisitlamasi: tumKoltuklar[i].cinsiyetKisitlamasi
                                });
                            }
                            
                            return {
                                seats: seats,
                                kontrol: {
                                    toplamDiv: tumKoltukDivleri.length,
                                    numaraliDiv: numaraliKoltukDivleri.length,
                                    islenenKoltuk: seats.length
                                }
                            };
                        """)
                        
                        if isinstance(seats, dict):
                            kontrol = seats.get('kontrol', {})
                            seats = seats.get('seats', [])
                            
                            toplam_div = kontrol.get('toplamDiv', 0)
                            numarali_div = kontrol.get('numaraliDiv', 0)
                            islenen = kontrol.get('islenenKoltuk', 0)
                            
                            if islenen < numarali_div:
                                trip.error = f"Koltuk sayısı tutarsız: {numarali_div} numaralı koltuk bulundu, {islenen} koltuk işlendi"
                        
                        bos_koltuklar = [s for s in seats if s['durum'] == 'bos']
                        dolu_koltuklar = [s for s in seats if s['durum'] == 'dolu']
                        
                        bos_koltuklar_sorted = sorted(bos_koltuklar, key=lambda x: int(x.get('koltuk_no', 0)))
                        
                        bos_koltuklar_list = []
                        for koltuk in bos_koltuklar_sorted:
                            koltuk_dict = {
                                'koltuk_no': koltuk['koltuk_no'],
                                'koltuk_tipi': koltuk['koltuk_tipi']
                            }
                            if koltuk.get('cinsiyet_kisitlamasi'):
                                koltuk_dict['cinsiyet_kisitlamasi'] = koltuk['cinsiyet_kisitlamasi']
                            bos_koltuklar_list.append(koltuk_dict)
                        
                        trip.koltuk_plani = SeatPlan(
                            toplam_koltuk=len(seats),
                            bos=len(bos_koltuklar),
                            dolu=len(dolu_koltuklar),
                            bos_koltuklar=bos_koltuklar_list
                        )
                        
                        try:
                            iptal_button = self.driver.find_element(By.CSS_SELECTOR, ".sefer-iptal")
                            if iptal_button.is_displayed():
                                self.driver.execute_script("arguments[0].click();", iptal_button)
                        except:
                            pass
                    except Exception as e:
                        trip.error = str(e)
                
                trips.append(trip)
            
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
            
            sefer_ara_button = self.wait.until(EC.element_to_be_clickable((By.ID, "btnSeferAra")))
            self.driver.execute_script("arguments[0].click();", sefer_ara_button)
            sleep(0.5)
            
            self.wait.until(EC.presence_of_element_located((By.ID, "seferAlanlari")))
            sleep(0.3)
            
            return self._extract_trips_from_page()
        except Exception as e:
            return [Trip(error=str(e))]
    
    def cleanup(self):
        if hasattr(self, 'driver'):
            self.driver.quit()
