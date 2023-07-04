import os
import json
import re

# Chargement des tags à partir du fichier tags.json
with open("tags.json", "r") as json_file:
    tags_data = json.load(json_file)
tags_list = [tag["name"] for tag in tags_data["tags"]]

# Création d'un dictionnaire pour faciliter la recherche des tags
existing_tags = [tag for tag in tags_list]

# Liste des fichiers sans tags
files_without_tags = []

directories = ["./content/post/", "./content/club/"]
tag_pattern = re.compile(r'tags\s*=\s*\[\]')

for directory in directories:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    tag_matches = tag_pattern.search(content)
                    if tag_matches:
                        # Recherche des mots correspondants aux tags existants dans le contenu du fichier
                        words = re.findall(r'\b\w+\b', content)
                        matching_tags = [tag for tag in existing_tags if tag in words]
                        matching_tags.sort()
                        tag_line = 'tags = [{}]'.format(', '.join('"{}"'.format(tag) for tag in matching_tags))
                        content = tag_pattern.sub(tag_line, content)
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content)
                        print("Tags mis à jour dans le fichier :", file_path)