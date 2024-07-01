import urllib.request
import requests
import re
import ast
import sys
import typer
from typing import Optional


def request_idref(nom):
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
        elif content['response']['numFound'] > 1:
            print("More than one match here's the list of names with idRef :")
            print(*[(name['affcourt_z'], name['ppn_z']) for name in content['response']['docs']], sep='\n')
            idref = input(f"Entrez l'identifiant correct pour le nom {nom} :\t")
            if idref == '':
                idref = 'TBD'
        elif content['response']['numFound'] == 0:
            idref = 'TBD'
            print("Nom introuvable")

    return idref


def find_idref_sparql(nom):
    from SPARQLWrapper import SPARQLWrapper, JSON
    endpoint_url = "https://data.idref.fr/sparql"
   
    query = f"""
    PREFIX bio: <http://purl.org/vocab/bio/0.1/> 
    PREFIX foaf: <http://xmlns.com/foaf/0.1/> 
    PREFIX xsd: <http://www.w3.org/2001/XMLSchema#> 
    select ?nom ?naissance ?id
    where {{
    ?id foaf:name ?nom;
        bio:event [a bio:Birth ; bio:date ?naissance] ; 
                                    foaf:name ?nom.
        ?nom bif:contains "{nom}".

    FILTER (xsd:integer(?naissance)<1800)

    }}
    LIMIT 10
    """
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

def start(nom_complet, sparql:Optional[bool]=False):
    if sparql == True:
        find_idref_sparql(nom_complet)
    else:
        request_idref(nom_complet)
    
if __name__=='__main__':
    typer.run(start)