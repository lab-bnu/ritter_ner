import typer
import csv
import re
import ast



def extract_names(doc, outdoc):
    """Ecrit les noms de personnes recensés dans le document de sortie de creation_dataset.py 
    Params: 
   doc: sortie en csv du programme creation_dataset.py contenant les données tokenisées et alignées avec leur étiquette correcte
    outdoc: document de sortie où seront listés les noms de personne"""
    with open(doc, "r", newline="", encoding="UTF-8") as f:
        names = []
        reader = csv.reader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for row in reader:
            tokens = ast.literal_eval(row[0])
            labels = ast.literal_eval(row[1])
            for t in tokens:
                if re.search('PER', labels[tokens.index(t)]):
                    names.append(t)
        with open(outdoc, "w", encoding="UTF-8") as g:
            for name in names:
               g.write(name+'\n')

if __name__ == '__main__':
    typer.run(extract_names)