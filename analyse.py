import json
import requests
from collections import Counter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint

console = Console()

# Header stylé
console.print(Panel.fit(
    "[bold magenta]🚀 GITHUB PORTFOLIO ANALYZER[/bold magenta]\n[dim]Analyse premium de votre profil et projets[/dim]",
    border_style="magenta"
))

username = console.input("[bold cyan]👉 Entrez le nom d'utilisateur GitHub : [/bold cyan]")

with Progress(
    SpinnerColumn(),
    TextColumn("[progress.description]{task.description}"),
    transient=True,
) as progress:
    
    # 1. Récupération du profil
    progress.add_task(description="Récupération du profil...", total=None)
    try:
        rep = requests.get(f"https://api.github.com/users/{username}")
        if rep.status_code != 200:
            console.print(f"[bold red]❌ Erreur : Impossible de trouver l'utilisateur '{username}' (Status: {rep.status_code})[/bold red]")
            exit()
        data = rep.json()

        # 2. Récupération des dépôts
        progress.add_task(description="Analyse des dépôts...", total=None)
        rep1 = requests.get(f"https://api.github.com/users/{username}/repos?per_page=100")
        if rep1.status_code != 200:
            console.print(f"[bold red]❌ Erreur lors de la récupération des dépôts (Status: {rep1.status_code})[/bold red]")
            exit()
        data1 = rep1.json()
    except Exception as e:
        console.print(f"[bold red]❌ Une erreur est survenue : {e}[/bold red]")
        exit()

# --- Traitement des données ---
langages = []
total_etoiles = 0
meilleur_projet = "Aucun"
max_etoi = -1

if isinstance(data1, list):
    for repo in data1:
        etoiles = repo.get("stargazers_count", 0)
        total_etoiles += etoiles
        
        # Détection du meilleur projet
        if etoiles >= max_etoi:
            max_etoi = etoiles
            meilleur_projet = repo.get("name")
            
        if repo.get("language"):
            langages.append(repo["language"])

compteur = Counter(langages)

# --- Calcul du Score ---
score = 0
score += min(data.get("public_repos", 0) * 2, 40)  # max 40 pts
score += min(total_etoiles * 3, 40)                 # max 40 pts
score += 20 if data.get("bio") else 0

# --- Affichage des résultats ---
console.print("\n")

# Panneau de profil
profil_grid = Table.grid(expand=True)
profil_grid.add_column(style="bold cyan", width=20)
profil_grid.add_column()

profil_grid.add_row("👤 Nom", data.get("name", "N/A"))
profil_grid.add_row("📝 Bio", data.get("bio", "Pas de bio"))
profil_grid.add_row("📁 Repos publics", str(data.get("public_repos", 0)))
profil_grid.add_row("👥 Followers", str(data.get("followers", 0)))
profil_grid.add_row("📅 Créé le", data.get("created_at")[:10] if data.get("created_at") else "N/A")

console.print(Panel(profil_grid, title=f"[bold blue]Analyse : {username}[/]", border_style="blue", expand=False))

# Panneau des stats et score
couleur_score = "green" if score > 70 else "yellow" if score > 40 else "red"

stats_info = (
    f"🌟 [bold]Total Étoiles :[/] {total_etoiles}\n"
    f"🏆 [bold]Top Projet :[/] [cyan]{meilleur_projet}[/] ({max_etoi} ⭐)\n\n"
    f"[bold]Score du Profil :[/] [{couleur_score}]{score}/100[/{couleur_score}]"
)

console.print(Panel(stats_info, title="[bold]Performances[/bold]", border_style=couleur_score, expand=False))

# Tableau des langages
if langages:
    lang_table = Table(title="🚀 Langages les plus utilisés", show_header=True, header_style="bold magenta", border_style="dim")
    lang_table.add_column("Langage", style="cyan")
    lang_table.add_column("Dépôts", justify="right", style="green")

    for langage, nombre in compteur.most_common(3):
        lang_table.add_row(langage, f"{nombre}")
    
    console.print(lang_table)

# Sauvegarde du rapport
rapport = {
    "username": username,
    "nom": data.get("name", "N/A"),
    "repos_publics": data.get("public_repos", 0),
    "followers": data.get("followers", 0),
    "langages": compteur.most_common(3),
    "score": score,
    "total_stars": total_etoiles,
    "top_project": meilleur_projet
}

with open(f"{username}_rapport.json", "w") as f:
    json.dump(rapport, f, indent=4)

console.print(f"\n[bold green]✅ Rapport sauvegardé :[/] [italic]{username}_rapport.json[/italic]")
