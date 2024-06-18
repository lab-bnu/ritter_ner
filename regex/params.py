label_names = ['O', 'B-PER', 'I-PER', 'B-DATE', 'I-DATE', 'B-LOC', 'I-LOC']
label2id = {label: id for id, label in enumerate(label_names)}
id2label = {id: label for label, id in label2id.items()}


# paramètres spécifiques à l'extraction regex
ANTIDICO =  ['voir', "und", "et", "de", 'poss.', "fin", "ff.", "des", "den", "der", "dem", "ein", "voir:", 'zum', 'bibl.', 'catal.', "l'auteur", 'list', 'anno' ]
PLACENAME = ["strasbourg", "strasbourg.", "strassburg", "strazburg", "sélestat", "bâle", "franckfort", "heidelberg", "argentorati"]

