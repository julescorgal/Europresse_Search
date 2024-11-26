import subprocess
import json
PYDEVD_DISABLE_FILE_VALIDATION=1

def charger_config(fichier="config.json"):
    with open(fichier, "r", encoding="utf-8") as f:
        config = json.load(f)
    return config
config = charger_config()


specific_years_toggle = config.get("specific_years_toggle", False)
liste_annee = config.get("specific_years", [])



if specific_years_toggle == True:

# Boucle pour exécuter le script Python pour chaque année
    for i in range(len(liste_annee)):
        annee = liste_annee[i]  # Calcul de l'année actuelle
        command = ['python', 'main.py', '--annee', str(annee)]
        try:
            # Exécuter la commande
            print(f"Exécution de la commande pour l'année {annee}...")
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            print(f"Erreur lors de l'exécution du script pour l'année {annee}.")




# Demander à l'utilisateur l'année de départ et le nombre d'années

if specific_years_toggle == False:
    try:
        annee_debut = int(input("Entrez l'année de départ : "))
        nombre_annees = int(input("Entrez le nombre d'années à analyser : "))
    except ValueError:
        print("Erreur : Veuillez entrer des valeurs numériques.")
        exit()

# Boucle pour exécuter le script Python pour chaque année
    for i in range(nombre_annees):
        annee = annee_debut + i  # Calcul de l'année actuelle
        # Construire la commande avec l'argument --annee
        command = ['python', 'main.py', '--annee', str(annee)]
    
        try:
            # Exécuter la commande
            print(f"Exécution de la commande pour l'année {annee}...")
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            print(f"Erreur lors de l'exécution du script pour l'année {annee}.")


