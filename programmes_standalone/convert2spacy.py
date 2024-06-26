# conversion to spacy standalone




import spacy.lang
import srsly
import typer
import warnings
from pathlib import Path
import random
import spacy
from spacy.tokens import DocBin
import csv
import ast
import re
import pandas as pd
from bs4 import BeautifulSoup
import glob


def convert(lang: str, input_path: Path, output_path: Path, output_path_test: Path):
    nlp = spacy.blank(lang)
    train_db = DocBin()
    test_db = DocBin()
    nlp = spacy.blank(lang)
    db = DocBin()
    data = []
    with open(input_path, newline='', encoding='UTF-8') as f:
        reader = csv.DictReader(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        next(reader)
        for row in reader: 
            originaltext = row['originaltext']
            labels = row['label']
            # text = ast.literal_eval(text)
            
            label = ast.literal_eval(label)
            ents = []
            for tok in text: 
                l = label[text.index(tok)]
                if l != 'O':             
                    lim = re.search(rf"{re.escape(tok)}", rf'{originaltext}')
    
                    ent = (lim.start(), lim.end(), l)
                    ents.append(ent)
            sent = {'text' : ch, 'entities': ents}
            data.append(sent)

        
        processing(nlp, db, data, output_path)
        
def processing(nlp, db, data, output_path):
    count = 0
    for line in data:

        text = line["text"]
        ents = set(line['entities'])

        doc = nlp.make_doc(text)
        res = []
        for  start, end, label in ents:
            span = doc.char_span(start, end, label=label)
            if span is None:
                count += 1
                msg = f"Skipping entity [{start}, {end}, {label}] in the following text '{doc.text[start:end]}' does not align with token boundaries:\n\n{repr(text)}'"
                warnings.warn(msg)
            else:
                res.append(span)
        doc.ents = res
        db.add(doc)
    print(count)
    db.to_disk(output_path)
        



train_set_path = "fine-tuning/dataset/train_test/"
out_doc = "spacy-llm/data/div_spacy.csv"

excluded_tags = ["div", "bibl", "title", "lb"]

included_tags = ['other', 'persName', 'placeName', 'date']
corr_label = ["O", "PER", "LOC", "DATE" ]

class_names = ['O', 'B-PER', 'I-PER', 'B-DATE', 'I-DATE', 'B-LOC', 'I-LOC'],
label2id = {'O': 0,
  'B-PER': 1,
  'I-PER': 2,
  'B-DATE': 3,
  'I-DATE': 4,
  'B-LOC': 5,
  'I-LOC': 6}
id2label = {0: 'O',
  1: 'B-PER',
  2: 'I-PER',
  3: 'B-DATE',
  4: 'I-DATE',
  5: 'B-LOC',
  6: 'I-LOC'}

def extract_dataset_div():
    """
    Extraction des noms du XML encodé dans un fichier CSV
    """
    files = [file for file in glob.glob(f"{train_set_path}xml_encode/*.xml")]
    print(files)
    nlp = spacy.load("fr_core_news_sm")
    result = []
    results1 = []
    for file in files:
        with open(file, "r", encoding="UTF-8") as f: 
            soup = BeautifulSoup(f, "xml")
            tagged = [] # list containing elements from included_tags list
            divs = soup.find_all("div")
            div_id = 0
            for div in divs[1:]:
                div_id += 1
                # div_content = []        # print(file)
                content = dict()
                # content['id'] = files.index(file)
                content["text"] = []
                content['label'] = []
                content['ner_tag'] = []
                for element in div.descendants :
                    if element.name in included_tags:
                        # fetch correct label 
                        label_number = included_tags.index(element.name)
                        label = corr_label[label_number]
                        # add the text in a list so that it doesn't get repeated
                        tagged.append(element.text)
                        # raw tokenization of the element's content
                        # full_name = element.text.split(" ")
                        # new tokenization with spacy.fr
                        full_name = nlp(element.text)
                        full_name = [t.text for t in full_name]
                        if len(full_name) > 1:
                            result.append((full_name[0], element.name, f"B-{label}"))
                            content["text"].append(full_name[0])
                            content["label"].append(f"B-{label}")
                            content["ner_tag"].append(label2id[f"B-{label}"])
                            for x in range(1, len(full_name)):
                                if not re.fullmatch(r"(\s+|\t|\n|)", full_name[x]):
                                    result.append((full_name[x], element.name, f"I-{label}"))
                                    content["text"].append(full_name[x])
                                    content["label"].append(f"I-{label}")
                                    content["ner_tag"].append(label2id[f"I-{label}"])
                        
                        else:
                            result.append((element.text, element.name, label))
                            content["text"].append(element.text)
                            content["label"].append(f"B-{label}")
                            content["ner_tag"].append(label2id[f"B-{label}"])
                    elif isinstance(element, str):
                        # check that it hasn't been dealt with already
                        if element.text not in tagged:
                            label_number = 0
                            # tokenize
                            for ele in element.text.split(" "):
                                if not re.fullmatch(r"(\s+|\t|\n|)", ele):
                                    result.append((ele, included_tags[label_number], corr_label[label_number]))
                                    content["text"].append(ele)
                                    content["label"].append("O")
                                    content['ner_tag'].append(0)
                    # print(content)

                # div_content.append(content)
                results1.append(content)  
    return results1




if __name__ == "__main__":
    # typer.run(convert)
    # all = extract_dataset_div()
    # df = pd.DataFrame.from_dict(all)
    # df = df.reset_index(drop=True)
    # print(df.info())
    # print(df.head())


    # df.to_csv(out_doc)
    convert("fr", "spacy-llm/data/div_spacy.csv", "spacy-llm/data/div_spacy.spacy", "spacy-llm/data/div_spacy_test.spacy")

    