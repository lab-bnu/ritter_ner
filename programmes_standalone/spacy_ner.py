import spacy
import csv
import warnings
import typer
from typing import Optional
from pathlib import Path
import sys
warnings.filterwarnings("ignore")

def ner(document:Path, model:Optional[str]="fr_core_news_sm", outpath:Optional[Path]=None): 
    """Extrait du document donné en argument les EN avec le modèle de spaCy spécifié (par défaut le modèle français). Enregistrement possible si le chemin de sortie est spécifié"""
    if Path(document).suffix != '.txt':
        warnings.warn("La reconnaissance d'EN nécessite un document au format txt")
    with open(document, 'r', encoding='utf8') as f: 
        lines = [line for line in f]
    try :
        nlp = spacy.load(model)        
    except OSError: 
            print(f"Télécharger le modèle en ligne de commande : spacy download {model}")
            sys.exit()
    res = [(ent.text, ent.label_) for doc in nlp.pipe(lines, disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"]) for ent in doc.ents]
    print(f"EN du document {document} :")
    for ent, label in res: 
        print(ent, '\t', label)
    if outpath is not None:
        if Path(outpath).suffix == '.txt':
            with open(f"{outpath}", "w", encoding="UTF-8") as f:
                for ent, label in res:
                    f.write(f"{ent};{label}\n")
        elif Path(outpath).suffix in ['.csv', '.tsv']:
            with open(outpath, 'w', newline='', encoding='utf8') as g:
                writer = csv.writer(g, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for ent, label in res: 
                    writer.writerow([ent, label])
    
    
if __name__=='__main__':
    typer.run(ner)