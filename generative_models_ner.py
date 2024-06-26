# batches 


import re
import json
import pandas as pd
import ast
import json
import glob
import csv
from transformers import AutoModelForCausalLM, AutoTokenizer
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix, classification_report
from pathlib import Path
from typing import Optional
import sys
import warnings
from getpass import getpass
import os
from params import param_general, param_IAgen

template = """Extrait en un fichier JSON les entités nommées B-PER, I-PER, B-DATE, I-DATE, B-LOC, I-LOC selon l'exemple :
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

# label_names = ['O', 'B-PER', 'I-PER', 'B-DATE', 'I-DATE', 'B-LOC', 'I-LOC']
# label_ids = label_names
# label2id = {label: id for id, label in enumerate(label_ids)}
# id2label = {id: label for label, id in label2id.items()}
class Batches:
    doc = []
    batches = []
    template = param_IAgen['template']
    textdir = param_IAgen['txtdir']
    model = param_IAgen['model']
    class_names = param_general['class_names']
    outdir = param_IAgen['outdir']

    def set_labels(self):
        """
        Construit le dictionnaire label2id avec IOB
        """
        if param_general['OIB'] == True:
            prefixes = ['B-', 'I-']
            class_names = [label if label == 'O' else f"{pref}{label}" for label in self.class_names for pref in prefixes]
            self.label2id = {label : id-1 for id, label in enumerate(class_names)}
            self.id2label = {id:label for label, id in self.label2id.items()}
        else:
            self.label2id = {label : id-1 for id, label in enumerate(self.class_names)}
            self.id2label = {id:label for label, id in self.label2id.items()}

    def set_tokenizer(self):
        if self.model not in ['mistral', 'gpt']: 
            print("nein")
        if self.model == 'mistral':
            # imports spécifiques au modèle
            from mistralai.client import MistralClient
            from transformers import AutoTokenizer
            # Tokenizer (if not saved, uncomment first lines)
            # tokenizer = AutoTokenizer.from_pretrained("tokenizer")
            self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mixtral-8x7B-v0.1")
            # save tokenizer for customization
            # tokenizer.save_pretrained("tokenizer")
            mistral_api_key = os.environ.get("MISTRAL_API_KEY")
            if not mistral_api_key:
                # PASS API KEY AS USER INPUT
                mistral_api_key = getpass("MISTRAL API Key: ")
            self.client = MistralClient(api_key=mistral_api_key)
            
            


        if self.model == 'gpt' :
            # import spécifiques au modèle
            from openai import OpenAI
            import tiktoken
            self.tokenizer = tiktoken.encoding_for_model(self.model)
            openai_api_key = os.environ.get("OPENAI_API_KEY")
            if not openai_api_key:
                # PASS API KEY AS USER INPUT
                openai_api_key = getpass("OpenAI API Key: ")
            self.client = OpenAI(api_key=openai_api_key)

            
    def tokenize(self, text:str): 
        if self.model == "mistral":
            return self.tokenizer.tokenize(text)
        if self.model == 'gpt':
            return self.tokenizer.encode(text)
        
    def set_text(self): 
        files = [file for file in glob.glob(f"{self.textdir}/*.txt")]
        if len(files) == 0:
            warnings.warn('Pas de document texte dans le dossier en paramètre')
        for file in files:
            with open(file, 'r', encoding='utf8') as f: 
                page_content = [line for line in f]
                self.doc.append(''.join(page_content))
        return self.doc
    
    def create_batches(self): 
        tokenized_template = self.tokenizer.tokenize(self.template)    
        for page in self.doc: 
            sentence = []
            tokenized_content = self.tokenizer.tokenize(page)
            for token in tokenized_content:
                if (len(sentence) + len(tokenized_template) + 1) < self.tokenizer.model_max_length: 
                    sentence.append(token)
                else: 
                    sentence.inset(0, self.template)
                    self.batches.append(sentence)
                    sentence = []
        return self.batches
    

    def write_batches(self):     
        for batch in self.batches: 
            with open(f"{self.outdir}/batch_{self.batches.index(batch)}.txt", "w", encoding="UTF-8") as f:
                f.write(" ".join(batch))



# predictions 
                
    def predict(self):
        

if __name__=='__main__':
    batch = Batches()
    print(batch.set_text())
    print(batch.create_batches())
    batch.write_batches()


# def div_batch(j: list):
#     res = []
#     batch = []
#     for l in j:
#         # print(l)
#         # print(len(tokenizer.tokenize(l)))
#         if len(tokenizer.tokenize(' '.join(batch)+ l + template)) > max_tok:
#             res.append(batch)
#             batch = []
#             batch.append(l)
#         else: 
#             # print(l)
#             batch.append(l)
#     if batch not in res:
#         res.append(batch)
#     return res

            

#     def division_testset()->list:
#         testset = []
#         with open("regex/data/test.csv", newline='', encoding='UTF-8') as f: 
#             reader = csv.reader(f, delimiter=',', quotechar='"')
#             for row in reader :
#                 words = ast.literal_eval(row[0])
                
#                 testset.append(' '.join(words))
#         return testset




# ################ Extraction de la vérité de terrain 
# def true_data(path):
        
#     data = dict()

#     with open(path, newline='', encoding='UTF-8') as f:
#         read = csv.reader(f, delimiter=",", quotechar='"')
#         text = []
#         labels = []
#         next(read)
#         for row in read: 
#             # print(type(ast.literal_eval(row[0].split())))
#             t = re.sub(r"[\[\]',\.]", '', row[0])
#             # lol
#             t = t.replace('\\n', '')
#             t = t.replace('\n', '')
#             # print(t)
#             text.append(t.split(' '))
#             l = re.sub(r"[\[\]'\n]", '', row[1])
#             labels.append(l.strip().split(' '))
#             # print(l)
#         data['text'] = text
#         data['labels'] = labels
#         return data


# ##### Extraction des prédictions

# def extraction(path)->dict:
#     with open(path, "r", encoding='UTF-8') as f:
#         try:
#             preds = json.load(f)
#         except json.decoder.JSONDecodeError as err: 
#             print(err)
#             return None
#         return preds



# def post_process(data, preds):
#     """Alignement des entitées extraites avec leur prédiction avec la vraie étiquette. 
#     """
#     # ensemble des tokens qui ont fait l'objet d'une prédiction et de leur étiquette 'entity'
#     preds_tokens = [tok['word'] for ent in preds for tok in ent ]
#     preds_ent = [tok['entity'] for ent in preds for tok in ent ]
#     preds_only = []
#     for notice in data["text"]:
#         for tok in notice:
#             # if token hasn't been predicted means Outside
#             if tok not in preds_tokens:
#                 label_pred = 0
#             else:
#                 lab_pred = preds_ent[preds_tokens.index(tok)]
#                 if lab_pred not in label_ids:
#                     label_pred = 0
#                 else:
#                     label_pred = label2id[lab_pred]
#             # affichage des tokens avec true label puis label_pred
#             # true_label = data['labels'][data['text'].index(notice)][notice.index(tok)]
#             # print((tok, int(true_label), label_pred))
#             preds_only.append(label_pred)

