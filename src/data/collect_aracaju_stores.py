from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
import sqlite3

def coletar_lojas_aracaju(termo_busca, bairro):
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.get("https://www.google.com.br/maps")
    time.sleep(3)

    # Faz a busca
    search_box = driver.find_element(By.ID, "searchboxinput")
    search_box.send_keys(f"{termo_busca} em {bairro}, Aracaju - SE")
    search_box.send_keys(Keys.ENTER)
    time.sleep(5)

    # Extração simples (Nome e Endereço)
    # Nota: Em um scraper real, você faria um loop nos resultados
    lojas_encontradas = []
    elementos = driver.find_elements(By.CLASS_NAME, "hfpxzc")[:5] # Pega os 5 primeiros
    
    for el in elementos:
        nome = el.get_attribute("aria-label")
        lojas_encontradas.append(nome)
    
    driver.quit()
    return lojas_encontradas

# Exemplo de uso:
# nomes = coletar_lojas_aracaju("Padaria", "13 de Julho")
# print(nomes)