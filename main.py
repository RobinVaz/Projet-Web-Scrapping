import requests
from bs4 import BeautifulSoup
import re
import pdfkit
import os
import urllib.parse

url = "https://fr.wikipedia.org/wiki/Retour_vers_le_futur"

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Partie 1 : Extraction des acteurs et création du fichier HTML


h2_tags = soup.find_all('h2')

distribution_section = None
for h2 in h2_tags:
    if "Distribution" in h2.get_text():  
        distribution_section = h2
        break

# Récupération de la liste des acteurs

if distribution_section:
    ul_tag = distribution_section.find_next('ul')
    
    if ul_tag:
        acteurs = []
        for li in ul_tag.find_all('li'):
            texte = li.get_text(strip=True)
            match = re.match(r'([^:]+)\(VF\s*[:|;]?\s*([^\)]+)\)\s*[:\-]?\s*(.*)', texte)
            if match:
                acteur = match.group(1).strip() 
                doublage_vf = match.group(2).strip()  
                role = match.group(3).strip()  
                acteurs.append(f"{acteur} (VF : {doublage_vf}) : {role}")
        
        # Structure du fichier Html

        html_content = "<html><head><title>Liste des Acteurs - Retour vers le futur</title></head><body>"
        html_content += "<h1>Acteurs du film Retour vers le futur</h1>"
        html_content += "<ul>"


        for acteur in acteurs:
            html_content += f"<li>{acteur}</li>"

        html_content += "</ul></body></html>"

        # Sauvegarde du fichier HTML
        
        with open("Acteur Retour vers le futur.html", "w", encoding="utf-8") as f:
            f.write(html_content)

        print("Le fichier HTML a été créé avec succès.")
    else:
        print("Aucune liste d'acteurs trouvée.")
else:
    print("La section 'Distribution' n'a pas été trouvée.")

# Partie 2 : Extraction des images de la galerie et sauvegarde


img_tags = soup.find_all('img')

output_dir = "Images Retour vers le futur"
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Téléchargement des images
for index, img in enumerate(img_tags):
    img_url = img.get('src')
    
    if img_url and img_url.startswith('/'):
        img_url = urllib.parse.urljoin('https://fr.wikipedia.org', img_url)
    
    try:
        img_data = requests.get(img_url).content
        
        img_name = f"image_{index}.jpg"  
        img_name = re.sub(r'[^\w\s.-]', '', img_name)  
        
        # Enregistrement de l'image
        with open(os.path.join(output_dir, img_name), 'wb') as f:
            f.write(img_data)
        
        print(f"Image sauvegardée : {os.path.join(output_dir, img_name)}")
    
    except Exception as e:
        print(f"Erreur lors de l'enregistrement de l'image {img_url}: {e}")

# Partie 3 : Extraction du sommaire et conversion en PDF

sommaire_section = soup.find('div', {'id': 'vector-toc-pinned-container'})

command = [
    'wkhtmltopdf',
    '--encoding', 'UTF-8',
    'sommaire_temp.html',
    'Sommaire_PDF/sommaire_retour_vers_le_futur.pdf'
]


# Vérification du sommaire :

