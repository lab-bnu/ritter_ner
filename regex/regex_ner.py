import re
import csv
from pathlib import Path
import ast

from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix, classification_report
import matplotlib.pyplot as plt
import typer

from typing import List
import warnings
from typing import Optional
from params import label_names, id2label, label2id, ANTIDICO, PLACENAME


class NerRegex:
    ref = []
    sentences = []

    def get_ents(self, table_alpha:Path)->List[str]:
        with open(table_alpha, 'r', encoding='UTF-8') as f: 
            ent = []
            for line in f: 
                if re.search(r'([^\d]*)', line):
                    full_ent = re.search(r'([^\d]*)', line)
                    ent.append(full_ent.group(1))
            for name in ent:
                name = re.sub(r',\s$', '', name)
                name = re.sub(r'\(.*', '', name)
                name = re.sub(r'\s$', '', name)
                name = re.sub(r'[\w\W]+\)', '', name)
                name = re.sub(r'[\*\?,]', '', name)
                if name:
                    for n in name.split():
                        if n.lower() not in ANTIDICO and len(n)>2:
                            self.ref.append(n.lower())
        return self.ref

    def regex_extract(self, data:Path) -> List[dict]:
        with open(data, newline='', encoding='UTF-8') as g:
            reader = csv.reader(g, delimiter=',', quotechar='"')
           
            for row in reader:
                old_label = ''
                words = ast.literal_eval(row[0])
                labels = ast.literal_eval(row[1])
                phr = []
                for w in words:
                    label = 'O'
                    if w.lower() in self.ref and w.lower() not in ANTIDICO and w.lower() not in PLACENAME:
                            # content = re.search(rf"(.*){w}(.*)", line)
                            # print(f"{content.group(1)}<persName>{w}</persName>{content.group(2)}")
                        label = "PER"
                    elif w.lower() in PLACENAME:
                        # content = re.search(rf"(.*){w}(.*)", line)
                        # print(f"{content.group(1)}<placeName>{w}</placeName>{content.group(2)}")
                        label = "LOC"
                    # extraction des dates : chiffres romains | XIV-XVIe siècle | "Anno"
                    elif re.fullmatch(r'(M?\.?[LXI]+\.*|1[456]\d\d\.?|Anno\W?)', w, flags=re.IGNORECASE) :
                        label = 'DATE'
                    true_label = id2label[labels[words.index(w)]]                       
                    
                    if label != old_label and label != 'O':
                        label = f"B-{label}"
                        old_label = label
                    elif label != 'O':
                        label = f"I-{label}"             
                    phr.append({'word': w, 'true_label': true_label, 'pred' : label })
                self.sentences.append(phr)
        return self.sentences
        
    
    def write2CoNLL(self, outdir:Path):
        with open(f"{outdir}/extraction_regex.csv", "w", newline='',  encoding='UTF-8') as g:
            writer = csv.writer(g, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for sent in self.sentences:
               for word in sent:
                    writer.writerow([word['word'], word['true_label'], word['pred']])
                
    def evaluation(self, output_dir:Path):
        preds_flat = [word['pred'] for sublist in self.sentences for word in sublist]
        truths_flat = [word['true_label'] for sublist in self.sentences for word in sublist ]
        if len(preds_flat) != len(truths_flat):
            warnings.warn("Evaluation impossible car le nombre de prédiction ne correspond pas au nombre de tokens annotés")
        cr = classification_report(y_true=truths_flat, y_pred=preds_flat)
        with open(f"{output_dir}/classification-report.txt", 'w', encoding='UTF-8') as f:
            f.write(cr)
        self.plot_confusion_matrix(output_dir, truths_flat, preds_flat, label_names)

    def plot_confusion_matrix(self, output_dir, y_true, y_preds, labels, norm:bool=True):
        if norm== True:
            cm = confusion_matrix(y_true, y_preds, normalize='true')
            val = ".2f"
            normalized = "Norm"
        else:
            cm = confusion_matrix(y_true, y_preds)
            val = None
            normalized = ''
        fig, ax = plt.subplots(figsize=(6, 6))
        # labels_for_fig = [l[0:4]+'.' for l in labels]
        disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                                    display_labels=sorted(labels))
        try : 
            disp.plot(cmap="Purples", values_format=val, ax=ax, colorbar=False)
        except ValueError as err:
            print(err)
            print("Peut s'expliquer par le fait que la regex n'a pas prédit une seule fois l'une des 7 étiquettes")
        plt.title(f"{normalized} confusion matrix regex")
        plt.savefig(f"{output_dir}/regex_cm{normalized}.png", format="png")
        # plt.show()

def regex(doc_table_alpha:Path, data:Path, outdir:Path, writeCoNLL:Optional[bool]=True):
    regex = NerRegex()
    regex.get_ents(doc_table_alpha)
    regex.regex_extract(data)
    regex.evaluation(outdir)
    if writeCoNLL != False:
        regex.write2CoNLL(outdir)

if __name__ == '__main__': 
    typer.run(regex)
    

            

