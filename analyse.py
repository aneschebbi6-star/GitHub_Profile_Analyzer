import json
import requests
from collections import Counter
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt
from rich.progress import track
from rich import print as rprint

console = Console()

username = Prompt.ask("[bold cyan]Entrez le nom d'utilisateur GitHub[/bold cyan]")

rep = requests.get(f"https://api.github.com/users/{username}")

if rep.status_code == 200:
    data = rep.json()
    profile_info = (
        f"[bold]Nom :[/bold] {data.get('name', 'N/A')}\n"
        f"[bold]Repos publics :[/bold] {data.get('public_repos', 0)}\n"
        f"[bold]Followers :[/bold] {data.get('followers', 0)}\n"
        f"[bold]Following :[/bold] {data.get('following', 0)}\n"
        f"[bold]Compte créé le :[/bold] {data.get('created_at', '')[:10]}\n"
        f"[bold]Lien profil :[/bold] [blue underline]{data.get('html_url')}[/blue underline]"
    )
    console.print(Panel(profile_info, title=f"[bold green]Profil de {username}[/bold green]", border_style="green", expand=False))
else:
    console.print(f"[bold red]Erreur lors de la récupération du profil : {rep.status_code}[/bold red]")
    exit()

langages = []
rep1 = requests.get(f"https://api.github.com/users/{username}/repos?per_page=100")

if rep1.status_code == 200:
    data1 = rep1.json()

    if isinstance(data1, list):
        repo_table = Table(title=f"Dépôts de {username}", header_style="bold magenta", border_style="magenta")
        repo_table.add_column("Projet", style="cyan")
        repo_table.add_column("Langage principal", style="yellow")
        repo_table.add_column("Étoiles", style="green", justify="right")

        max_etoi = 0
        best_repo = "N/A"
        total_etoiles = 0

        # Utilisation d'une barre de progression pour l'analyse des dépôts
        for repo in track(data1, description="[cyan]Analyse des dépôts..."):
            name = repo.get("name", "N/A")
            lang = repo.get("language")
            stars = repo.get("stargazers_count", 0)
            
            repo_table.add_row(name, lang if lang else "Inconnu", str(stars))

            if lang:
                langages.append(lang)
                
            total_etoiles += stars
            if stars > max_etoi:
                max_etoi = stars
                best_repo = name

        console.print(repo_table)

        compteur = Counter(langages)

        lang_table = Table(title="🏆 Langages les plus utilisés", show_header=False, border_style="gold1", expand=False)
        lang_table.add_column("Langage", style="bold yellow")
        lang_table.add_column("Nombre", style="bold white")
        
        for langage, nombre in compteur.most_common(5):
            lang_table.add_row(f"⭐ {langage}", f"{nombre} repos")
            
        console.print(lang_table)

        # Calculer le score
        score = 0
        score += min(data.get("public_repos", 0) * 2, 40)  # max 40 pts
        score += min(total_etoiles * 3, 40)                 # max 40 pts
        score += 20 if data.get("bio") else 0
        
        score_info = (
            f"[bold cyan]Total Étoiles :[/bold cyan] {total_etoiles} ⭐\n"
            f"[bold cyan]Projet le plus populaire :[/bold cyan] {best_repo} ({max_etoi} ⭐)\n"
            f"\n[bold magenta]Score du Profil :[/bold magenta] [bold yellow]{score}/100[/bold yellow]"
        )
        
        console.print(Panel(score_info, title="[bold magenta]Bilan & Score[/bold magenta]", border_style="magenta", expand=False))

        rapport = {
            "username": username,
            "nom": data.get("name", "N/A"),
            "repos_publics": data.get("public_repos", 0),
            "followers": data.get("followers", 0),
            "langages": compteur.most_common(5),
            "score": score
        }

        with open(f"{username}_rapport.json", "w", encoding="utf-8") as f:
            json.dump(rapport, f, indent=4, ensure_ascii=False)

        console.print(f"\n[bold green]✅ Rapport sauvegardé avec succès :[/bold green] [italic]{username}_rapport.json[/italic]")

    else:
        console.print("[bold red]Format de données inattendu pour les dépôts.[/bold red]")

else:
    console.print(f"[bold red]Erreur lors de la récupération des dépôts : {rep1.status_code}[/bold red]")
