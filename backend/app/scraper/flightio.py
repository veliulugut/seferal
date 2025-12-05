from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium_stealth import stealth
import chromedriver_autoinstaller
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from typing import List
from datetime import datetime
import re
from app.models.flight import Flight, FlightSegment, FlightSearchResponse


class FlightioScraper:
    """Flight scraper for flightlist.io"""
    
    def __init__(self, headless: bool = False):
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
        self.wait = WebDriverWait(self.driver, 15)
    
    def _setup(self):
        self.driver.get("https://www.flightlist.io/index.php")
        sleep(2)
        
        try:
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        except:
            pass
    
    def _select_origin(self, origin: str):
        try:
            origin_input = self.wait.until(EC.presence_of_element_located((By.ID, "from-input")))
            self.driver.execute_script("arguments[0].value = '';", origin_input)
            origin_input.clear()
            origin_input.send_keys(origin)
            sleep(0.8)
            
            try:
                first_option = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#eac-container-from-input ul li:first-child, .autocomplete li:first-child, [role='option']:first-child")))
                first_option.click()
            except:
                self.driver.execute_script("arguments[0].blur();", origin_input)
            sleep(0.3)
        except Exception as e:
            raise Exception(f"Origin selection failed: {str(e)}")
    
    def _select_destination(self, destination: str):
        try:
            dest_input = self.wait.until(EC.presence_of_element_located((By.ID, "to-input")))
            self.driver.execute_script("arguments[0].value = '';", dest_input)
            dest_input.clear()
            dest_input.send_keys(destination)
            sleep(0.8)
            
            try:
                first_option = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#eac-container-to-input ul li:first-child, .autocomplete li:first-child, [role='option']:first-child")))
                first_option.click()
            except:
                self.driver.execute_script("arguments[0].blur();", dest_input)
            sleep(0.3)
        except Exception as e:
            raise Exception(f"Destination selection failed: {str(e)}")
    
    def _select_date(self, tarih: datetime):
        try:
            date_str = tarih.strftime("%Y-%m-%d")
            
            result = self.driver.execute_script(f"""
                var dateStr = '{date_str}';
                var selectors = [
                    'input#depart',
                    'input[name="depart"]',
                    '#depart',
                    'input[type="date"]',
                    'input[placeholder*="Date"]',
                    'input[placeholder*="date"]',
                    '[id*="depart"]',
                    '[name*="depart"]',
                    '[id*="date"]'
                ];
                
                for (var i = 0; i < selectors.length; i++) {{
                    var input = document.querySelector(selectors[i]);
                    if (input) {{
                        input.focus();
                        input.value = dateStr;
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        if (input.onchange) input.onchange();
                        return {{ found: true, selector: selectors[i] }};
                    }}
                }}
                return {{ found: false }};
            """)
            
            if not result or not result.get('found'):
                sleep(1)
                try:
                    date_input_element = self.wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input#depart, input[name='depart'], #depart, input[type='date']")))
                    self.driver.execute_script(f"""
                        var input = arguments[0];
                        input.focus();
                        input.value = '{date_str}';
                        input.dispatchEvent(new Event('input', {{ bubbles: true }}));
                        input.dispatchEvent(new Event('change', {{ bubbles: true }}));
                        if (input.onchange) input.onchange();
                    """, date_input_element)
                except:
                    pass
            
            sleep(0.3)
        except Exception as e:
            pass
    
    def _select_passengers(self, adults: int = 1, children: int = 0):
        try:
            adults_select_element = self.wait.until(EC.presence_of_element_located((By.ID, "adults")))
            self.driver.execute_script(f"arguments[0].value = '{adults}';", adults_select_element)
            self.driver.execute_script("if (arguments[0].onchange) arguments[0].onchange();", adults_select_element)
            sleep(0.2)
            
            children_select_element = self.wait.until(EC.presence_of_element_located((By.ID, "children")))
            self.driver.execute_script(f"arguments[0].value = '{children}';", children_select_element)
            self.driver.execute_script("if (arguments[0].onchange) arguments[0].onchange();", children_select_element)
            sleep(0.2)
        except Exception as e:
            pass
    
    def _click_search(self):
        try:
            search_selectors = [
                "button#submit",
                "button[type='submit']",
                ".search button",
                ".btn-search",
                "#submit",
                "button.search",
                "input[type='submit']",
                "button.btn-primary",
                "button.btn",
                "[onclick*='search']"
            ]
            
            search_button = None
            for selector in search_selectors:
                try:
                    search_button = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    if search_button and search_button.is_displayed():
                        break
                except:
                    continue
            
            if not search_button:
                try:
                    form = self.driver.find_element(By.CSS_SELECTOR, "form")
                    self.driver.execute_script("arguments[0].submit();", form)
                    sleep(3)
                    return
                except:
                    raise Exception("Search button not found")
            
            self.driver.execute_script("arguments[0].click();", search_button)
            sleep(3)
        except Exception as e:
            raise Exception(f"Search button click failed: {str(e)}")
    
    def _extract_flights_from_page(self) -> List[Flight]:
        flights = []
        
        sleep(2)
        
        try:
            flight_items = self.wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".flights-list li.flight, .flight-item, .result-item, [class*='flight-result'], [class*='flight-card']")))
        except:
            try:
                flight_items = self.driver.find_elements(By.CSS_SELECTOR, ".flights-list li.flight, .flight-item, .result-item")
            except:
                flight_items = self.driver.find_elements(By.CSS_SELECTOR, "li.flight, [class*='flight'], [class*='result']")
        
        if not flight_items:
            return flights
        
        for item in flight_items:
            try:
                flight_data = self.driver.execute_script("""
                    var item = arguments[0];
                    var data = {};
                    var allText = item.textContent || item.innerText || '';
                    
                    var priceEl = item.querySelector('.price, [class*="price"], .cost, [class*="cost"], [class*="Price"], [class*="Cost"], .amount, [class*="amount"]');
                    if (priceEl) {
                        var priceText = priceEl.textContent.trim();
                        var priceMatch = priceText.match(/[\\$€£]?([\\d,]+(?:\\.[\\d]{2})?)/);
                        if (priceMatch) {
                            data.price = priceMatch[1];
                        } else {
                            data.price = priceText;
                        }
                    }
                    
                    var airlineEl = item.querySelector('img[alt*="airline"], img[alt*="Airline"], img[alt*="logo"], .airline img, [class*="airline"] img');
                    if (airlineEl) {
                        data.airline = airlineEl.getAttribute('alt') || airlineEl.getAttribute('title') || '';
                    } else {
                        var airlineTextEl = item.querySelector('.airline, [class*="airline"], .company, [class*="company"]');
                        if (airlineTextEl) {
                            data.airline = airlineTextEl.textContent.trim();
                        }
                    }
                    
                    var durationEl = item.querySelector('.duration, [class*="duration"], .time, [class*="time"], [class*="Duration"], [class*="Time"], .flight-duration');
                    if (durationEl) {
                        data.duration = durationEl.textContent.trim();
                    }
                    
                    var timeContainer = item.querySelector('.times, [class*="time"], .schedule, [class*="schedule"]');
                    if (timeContainer) {
                        var times = timeContainer.textContent.match(/(\\d{1,2}):(\\d{2})\\s*(?:AM|PM)?/gi);
                        if (times && times.length >= 2) {
                            data.depTime = times[0].trim();
                            data.arrTime = times[1].trim();
                        }
                    }
                    
                    var depTimeEl = item.querySelector('.departure-time, [class*="departure"], .dep-time, [class*="dep"], time[datetime], [data-departure-time]');
                    if (depTimeEl) {
                        data.depTime = depTimeEl.textContent.trim() || depTimeEl.getAttribute('datetime') || depTimeEl.getAttribute('data-departure-time') || '';
                    }
                    
                    var arrTimeEl = item.querySelector('.arrival-time, [class*="arrival"], .arr-time, [class*="arr"], time[datetime], [data-arrival-time]');
                    if (arrTimeEl) {
                        data.arrTime = arrTimeEl.textContent.trim() || arrTimeEl.getAttribute('datetime') || arrTimeEl.getAttribute('data-arrival-time') || '';
                    }
                    
                    var routeEl = item.querySelector('.route, [class*="route"], .airports, [class*="airports"]');
                    if (routeEl) {
                        var routeText = routeEl.textContent;
                        var airportMatch = routeText.match(/([A-Z]{3})\\s*[-→]\\s*([A-Z]{3})/);
                        if (airportMatch) {
                            data.depAirport = airportMatch[1];
                            data.arrAirport = airportMatch[2];
                        }
                    }
                    
                    var depAirportEl = item.querySelector('.departure-airport, [class*="departure-airport"], .dep-airport, [class*="from"], [data-from], [data-departure-airport]');
                    if (depAirportEl) {
                        var text = depAirportEl.textContent.trim();
                        var codeMatch = text.match(/\\(([A-Z]{3})\\)/);
                        if (codeMatch) {
                            data.depAirport = codeMatch[1];
                        } else {
                            data.depAirport = text || depAirportEl.getAttribute('data-from') || depAirportEl.getAttribute('data-departure-airport') || '';
                        }
                    }
                    
                    var arrAirportEl = item.querySelector('.arrival-airport, [class*="arrival-airport"], .arr-airport, [class*="to"], [data-to], [data-arrival-airport]');
                    if (arrAirportEl) {
                        var text = arrAirportEl.textContent.trim();
                        var codeMatch = text.match(/\\(([A-Z]{3})\\)/);
                        if (codeMatch) {
                            data.arrAirport = codeMatch[1];
                        } else {
                            data.arrAirport = text || arrAirportEl.getAttribute('data-to') || arrAirportEl.getAttribute('data-arrival-airport') || '';
                        }
                    }
                    
                    var stopsEl = item.querySelector('.stops, [class*="stop"], .connection, [class*="connection"], [class*="Stops"], [class*="Stop"]');
                    if (stopsEl) {
                        data.stops = stopsEl.textContent.trim();
                    }
                    
                    var depDateEl = item.querySelector('.departure-date, [class*="departure-date"], .dep-date, [data-date], [data-departure-date]');
                    if (depDateEl) {
                        data.depDate = depDateEl.textContent.trim() || depDateEl.getAttribute('data-date') || depDateEl.getAttribute('data-departure-date') || '';
                    }
                    
                    var arrDateEl = item.querySelector('.arrival-date, [class*="arrival-date"], .arr-date, [data-arrival-date]');
                    if (arrDateEl) {
                        data.arrDate = arrDateEl.textContent.trim() || arrDateEl.getAttribute('data-arrival-date') || '';
                    }
                    
                    if (!data.price && allText) {
                        var priceMatch = allText.match(/[\\$€£]?([\\d,]+(?:\\.[\\d]{2})?)/);
                        if (priceMatch) {
                            data.price = priceMatch[1];
                        }
                    }
                    
                    if (!data.duration && allText) {
                        var durMatch = allText.match(/(\\d+)\\s*h(?:our)?s?\\s*(\\d+)?\\s*m(?:in)?s?/i);
                        if (durMatch) {
                            var hours = durMatch[1];
                            var mins = durMatch[2] || '0';
                            data.duration = hours + 'h ' + mins + 'm';
                        }
                    }
                    
                    if (!data.depTime && allText) {
                        var timeMatch = allText.match(/(\\d{1,2}):(\\d{2})\\s*(?:AM|PM)?/i);
                        if (timeMatch) {
                            data.depTime = timeMatch[0];
                        }
                    }
                    
                    if (!data.depAirport && allText) {
                        var airportMatch = allText.match(/([A-Z]{3})\\s*[-→]\\s*([A-Z]{3})/);
                        if (airportMatch) {
                            data.depAirport = airportMatch[1];
                            data.arrAirport = airportMatch[2];
                        }
                    }
                    
                    return data;
                """, item)
                
                if not flight_data.get('price'):
                    continue
                
                price = flight_data.get('price', '').replace('$', '').replace(',', '').strip()
                airline = flight_data.get('airline', '').strip()
                duration = flight_data.get('duration', '').strip()
                dep_time = flight_data.get('depTime', '').strip()
                arr_time = flight_data.get('arrTime', '').strip()
                dep_airport = flight_data.get('depAirport', '').strip()
                arr_airport = flight_data.get('arrAirport', '').strip()
                stops_text = flight_data.get('stops', '').strip()
                dep_date = flight_data.get('depDate', '').strip()
                arr_date = flight_data.get('arrDate', '').strip()
                
                stops_count = 0
                if stops_text:
                    if 'direct' in stops_text.lower() or 'nonstop' in stops_text.lower() or stops_text == '0':
                        stops_count = 0
                    else:
                        stop_match = re.search(r'(\d+)', stops_text)
                        if stop_match:
                            stops_count = int(stop_match.group(1))
                
                segment = FlightSegment(
                    kalkis_havaalani=dep_airport or "Unknown",
                    varis_havaalani=arr_airport or "Unknown",
                    kalkis_saati=dep_time or "Unknown",
                    varis_saati=arr_time or "Unknown",
                    kalkis_tarih=dep_date or "",
                    varis_tarih=arr_date or "",
                    havayolu=airline or None,
                    sure=duration or None
                )
                
                flight = Flight(
                    toplam_fiyat=price or "0",
                    havayolu=airline or None,
                    segmentler=[segment],
                    aktarma_sayisi=stops_count,
                    toplam_sure=duration or None,
                    kalkis_havaalani=dep_airport or "Unknown",
                    varis_havaalani=arr_airport or "Unknown",
                    kalkis_tarih=dep_date or "",
                    varis_tarih=arr_date or "",
                    kalkis_saati=dep_time or "Unknown",
                    varis_saati=arr_time or "Unknown"
                )
                
                flights.append(flight)
                
            except Exception as e:
                continue
        
        return flights
    
    def search_flights(self, nereden: str, nereye: str, tarih: datetime, adults: int = 1, children: int = 0) -> FlightSearchResponse:
        """
        Search for flights
        
        Args:
            nereden: Origin airport/city code
            nereye: Destination airport/city code
            tarih: datetime object for departure date
            adults: Number of adult passengers (default: 1)
            children: Number of child passengers (default: 0)
        
        Returns:
            FlightSearchResponse with all flights
        """
        try:
            self._setup()
            self._select_origin(nereden)
            self._select_destination(nereye)
            self._select_date(tarih)
            self._select_passengers(adults=adults, children=children)
            self._click_search()
            
            flights = self._extract_flights_from_page()
            
            return FlightSearchResponse(
                nereden=nereden,
                nereye=nereye,
                gidis_tarih=tarih.strftime("%Y-%m-%d"),
                toplam_ucus=len(flights),
                ucusler=flights
            )
            
        except Exception as e:
            return FlightSearchResponse(
                nereden=nereden,
                nereye=nereye,
                gidis_tarih=tarih.strftime("%Y-%m-%d"),
                toplam_ucus=0,
                ucusler=[],
                error=str(e)
            )
    
    def cleanup(self):
        """Cleanup resources"""
        if hasattr(self, 'driver'):
            self.driver.quit()

