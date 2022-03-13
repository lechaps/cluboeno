# coding: utf8

import glob

target_path    = ["./content/post/", "./content/club/"]                 
tag_line_start = "tags = "
status         = ""
for path in target_path:                                                #pour tous les dossiers à inspecter
    nbfile = 0
    print(path)
    path_file_list = glob.glob(path + '*md' )                           #recherche les fichiers .md
    for path_file in path_file_list:                                    #pour tous les fichiers à inspecter
        with open(path_file, mode='r', encoding="utf8") as f :               #ouverture du fichier en mode lecture
            content = []
            for line in f:                                                          #pour toutes les lignes du fichier
                if line[:7]==tag_line_start:                                            #si la ligne est celle des tags
                    tags_str  = (line[8:line.index(']')])                                   #chaine contenant les tags
                    tags_list = tags_str.split(",")                                         #liste contenant les tags
                    nbtag     = len(tags_list)
                    tags_list = [i.strip() for i in tags_list]                              #nettoyage des espaces dans les éléments de la liste
                    tags_list = list(set(tags_list))                                        #suppression des tags en doublons
                    message="   > "+path_file
                    if nbtag!=len(tags_list):                                               #si le nombre de tags a changé
                        message+=" (+suppression doublon)"
                    print(message)
                    tags_list.sort()                                                        #liste par ordre alpahabétique
                    line      = tag_line_start+"["+", ".join(tags_list)+"] \n"                   #constitution de la line du fichier contenant les tags
                    nbfile+=1
                content.append(line)                                                #constitution du contenu du fichier
        with open(path_file, mode='w', encoding="utf8") as f:                #enregistrement dans le fichier
            f.writelines(content)
    status+= (str(nbfile)+" fichiers modifiés dans le repertoire "+path+"\n")
print("Bilan : \n"+status)
