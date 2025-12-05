from pydantic import BaseModel
from typing import Optional


class Seat(BaseModel):
    koltuk_no: str
    koltuk_id: Optional[str] = None
    durum: str
    musait: bool
    text: Optional[str] = None
    koltuk_tipi: Optional[str] = None
    cinsiyet_kisitlamasi: Optional[str] = None

