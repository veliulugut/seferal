from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.scraper.manager import ScraperManager
from app.models.trip import SearchResponse

app = FastAPI(title="Seferal API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = ScraperManager()


class SearchRequest(BaseModel):
    nereden: str = Field(..., description="Kalkış şehri")
    nereye: str = Field(..., description="Varış şehri")
    tarih: str = Field(..., description="Tarih (YYYY-MM-DD formatında)")
    companies: Optional[List[str]] = Field(None, description="Firma listesi (None = tüm firmalar)")


@app.get("/")
async def root():
    return {"message": "Seferal API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/companies")
async def get_companies():
    """Mevcut firmaları listele"""
    return {"companies": manager.get_available_companies()}


@app.post("/search", response_model=SearchResponse)
async def search_trips(request: SearchRequest):
    """Sefer ara"""
    try:
        tarih = datetime.strptime(request.tarih, "%Y-%m-%d")
    except ValueError:
        raise HTTPException(status_code=400, detail="Tarih formatı hatalı. YYYY-MM-DD formatında olmalı.")
    
    result = manager.search_all(
        nereden=request.nereden,
        nereye=request.nereye,
        tarih=tarih,
        companies=request.companies
    )
    
    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

