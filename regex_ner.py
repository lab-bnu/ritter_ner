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
import os.path

from params import param_general, param_regex


class NerRegex:
    ref = []
    sentences = []
    class_names = param_general['class_names']
    table_alpha = param_regex['doc_table_alpha']
    datadoc = f"{param_general['datadir']}/{param_general['datadoc']}.csv"
    outdir = param_regex['outdir_regex']
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    antidictionnaire = param_regex['antidictionnaire']

    def set_labels(self):
        """
        Construit le dictionnaire label2id avec IOB
        """
        if param_general['OIB'] == True:
            prefixes = ['B-', 'I-']
            self.class_names = [label if label == 'O' else f"{pref}{label}" for label in self.class_names for pref in prefixes]
        self.label2id = {label : id-1 for id, label in enumerate(self.class_names)}
        self.id2label = {id:label for label, id in self.label2id.items()}
    

    def get_ents(self)->List[str]:
        with open(self.table_alpha, 'r', encoding='UTF-8') as f: 
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
                        if n.lower() not in self.antidictionnaire and len(n)>2:
                            self.ref.append(n.lower())
        return self.ref

    def regex_extract(self) -> List[dict]:
        with open(self.datadoc, newline='', encoding='UTF-8') as g:
            reader = csv.DictReader(g, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            next(reader)
            for row in reader:
                old_label = ''
                words = ast.literal_eval(row['text'])
                labels = ast.literal_eval(row['tags'])
                phr = []
                for w in words:
                    label = 'O'
                    if w.lower() in self.ref and w.lower() not in self.antidictionnaire and w.lower() not in param_regex['LOC']:
                        label = "PER"
                        # print(w)
                    elif w.lower() in param_regex['LOC']:
                        label = "LOC"
                        # print("loc")
                    # extraction des dates : chiffres romains | XV-XVIIe siècle | "Anno"
                    elif re.fullmatch(param_regex['DATE'], w, flags=re.IGNORECASE) :
                        label = 'DATE'     
                    if label != old_label :
                        old_label = label
                        if label != 'O':
                            label = f"B-{label}"
                        
                    elif label != 'O' and label == old_label:
                        label = f"I-{label}"  
                    true_label = labels[words.index(w)]               
                    phr.append({'word': w, 'true_label': true_label, 'pred' : label })
                self.sentences.append(phr)
        return self.sentences
        
    
    def write2CoNLL(self):
        with open(f"{self.outdir}/extraction_regex.tsv", "w", newline='',  encoding='UTF-8') as g:
            writer = csv.writer(g, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for sent in self.sentences:
               for word in sent:
                    writer.writerow([word['word'], word['true_label'], word['pred']])
                
    def evaluation(self, norma:Optional[bool]=True):
        labels = list(self.label2id.keys())
        preds_flat = [word['pred'] for sublist in self.sentences for word in sublist]
        truths_flat = [word['true_label'] for sublist in self.sentences for word in sublist ]
        if len(preds_flat) != len(truths_flat):
            warnings.warn("Evaluation impossible car le nombre de prédiction ne correspond pas au nombre de tokens annotés")
        cr = classification_report(y_true=truths_flat, y_pred=preds_flat, zero_division=0, labels=labels)
        with open(f"{self.outdir}/classification-report.txt", 'w', encoding='UTF-8') as f:
            f.write(cr)
        self.plot_confusion_matrix(self.outdir, truths_flat, preds_flat, labels, norma)

    def plot_confusion_matrix(self, output_dir, y_true, y_preds, labels, norm:bool=True):
        if norm== True:
            cm = confusion_matrix(y_true, y_preds, normalize='true', labels=labels)
            val = ".2f"
            normalized = "Norm"
        else:
            cm = confusion_matrix(y_true, y_preds, labels=labels)
            val = None
            normalized = ''
        fig, ax = plt.subplots(figsize=(6, 6))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                                    display_labels=labels)
        try : 
            disp.plot(cmap="Purples", values_format=val, ax=ax, colorbar=False)
        except ValueError as err:
            print(err)
            print("Au moins une des classes n'a pas été prédite une seule fois")
        plt.title(f"{normalized} confusion matrix regex")
        plt.savefig(f"{output_dir}/regex_cm{normalized}.png", format="png")
        # plt.show()

def regex(writeCoNLL:Optional[bool]=True, confmatrixnorm:Optional[bool]=True):
    regex = NerRegex()
    regex.set_labels()
    regex.get_ents()
    regex.regex_extract()
    if confmatrixnorm == True:
        regex.evaluation()
    else:
        regex.evaluation(False)
    if writeCoNLL != False:
        regex.write2CoNLL()

if __name__ == '__main__': 
    typer.run(regex)
    

            

