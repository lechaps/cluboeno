import os
import json
import re

tags = {}

files_without_tags = []

directories = ["./content/post/", "./content/club/"]

tag_pattern = re.compile(r'tags\s*=\s*\[([^\]]+)\]')

for directory in directories:
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith(".md"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", encoding="utf-8") as f:
                    content = f.read()
                    tag_matches = tag_pattern.search(content)
                    if tag_matches:
                        tags_list = re.findall(r'"([^"]+)"', tag_matches.group(1))
                        tags_list.sort()  
                        tag_line = 'tags = [{}]'.format(', '.join('"{}"'.format(tag) for tag in tags_list)) 
                        content = tag_pattern.sub(tag_line, content) 
                        with open(file_path, "w", encoding="utf-8") as f:
                            f.write(content) 
                        for tag in tags_list:
                            if tag:
                                tags[tag] = tags.get(tag, 0) + 1
                    else:
                        files_without_tags.append(file_path)

if files_without_tags:
    print("Fichiers sans tag :")
    for file_path in files_without_tags:
        print(file_path)

sorted_tags = sorted(tags.items(), key=lambda x: x[0])

json_data = {
    "tags": [{"name": name, "count": count} for name, count in sorted_tags if name]
}

with open("tags.json", "w", encoding="utf-8") as json_file:
    json.dump(json_data, json_file, indent=4, ensure_ascii=False)