if sommaire_section:

    sections = sommaire_section.find_all('a')

    sommaire_text = "Sommaire - Retour vers le futur\n\n"
    

    for section in sections:
        section_text = section.get_text()
        sommaire_text += f"- {section_text}\n"

    sommaire_html = f"""
    <html>
    <head>
        <meta charset="UTF-8"> <!-- Définir l'encodage UTF-8 -->
        <title>Sommaire - Retour vers le futur</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
                color: #333;
            }}
            h1 {{
                text-align: center;
                font-size: 28px;
                color: #3498db;
                margin-bottom: 20px;
            }}
            ul {{
                list-style-type: none;
                padding-left: 20px;
            }}
            li {{
                font-size: 16px;
                margin: 5px 0;
            }}
            li a {{
                text-decoration: none;
                color: #333;
            }}
            li a:hover {{
                color: #3498db;
            }}
            .section-title {{
                font-size: 18px;
                font-weight: bold;
                margin-top: 15px;
            }}
            .sub-section {{
                margin-left: 20px;
                font-size: 16px;
            }}
        </style>
    </head>
    <body>
        <h1>Sommaire - Retour vers le futur</h1>
        <ul>
    """

    for section in sections:
        section_text = section.get_text()
        sommaire_html += f'<li><a href="#">{section_text}</a></li>\n'

    sommaire_html += """
        </ul>
    </body>
    </html>
    """

    # Création du PDF
    pdf_folder = "Sommaire_PDF"
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)

    with open("sommaire_temp.html", "w", encoding="utf-8") as f:
        f.write(sommaire_html)
    print("Le fichier HTML temporaire a été créé avec succès.")

    pdf_output_path = os.path.join(pdf_folder, "sommaire_retour_vers_le_futur.pdf")
    try:
        pdfkit.from_file("sommaire_temp.html", pdf_output_path)
        print(f"Le PDF du sommaire a été créé avec succès : {pdf_output_path}")

        os.remove("sommaire_temp.html")
        print("Le fichier HTML temporaire a été supprimé.")
    except Exception as e:
        print(f"Erreur lors de la conversion du sommaire en PDF : {e}")
else:
    print("Aucun sommaire trouvé sur la page.")

# Partie 4 et 5 et 6: Extraire les 10 villes d'allemagnes

url = "https://www.worldometers.info/world-population/germany-population/"

response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

table = soup.find('table', {'class': 'table table-hover table-condensed table-list'})

if table:
    # Extraire les lignes du tableau

    rows = table.find_all('tr')
    cities_population = []

    # Parcourir chaque ligne et extraire le nom de la ville et la population
    for row in rows[1:11]:  
        columns = row.find_all('td')

        if len(columns) >= 2:  
            city = columns[1].get_text(strip=True)  
            population = columns[2].get_text(strip=True) 
            cities_population.append((city, population))

    # Créer du dossier pour le PDF
    pdf_output_dir = "rendu PDF"
    if not os.path.exists(pdf_output_dir):
        os.makedirs(pdf_output_dir)

    html_output_dir = "rendu HTML"
    if not os.path.exists(html_output_dir):
        os.makedirs(html_output_dir)

    # Structure du fichier Html
    html_content = """
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Classement des 10 Premières Villes d'Allemagne par Population</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f4f4f4;
                color: #333;
            }
            h1 {
                text-align: center;
                font-size: 28px;
                color: #3498db;
                margin-bottom: 30px;
            }
            ol {
                list-style-type: decimal;
                padding-left: 40px;
            }
            li {
                font-size: 18px;
                margin: 10px 0;
                padding: 10px;
                background-color: #e3f2fd;
                border-radius: 5px;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
            }
            li span {
                font-weight: bold;
                color: #2c3e50;
            }
            .rank {
                color: #3498db;
                font-weight: bold;
                margin-right: 10px;
            }
        </style>
    </head>
    <body>
        <h1>Classement des 10 Premières Villes d'Allemagne par Population</h1>
        <ol>
    """

    for index, (city, population) in enumerate(cities_population, start=1):
        html_content += f"""
        <li>
            <span class="rank">{index}.</span>
            <span class="city">{city}</span> : <span class="population">{population}</span>
        </li>
        """

    html_content += """
        </ol>
    </body>
    </html>
    """

    # Sauvegarder du contenu dans un fichier
    html_file_path = os.path.join(html_output_dir, "classement_villes_allemagne.html")
    with open(html_file_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Le fichier HTML a été créé avec succès : {html_file_path}")

    # Convertir le fichier en PDF
    pdf_output_path = os.path.join(pdf_output_dir, "classement_villes_allemagne.pdf")
    try:
        pdfkit.from_file(html_file_path, pdf_output_path)
        print(f"Le PDF a été créé avec succès : {pdf_output_path}")
    except Exception as e:
        print(f"Erreur lors de la conversion en PDF : {e}")

else:
    print("Le tableau des villes n'a pas été trouvé.")