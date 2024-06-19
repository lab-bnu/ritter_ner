from bs4 import BeautifulSoup
import glob
import re
import csv
import sys
from typing import Optional
from pathlib import Path
import typer
from params import param_general, creation_param


class Doc: 
    
    files = []
    tokenizer = creation_param['tokenizer']
    tags_to_extract = param_general['tags_to_extract']
    class_names = param_general['class_names']
    xml_dir = creation_param['xml_dir']
    outdoc = param_general['datadoc']
    by_element = creation_param['by_element']
    out = []
    
    if tokenizer == "spacy":
        import spacy
        nlp = spacy.load("fr_core_news_sm")

    def set_label2id(self):
        """
        Construit le dictionnaire label2id avec IOB
        """
        prefixes = ['B-', 'I-']
        class_names = [label if label == 'O' else f"{pref}{label}" for label in self.class_names for pref in prefixes]
        self.label2id = {label : id-1 for id, label in enumerate(class_names)}
    
    def set_id2label(self):
        self.id2label = {id:label for label, id in self.label2id.items()}
        return self.id2label, self.label2id
    

    def tokenize(self, text:str) -> list: 
        if self.tokenizer == "split": 
            tokenized_content = text.split(" ")
        elif self.tokenizer == "spacy":
            doc = self.nlp(text)
            tokenized_content = [w.text for w in doc]
        else:
            raise ValueError("Tokenizer must be 'spacy' or 'split'")
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
                div_id = 0
                for div in divs:
                    div_id += 1
                    # div_content = []        # print(file)
                    content = dict()
                    # content['id'] = files.index(file)
                    content["text"] = []
                    content['tag'] = []
                    content['tag_id'] = []
                    content['prov'] = file
                    for element in div.descendants :
                        if element.name in self.tags_to_extract:
                            # fetch correct label 
                            label_number = self.tags_to_extract.index(element.name)
                            label = self.class_names[label_number]
                            # add the text in a list so that it doesn't get repeated
                            tagged.append(element.text)
                            full_name = self.tokenize(element.text)
                            if len(full_name) > 1:
                                result.append((full_name[0], element.name, f"B-{label}"))
                                content["text"].append(full_name[0])
                                content["tag"].append(f"B-{label}")
                                content["tag_id"].append(self.label2id[f"B-{label}"])
                                for x in range(1, len(full_name)):
                                    if not re.fullmatch(r"(\s+|\t|\n|)", full_name[x]):
                                        result.append((full_name[x], element.name, f"I-{label}"))
                                        content["text"].append(full_name[x])
                                        content["tag"].append(f"I-{label}")
                                        content["tag_id"].append(self.label2id[f"I-{label}"])
                            
                            else:
                                result.append((element.text, element.name, label))
                                content["text"].append(element.text)
                                content["tag"].append(f"B-{label}")
                                content["tag_id"].append(self.label2id[f"B-{label}"])
                        elif isinstance(element, str):
                            # check that it hasn't been dealt with already
                            if element.text not in tagged:
                                label_number = 0
                                tokenized_content = self.tokenize(element.text)
                                for ele in tokenized_content:
                                    if ele:
                                        result.append((ele, self.tags_to_extract[label_number], self.class_names[label_number]))
                                        content["text"].append(ele)
                                        content["tag"].append("O")
                                        content['tag_id'].append(0)
                    
                    self.out.append(content)  
        return self.out





    def writing_csv(self):
        with open(self.outdoc, "w", newline="", encoding="UTF-8") as g:
            writer = csv.writer(g, delimiter=";", quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for div in self.out:
                if len(div['text'])>=1:
                    writer.writerow([div['text'], div['tag'], div['tag_id'], div['prov']])

def creation_dataset():
    data = Doc()
    data.get_files()
    data.set_label2id()
    data.set_id2label()
    data.extract_dataset_by_div()
    data.writing_csv()

if __name__ == "__main__":
    typer.run(creation_dataset)
    
    