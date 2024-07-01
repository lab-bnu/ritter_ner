import re
import glob
import warnings
from getpass import getpass
import os
from params import param_general, param_IAgen
import typer

class Batches:
    doc = []
    batches = []
    template = param_IAgen['template']
    textdir = param_IAgen['txtdir']
    model = param_IAgen['model']
    class_names = param_general['class_names']
    outdir = param_IAgen['outdir']
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    def set_tokenizer(self):
        if self.model not in ['mistral', 'gpt']: 
            print("nein")
        if self.model == 'mistral':
            # imports spécifiques au modèle
            from mistralai.client import MistralClient
            from transformers import AutoTokenizer
            self.tokenizer = AutoTokenizer.from_pretrained("mistralai/Mistral-7B-v0.1")
            mistral_api_key = os.environ["MISTRAL_API_KEY"]            
            if not mistral_api_key:
                # PASS API KEY AS USER INPUT
                mistral_api_key = getpass("MISTRAL API Key: ")
            print(mistral_api_key)
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
                if (len(sentence) + len(tokenized_template) + 1) < param_IAgen['max_length']: 
                    token = re.sub('▁', ' ', token)
                    sentence.append(token)
                else: 
                    print(sentence)
                    sentence.insert(0, self.template)                    
                    self.batches.append(sentence)
                    sentence = []
        return self.batches
    

    def write_batches(self):     
        for batch in self.batches: 
            with open(f"{self.outdir}/batch_{self.batches.index(batch)+1}.txt", "w", encoding="UTF-8") as f:
                f.write(''.join(batch))

def start():
    """Créé des batches de textes pour en fonction du nombre de tokens maximum indiqué et du template donné dans les paramètres. """
    batch = Batches()
    print(batch.set_text())
    batch.set_tokenizer()
    print(batch.create_batches())
    batch.write_batches()

if __name__=='__main__':
    typer.run(start)