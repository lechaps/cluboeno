# coding: utf8

import glob

path_to_target = ["./content/post/", "./content/club/"]

for path in path_to_target:                                             #pour tous les dossiers à inspectés
    print(path)
    path_to_file_list = glob.glob(path + '*md' )                            #recherche les fichiers .md
    for path_to_file in path_to_file_list:                                  #pour tous les fichiers à inspecter
        print('     > '+path_to_file)
        with open(path_to_file, mode='r', encoding="utf8") as f :               #ouverture du fichier en mode lecture
            content = []
            for line in f:                                                          #pour toutes les lignes du fichier
                if line[:7]=="tags = ":                                             #si la ligne est celle des tags
                    tags=(line[8:line.index(']')])                                      #chaine contenant les tags
                    tabs=tags.split(",")                                                #liste contenant les tags
                    nb=len(tabs)
                    tabs=[i.strip() for i in tabs]                                      #nettoyage des espaces dans les éléments de la liste
                    tabs=list(set(tabs))                                                #suppression des doublons
                    if nb!=len(tabs):                                                   #si le nombre de tags a changé
                        print("     -> supression doublon")
                    tabs.sort()                                                         #liste par ordre alpahabétique
                    line="tags = ["+", ".join(tabs)+"] \n"                              #constitution de la chaine contenant les tags
                content.append(line)                                                #constitution du contenu du fichier
        with open(path_to_file, mode='w', encoding="utf8") as f:                #enregistrement dans le fichier
            f.writelines(content)
    

