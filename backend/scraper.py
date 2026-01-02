"""
Scraper para DropKiller y Adskiller
"""
import requests
import time
from typing import List, Dict, Optional
from config import COUNTRIES

class DropKillerScraper:
    """Scraper para obtener productos de DropKiller"""
    
    BASE_URL = "https://app.dropkiller.com"
    PUBLIC_API = "https://extension-api.dropkiller.com"
    
    def __init__(self, jwt: str):
        self.jwt = jwt
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {jwt}",
            "Cookie": f"__session={jwt}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
    
    def get_products(
        self,
        country_code: str = "CO",
        platform: str = "dropi",
        min_sales_7d: int = 50,
        min_stock: int = 30,
        min_price: int = 20000,
        max_price: int = 200000,
        limit: int = 50,
        page: int = 1
    ) -> List[Dict]:
        """
        Obtiene productos del dashboard de DropKiller con filtros
        """
        country = COUNTRIES.get(country_code, COUNTRIES["CO"])
        
        params = {
            "platform": platform,
            "country": country["dropkiller_id"],
            "limit": limit,
            "page": page,
            "s7min": min_sales_7d,
            "stock-min": min_stock,
            "price-min": min_price,
            "price-max": max_price
        }
        
        try:
            url = f"{self.BASE_URL}/api/products"
            response = self.session.get(url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return data.get("products", data.get("data", []))
            else:
                print(f"Error {response.status_code}: {response.text[:200]}")
                return []
                
        except Exception as e:
            print(f"Error obteniendo productos: {e}")
            return []
    
    def get_product_history(self, product_ids: List[str], country_code: str = "CO") -> Dict:
        """
        Obtiene historial de ventas de la API publica (sin auth)
        """
        if not product_ids:
            return {}
        
        ids_str = ",".join(str(pid) for pid in product_ids)
        url = f"{self.PUBLIC_API}/api/v3/history?ids={ids_str}&country={country_code}"
        
        try:
            response = requests.get(url, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                return {item["externalId"]: item for item in data}
            else:
                print(f"Error historial: {response.status_code}")
                return {}
                
        except Exception as e:
            print(f"Error obteniendo historial: {e}")
            return {}
    
    def get_product_detail(self, product_id: str, platform: str = "dropi") -> Optional[Dict]:
        """
        Obtiene detalle completo de un producto
        """
        try:
            url = f"{self.BASE_URL}/api/products/{product_id}?platform={platform}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"Error detalle producto: {e}")
            return None


class AdskillerScraper:
    """Scraper para obtener anuncios de competencia de Adskiller"""
    
    BASE_URL = "https://app.dropkiller.com"
    
    def __init__(self, jwt: str):
        self.jwt = jwt
        self.session = requests.Session()
        self.session.headers.update({
            "Authorization": f"Bearer {jwt}",
            "Cookie": f"__session={jwt}",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
            "Content-Type": "application/json"
        })
    
    def search_ads(
        self,
        search_term: str,
        country_code: str = "CO",
        platform: str = "facebook",
        limit: int = 20
    ) -> List[Dict]:
        """
        Busca anuncios relacionados con un termino (nombre de producto)
        """
        country = COUNTRIES.get(country_code, COUNTRIES["CO"])
        
        payload = {
            "platform": platform,
            "enabled": True,
            "sortBy": "updated_at",
            "order": "desc",
            "countryId": country["adskiller_id"],
            "search": search_term,
            "limit": limit
        }
        
        try:
            url = f"{self.BASE_URL}/api/adskiller"
            response = self.session.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if data.get("success"):
                    return data.get("data", {}).get("data", [])
            
            return []
            
        except Exception as e:
            print(f"Error buscando ads: {e}")
            return []
    
    def get_ad_detail(self, ad_id: str) -> Optional[Dict]:
        """
        Obtiene detalle completo de un anuncio con analisis IA
        """
        try:
            url = f"{self.BASE_URL}/api/adskiller/{ad_id}"
            response = self.session.get(url, timeout=30)
            
            if response.status_code == 200:
                return response.json()
            return None
            
        except Exception as e:
            print(f"Error detalle ad: {e}")
            return None
    
    def find_competitors(self, product_name: str, country_code: str = "CO") -> List[Dict]:
        """
        Encuentra competidores vendiendo un producto similar
        Busca en Facebook e Instagram
        """
        competitors = []
        
        keywords = product_name.lower().split()[:3]
        search_term = " ".join(keywords)
        
        fb_ads = self.search_ads(search_term, country_code, "facebook", limit=15)
        competitors.extend(fb_ads)
        
        time.sleep(0.5)
        
        tt_ads = self.search_ads(search_term, country_code, "tiktok", limit=10)
        competitors.extend(tt_ads)
        
        return competitors


def extract_competitor_data(ads: List[Dict]) -> List[Dict]:
    """
    Extrae datos relevantes de los anuncios para analisis de competencia
    """
    competitors = []
    
    for ad in ads:
        sales_angles = ad.get("salesAngles", [])
        main_angle = sales_angles[0].get("angle", "") if sales_angles else ""
        
        active_time = ad.get("active_time", 0)
        active_days = active_time // (24 * 60 * 60) if active_time else 0
        
        competitor = {
            "page_name": ad.get("page_name", ""),
            "company_name": ad.get("company_name", ""),
            "ad_url": ad.get("url", ""),
            "store_url": ad.get("link", ""),
            "likes": ad.get("likes", 0),
            "comments": ad.get("comments", 0),
            "shares": ad.get("shares", 0),
            "active_days": active_days,
            "main_angle": main_angle,
            "sales_angles": [a.get("angle") for a in sales_angles],
            "thumbnail_url": ad.get("images", [""])[0] if ad.get("images") else "",
            "video_url": ad.get("videos", [""])[0] if ad.get("videos") else "",
            "cta": ad.get("cta", ""),
            "description": ad.get("description", "")[:500],
            "platforms": ad.get("platforms", []),
        }
        
        total_engagement = competitor["likes"] + competitor["comments"] * 2 + competitor["shares"] * 3
        if total_engagement > 1000:
            competitor["engagement_level"] = "Alto"
        elif total_engagement > 200:
            competitor["engagement_level"] = "Medio"
        else:
            competitor["engagement_level"] = "Bajo"
        
        competitors.append(competitor)
    
    return competitors


def extract_used_angles(competitors: List[Dict]) -> List[str]:
    """
    Extrae todos los angulos de venta usados por la competencia
    """
    angles = set()
    for comp in competitors:
        for angle in comp.get("sales_angles", []):
            if angle:
                angles.add(angle)
        if comp.get("main_angle"):
            angles.add(comp["main_angle"])
    return list(angles)
