# chaîne entière du XML non encodé au XML encodé avec les prédictions du modèle spacy 
from bs4 import BeautifulSoup
import glob
import re
import csv
from typing import Optional
from pathlib import Path
from params import param_general, param_chaine_prediction
import os.path
import ast
import spacy
import requests
from lxml import etree
import warnings
warnings.filterwarnings("ignore")
import sys

class Data:
    outdir = param_chaine_prediction['outdir']
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    outdoc = f"{outdir}/{param_chaine_prediction['csvdocname']}"
    data = []
    try:
        nlp = spacy.load(param_chaine_prediction['model_spacy'])
    except OSError:
         sys.exit(f"Télécharger le modèle en ligne de commande : spacy download {param_chaine_prediction['model_spacy']}")


    def get_files(self):
        self.files = [file for file in glob.glob(f"{param_chaine_prediction['xml_dir']}/*.xml")]
        return self.files
    
    def tokenize(self, text:str) -> list: 
        doc = self.nlp(text)
        return [w.text for w in doc]
    

    def set_data(self, file:Path):
        dictdata = self.xml2data(file)
        self.data.append(dictdata)

    def get_data(self):
        return self.data
    
    def xml2data(self, file:Path):
        """
        Extraction du XML et prédiction du modèle
        """
        content = dict()
        with open(file, "r", encoding="UTF-8") as f: 
            soup = BeautifulSoup(f, "xml")
            page = soup.find('body')   
            originaltext = re.sub(r'(\t|)', '', page.text)
            originaltext = re.sub(r'(\n|\s\s+)', ' ', originaltext)
            content['originaltext'] = originaltext
            content["tokens"] = self.tokenize(originaltext)
            ents =  self.predict([originaltext])  # must be a list of full sentences (in this case just one page )          
            full_names = self.set_list_full_name(ents)
            for ent in full_names:
                if ent['label'] == "PER":
                    idref = self.get_idref(ent['entity'])
                    if idref is not None:
                        ent['idref'] = idref
            content['ents'] = full_names
            content['prov'] = os.path.basename(file)
            return content
        
    def predict(self, fulltext:list):
         return [[ent.text, ent.label_] for doc in self.nlp.pipe(fulltext, disable=["tok2vec", "tagger", "parser", "attribute_ruler", "lemmatizer"]) for ent in doc.ents]
    

    def set_list_full_name(self, ents:list):
        full_names = []
        name = []
        label = '_'
        for ent, l in ents:
            if l.startswith("B-"): 
                if label != '_':
                    full_names.append({'entity': ' '.join(name), 'label': label})
                    name = []
                name.append(ent)
                label = re.search(r"B-(.*)", l)
                label = label.group(1)
            elif l.startswith('I-') and not re.fullmatch(r'\W', ent) and l.endswith(label):
                name.append(ent)
            elif l.startswith('I-') and not l.endswith(label) :
                if label != '_':
                    full_names.append({'entity': ' '.join(name), 'label': label})
                name = []
                name.append(ent)
                label = re.search(r"I-(.*)", l)
                label = label.group(1)
        if name and label != '_':
            full_names.append({'entity': ' '.join(name), 'label': label})
        return full_names


    def get_idref(self, nom):
        url = "https://www.idref.fr/Sru/Solr?q=persname_t:"
        parameters = {"wt":"json"}
        if nom.split(' '):
            nom = re.sub(" ", '%20AND%20', nom)
            url += '('+nom+')'
            try: 
                response = requests.get(url, params=parameters)
            except requests.exceptions.ConnectionError: 
                print("Too many requests :(")
                
            content = ast.literal_eval(response.content.decode('utf-8'))
            if content['response']['numFound'] == 1:
                name_info = content['response']['docs'][0]["affcourt_z"]            
                idref = content['response']['docs'][0]['ppn_z']
                print((name_info, idref))
            else:
                idref = None
        return idref

    def prettyprint(self, element, **kwargs):
        xml = etree.tostring(element, pretty_print=True, **kwargs)
        print(xml.decode(), end='')

    def write_xml(self):
        for page in self.data:
            xml = etree.Element('xml')
            root = etree.SubElement(xml, 'body')    
            div = etree.SubElement(root, 'div')                
            p = etree.SubElement(div, 'p')  
            ch = ''
            for tok in page['tokens']:
                print(tok)
                entity = ''                
                if any(tok == ent['entity'].split()[i] for ent in page['ents'] for i in range(len(ent['entity'].split()))):
                    for e in page['ents']:
                        if tok == e['entity'].split()[0]:
                            if e == entity:
                                continue
                            entity = e
                            try:
                                ch = re.sub(r"\s(\W)", r"\1", ch )
                                ch =  ch
                                entity_elem.tail = ch
                                ch = ''
                            except UnboundLocalError:
                                ch = re.sub(r"\s(\W)", r"\1", ch )
                                p.text = ch
                                ch = ''                            
                            entity_elem = etree.SubElement(p, f"{param_general['tags_to_extract'][param_general['class_names'].index(entity['label'])]}")
                            if "idref" in list(entity.keys()):
                                entity_elem.attrib['idref'] = entity['idref']
                            entity_elem.text = entity['entity']                            
                else:
                    # prévision de la tokenisation des modèles Transformers type camembert qui ajoutent un _ pour signaler début de mot 
                    # tok = re.sub(r"[▁#]", r" ", tok )
                    ch += tok + ' '
            if ch: 
                ch = re.sub(r"\s(\W)", r"\1", ch )
                entity_elem.tail = ch
            tree = etree.ElementTree(xml)
            tree.write(f"{self.outdir}/{page['prov']}", pretty_print=True, encoding='utf-8', xml_declaration=True)           

    def writedata(self):
        with open(f"{self.outdoc}.csv", 'a', newline='', encoding="utf-8") as g:
            writer = csv.DictWriter(g, fieldnames=list(self.data[0].keys()), delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.data[-1])

    def get_xml(self, file):
        with open(file, "r", encoding="utf-8") as f:
            tree = etree.parse(f)
            print(etree.tostring(tree))

if __name__=='__main__':
    
    files = [file for file in glob.glob(f"{param_chaine_prediction['xml_dir']}/*.xml")]
    done = [encoded for encoded in os.listdir(f"{param_chaine_prediction['outdir']}/")]
    for file in files:
        if os.path.basename(file) not in done:
            data = Data()
            data.set_data(file)
            print(data.get_data())
            data.writedata()
            data.write_xml()
            data.get_xml(file)
        else:
            print(f"Already done {file}")
