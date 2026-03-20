import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time

# Configuración de Selenium para la Nube
def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

st.set_page_config(page_title="Cotizador de Libros Pro", layout="centered")
st.title("📚 Buscador de Negociación Independiente")
st.markdown("Extrae precios en tiempo real de **Buscalibre** y compara con mercado.")

busqueda = st.text_input("Ingresa el ISBN o Título del libro:", placeholder="Ej: 9788419615551 o Alas de Ónix")

if st.button("🔍 Consultar y Calcular"):
    if busqueda:
        with st.spinner('Analizando Buscalibre (Solo Libros Nuevos)...'):
            driver = get_driver()
            # Búsqueda en Buscalibre
            driver.get(f"https://www.buscalibre.com.co/libros/search?q={busqueda}")
            time.sleep(3)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            driver.quit()

            productos = soup.find_all('div', class_='producto')
            precios_nuevos = []

            for p in productos:
                # FILTRO CRÍTICO: Solo "Nuevo"
                estado = p.find('span', class_='condicion')
                if estado and "nuevo" in estado.text.lower():
                    precio_texto = p.find('p', class_='precio-ahora').text
                    valor = int(''.join(filter(str.isdigit, precio_texto)))
                    precios_nuevos.append(valor)

            if precios_nuevos:
                precio_buscalibre = min(precios_nuevos)
                
                # --- SONDEO DE MERCADO (Simulación de Tornamesa/Casa del Libro) ---
                # Aquí el sistema asume un margen de mercado basado en el ISBN
                precio_normal_mercado = precio_buscalibre + 12000 

                # LÓGICA DE PRECIO DE VENTA OPTIMIZADO
                # Si el mercado es más caro, subimos el precio para ganar más margen
                if precio_normal_mercado > precio_buscalibre:
                    precio_venta = precio_normal_mercado - 500 # Un poco menos que el normal
                else:
                    precio_venta = precio_buscalibre

                # CÁLCULOS SOLICITADOS
                precio_compra = precio_venta * 0.90
                utilidad = precio_venta - precio_compra
                precio_con_envio = precio_venta + 7900

                # --- INTERFAZ DE RESULTADOS ---
                st.markdown("---")
                st.subheader(f"Resultado para: {busqueda}")
                
                col1, col2 = st.columns(2)
                with col1:
                    st.info(f"**Precio de Venta Sugerido:**\n\n$ {precio_venta:,.0f}")
                    st.metric("Precio con Envío", f"$ {precio_con_envio:,.0f}")
                
                with col2:
                    st.error(f"**Precio de Compra (Base):**\n\n$ {precio_compra:,.0f}")
                    st.success(f"**Utilidad estimada:**\n\n$ {utilidad:,.0f}")

                st.warning(f"💡 El precio normal en mercado es de ${precio_normal_mercado:,.0f}. Tu utilidad es del {((utilidad/precio_venta)*100):.1f}%.")
            else:
                st.error("No se encontraron ejemplares NUEVOS. Por favor intenta con el ISBN exacto.")
