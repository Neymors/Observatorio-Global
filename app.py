
from flask import Flask, render_template
import feedparser
import re
from cachetools import cached, TTLCache
from functools import lru_cache  # Importa lru_cache

app = Flask(__name__)

# Feeds RSS de ejemplo (puedes agregar o quitar)
RSS_FEEDS = [
    "https://www.infobae.com/feeds/rss/",
    "https://www.clarin.com/rss/lo-ultimo/",
    "https://www.pagina12.com.ar/rss/ultimas-noticias",
    "https://feeds.bbci.co.uk/mundo/rss.xml",
    "https://www.cronista.com/",
    "https://news.google.com/home?hl=es-419&gl=AR&ceid=AR%3Aes-419",
    "https://news.google.com/foryou?hl=es-419&gl=AR&ceid=AR%3Aes-419",
    "https://tn.com.ar/politica/",
    "https://tn.com.ar/economia/",
    "https://tn.com.ar/internacional/",
    "https://tn.com.ar/policiales/",
    "https://www.ambito.com/",
    "https://www.lacapital.com.ar/",
    "https://www.infobae.com/tag/javier-milei/",
    "https://www.infobae.com/tag/trump/",
    "https://www.infobae.com/tag/giorgia-meloni/",
    "https://www.infobae.com/politica/",
    "https://www.infobae.com/economia/",
    "https://www.infobae.com/sociedad/policiales/",
    "https://www.infobae.com/judiciales/",
    "https://eleconomista.com.ar/",
    "https://eleconomista.com.ar/especial/dolar",
    "https://eleconomista.com.ar/criptomonedas/",
    "https://eleconomista.com.ar/especial/inversiones",
    "https://eleconomista.com.ar/politica/",
    "https://eleconomista.com.ar/internacional/",
    "https://eleconomista.com.ar/negocios/",
    "https://mi8.com.ar/category/locales/",
    "https://www.bbc.com/news",
    "https://www.bbc.com/news/topics/c2vdnvdg6xxt",
    "https://www.bbc.com/news/war-in-ukraine",
    "https://www.bbc.com/business",
    "https://www.bbc.com/business/technology-of-business",
    "https://www.bbc.com/business/future-of-business",
    "https://www.lanacion.com.ar/economia/",
    "https://www.lanacion.com.ar/politica/",
    "https://www.economist.com/",
    "https://www.nytimes.com/international/",
    "https://www.nytimes.com/international/section/us",
    "https://www.nytimes.com/international/section/business",
    "https://www.nytimes.com/international/section/world",
    "https://www.economist.com/topics/economy",
    "https://www.economist.com/",
    "https://www.ft.com/",
    "https://www.ft.com/world",
    "https://www.ft.com/middle-east-war",
    "https://www.ft.com/us",
    "https://www.ft.com/technology",
    "https://www.wsj.com/",
    "https://www.wsj.com/world?mod=nav_top_section",
    "https://www.wsj.com/business?mod=nav_top_section",
    "https://www.wsj.com/personal-finance?mod=nav_top_section",
    "https://www.kp.ru/",
    "https://www.kp.ru/money/",
    "https://www.radaraustral.com/",
    "https://www.radaraustral.com/articulos/categoria/indopacifico/",
    "https://www.radaraustral.com/articulos/categoria/argentina/",
    "https://www.radaraustral.com/articulos/categoria/global/",
    "https://www.radaraustral.com/articulos/categoria/conflictos/",
    "https://www.radaraustral.com/articulos/categoria/ecom/",
    "https://www.radaraustral.com/articulos/categoria/moafrica/",
    "https://elpais.com/noticias/geopolitica/",
    "https://www.infobae.com/tag/geopolitica/",
    "https://elpais.com/us/?ed=us",
    "https://foreignpolicy.com/2024/03/27/europe-eu-nato-european-army-russia-ukraine-defense-military-strategy/",
]

# Creamos una caché con 128 entradas y TTL de 1800 segundos (30 minutos)
cache = TTLCache(maxsize=128, ttl=1800)

def extract_image(entry):
    """
    Intenta extraer la URL de la imagen de 'media_content', 'media_thumbnail'
    o del HTML en 'summary'. Si no encuentra ninguna, devuelve cadena vacía.
    """
    # 1) media_content
    if 'media_content' in entry and entry.media_content:
        return entry.media_content[0].get('url', '')

    # 2) media_thumbnail
    if 'media_thumbnail' in entry and entry.media_thumbnail:
        return entry.media_thumbnail[0].get('url', '')

    # 3) Buscar un <img src="..."> en el summary (a veces viene ahí)
    if hasattr(entry, 'summary'):
        match = re.search(r'<img.*?src=[\"\\\'](.*?)[\"\\\']', entry.summary, re.IGNORECASE)
        if match:
            return match.group(1)

    # Si no encuentra nada, devuelve vacío

@lru_cache(maxsize=128)
def get_news():
    news_items = []

    for feed_url in RSS_FEEDS:
        feed = feedparser.parse(feed_url)

        for entry in feed.entries:
            try:
                image_url = extract_image(entry)
                if not image_url:
                    continue  # Saltar si no hay imagen

                description = 'Sin descripción'
                if hasattr(entry, 'summary'):
                    description = entry.summary

                source = 'Fuente desconocida'
                if hasattr(feed.feed, 'title'):
                    source = feed.feed.title

                pub_date = 'Fecha no disponible'
                if hasattr(entry, 'published'):
                    pub_date = entry.published

                news_items.append({
                    "title": entry.title,
                    "link": entry.link,
                    "description": description,
                    "source": source,
                    "pubDate": pub_date,
                    "image_url": image_url
                })

            except Exception as e:
                print(f"Error al procesar la entrada: {e}")
                continue  # Saltar a la siguiente entrada en caso de error

    return news_items    

@app.route("/")
def home():
    # Se obtienen las noticias desde la función cacheada
    news_items = get_news()
    return render_template("index.html", news_items=news_items)

if __name__ == "__main__":
    app.run()
