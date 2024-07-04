import urllib.request
import requests
import re
import csv
from params import param_general, param_alignement, param_creation_dataset
from pathlib import Path
import ast
import sys
import typer
from typing import Optional
from lxml import etree
import os.path
import json
import inputimeout
class Document:

    class_names = param_general["class_names"]
    ents = []
    ents_idref = []
    data = []
    outdir = param_alignement['outdir']
    if not os.path.isdir(outdir):
        os.mkdir(outdir)
    

    def set_labels(self):
        """
        Construit le dictionnaire label2id avec IOB
        """
        if param_general['OIB'] == True:
            prefixes = ['B-', 'I-']
            self.class_names = [label if label == 'O' else f"{pref}{label}" for label in self.class_names for pref in prefixes]
        self.label2id = {label : id-1 for id, label in enumerate(self.class_names)}
        self.id2label = {id:label for label, id in self.label2id.items()}
        self.baselabel2id = []



    def set_data(self):
        datapath = param_alignement['ents_doc_path']
        if datapath == None:
            datapath = f"{param_general['datadir']}/{param_general['datadoc']}.csv"
        if Path(datapath).suffix == '.csv':
            with open(datapath, 'r', newline='', encoding='utf-8') as f: 
                reader = csv.DictReader(f, delimiter=';', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for line in reader:
                    self.data.append(line)
                    ents = ast.literal_eval(line[param_alignement['ents_id_colname']])
                    for x in range(len(ents)):                        
                        self.ents.append((ast.literal_eval(line[param_alignement['tokens_colname']])[x], self.id2label[ents[x]]))
            
            self.set_full_name()
        else: 
            sys.exit('Document doit être un csv avec délimiteur ";"')
        return self.ents
    
    def set_full_name(self):
        full_names = []
        name = None
        label = None
        for ent, l in self.ents:
            if param_general['OIB'] == True:
                if l.startswith("B-"): 
                    full_names.append((name, label))
                    name = ent
                    label = re.search(r"B-(.*)", l)
                    label = label.group(1)
                if l.startswith('I-') and not re.fullmatch(r'\W', ent):
                    name += f" {ent}"                     
            else:
                if l != label:
                    full_names.append((name, label))
                    name = ent
                    label = l
                elif l == label and not re.fullmatch(r'\W', ent):
                    name += f" {ent}"
        if len(full_names) <=1:
            full_names.append((name, label))
            # full_names.append((' '.join([name for name,l in self.ents]), re.fullmatch(r'[BI]-(\w*)', l)))
        self.ents = [[name,label] for name,label in full_names if name != None]
        

    
    
    
    def set_idref(self):
        base_url = "https://www.idref.fr/Sru/Solr?q=persname_t:"
        parameters = {"wt":"json"}
        for ent in self.ents:
                if ent[1] == 'PER':
                    if ent[0].split(' '):
                        ent[0] = re.sub(" ", '%20AND%20', ent[0])
                    url =  base_url + '('+ent[0]+')'+"%20AND%20anneenaissance_dt:[1400-01-01T23:59:59.999Z TO 1650-01-01T23:59:59.999Z]"
                    try: 
                        response = requests.get(url, params=parameters)
                    except requests.exceptions.ConnectionError: 
                        print(f"Skipping {ent[0]} because too many requests sent")
                        continue
                    try:
                        resp = ast.literal_eval(response.content.decode('utf-8'))
                    except SyntaxError:
                        print(f"{ent} not found")
                    if resp['response']['numFound'] == 1:
                        name_info = resp['response']['docs'][0]["affcourt_z"]
                        idref = resp['response']['docs'][0]['ppn_z']
                    elif resp['response']['numFound'] > 1:
                        print("More than one match here's the list of names with idRef :")
                        print(*[(name['affcourt_z'], name['ppn_z']) for name in resp['response']['docs']], sep='\n')
                        try:
                            idref = inputimeout(prompt=f"Entrez l'identifiant correct pour le nom {ent}", timeout=5)
                        except TimeoutError:
                            idref = ''
                        if idref == '':
                            idref = 'TBD'
                    elif resp['response']['numFound'] == 0:
                        idref = 'TBD'
                        print(f"{ent[0]} introuvable")
                    self.ents_idref.append({'entity':ent[0], 'label': ent[1], 'idref': idref })
                else:
                    self.ents_idref.append({'entity':ent[0], 'label': ent[1], 'idref': 'TBD'})

        return self.ents_idref




    def find_idref_sparql(self):
        from SPARQLWrapper import SPARQLWrapper, JSON
        endpoint_url = "https://data.idref.fr/sparql"
        for ent, label in self.ents:
            if label == "PER":
                query = f"""
                PREFIX bio: <http://purl.org/vocab/bio/0.1/> 
                PREFIX foaf: <http://xmlns.com/foaf/0.1/> 
                PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
                select ?nom ?naissance ?id
                where {{
                ?id foaf:name ?nom;
                    bio:event [a bio:Birth ; bio:date ?naissance] ; 
                                             foaf:name ?nom.
  					?nom bif:contains "{ent.encode('utf-8').decode('utf-8')}".

                FILTER (xsd:integer(?naissance)<1800)

                }}
                LIMIT 10
                """

                print(query)

                user_agent = "WDQS-example Python/%s.%s" % (sys.version_info[0], sys.version_info[1])
                # TODO adjust user agent; see https://w.wiki/CX6
                sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
                sparql.setQuery(query)
                sparql.setReturnFormat(JSON)
                try:
                    results  = sparql.query().convert()
                    for result in results["results"]["bindings"]:
                        print(result['nom']['value'])
                        print(result['id']['value'].split('/')[-2])
                except urllib.error.URLError as err:
                    print(err)


    def write_ents_idref(self):
        with open(f"{self.outdir}/ents_idref.tsv", 'w', newline='', encoding='utf-8') as f: 
            writer = csv.DictWriter(f, fieldnames=list(self.ents_idref[0].keys()), delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for ents in self.ents_idref: 
                writer.writerow(ents)
    
    def prettyprint(self, element, **kwargs):
        xml = etree.tostring(element, pretty_print=True, **kwargs)
        print(xml.decode(), end='')

    def write_xml(self):
        docs = self.gather_by_prov()
        for docname, rows in docs.items():
            # un seul div par document d'origine
            if len(rows) == 1:
                if param_alignement['originaltext_colname'] == param_alignement['tokens_colname']:
                    originaltext = ' '.join(rows[0][param_alignement['originaltext_colname']])
                else:
                    originaltext = rows[0][param_alignement['originaltext_colname']]

                xml = etree.Element('xml')
                root = etree.SubElement(xml, 'body')                    
                for ent in self.ents_idref:                            
                    groups = re.match(rf'(.*)({ent['entity']})(.*)', originaltext, flags=re.DOTALL)
                    if groups:
                        div.text = groups.group(1).encode('UTF-8').decode('UTF-8')
                        subelement = etree.SubElement(div, f"{param_general['tags_to_extract'][param_general['class_names'].index(ent['label'])]}", attrib={'idref':ent['idref']})
                        subelement.text = groups.group(2)
                        subelement.tail = groups.group(3)
                    else: 
                        root.text = originaltext
                tree = etree.ElementTree(xml)
                tree.write(f"{self.outdir}/{docname}", pretty_print=True, encoding='utf-8', xml_declaration=True)

            # plusieurs div pour le document d'origine (si traité par élément "div")
            elif len(rows) > 1:         
                    xml = etree.Element('xml')
                    root = etree.SubElement(xml, 'body')
                    for row in rows: 
                        if param_alignement['originaltext_colname'] == param_alignement['tokens_colname']:
                            originaltext = ' '.join(row[param_alignement['originaltext_colname']])
                        else:
                            originaltext = row[param_alignement['originaltext_colname']]
                        div = etree.SubElement(root, 'div')
                        for ent in self.ents_idref:                            
                            groups = re.match(rf'(.*)({ent['entity']})(.*)', originaltext, flags=re.DOTALL)
                            if groups:
                                div.text = groups.group(1).encode('UTF-8').decode('UTF-8')
                                if ent['idref'] != 'TBD':
                                    subelement = etree.SubElement(div, f"{param_general['tags_to_extract'][param_general['class_names'].index(ent['label'])]}", attrib={'idref':ent['idref']})
                                else:
                                    subelement = etree.SubElement(div, f"{param_general['tags_to_extract'][param_general['class_names'].index(ent['label'])]}")
                                subelement.text = groups.group(2)
                                subelement.tail = groups.group(3)

                            else: 
                                div.text = originaltext
                    tree = etree.ElementTree(xml)
                    tree.write(f"{self.outdir}/{docname}", pretty_print=True, encoding='utf-8', xml_declaration=True)


    def gather_by_prov(self): 
        provenances = [row['prov'] for row in self.data]
        return {prov : [row for row in self.data if row['prov'] == prov] for prov in provenances}




def start(writetsv:Optional[bool]=True, writexml:Optional[bool]=True):
    """Cherche les idRef des EN d'un texte tokenisé et aligné avec les étiquettes correctes"""
    doc = Document()
    doc.set_labels()
    doc.set_data()
    doc.set_idref()
    doc.gather_by_prov()
    if writetsv == True:
        doc.write_ents_idref()
    if writexml== True:
        doc.write_xml()

if __name__=="__main__":
    typer.run(start)