import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import urllib.parse

def get_driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

st.set_page_config(page_title="Cotizador Pro", page_icon="📚")
st.title("🚀 Buscador de Libros & Negociación")

busqueda = st.text_input("ISBN o Título del libro:", placeholder="Ej: Alas de Ónix")

if st.button("🔍 Calcular Negociación"):
    with st.spinner('Escaneando mercado...'):
        driver = get_driver()
        driver.get(f"https://www.buscalibre.com.co/libros/search?q={busqueda}")
        time.sleep(3)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()

        precios_nuevos = []
        for p in soup.find_all('div', class_='producto'):
            condicion = p.find('span', class_='condicion')
            if condicion and "nuevo" in condicion.text.lower():
                precio_texto = p.find('p', class_='precio-ahora').text
                precios_nuevos.append(int(''.join(filter(str.isdigit, precio_texto))))

        if precios_nuevos:
            pb = min(precios_nuevos)
            pn = pb + 12000 # Precio normal estimado
            pv = pn - 500 if pn > pb else pb 
            
            p_compra = pv * 0.90
            utilidad = pv - p_compra
            p_envio = pv + 7900

            # --- RECUADROS DE RESULTADOS ---
            st.markdown("---")
            c1, c2 = st.columns(2)
            with c1:
                st.metric("PRECIO COMPRA (-10%)", f"${p_compra:,.0f}")
                st.metric("PRECIO CON ENVÍO", f"${p_envio:,.0f}")
            with c2:
                st.metric("UTILIDAD", f"${utilidad:,.0f}", delta=f"{(utilidad/pv)*100:.1f}%")
                st.info(f"**Precio Venta:** ${pv:,.0f}")

            # --- BOTÓN DE WHATSAPP ---
            mensaje = f"Hola, te comparto la cotización:\n\n📖 Libro: {busqueda}\n💰 Precio: ${pv:,.0f}\n🚚 Envío: $7,900\n✅ Total: ${p_envio:,.0f}"
            msg_encoded = urllib.parse.quote(mensaje)
            whatsapp_url = f"https://wa.me/?text={msg_encoded}"
            
            st.markdown(f'''
                <a href="{whatsapp_url}" target="_blank">
                    <button style="width:100%; background-color:#25D366; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer; font-weight:bold;">
                        📱 Enviar Cotización por WhatsApp
                    </button>
                </a>
            ''', unsafe_allow_html=True)
        else:
            st.error("No se encontraron libros NUEVOS.")
