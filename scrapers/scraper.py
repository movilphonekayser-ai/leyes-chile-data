import asyncio
import aiohttp
import json
import logging
from bs4 import BeautifulSoup
from typing import List, Dict, Any
from urllib.parse import urljoin
import re
from datetime import datetime
import os

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ScraperDiputadosReales:
    BASE_URL = "https://www.camara.cl"
    LISTADO_URL = f"{BASE_URL}/diputados/diputados.aspx"
    
    def __init__(self):
        self.session = None
        self.diputados = []
        
    async def fetch(self, url: str) -> str:
        """Obtener HTML de una URL"""
        try:
            async with self.session.get(
                url, 
                timeout=aiohttp.ClientTimeout(total=30),
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
            ) as response:
                response.raise_for_status()
                return await response.text()
        except asyncio.TimeoutError:
            logger.error(f"Timeout en {url}")
            return ""
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return ""
    
    async def obtener_listado_diputados(self) -> List[Dict[str, str]]:
        """Obtener lista de todos los diputados con sus IDs"""
        logger.info("Obteniendo listado de diputados...")
        html = await self.fetch(self.LISTADO_URL)
        if not html:
            return []
            
        soup = BeautifulSoup(html, 'html.parser')
        diputados_links = []
        
        # Método 1: Buscar enlaces directos
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'diputado.aspx?prmId=' in href:
                match = re.search(r'prmId=(\d+)', href)
                if match:
                    diputado_id = match.group(1)
                    nombre = link.get_text(strip=True)
                    
                    if not nombre or len(nombre) < 3:
                        # Buscar nombre en elementos cercanos
                        for parent in link.find_parents(['div', 'li', 'td', 'h3', 'h4']):
                            text = parent.get_text(strip=True)
                            if len(text) > 10 and len(text) < 100:
                                nombre = text
                                break
                    
                    if nombre and len(nombre) > 2:
                        diputados_links.append({
                            'id': diputado_id,
                            'nombre': nombre[:100],
                            'url': urljoin(self.BASE_URL, href)
                        })
        
        # Método 2: Buscar por patrones alternativos
        if not diputados_links:
            for script in soup.find_all('script'):
                if script.string and 'prmId' in script.string:
                    matches = re.findall(r'prmId=(\d+)', script.string)
                    for match in matches:
                        diputados_links.append({
                            'id': match,
                            'nombre': f"Diputado ID {match}",
                            'url': f"{self.BASE_URL}/diputados/diputado.aspx?prmId={match}"
                        })
        
        # Eliminar duplicados por ID
        unique_diputados = {}
        for dip in diputados_links:
            if dip['id'] not in unique_diputados:
                unique_diputados[dip['id']] = dip
        
        logger.info(f"Encontrados {len(unique_diputados)} diputados únicos")
        return list(unique_diputados.values())
    
    def extraer_datos_diputado(self, html: str, diputado_id: str, nombre: str, url: str) -> Dict[str, Any]:
        """Extraer datos detallados de un diputado"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Inicializar datos
        datos = {
            'id': diputado_id,
            'nombre': nombre,
            'pagina_url': url,
            'ultima_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'partido': 'No disponible',
            'region': 'No disponible',
            'distrito': 'No disponible',
            'comisiones': [],
            'biografia': '',
            'foto_url': '',
            'email': '',
            'telefono': '',
            'periodo': '2022-2026'
        }
        
        try:
            # 1. FOTO
            img_selectors = [
                {'class': 'fotoDiputado'},
                {'id': 'fotoDiputado'},
                {'src': re.compile(r'img\.aspx')},
                {'alt': re.compile(r'diputado|diputada', re.I)}
            ]
            
            for selector in img_selectors:
                img = soup.find('img', selector)
                if img and 'src' in img.attrs:
                    datos['foto_url'] = urljoin(self.BASE_URL, img['src'])
                    break
            
            # 2. DATOS BÁSICOS
            contenido = soup.find('div', {'class': re.compile(r'contenido|content|info', re.I)}) or soup.body
            
            if contenido:
                texto_completo = contenido.get_text(' ', strip=True)
                
                # Partido
                partido_patterns = [
                    r'Partido:\s*([^\n\.]+)',
                    r'Partido\s+pol[ií]tico:\s*([^\n\.]+)',
                    r'[\w\s]+Partido\s+([^\n\.]+)',
                    r'Militante[\s:]+([^\n\.]+)'
                ]
                
                for pattern in partido_patterns:
                    match = re.search(pattern, texto_completo, re.IGNORECASE)
                    if match:
                        datos['partido'] = match.group(1).strip()
                        break
                
                # Región
                region_patterns = [
                    r'Regi[oó]n[:\s]+([^\n\.]+)',
                    r'Representa a[\s:]+([^\n\.]+)',
                    r'Circunscripci[oó]n[:\s]+([^\n\.]+)'
                ]
                
                for pattern in region_patterns:
                    match = re.search(pattern, texto_completo, re.IGNORECASE)
                    if match:
                        datos['region'] = match.group(1).strip()
                        break
                
                # Distrito
                distrito_match = re.search(r'Distrito[:\sN°]*(\d+)', texto_completo, re.IGNORECASE)
                if distrito_match:
                    datos['distrito'] = f"Distrito N° {distrito_match.group(1)}"
            
            # 3. COMISIONES
            comisiones_keywords = ['comisión', 'comision', 'commission', 'integrante de']
            for elem in soup.find_all(['h2', 'h3', 'h4', 'strong', 'b']):
                texto_elem = elem.get_text().lower()
                if any(keyword in texto_elem for keyword in comisiones_keywords):
                    siguiente = elem.find_next(['ul', 'ol', 'div', 'table', 'p'])
                    if siguiente:
                        comisiones = []
                        # Buscar en listas
                        for li in siguiente.find_all('li'):
                            comision = li.get_text(strip=True)
                            if comision and len(comision) > 5:
                                comisiones.append(comision)
                        
                        # Si no hay listas, buscar texto directo
                        if not comisiones:
                            texto = siguiente.get_text(strip=True)
                            if len(texto) > 20:
                                # Dividir por comas, puntos, etc.
                                posibles = re.split(r'[,;•\-–—]', texto)
                                for posible in posibles:
                                    limpio = posible.strip()
                                    if len(limpio) > 5 and len(limpio) < 100:
                                        comisiones.append(limpio)
                        
                        if comisiones:
                            datos['comisiones'] = comisiones[:10]  # Limitar a 10
                        break
            
            # 4. BIOGRAFÍA
            biografia_selectors = [
                {'class': 'biografia'},
                {'id': 'biografia'},
                {'class': re.compile(r'bio|resena|historial', re.I)},
                {'id': re.compile(r'bio|resena', re.I)}
            ]
            
            bio_encontrada = False
            for selector in biografia_selectors:
                bio_elem = soup.find('div', selector)
                if bio_elem:
                    bio_text = bio_elem.get_text(strip=True)
                    if len(bio_text) > 100:
                        datos['biografia'] = bio_text[:1500]
                        bio_encontrada = True
                        break
            
            # Si no encuentra biografía específica, tomar párrafos largos
            if not bio_encontrada:
                parrafos_largos = []
                for p in soup.find_all('p'):
                    texto_p = p.get_text(strip=True)
                    if len(texto_p) > 200 and len(texto_p) < 2000:
                        parrafos_largos.append(texto_p)
                
                if parrafos_largos:
                    datos['biografia'] = ' '.join(parrafos_largos)[:1500]
            
            # 5. CONTACTO
            contacto_text = soup.get_text()
            
            # Email
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', contacto_text)
            if email_match:
                datos['email'] = email_match.group(0)
            
            # Teléfono
            telefono_patterns = [
                r'\+56\s*\d[\d\s\-]{8,}',
                r'Tel[ée]fono[:\s]+([\d\s\-\(\)]{8,})',
                r'Fono[:\s]+([\d\s\-]{8,})',
                r'Contacto[:\s]+([\d\s\-]{8,})'
            ]
            
            for pattern in telefono_patterns:
                match = re.search(pattern, contacto_text, re.IGNORECASE)
                if match:
                    telefono = match.group(0) if isinstance(match.group(0), str) else match.group(1)
                    datos['telefono'] = re.sub(r'\s+', ' ', telefono).strip()
                    break
            
            # Limpiar campos
            for key in ['partido', 'region', 'distrito']:
                if datos[key] == 'No disponible':
                    datos[key] = ''
            
            # Limitar longitud de biografía
            if datos['biografia']:
                datos['biografia'] = datos['biografia'][:1500]
                
        except Exception as e:
            logger.warning(f"Error extrayendo datos para diputado {diputado_id}: {e}")
            import traceback
            logger.debug(traceback.format_exc())
        
        return datos
    
    async def procesar_diputado(self, diputado_info: Dict[str, str]) -> Dict[str, Any]:
        """Procesar un diputado individual"""
        try:
            html = await self.fetch(diputado_info['url'])
            if html:
                datos = self.extraer_datos_diputado(
                    html, 
                    diputado_info['id'], 
                    diputado_info['nombre'],
                    diputado_info['url']
                )
                logger.info(f"✅ Procesado: {diputado_info['nombre']} ({diputado_info['id']})")
                return datos
        except Exception as e:
            logger.error(f"❌ Error procesando {diputado_info['id']}: {e}")
        return None
    
    async def scrape_completo(self, max_concurrent: int = 5) -> List[Dict[str, Any]]:
        """Ejecutar scraping completo con concurrencia controlada"""
        logger.info("🚀 Iniciando scraping completo...")
        
        connector = aiohttp.TCPConnector(ssl=False, limit=10)
        timeout = aiohttp.ClientTimeout(total=300)
        
        async with aiohttp.ClientSession(
            connector=connector, 
            timeout=timeout,
            headers={'User-Agent': 'Mozilla/5.0'}
        ) as session:
            self.session = session
            
            # 1. Obtener listado
            diputados_lista = await self.obtener_listado_diputados()
            
            if not diputados_lista:
                logger.error("No se pudo obtener el listado de diputados")
                return []
            
            logger.info(f"📋 {len(diputados_lista)} diputados para procesar")
            
            # 2. Procesar con semáforo para controlar concurrencia
            semaphore = asyncio.Semaphore(max_concurrent)
            
            async def process_with_semaphore(diputado):
                async with semaphore:
                    return await self.procesar_diputado(diputado)
            
            # 3. Ejecutar todas las tareas
            tasks = [process_with_semaphore(dip) for dip in diputados_lista]
            resultados = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 4. Filtrar resultados válidos
            diputados_validos = []
            errores = 0
            
            for i, resultado in enumerate(resultados):
                if isinstance(resultado, Exception):
                    logger.error(f"❌ Error grave en diputado {i}: {resultado}")
                    errores += 1
                elif resultado:
                    diputados_validos.append(resultado)
                else:
                    errores += 1
            
            logger.info(f"📊 Scraping completado. {len(diputados_validos)} exitosos, {errores} errores")
            return diputados_validos
    
    def guardar_json(self, datos: List[Dict[str, Any]], archivo: str = "data/diputados.json"):
        """Guardar datos en formato JSON"""
        # Crear directorio si no existe
        os.makedirs(os.path.dirname(archivo), exist_ok=True)
        
        output = {
            'fecha_generacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_diputados': len(datos),
            'diputados': sorted(datos, key=lambda x: x['nombre'])
        }
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(output, f, ensure_ascii=False, indent=2, sort_keys=True)
        
        logger.info(f"💾 Datos guardados en {archivo}")
        
        # También guardar versión mínima para el dashboard
        output_min = {
            'ultima_actualizacion': output['fecha_generacion'],
            'diputados': output['diputados']
        }
        
        with open(archivo.replace('.json', '_min.json'), 'w', encoding='utf-8') as f:
            json.dump(output_min, f, ensure_ascii=False)
        
        return archivo

async def main():
    """Función principal"""
    scraper = ScraperDiputadosReales()
    
    try:
        # Ejecutar scraping
        datos = await scraper.scrape_completo()
        
        if datos:
            # Guardar resultados
            archivo = scraper.guardar_json(datos)
            
            # Mostrar resumen
            print(f"\n{'='*60}")
            print("✅ SCRAPING COMPLETADO EXITOSAMENTE")
            print(f"{'='*60}")
            print(f"📈 Total diputados procesados: {len(datos)}")
            
            # Estadísticas
            partidos = {}
            regiones = {}
            
            for dip in datos:
                partido = dip['partido'] if dip['partido'] else 'Sin partido'
                region = dip['region'] if dip['region'] else 'Sin región'
                
                partidos[partido] = partidos.get(partido, 0) + 1
                regiones[region] = regiones.get(region, 0) + 1
            
            print(f"\n🏛️  Distribución por partido:")
            for partido, count in sorted(partidos.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"   {partido}: {count}")
            
            print(f"\n📍 Distribución por región:")
            for region, count in sorted(regiones.items(), key=lambda x: x[1], reverse=True):
                if region and region != 'Sin región':
                    print(f"   {region}: {count}")
            
            print(f"\n💾 Archivo guardado: {archivo}")
            print(f"📊 Tamaño: {os.path.getsize(archivo) / 1024:.1f} KB")
            
        else:
            print("❌ No se obtuvieron datos. Revisar logs.")
            
    except Exception as e:
        logger.error(f"❌ Error en scraping: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)
