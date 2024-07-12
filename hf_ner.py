import ast
import os.path
from transformers import AutoTokenizer, pipeline
import csv
import typer
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix, classification_report
import matplotlib.pyplot as plt
from typing import Optional
import sys
import warnings
warnings.filterwarnings("ignore")

from params import param_hf_ner


class HFpred:

    class_names = param_hf_ner["class_names"]
    data = []
    
    classifier = pipeline("ner", model=param_hf_ner['model'], tokenizer=param_hf_ner['model'])
    task = "ner"
    label_all_tokens = True
    outdir = param_hf_ner['outdir']
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    outdoc = f"{outdir}/{param_hf_ner['outdoc']}"          
    tokenizer = AutoTokenizer.from_pretrained(param_hf_ner['model'])

    def set_data(self):
        
        with open(param_hf_ner['datadoc'], 'r', newline='', encoding='UTF-8') as f: 
            reader = csv.DictReader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for row in reader:
                self.data.append(row)
        self.set_labels()
        

    def set_labels(self):
        """
        Construit le dictionnaire label2id avec IOB
        """
        if param_hf_ner['OIB'] == True:
            prefixes = ['B-', 'I-']
            self.class_names = [label if label == 'O' else f"{pref}{label}" for label in self.class_names for pref in prefixes]
        self.label2id = {label : id-1 for id, label in enumerate(self.class_names)}
        self.id2label = {id:label for label, id in self.label2id.items()}
    

    def predict(self, example):
        return self.classifier(example)
    
    def add_tokens(self, sent):
        tokens = self.tokenizer.tokenize(sent['originaltext'])
        return tokens

    def normalize_preds(self, sent):
        tokenized_inputs = self.tokenizer(sent['originaltext'])
        word_ids = tokenized_inputs.word_ids()
        # print(word_ids)
        previous_word_idx = None
        label_ids = []
        batch = -1
        for word_idx in word_ids:
            if word_idx is None:
                continue
            elif word_idx != previous_word_idx:
                batch += 1
            label_ids.append(ast.literal_eval(sent['tag_ids'])[batch])
            
            previous_word_idx = word_idx
        return label_ids
    
    def get_data(self):
        return self.data
    
    def process(self, sent):
        preds = self.predict(sent['originaltext'])
        preds_tokens = [tok['word'] for tok in preds ]
        preds_ent = [tok['entity'] for tok in preds ]       
        preds_only = []
        for tok in sent['text']:
            # if token hasn't been predicted means Outside
            if tok not in preds_tokens:
                label_pred = 0
            else:
                ind = preds_tokens.index(tok)
                lab_pred = preds_ent[ind]
                #  if the label predicted is not within class_names
                if lab_pred not in self.class_names:
                    label_pred = 0
                else:
                    label_pred = self.label2id[lab_pred]       
            preds_only.append(label_pred)
        return preds_only   
            

    def add_preds(self):
        
        for sent in self.data: 
            if param_hf_ner['tokenized_with_model'] == False:   
                sent['text'] = self.add_tokens(sent)  
            sent['preds'] = self.process(sent)
            
            if param_hf_ner['eval'] == True:
                sent['tag_ids'] = self.normalize_preds(sent)
        return self.data
    

    def write_full(self):
        with open(f"{self.outdoc}.csv", "w", newline='', encoding='utf8') as f:
            writer = csv.DictWriter(f, fieldnames=list(self.data[0].keys()), delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for sent in self.data:
                writer.writerow(sent)

    def evaluate(self):
        labels = list(self.label2id.keys())
        if param_hf_ner['ents_annotated'] == False:
            sys.exit("L'évaluation n'est possible que si les données ont été annotées manuellement")
        else:
            preds_flat = [self.id2label[label] for sublist in self.data for label in sublist['preds']]
            truths_flat = [self.id2label[label] for sublist in self.data for label in sublist['tag_ids']]
            if len(truths_flat) != len(preds_flat):
                warnings.warn(f'Le nombre de prédictions {len(preds_flat)} ne correspond pas au nombre de tokens {len(truths_flat)}')
            else:
                cr = classification_report(y_true=truths_flat, y_pred=preds_flat, labels=labels, zero_division=0)
                print(cr)
                with open(f"{self.outdoc}_cr.txt", 'w', encoding='UTF-8') as g:
                    g.write(cr)
                self.plot_confusion_matrix(truths_flat, preds_flat, labels, True)
                self.plot_confusion_matrix(truths_flat, preds_flat, labels, False)

    
    def plot_confusion_matrix(self, y_true, y_preds, labels, norm:bool):
        if norm== True:
            cm = confusion_matrix(y_true, y_preds, normalize='true', labels=labels)
            title = 'normalized'
            val = ".2f"
        else:
            cm = confusion_matrix(y_true, y_preds, labels=labels)
            val = None
            title = ''
        fig, ax = plt.subplots(figsize=(6, 6))
        disp = ConfusionMatrixDisplay(confusion_matrix=cm,
                                    display_labels=labels)
        disp.plot(cmap="Purples", values_format=val, ax=ax, colorbar=False)
        plt.title(f"confusion matrix {title}")
        plt.savefig(f"{self.outdoc}_confmatrix{title}.png", format="png")
        # plt.show()
    
if __name__ == '__main__':
    # Produit les prédictions pour le modèle dispo sur HF donné et les enregistre avec les données d'entrées dans un nouveau document 
    # Params:
    # --eval produit l'évaluation de la prédiction à partir du document en sortie
    preds = HFpred()
    preds.set_data()
    preds.add_preds()
    preds.write_full()
    if param_hf_ner['eval'] == True:
        preds.evaluate()