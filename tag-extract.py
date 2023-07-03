import os
import json
import re

tags = {}

files_without_tags = []  # Liste des fichiers sans tags

# Liste des répertoires à parcourir
directories = ["./content/post/", "./content/club/"]

# Expression régulière pour extraire les tags
tag_pattern = re.compile(r'tags\s*=\s*\[([^\]]+)\]')

# Parcours des répertoires
for directory in directories:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                # Ouvrir le fichier et extraire les tags
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Rechercher les tags dans le contenu du fichier
                    tag_matches = tag_pattern.search(content)
                    if tag_matches:
                        tags_list = re.findall(r'"([^"]+)"', tag_matches.group(1))
                        tags_list.sort()  # Tri des tags par ordre alphabétique
                        tag_line = 'tags = [{}]'.format(', '.join('"{}"'.format(tag) for tag in tags_list))  # Création de la ligne des tags triés
                        content = tag_pattern.sub(tag_line, content)  # Remplacement de la ligne des tags dans le contenu du fichier
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)  # Écriture du contenu modifié dans le fichier
                            print("Tags triés et remplacés dans le fichier :", file_path)
                        for tag in tags_list:
                            if tag:
                                tags[tag] = tags.get(tag, 0) + 1
                    else:
                        files_without_tags.append(file_path)  # Ajout du chemin du fichier sans tags dans la liste

# Affichage des fichiers sans tags à la fin
if files_without_tags:
    print("Fichiers sans tag :")
    for file_path in files_without_tags:
        print(file_path)

# Trier les tags par ordre alphabétique
sorted_tags = sorted(tags.items(), key=lambda x: x[0])

# Création de la structure JSON
json_data = {
    "tags": [{"name": name, "count": count} for name, count in sorted_tags if name]
}

# Écriture du fichier JSON
with open("tags.json", "w", encoding="utf-8") as json_file:
    json.dump(json_data, json_file, indent=4, ensure_ascii=False)
