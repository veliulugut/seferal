from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class FlightSegment(BaseModel):
    """Represents a single flight segment"""
    kalkis_havaalani: str
    varis_havaalani: str
    kalkis_saati: str
    varis_saati: str
    kalkis_tarih: str
    varis_tarih: str
    havayolu: Optional[str] = None
    ucus_no: Optional[str] = None
    sure: Optional[str] = None


class Flight(BaseModel):
    """Represents a complete flight (may have multiple segments for connections)"""
    toplam_fiyat: str
    para_birimi: Optional[str] = "USD"
    havayolu: Optional[str] = None
    segmentler: List[FlightSegment] = Field(default_factory=list)
    aktarma_sayisi: int = 0
    toplam_sure: Optional[str] = None
    kalkis_havaalani: str
    varis_havaalani: str
    kalkis_tarih: str
    varis_tarih: str
    kalkis_saati: str
    varis_saati: str
    error: Optional[str] = None


class FlightSearchRequest(BaseModel):
    nereden: str
    nereye: str
    gidis_tarih: datetime
    donus_tarih: Optional[datetime] = None
    yolcu_sayisi: int = 1


class FlightSearchResponse(BaseModel):
    nereden: str
    nereye: str
    gidis_tarih: str
    donus_tarih: Optional[str] = None
    toplam_ucus: int
    ucusler: List[Flight]
    error: Optional[str] = None

