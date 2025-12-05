from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class Seat(BaseModel):
    koltuk_no: str
    koltuk_id: Optional[str] = None
    durum: str
    musait: bool
    text: Optional[str] = None
    koltuk_tipi: Optional[str] = None
    cinsiyet_kisitlamasi: Optional[str] = None


class SeatPlan(BaseModel):
    toplam_koltuk: int
    bos: int
    dolu: int
    bos_koltuklar: List[Dict[str, Any]] = Field(default_factory=list)


class Trip(BaseModel):
    sefer_takip_no: Optional[str] = None
    kalkis_saati: Optional[str] = None
    sefer_tipi: Optional[str] = None
    otobus_tipi: Optional[str] = None
    fiyat: Optional[str] = None
    firma: Optional[str] = None
    koltuk_plani: Optional[SeatPlan] = None
    error: Optional[str] = None


class SearchRequest(BaseModel):
    nereden: str
    nereye: str
    tarih: datetime


class SearchResponse(BaseModel):
    nereden: str
    nereye: str
    tarih: str
    toplam_sefer: int
    seferler: List[Trip]
    error: Optional[str] = None

