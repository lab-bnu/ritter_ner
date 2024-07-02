from bs4 import BeautifulSoup
import glob
import re
import csv
import sys
from typing import Optional
from pathlib import Path
import typer
from params import param_general, param_creation_dataset
import os.path
import ast
import warnings

class Dataset: 
    
    files = []
    tokenizer = param_creation_dataset['tokenizer'].lower()
    tags_to_extract = param_general['tags_to_extract']
    class_names = param_general['class_names']
    xml_dir = param_creation_dataset['xml_dir']
    outdir = param_general['datadir']
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    outdoc = f"{outdir}/{param_general['datadoc']}"
    by_element = param_creation_dataset['by_element']
    out = []
    

    
    if tokenizer == "spacy":
        import spacy
        nlp = spacy.load("fr_core_news_sm")
    elif tokenizer != 'split':
        from transformers import AutoTokenizer, pipeline
        autotokenizer = AutoTokenizer.from_pretrained(tokenizer)

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
    

    def tokenize(self, text:str) -> list: 
        if self.tokenizer == "split": 
            tokenized_content = text.split(" ")
        elif self.tokenizer == "spacy":
            doc = self.nlp(text)
            tokenized_content = [w.text for w in doc]
        else:
            tokenized_content = self.autotokenizer.tokenize(text)
        return tokenized_content


    def get_files(self):
        self.files = [file for file in glob.glob(f"{self.xml_dir}/*.xml")]
        return self.files

    def extract_dataset_by_div(self):
        """
        Extraction des EN du XML encodé selon les div 
        """
        if self.by_element == None:
            div_tag = 'body'
        else:
            div_tag = self.by_element
        result = []
        for file in self.files:
            with open(file, "r", encoding="UTF-8") as f: 
                soup = BeautifulSoup(f, "xml")
                tagged = [] # list containing elements from included_tags list
                divs = soup.find_all(div_tag)
                # skipping first div as it contains the entire XML page
                if div_tag == 'div':
                    start = 1
                else:
                    start = 0
                for div in divs[start:]:
                    # div_content = []        # print(file)
                    content = dict()
                    # content['id'] = files.index(file)
                    originaltext = re.sub(r'(\t|)', '', div.text)
                    originaltext = re.sub(r'(\n|\s\s+)', ' ', originaltext)
                    content['originaltext'] = originaltext
                    content["text"] = []
                    content['tags'] = []
                    content['tag_ids'] = []
                    content['ents'] = []
                    content['prov'] = os.path.basename(file)
                    
                    for element in div.descendants :
                        clean_text = re.sub(r'(\t|)', '', element.text)
                        clean_text = re.sub(r'(\n|\s\s+)', ' ', clean_text)
                        if element.name in self.tags_to_extract:
                            
                            # fetch correct label 
                            label_number = self.tags_to_extract.index(element.name)
                            label = self.class_names[label_number]
                            # add the text in a list so that it doesn't get repeated
                            tagged.append(clean_text)
                            full_name = self.tokenize(clean_text)
                            if param_general['OIB'] == True:                                                              
                                content["text"].append(full_name[0])                    
                                content["tags"].append(f"B-{label}")
                                content["tag_ids"].append(self.label2id[f"B-{label}"])
                                full_name[0] = re.sub('▁', '', full_name[0])
                                try:
                                    limits = re.search(rf'{re.escape(full_name[0])}', rf'{originaltext}')
                                    content['ents'].append((limits.start(), limits.end(), f"B-{label}")) 
                                except AttributeError: 
                                    print(f"{full_name[0]} not found in {originaltext}")                               
                                if len(full_name) > 1:     
                                    for x in range(1, len(full_name)):
                                        if not re.fullmatch(r"(\s+|\t|\n|)", full_name[x]):
                                            content["text"].append(full_name[x])
                                            content["tags"].append(f"I-{label}")
                                            content["tag_ids"].append(self.label2id[f"I-{label}"])
                                            full_name[x] = re.sub('▁', '', full_name[x])
                                            try: 
                                                limits = re.search(rf'{re.escape(full_name[x])}', rf'{originaltext}')
                                                content['ents'].append((limits.start(), limits.end(), f"I-{label}"))
                                            except AttributeError: 
                                                print(f"{full_name[x]} not found in {originaltext}")
                            else:
                                for tok in full_name:
                                    content['text'].append(tok)
                                    content['tags'].append(label)
                                    content['tag_ids'].append(self.label2id[label])
                                    tok = re.sub('▁', '', tok)
                                    try:
                                        limits = re.search(rf'{re.escape(tok)}', rf'{originaltext}')
                                        content['ents'].append((limits.start(), limits.end(), f"{label}")) 
                                    except AttributeError: 
                                        print(f"{tok} not found in {originaltext}")
                        elif isinstance(element, str):
                            # check that it hasn't been dealt with already
                            if clean_text not in tagged:
                                label_number = 0
                                tokenized_content = self.tokenize(clean_text)
                                for ele in tokenized_content:
                                    # if not re.fullmatch(r'(\n|\t|\s+|)', ele):
                                        result.append((ele, self.tags_to_extract[label_number], self.class_names[label_number]))
                                        content["text"].append(ele)
                                        content["tags"].append("O")
                                        content['tag_ids'].append(0)
                        
                    
                    self.out.append(content)  
        return self.out


    def writing(self):
        fieldnames = list(self.out[0].keys())
        with open(f"{self.outdoc}.csv", "w", newline="", encoding="UTF-8") as g:
            writer = csv.DictWriter(g, delimiter=";", fieldnames=fieldnames, quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writeheader()
            for div in self.out:
                if len(div['text'])>=1:                    
                    writer.writerow(div)
        if param_creation_dataset['tokenizer'] == 'spacy':
            self.convert(self.out, self.outdoc)
        if param_creation_dataset['train_test_split'] == True:
            train, test = self.train_test_split()
            with open(f"{self.outdoc}_train.csv", "w", newline="", encoding="UTF-8") as gtrain,\
                open(f"{self.outdoc}_test.csv", "w", newline='', encoding="utf8") as gtest:
                writer1 = csv.DictWriter(gtrain, fieldnames=fieldnames, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer2 = csv.DictWriter(gtest, fieldnames=fieldnames, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                writer1.writeheader()
                writer2.writeheader()
                for sent in train:
                    if list(sent.keys())== fieldnames:
                        writer1.writerow(sent)
                for sent in test:
                    writer2.writerow(sent)
        
        if param_creation_dataset['train_test_split'] == True and self.tokenizer == 'spacy':
                self.convert(train, f"{self.outdoc}_train")
                self.convert(test, f"{self.outdoc}_test")
        
            
    
    def train_test_split(self):
        import random
        prop = int(len(self.out)*0.8)
        random.seed(1)
        random.shuffle(self.out)
        train =  self.out[:prop]
        test = self.out[prop:]
        return train, test
    
    def convert(self, data, outdocname):
        """This block written by Connor MacLean + https://spacy.io/usage/training"""
        from spacy.tokens import DocBin, Doc
        import spacy.lang
        self.nlp = spacy.blank("fr")
        db = DocBin()
        count = 0
        count_res = 0
        for sent in data:            
            doc = self.nlp.make_doc(sent['originaltext'])
            print(doc)
            
            res = []
            for  start, end, label in set(sent['ents']):
                print(start, end, label)
                span = doc.char_span(start, end, label=label)
                if span is None:
                    count += 1
                    msg = f"Skipping entity [{start}, {end}, {label}] in the following text '{doc.text[start:end]}' does not align with token boundaries:\n\n{repr(sent['originaltext'])}'"
                    warnings.warn(msg)
                else:
                    res.append(span)
            try:
                doc.ents = res
            except ValueError as err:
                print(err)
                count+=1
            db.add(doc)
            count_res += len(res)
        print(f"Nombre d'EN skipped :{count}\nNombre d'EN : {count_res}. \nRatio {(count*100)/(count_res+count):.2f}% des EN ou portion d'EN (souvent ponctuation ou espace entre deux mots d'une même).")
        db.to_disk(f"{outdocname}.spacy")


def creation_dataset():
    data = Dataset()
    data.get_files()
    data.set_labels()
    data.extract_dataset_by_div()
    data.writing()
    
    

if __name__ == "__main__":
    typer.run(creation_dataset)
    
    