
# paramètres commun à tous les programmes
param_general = {
    "tags_to_extract" :['_', 'persName', 'placeName', 'date'], # '_' servira pour les tokens Outside/non-EN.
    "class_names" :['O', 'PER', 'LOC', 'DATE'],
    'OIB' : True,
    "datadir" : "data/ritter_complet",
    "datadoc" : "ritter_vol1" ,
}

param_xlm2encoded_xml_ner = {
    "outdir" : "data/A121078-2/xml_w_ner",
    "csvdocname" : "ritter_vol2" ,
    "xml_dir" : "data/A121078-2/xml/export_doc57_volume_2_teixml_202404121230",
    "model_spacy" : "fr_camembert_ritter",
}

# paramètres pour la création du jeu de données :
param_creation_dataset = {"by_element" : None,# peut être None, traitera chaque page en entier
                        "tokenizer" : "spacy", # les choix sont ["spacy", "split"] ou l'URL HF d'un modèle
                        "xml_dir" : "data/A121078-1/xml/export_doc50_volume_1_teixml_202404101446",# dossier où se trouvent les doc XML annotés
                        "train_test_split" : True
}

# paramètres spécifiques au NER regex avec PER, LOC, DATE et O
param_regex =  {
    'antidictionnaire': ['voir', "und", "et", "de", 'poss.', "fin", "ff.", "des", "den", "der", "dem", "ein", "voir:", 'zum', 'bibl.', 'catal.', "l'auteur", 'list', 'anno' ],
    'LOC': ["strasbourg", "strasbourg.", "strassburg", "strazburg", "sélestat", "bâle", "franckfort", "heidelberg", "argentorati"],
    "DATE" : r'(M?\.?[LXI]+\.*|1[456]\d\d\.?|Anno\W?)',
    "doc_table_alpha" : "regex/data/table_alpha.txt",
    "outdir_regex" :'regex/out'
}

# paramètre modèles HF (hors compatibilité spaCy)
param_hf = {'model': "Jean-Baptiste/camembert-ner-with-dates",
            'outdir' : "test",
            'outdoc' : "camembert-ner-with-dates_preds",
            'tokenized_with_model' : True,
            'ents_annotated': True,
            'eval': True}

param_IAgen = {
    "mode": "api", # ['manuel', "api"] avec "manuel" écriture des batches qui doivent être placées dans l'interface web ou "api" qui interroge l'API directement
    'inputdir': "data/demo/",
    'outdir': 'data/mistral_demo',
    "max_length": 3000, 
    "temperature": 0, # only if "api" mode
    'template' : """Extrait en un fichier JSON les entités nommées B-PER, I-PER, B-DATE, I-DATE, B-LOC, I-LOC selon l'exemple :
Exemple =  "HANNENBEIN, Georg . Voir: LIED (Neu Klaglied der Bauern) n° 340.
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
}

param_alignement = {
    "ents_doc_path" :None, #can be None : param_general['datadir']/param_general['datadoc'].csv will be used
    "ents_id_colname" : 'tag_ids',
    "tokens_colname" : "text",
    'originaltext_colname' : 'originaltext', #can be same as tokens_colname
    "outdir": "data/test_alignement/"
    } 