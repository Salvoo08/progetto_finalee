from bs4 import BeautifulSoup
import requests
from gensim.summarization import summarize, keywords
from difflib import SequenceMatcher

# Dizionario dei siti affidabili
siti_affidabili = {
    "ONU Italia": "https://unric.org/it/effetti-del-cambiamento-climatico/",
    "IPCC Italia": "https://ipccitalia.cmcc.it/",
    "NASA": "https://climate.nasa.gov/",
    "NOAA": "https://www.noaa.gov/climate",
    "FAO": "https://www.fao.org/climate-change/en/"
}

# Funzione per ottenere il contenuto della pagina
def get_page_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Errore durante la richiesta: {e}")
        return None

# Funzione per riassumere il contenuto della pagina
def summarize_content(content):
    try:
        summary = summarize(content, word_count=100)
        key_topics = keywords(content, words=10, lemmatize=True)
        return summary, key_topics
    except ValueError as e:
        print(f"Errore nel creare il riassunto: {e}")
        return None, None

# Funzione per confrontare le informazioni
def compare_keywords(page_keywords, reliable_keywords):
    match_ratio = SequenceMatcher(None, page_keywords, reliable_keywords).ratio()
    return match_ratio

# Richiedere l'URL all'utente
url = input("Inserisci l'URL della pagina web: ")

# Ottenere il contenuto della pagina
page_content = get_page_content(url)

if page_content:
    # Creare l'oggetto BeautifulSoup
    bs = BeautifulSoup(page_content, "lxml")
    
    # Estrarre il testo principale della pagina
    main_content = ' '.join([p.text for p in bs.find_all('p')])
    
    # Riassumere il contenuto
    summary, key_topics = summarize_content(main_content)
    
    if summary and key_topics:
        print("Riassunto della pagina:")
        print(summary)
        print("\nArgomenti principali:")
        print(key_topics)
        
        # Confrontare le parole chiave della pagina con quelle dei siti affidabili
        reliable = False
        for site_name, site_url in siti_affidabili.items():
            site_content = get_page_content(site_url)
            if site_content:
                site_bs = BeautifulSoup(site_content, "lxml")
                site_text = ' '.join([p.text for p in site_bs.find_all('p')])
                _, site_keywords = summarize_content(site_text)
                if site_keywords:
                    match_ratio = compare_keywords(key_topics, site_keywords)
                    if match_ratio >= 0.6:  # Consideriamo affidabile se almeno il 60% coincide
                        reliable = True
                        print(f"\nLe informazioni sono affidabili e coerenti con quelle di {site_name}.")
                        break
        
        if not reliable:
            print("\nLe informazioni fornite potrebbero non essere affidabili in base alla tua descrizione e ai siti affidabili.")
    else:
        print("Impossibile creare il riassunto o trovare gli argomenti principali.")
else:
    print("Impossibile recuperare il contenuto della pagina.")