#     return preds_only

# def plot_confusion_matrix(y_true, y_preds, labels, norm:bool):
#     if norm== True:
#       cm = confusion_matrix(y_true, y_preds, normalize='true')
#       val = ".2f"
#       normalized = "Norm"
#     else:
#       cm = confusion_matrix(y_true, y_preds)
#       val = None
#       normalized = ''
#     fig, ax = plt.subplots(figsize=(6, 6))
#     # labels_for_fig = [l[0:4]+'.' for l in labels]
#     disp = ConfusionMatrixDisplay(confusion_matrix=cm,
#                                   display_labels=labels)
#     disp.plot(cmap="Purples", values_format=val, ax=ax, colorbar=False)
#     plt.title(f"{normalized} confusion matrix Mistral")
#     plt.savefig(f"extraction_mistral/out/cm{normalized}.png", format="png")
#     # files.download(f"extraction_mistral/out_cm{normalized}.png")
#     plt.show()


# if __name__ == '__main__':
#     tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
#     max_tok = tokenizer.model_max_length
#     # testset = division_testset()
#     # write_batches(testset)
#     path = "extraction_mistral/out"
#     files = [file for file in glob.glob(f"{path}/*.json")]
#     preds_all = []
#     truths_all = []
#     for file in files:
#         f = extraction(file)
#         if f:
#             path2 = f"extraction_mistral/true/batch_{files.index(file)}_true.csv"
#             data = true_data(path2)
#             # print(data['labels'])
#             truths = [tok for sent in data["labels"] for tok in sent]
#             truths_all.append(truths)
#             preds = post_process(data, f)
#             # print(preds)
#             preds_all.append(preds)
#     preds_flat = [int(pred) for sent in preds_all for pred in sent]
    
#     truths_flat = [int(true) for sent in truths_all for true in sent]
#     print((len(preds_flat), len(truths_flat)))
#     cr = classification_report(y_true=truths_flat, y_pred=preds_flat, target_names=label_ids)
#     with open(f"{path}/cr.txt", 'w') as f:
#         f.write(cr)
#     plot_confusion_matrix(truths_flat, preds_flat, label_ids, True)
#     plot_confusion_matrix(truths_flat, preds_flat, label_ids, False)