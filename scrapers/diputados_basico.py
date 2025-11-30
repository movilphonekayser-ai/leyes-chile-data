import requests
from bs4 import BeautifulSoup
import json
import pandas as pd

def scrapear_diputados_basico():
    """Scraper inicial para información basal de diputados"""
    print("🔄 Iniciando scraper de diputados...")
    
    # URL de la Cámara de Diputados
    url = "https://www.camara.cl/diputados/diputados.aspx"
    
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        diputados = []
        
        # Aquí va la lógica de scraping específica
        # Por ahora datos de ejemplo para la estructura
        diputados_ejemplo = [
            {
                "id": 1,
                "nombre": "Ejemplo Diputado 1",
                "partido": "Partido Ejemplo",
                "distrito": "RM-1",
                "comisiones": ["Educación", "Salud"],
                "email": "ejemplo@camara.cl",
                "telefono": "+56 2 1234 5678"
            }
        ]
        
        # Guardar datos
        with open('../data/diputados.json', 'w', encoding='utf-8') as f:
            json.dump(diputados_ejemplo, f, ensure_ascii=False, indent=2)
            
        print("✅ Datos de diputados guardados exitosamente")
        return diputados_ejemplo
        
    except Exception as e:
        print(f"❌ Error en scraping: {e}")
        return []

if __name__ == "__main__":
    scrapear_diputados_basico()
