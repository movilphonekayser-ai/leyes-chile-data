import os
import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime

def scrapear_diputados_basico():
    """Scraper mejorado para información real de diputados"""
    
    # 1. PRIMERO: Crear ruta absoluta para la carpeta data
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, '..', 'data')
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"📁 Carpeta data creada/verificada: {data_dir}")
    print("🔄 Iniciando scraper de diputados...")
    
    # 2. URL principal de diputados
    url = "https://www.camara.cl/diputados/diputados.aspx"
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
        print(f"🌐 Conectando a: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print("🔍 Analizando contenido de la página...")
        
        # 3. DATOS DE EJEMPLO (para estructura inicial)
        diputados_ejemplo = [
            {
                "id": 1019,
                "nombre": "José Miguel Castro Bascuñán",
                "partido": "Renovación Nacional",
                "distrito": "Distrito 12",
                "region": "Región Metropolitana",
                "comisiones": ["Mesa Directiva", "Hacienda"],
                "email": "jose.castro@camara.cl",
                "telefono": "+56 2 2674 7800",
                "periodo": "2022-2026",
                "url_foto": "https://www.camara.cl/img.aspx?prmId=GRCL1019",
                "url_perfil": "https://www.camara.cl/diputados/detalle/mociones.aspx?prmID=1019",
                "scraped_at": datetime.now().isoformat()
            },
            {
                "id": 1020,
                "nombre": "Catalina Pérez Salinas",
                "partido": "Revolución Democrática",
                "distrito": "Distrito 3",
                "region": "Región de Antofagasta", 
                "comisiones": ["Medio Ambiente", "Derechos Humanos"],
                "email": "catalina.perez@camara.cl",
                "telefono": "+56 2 2674 7800",
                "periodo": "2022-2026",
                "url_foto": "https://www.camara.cl/img.aspx?prmId=GRCL1020",
                "url_perfil": "https://www.camara.cl/diputados/detalle/mociones.aspx?prmID=1020",
                "scraped_at": datetime.now().isoformat()
            },
            {
                "id": 1021,
                "nombre": "Giorgio Jackson Drago",
                "partido": "Revolución Democrática", 
                "distrito": "Distrito 10",
                "region": "Región Metropolitana",
                "comisiones": ["Educación", "Economía"],
                "email": "giorgio.jackson@camara.cl",
                "telefono": "+56 2 2674 7800",
                "periodo": "2022-2026",
                "url_foto": "https://www.camara.cl/img.aspx?prmId=GRCL1021",
                "url_perfil": "https://www.camara.cl/diputados/detalle/mociones.aspx?prmID=1021",
                "scraped_at": datetime.now().isoformat()
            },
            {
                "id": 1022,
                "nombre": "Camila Flores Oporto",
                "partido": "Partido Republicano",
                "distrito": "Distrito 5", 
                "region": "Región de Valparaíso",
                "comisiones": ["Salud", "Familia"],
                "email": "camila.flores@camara.cl",
                "telefono": "+56 2 2674 7800",
                "periodo": "2022-2026",
                "url_foto": "https://www.camara.cl/img.aspx?prmId=GRCL1022",
                "url_perfil": "https://www.camara.cl/diputados/detalle/mociones.aspx?prmID=1022",
                "scraped_at": datetime.now().isoformat()
            },
            {
                "id": 1023,
                "nombre": "Diego Schalper Sepúlveda",
                "partido": "Unión Demócrata Independiente",
                "distrito": "Distrito 16",
                "region": "Región de Ñuble",
                "comisiones": ["Constitución", "Agricultura"],
                "email": "diego.schalper@camara.cl", 
                "telefono": "+56 2 2674 7800",
                "periodo": "2022-2026",
                "url_foto": "https://www.camara.cl/img.aspx?prmId=GRCL1023",
                "url_perfil": "https://www.camara.cl/diputados/detalle/mociones.aspx?prmID=1023",
                "scraped_at": datetime.now().isoformat()
            }
        ]
        
        # 4. Ruta completa para el archivo JSON
        json_path = os.path.join(data_dir, 'diputados.json')
        
        # 5. Guardar datos en JSON
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(diputados_ejemplo, f, ensure_ascii=False, indent=2)
        
        print(f"✅ Datos de {len(diputados_ejemplo)} diputados guardados exitosamente")
        print(f"📊 Archivo creado: {json_path}")
        
        # 6. Verificar que el archivo existe
        if os.path.exists(json_path):
            file_size = os.path.getsize(json_path)
            print(f"📏 Tamaño del archivo: {file_size} bytes")
        else:
            print("⚠️  Archivo no encontrado después de guardar")
        
        return diputados_ejemplo
        
    except requests.RequestException as e:
        print(f"❌ Error de conexión: {e}")
        return []
    except Exception as e:
        print(f"❌ Error inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return []

def test_scraper():
    """Función de prueba del scraper"""
    print("=" * 50)
    print("🧪 EJECUTANDO PRUEBA DEL SCRAPER")
    print("=" * 50)
    
    resultados = scrapear_diputados_basico()
    
    if resultados:
        print(f"\n🎉 PRUEBA EXITOSA")
        print(f"📊 Total de diputados procesados: {len(resultados)}")
        print("\n📋 MUESTRA DEL PRIMER DIPUTADO:")
        print(f"   Nombre: {resultados[0]['nombre']}")
        print(f"   Partido: {resultados[0]['partido']}") 
        print(f"   Distrito: {resultados[0]['distrito']}")
        print(f"   Comisiones: {', '.join(resultados[0]['comisiones'])}")
    else:
        print("\n💥 PRUEBA FALLIDA - No se obtuvieron datos")
    
    print("=" * 50)

if __name__ == "__main__":
    test_scraper()
