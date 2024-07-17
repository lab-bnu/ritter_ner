# Extraction HF version standalone
from transformers import AutoTokenizer, pipeline
import warnings
import typer
from typing import Optional
from pathlib import Path
import sys
import csv
warnings.filterwarnings("ignore")

def predict(document:Path, model:Optional[str]="Jean-Baptiste/camembert-ner-with-dates", outpath:Optional[Path]=None):
    """Extrait du document donné en argument les EN avec le modèle Transformers disponible via la plateforme HF. Si un chemin est donné à l'argument --outpath le résultat sera enregistré (format accepté txt/csv/tsv)"""
    if Path(document).suffix != '.txt':
        warnings.warn("La reconnaissance d'EN nécessite un document au format txt")
    with open(document, 'r', encoding='utf8') as f: 
        lines = [line for line in f]
    try:
        classifier = pipeline("ner", model=model, tokenizer=model)
    except OSError:
        print("Modèle non disponible sur HF : https://huggingface.co/")
        sys.exit()
    preds = classifier(lines)
    res = []
    for sent in preds:
        for tok in sent:
            print(tok['word'], '\t', tok['entity'])
            res.append((tok['word'],tok['entity']))
    if outpath is not None:
        if Path(outpath).suffix == '.txt':
            with open(f"{outpath}", "w", encoding="UTF-8") as f:
                for ent, label in res:
                    f.write(f"{ent}\t{label}")
        elif Path(outpath).suffix in ['.csv', '.tsv']:
            with open(outpath, 'w', newline='', encoding='utf8') as g:
                writer = csv.writer(g, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for ent, label in res :
                    writer.writerow([ent, label])

if __name__ == '__main__':
    typer.run(predict)