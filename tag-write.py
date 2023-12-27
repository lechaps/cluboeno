import json
import os
import re

json_file_path = 'tags-dictionnary.json'
with open(json_file_path, 'r') as json_file:
    tags_dict = json.load(json_file)

directories = ["./content/post/", "./content/club/"]

def recursive_tag_search(tag_entry, md_content_outside_frontmatter, parent_tags=None):
    if parent_tags is None:
        parent_tags = []
    positive_search_tags = []
    search_tags = tag_entry.get('search', [])

    if search_tags and any(tag in md_content_outside_frontmatter for tag in search_tags):
        positive_search_tags.append(tag_entry["tag"])
        positive_search_tags.extend(parent_tags)

    current_parent_tags = parent_tags + [tag_entry["tag"]]
    
    if 'children' in tag_entry:
        for child_entry in tag_entry['children']:
            positive_search_tags.extend(recursive_tag_search(child_entry, md_content_outside_frontmatter, parent_tags=current_parent_tags))

    return positive_search_tags

for directory in directories:
    file_count = 0
    tagfile_count = 0
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".md"):
            file_count+=1
            md_file_path = os.path.join(directory, filename)
            with open(md_file_path, 'r') as md_file:
                md_content = md_file.read()

            md_content_outside_frontmatter = re.split(r'\+\+\+', md_content, maxsplit=2)
            if len(md_content_outside_frontmatter) > 2:
                md_content_outside_frontmatter = md_content_outside_frontmatter[2]
            else:
                md_content_outside_frontmatter = md_content_outside_frontmatter[0]

            positive_search_tags = []
            for tag_entry in tags_dict['tags']:
                positive_search_tags.extend(recursive_tag_search(tag_entry, md_content_outside_frontmatter))
            positive_search_tags = sorted(set(positive_search_tags))

            existing_tags_match = re.search(r'tags\s*=\s*\[([^\]]*)\]', md_content)

            new_tags_line = 'tags = [{}]'.format(', '.join('"{}"'.format(tag) for tag in positive_search_tags))

            if existing_tags_match:
                md_content = re.sub(r'tags\s*=\s*\[([^\]]*)\]', new_tags_line, md_content)
            else:
                md_content_outside_frontmatter = re.split(r'\+\+\+', md_content, maxsplit=2)
                if len(md_content_outside_frontmatter) > 2:
                    md_content = f"+++{md_content_outside_frontmatter[0]}{md_content_outside_frontmatter[1]}{new_tags_line}\n+++{md_content_outside_frontmatter[2]}"
                else:
                    md_content = f"+++{md_content_outside_frontmatter[0]}{new_tags_line}+++{md_content_outside_frontmatter[1]}"


            with open(md_file_path, 'w') as md_file:
                md_file.write(md_content)

            if not positive_search_tags :
                print(f"Aucun tag existant trouvé dans {md_file_path}.")
            else : 
                tagfile_count+=1

    print(f"{directory} : {tagfile_count} fichiers sur {file_count} mis à jour avec succès.")
                
