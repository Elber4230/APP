import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import urllib.parse
import os

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    # User-Agent para que Buscalibre no nos bloquee
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    if os.path.exists("/usr/bin/chromium"):
        options.binary_location = "/usr/bin/chromium"
    return webdriver.Chrome(options=options)

st.set_page_config(page_title="Cotizador Pro", page_icon="📚")
st.title("🚀 Buscador de Libros & Negociación")

busqueda = st.text_input("ISBN o Título del libro:", placeholder="Ej: Cien años de soledad")

if st.button("🔍 Calcular Negociación"):
    if busqueda:
        with st.spinner('Buscando el mejor precio de libro NUEVO...'):
            try:
                driver = get_driver()
                # Buscamos directamente en la URL de Colombia
                url = f"https://www.buscalibre.com.co/libros/search?q={urllib.parse.quote(busqueda)}"
                driver.get(url)
                time.sleep(5) # Esperamos a que cargue todo el contenido
                
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                driver.quit()

                # Buscamos todos los contenedores de libros
                productos = soup.select('div.producto, .buscar-un-producto')
                precios_nuevos = []

                for p in productos:
                    texto_completo = p.get_text().lower()
                    
                    # FILTRO: Solo si NO dice "usado" y SI tiene precio ahora
                    # Buscalibre a veces no tiene la etiqueta 'condicion' clara, 
                    # así que buscamos por exclusión de la palabra "usado"
                    if "usado" not in texto_completo:
                        precio_tag = p.select_one('.precio-ahora, .p-ahora')
                        if precio_tag:
                            valor = int(''.join(filter(str.isdigit, precio_tag.text)))
                            if valor > 0:
                                precios_nuevos.append(valor)

                if precios_nuevos:
                    pb = min(precios_nuevos)
                    # Lógica de Negociación Solicitada
                    pn = pb + 15000 # Sondeo mercado estimado
                    pv = pn - 500 if pn > pb else pb 
                    
                    p_compra = pv * 0.90
                    utilidad = pv - p_compra
                    p_envio = pv + 7900

                    # --- INTERFAZ ---
                    st.markdown("---")
                    st.subheader(f"Mejor Precio Nuevo Encontrado: ${pb:,.0f}")
                    
                    c1, c2, c3 = st.columns(3)
                    with c1:
                        st.metric("PRECIO COMPRA", f"${p_compra:,.0f}")
                    with c2:
                        st.metric("UTILIDAD", f"${utilidad:,.0f}", delta=f"{(utilidad/pv)*100:.1f}%")
                    with c3:
                        st.metric("CON ENVÍO", f"${p_envio:,.0f}")
                    
                    st.success(f"**Precio de Venta sugerido para negociar:** ${pv:,.0f}")

                    # Botón WhatsApp
                    txt = f"📖 Cotización: {busqueda}\n💰 Precio: ${pv:,.0f}\n🚚 Envío: $7,900\n✅ TOTAL: ${p_envio:,.0f}"
                    url_wa = f"https://wa.me/?text={urllib.parse.quote(txt)}"
                    st.markdown(f'<a href="{url_wa}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; cursor:pointer; font-weight:bold;">📱 Enviar por WhatsApp</button></a>', unsafe_allow_html=True)
                else:
                    st.error("No se detectaron precios para libros nuevos. Intenta ser más específico (ej. agrega el autor o ISBN).")
                    
            except Exception as e:
                st.error(f"Error de conexión: {e}")
