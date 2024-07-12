# paramètres pour la chaîne de xml/txt non encodé à xml
param_doc2encoded_xml_ner = {
    "inputdir" : "data/test", # doc xml ou txt
    "model_spacy" : "fr_camembert_ritter", # spacy download fr_camembert_ritter
    "outdir" : "data/demo_encoded",
    "csvdocname" : "demo" ,
    "tags": {"PER": "persName", "LOC":'placeName', 'DATE': 'date'} # clé étiquette donnée, valeur élément xml correspondant, 
    # NB : le programme prend en charge seul le système OIB si le modèle prédit les classes B-PER, I-PER au lieu de PER
}

# Programmes pour évaluation depuis "vérité de terrain"
# paramètres pour la création du jeu de données XML déjà annoté :
param_creation_dataset = {
    "xml_dir" : "data/test", # dossier où se trouvent les doc XML annotés
    "tags_to_extract" : ['_', 'persName', 'placeName', 'date'], # '_' servira pour les tokens Outside/non-EN.
    "class_names" :['O', 'PER', 'LOC', 'DATE'],
    'OIB' : True,
    "datadir" : "data/ritter_complet", #document créé par creation_dataset depuis extraction d'un document xml annoté
    "datadoc" : "test1" ,
    "by_element" : 'div',# peut être None, traitera chaque page en entier
    "tokenizer" : "spacy", # les choix sont ["spacy", "split"] ou l'URL HF d'un modèle
    "train_test_split" : True,
}

# paramètres spécifiques au programme d'extraction des EN avec regex
param_regex =  {
    'datadoc' : 'data/ritter_complet/test1_test.csv', # doit etre un doc csv contenant vérité de terrain
    "class_names" :['O', 'PER', 'LOC', 'DATE'],
    'OIB' : True,
    "doc_table_alpha" : "regex/data/table_alpha.txt",
    'antidictionnaire': ['voir', "und", "et", "de", 'poss.', "fin", "ff.", "des", "den", "der", "dem", "ein", "voir:", 'zum', 'bibl.', 'catal.', "l'auteur", 'list', 'anno' ],
    'LOC': ["strasbourg", "strasbourg.", "strassburg", "strazburg", "sélestat", "bâle", "franckfort", "heidelberg", "argentorati"],
    "DATE" : r'(M?\.?[LXI]+\.*|1[456]\d\d\.?|Anno\W?)',
    "outdir_regex" :'regex/out',
    'confusion_matrix_normalisee': True,
    'writeCoNLL': True,

}

# paramètre modèles HF (hors compatibilité spaCy)
param_hf_ner = {
    'datadoc' : 'data/ritter_complet/test1_test.csv', # doit etre un doc csv contenant vérité de terrain
    "class_names" :['O', 'PER', 'LOC', 'DATE'],
    'OIB' : True,
    'model': "Jean-Baptiste/camembert-ner-with-dates",
    'outdir' : "test",
    'outdoc' : "camembert-ner-with-dates_preds10",
    'tokenized_with_model' : True,
    'ents_annotated': True,
    'eval': True}


# paramètres Mistral
param_IAgen = {
    "mode": "api", # ['manuel', "api"] avec "manuel" écriture des batches qui doivent être placées dans l'interface web ou "api" qui interroge l'API directement
        "class_names" :['O', 'PER', 'LOC', 'DATE'],
    'inputdir': "data/demo/",
    'outdir': 'data/mistral_demo',
    "max_length": 3000, 
    "temperature": 0, # only if "api" mode
}
param_IAgen['template'] = f"""Extrait en un fichier JSON les entités nommées {param_IAgen['class_names']}:
Exemples =  "HANNENBEIN, Georg . Voir: LIED (Neu Klaglied der Bauern) n° 340.
PETRUS DE CRESCENTIS
( WUERFELBUCH ]
 Strasbourg , ( Christian Egenolff ), 1529 
 Marque typ. de Chris. Egenolff. Anno M. D. LXXXII 
 Stadtbibl. Strassburg 1192". 
Réponse = 
[
[{'entity': 'B-PER',
   'word': 'HANNENBEIN',
},
  {'entity': 'I-PER',
   'word': ',',
},
  {'entity': 'I-PER',
   'word': 'Georg',
},
],[
{'entity': 'B-PER',
   'word': 'PETRUS',
},
{'entity': 'I-PER',
'word': 'DE',
},
{'entity': 'I-PER',
'word': 'CRESCENTIS',
},
],[
{
'entity':'B-LOC', 
'word': 'Strasbourg',
},
],[
{
'entity': 'B-PER',
'word': 'Christian'
},
{
'entity':'I-PER',
'word': 'Egenolff'
},
],[
{'entity': 'B-DATE',
'word': '1529'},
],[
{'entity':'B-PER',
'word': 'Chris.'},
{'entity': 'I-PER',
'word': 'Egenolff'},
],[
{'entity':'B-DATE',
'word': 'M.'},
{'entity': 'I-DATE', 
'word': 'D.'},
{'entity':'I-DATE',
'word': 'LXXXII'},
],[
{'entity': 'B-LOC',
'word': 'Strassburg'}
]
]
Maintenant, extrait en JSON les entités nommées des phrases suivantes :"""


