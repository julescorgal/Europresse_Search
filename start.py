import subprocess

# Demander à l'utilisateur l'année de départ et le nombre d'années
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