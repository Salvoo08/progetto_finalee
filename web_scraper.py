from bs4 import BeautifulSoup
import requests
from gensim.summarization import summarize, keywords
from difflib import SequenceMatcher

siti_affidabili = {
    "ONU Italia": "https://unric.org/it/effetti-del-cambiamento-climatico/",
    "IPCC Italia": "https://ipccitalia.cmcc.it/",
    "NASA": "https://climate.nasa.gov/",
    "NOAA": "https://www.noaa.gov/climate",
    "FAO": "https://www.fao.org/climate-change/en/"
}

def get_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta: {e}")
        return None

def summarize_content(content):
    try:
        summary = summarize(content, word_count=100)
        key_topics = keywords(content, words=10, lemmatize=True)
        return summary, key_topics
    except ValueError as e:
        print(f"Errore nel creare il riassunto: {e}")
        return None, None

def compare_keywords(page_keywords, reliable_keywords):
    match_ratio = SequenceMatcher(None, page_keywords, reliable_keywords).ratio()
    return match_ratio

def read_model(url):
    page_content = get_page_content(url)
    if page_content:
        bs = BeautifulSoup(page_content, "lxml")
        main_content = ' '.join([p.text for p in bs.find_all('p')])
        summary, key_topics = summarize_content(main_content)
        if summary and key_topics:
            reliable = False
            for site_name, site_url in siti_affidabili.items():
                site_content = get_page_content(site_url)
                if site_content:
                    site_bs = BeautifulSoup(site_content, "lxml")
                    site_text = ' '.join([p.text for p in site_bs.find_all('p')])
                    _, site_keywords = summarize_content(site_text)
                    if site_keywords:
                        match_ratio = compare_keywords(key_topics, site_keywords)
                        if match_ratio >= 0.6:
                            reliable = True
                            return summary, key_topics, f"Informazioni affidabili e coerenti con quelle di {site_name}."
            if not reliable:
                return summary, key_topics, "Le informazioni potrebbero non essere affidabili."
        return None, None, "Impossibile creare il riassunto o trovare gli argomenti principali."
    return None, None, "Impossibile recuperare il contenuto della pagina."
