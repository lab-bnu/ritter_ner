
# paramètres commun à tous les programmes
param_general = {
    "tags_to_extract" :['_', 'persName', 'placeName', 'date'],
    "class_names" :['O', 'PER', 'LOC', 'DATE'],
    "datadoc" : "data/datasets/data_div.csv" # document de sortie : alignement des tokens avec la bonne étiquette
}

# paramètres pour la création du jeu de données :
creation_param = {"by_element" : "div",# peut être None 
                  "tokenizer" : "split",# les choix sont ["spacy", "split"]
                  "xml_dir" : "data/xml_ner"# dossier où se trouvent les doc XML
                  }


# paramètres spécifiques au NER regex
regex_param =  {
    'antidictionnaire': 
              ['voir', "und", "et", "de", 'poss.', "fin", "ff.", "des", "den", "der", "dem", "ein", "voir:", 'zum', 'bibl.', 'catal.', "l'auteur", 'list', 'anno' ]
             ,
    'LOC': ["strasbourg", "strasbourg.", "strassburg", "strazburg", "sélestat", "bâle", "franckfort", "heidelberg", "argentorati"]
    ,
    "DATE" : r'(M?\.?[LXI]+\.*|1[456]\d\d\.?|Anno\W?)'
    ,
    "doc_table_alpha" : "regex/data/table_alpha.txt",
    "outdir_regex" :'regex/out'
}