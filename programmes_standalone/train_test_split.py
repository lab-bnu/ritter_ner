import random
import csv
import typer

def train_test_split(doc, outdir):
    """Créé les csv contenant les jeux d'entrainement et de test
    Params:
    doc: sortie en csv du programme creation_dataset.py contenant les données tokenisées et alignées avec leur étiquette correcte
    outdir: dossier où seront écrits les jeux d'entrainement et de test en format csv"""
    with open(doc, "r", newline="", encoding="UTF-8") as f:
        reader = csv.reader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        data = [row for row in reader]
        prop = int(len(data)*0.8)
        random.seed(1)
        random.shuffle(data)
        train =  data[:prop]
        test = data[prop:]
        with open(f"{outdir}/{''.join(doc.split('.')[:-1])}_train.csv", "w", newline="", encoding="UTF-8") as gtrain,\
            open(f"{outdir}/{''.join(doc.split('.')[:-1])}_test.csv", "w", newline='', encoding="utf8") as gtest:

            writer = csv.writer(gtrain, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer2 = csv.writer(gtest, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerows(train)
            writer2.writerows(test)

if __name__ == '__main__':
    typer.run(train_test_split)