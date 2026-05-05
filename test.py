import json
import requests
from collections import Counter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint




console = Console()




username = input("entrer le nom d'utilisateur github : ")

rep = requests.get(f"https://api.github.com/users/{username}")

if rep.status_code == 200:
    data = rep.json()
    print("Nom :", data.get("name", "N/A"))
    print("Repos publics :", data.get("public_repos", 0))
    print("Followers :", data.get("followers", 0))
    print("Following :", data.get("following", 0))
    print("Compte créé le :", data.get("created_at"))
    print("Lien profil :", data.get("html_url"))
else:
    print(f"Erreur lors de la récupération du profil : {rep.status_code}")

print("-" * 20)

# ✅ ICI la variable doit exister AVANT utilisation
langages = []

rep1 = requests.get(f"https://api.github.com/users/{username}/repos")

if rep1.status_code == 200:
    data1 = rep1.json()

    if isinstance(data1, list):
        for repo in data1:
            print("Projet :", repo["name"])

            if repo.get("language"):
                langages.append(repo["language"])

        compteur = Counter(langages)

        print("\n" + "=" * 30)
        print("🏆 Tes langages les plus utilisés :")

        for langage, nombre in compteur.most_common(3):
            print(f"  {langage} → {nombre} repos")

    else:
        print("Format de données inattendu pour les dépôts.")

else:
    print(f"Erreur lors de la récupération des dépôts : {rep1.status_code}")


# Calculer le total des étoiles
total_etoiles = sum(repo.get("stargazers_count", 0) for repo in data1)

# Calculer le score
score = 0
score += min(data.get("public_repos", 0) * 2, 40)  # max 40 pts
score += min(total_etoiles * 3, 40)                 # max 40 pts
score += 20 if data.get("bio") else 0

max_etoi = 0
for repo in data1:
    if repo.get("stargazers_count") > max_etoi:
        max_etoi = repo.get("stargazers_count")
        print("le projet qui a le plus d'etoiles est :", repo.get("name"))


print("\n" + "=" * 30)
print(f"⭐ Score du profil : {score}/100")


rapport = {
    "username": username,
    "nom": data.get("name", "N/A"),
    "repos_publics": data.get("public_repos", 0),
    "followers": data.get("followers", 0),
    "langages": compteur.most_common(3),
    "score": score
}

with open(f"{username}_rapport.json", "w") as f:
    json.dump(rapport, f, indent=4)

print(f"\n✅ Rapport sauvegardé : {username}_rapport.json")
