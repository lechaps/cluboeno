import os
import json

def extract_tags_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        start_index = content.find('tags = [') + len('tags = [')
        end_index = content.find(']', start_index)
        tags_str = content[start_index:end_index]
        tags = [tag.strip().strip('"') for tag in tags_str.split(',')]
        return tags

def extract_tags_from_directory(directory):
    tags_dict = {}
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.md'):
                file_path = os.path.join(root, file)
                tags = extract_tags_from_file(file_path)
                for tag in tags:
                    if tag in tags_dict:
                        tags_dict[tag] += 1
                    else:
                        tags_dict[tag] = 1
    return tags_dict

post_directory = "./content/post/"
club_directory = "./content/club/"
output_file = "tags.json"

post_tags = extract_tags_from_directory(post_directory)
club_tags = extract_tags_from_directory(club_directory)

all_tags = {}
for tag, count in post_tags.items():
    all_tags[tag] = count
for tag, count in club_tags.items():
    if tag in all_tags:
        all_tags[tag] += count
    else:
        all_tags[tag] = count

sorted_tags = {tag: count for tag, count in sorted(all_tags.items())}

tags_json = json.dumps(sorted_tags, indent=4, ensure_ascii=False)

with open(output_file, 'w', encoding='utf-8') as file:
    file.write(tags_json)

print("Tags have been extracted and saved to", output_file)
