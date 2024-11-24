#init et importation de packages
import re
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.firefox.options import Options
import time
import argparse
import csv
import os
import json

# Charger le fichier config.json
def charger_config(fichier="config.json"):
    with open(fichier, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config

config = charger_config()

# Accéder aux variables de config
username = config.get("username")
password = config.get("password")
nom_source = config.get("nom_source")

date_first = config.get("date_first", {})
date_second = config.get("date_second", {})


target_count = config.get("target_count")
mots_whitelist = config.get("mots_whitelist", [])


jour_first = date_first.get("jour_first") 
mois_first = date_first.get("mois_first") 
annee_first = date_first.get("annee_first")

jour_second = date_second.get("jour_second") 
mois_second = date_second.get("mois_second") 
annee_second = date_second.get("annee_second")


# Initialisation du parser d'arguments
parser = argparse.ArgumentParser(description="arguments python")

# Définition de l'argument --annee
parser.add_argument('--annee', type=int, help="Année de départ et de fin", default=None)

# Parsing des arguments
args = parser.parse_args()

# Vérification si l'argument --annee a été passé
if args.annee is not None:
    annee_first = args.annee
    annee_second = args.annee
else:
    print("")


anneecsv = annee_first



annee_first = (annee_first - 1840)+1
annee_second = (annee_second - 1840)+1
if jour_second == 31:
    jour_second = 30

separateur = ' | '
keywords = separateur.join(mots_whitelist)
#init webcrawler
firefox_options = Options()
firefox_options.set_preference("accept_insecure_certs", True)
firefox_options.add_argument("--start-maximized")
driver = webdriver.Firefox(options=firefox_options)

#authentification proxy dauphine
driver.get("https://passeport.dauphine.fr/cas/login?service=http://bu.dauphine.psl.eu/index.html%3F%26target%3Dauth")

driver.find_element("id", "username").send_keys(username)
driver.find_element("id", "password").send_keys(password)
time.sleep(0.5)
driver.find_element("name", "submit").click()

#connection europresse avec proxy dauphine
driver.get("https://proxy.bu.dauphine.fr/login?url=https://nouveau.europresse.com/access/ip/default.aspx?un=PSLT_10")
time.sleep(0.5)
driver.get("https://nouveau-europresse-com.proxy.bu.dauphine.fr/Search/AdvancedMobile")
time.sleep(0.5)

#filtre de recherche pour l'huma
driver.find_element("id", "specific-sources-rd").click()
time.sleep(2)
driver.find_element("id", "sourcesFilter").send_keys(nom_source)
time.sleep(2)

driver.find_element("xpath", '//*[@id="sf_242"]').click()
time.sleep(0.3)
driver.find_element("xpath", '//*[@id="DateFilter_DateRange"]').click()
time.sleep(0.3)
driver.find_element("xpath", '/html/body/section/form/div/div[2]/div[1]/div[5]/div[3]/div/select/option[11]').click()

#filtre de recherche par date
time.sleep(0.3)
driver.find_element("xpath", f'/html/body/section/form/div/div[2]/div[1]/div[5]/div[3]/div/div[2]/span[1]/span/select[1]/option[{jour_first}]').click()
time.sleep(0.3)
driver.find_element("xpath", f'/html/body/section/form/div/div[2]/div[1]/div[5]/div[3]/div/div[2]/span[1]/span/select[2]/option[{mois_first}]').click()
time.sleep(0.3)
driver.find_element("xpath", f'/html/body/section/form/div/div[2]/div[1]/div[5]/div[3]/div/div[2]/span[1]/span/select[3]/option[{annee_first}]').click()
time.sleep(0.3)
driver.find_element("xpath", f'/html/body/section/form/div/div[2]/div[1]/div[5]/div[3]/div/div[2]/span[2]/span/select[3]/option[{annee_second}]').click()
time.sleep(0.3)
driver.find_element("xpath", f'/html/body/section/form/div/div[2]/div[1]/div[5]/div[3]/div/div[2]/span[2]/span/select[1]/option[{jour_second}]').click()
time.sleep(0.3)
driver.find_element("xpath", f'/html/body/section/form/div/div[2]/div[1]/div[5]/div[3]/div/div[2]/span[2]/span/select[2]/option[{mois_second}]').click()
time.sleep(0.3)
driver.find_element("xpath", '//*[@id="Keywords"]').send_keys(keywords)
time.sleep(0.3)
driver.find_element("xpath", '//*[@id="btnSearch"]').click()
time.sleep(4)

compteur_mots_global = {}

compteur_liens_analyses = 0

def collect_links(target_count, scroll_pause_time=2):
    # Liste pour stocker les liens
    if target_count > 1000:
        target_count = 1000
    links = []
    
    # Récupérer les liens tant qu'on n'a pas atteint `target_count`
    while len(links) < target_count:
        # Trouver tous les liens sur la page actuelle
        elements = driver.find_elements(By.CLASS_NAME, "docList-links")
        
        # Récupérer les href des éléments trouvés (uniquement ceux qui n'ont pas encore été ajoutés)
        for element in elements:
            href = element.get_attribute("href")
            if href and href not in links:
                links.append(href)
            
            # Arrêter si nous avons atteint ou dépassé le nombre cible de liens
            if len(links) >= target_count:
                break
        
        if len(links) < target_count:
            # Défiler jusqu'en bas de la page
            last_height = driver.execute_script("return document.body.scrollHeight")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(scroll_pause_time)  # Attendre quelques secondes pour que la page se charge

            
    
    return links[:target_count]

all_links = collect_links(target_count)


def compter_mots(lien, mots_whitelist, compteur_mots_global):
    lien = lien.replace("'", "")
    driver.execute_script(f"window.open('', '_blank');")
    time.sleep(0.5)  
    driver.switch_to.window(driver.window_handles[-1])
    driver.get(lien)

    try:
        texte = driver.find_element(By.CLASS_NAME, "docOcurrContainer").text
    except Exception as e:
        print(f"Erreur lors de la récupération du texte de {lien}: {e}")
        texte = ""

    texte2 = re.sub('[^A-Za-z0-9 \'èéàçù-]+', '', texte)
    texte3 = texte2.lower()
    mots = tuple(texte3.split())

    for mot in mots:
        if mot in mots_whitelist:
            if mot in compteur_mots_global:
                compteur_mots_global[mot] += 1
            else:
                compteur_mots_global[mot] = 1
    time.sleep(2)
    driver.close()
    driver.switch_to.window(driver.window_handles[0])

    return compteur_mots_global

for url in all_links:
    compteur_mots_global = compter_mots(url, mots_whitelist, compteur_mots_global)
    
    compteur_liens_analyses += 1

def export_dict_to_csv(dictionnaire,anneecsv):
    nom_fichier = f"result_{anneecsv}.csv"
    
    if os.path.exists(nom_fichier):
        suffix = 1
        while os.path.exists(f"result_{anneecsv}_{suffix}.csv"):
            suffix += 1
        nom_fichier = f"result_{anneecsv}_{suffix}.csv"
    
    with open(nom_fichier, mode='w', newline='') as file:
        writer = csv.writer(file)
        
        writer.writerow(dictionnaire.keys())
        
        writer.writerow(dictionnaire.values())

for mot_comptage in mots_whitelist:
            if mot_comptage not in compteur_mots_global:
                compteur_mots_global[mot_comptage] = 0


export_dict_to_csv(compteur_mots_global,anneecsv)

driver.quit()



