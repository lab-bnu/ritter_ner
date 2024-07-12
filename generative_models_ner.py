import re
import glob
from getpass import getpass
import os
import typer
from typing import List, Optional
from pathlib import Path
from mistralai.client import MistralClient
import mistralai.exceptions
from transformers import AutoTokenizer
from mistralai.models.chat_completion import ChatMessage
import csv
import sys
from bs4 import BeautifulSoup
import warnings
warnings.filterwarnings("ignore")

from params import param_IAgen

class Batches:
    doc = []
    batches = []
    template = param_IAgen['template']
    textdir = param_IAgen['inputdir']
    class_names = param_IAgen['class_names']
    outdir = param_IAgen['outdir']
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    tokenizer = AutoTokenizer.from_pretrained("mistralai/Mixtral-8x7B-v0.1")
    mistral_api_key = os.environ["MISTRAL_API_KEY"]         
    if not mistral_api_key:
        # PASS API KEY AS USER INPUT
        mistral_api_key = getpass("MISTRAL API Key: ")
    print(mistral_api_key)
    client = MistralClient(api_key=mistral_api_key)
            
            
            
    def tokenize(self, text:str): 
        return self.tokenizer.tokenize(text)

        
    def set_text(self): 
        files = [file for file in glob.glob(f"{self.textdir}/*")]
        for file in files:
            if Path(file).suffix == ".txt":
                with open(file, 'r', encoding='utf8') as f: 
                    page_content = [line for line in f]
                    self.doc.append(''.join(page_content))
            elif Path(file).suffix == ".xml":
                with open(file, "r", encoding="UTF-8") as f: 
                    soup = BeautifulSoup(f, "xml")
                    page_content = soup.find('body')   
                    page_content =re.sub(r'(\t|)', '', page_content.text)
                    page_content = re.sub(r'(\n|\s\s+)', ' ', page_content)
                    self.doc.append(page_content) 
        if not self.doc:
            sys.exit('Pas de document .txt ou .xml dans le dossier en paramètre')
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
                    sentence.insert(0, self.template)                    
                    self.batches.append(sentence)
                    sentence = []
            # in case the document is shorter than max_length
            if sentence:
                sentence.insert(0, self.template)
                self.batches.append(sentence)
        return self.batches
    

    def write_batches(self):     
        for batch in self.batches: 
            with open(f"{self.outdir}/batch_{self.batches.index(batch)+1}.txt", "w", encoding="UTF-8") as f:
                f.write(''.join(batch))

    def get_batches(self):
        return self.batches
    
    def format_prompt(self, batch:List[str]) -> List[ChatMessage] :
        """    Formats the template with the document or chunk of document to form a valid prompt
        Args:
            batch: index 0 = template, following indexes = query
        Returns:
            ChatMessage for MistralAI ChatMessage 
        """
        formatted_prompt = [
            ChatMessage(role="system", content=batch[0]),
            ChatMessage(role="user", content="".join(batch[1:]))
            ]
        return formatted_prompt
    
    def request_api(self):
        output = [] 
        for x in range(len(self.batches)):
            output_batch = []
            formatted_prompt = self.format_prompt(self.batches[x])
            try:
                response = self.client.chat(model="mistral-small", temperature=param_IAgen['temperature'], messages=formatted_prompt)
                answer = response.choices[0].message.content
                output_batch.append(answer)
                output.append(' '.join(output_batch))
                self.write_answers(self.batches[x], " ".join(output_batch))
            except mistralai.exceptions.MistralException:
                print(f"Request operation timed out, skipping batch :\n{self.batches[x]}")
        return ' '.join(output)
    
    def write_answers(self, batch:List[str], output:str): 
        with open(f"{param_IAgen['outdir']}/api_answers.csv", "a", newline="\n", encoding="utf-8") as g:
            csvwriter = csv.writer(g, delimiter=';',
                        quotechar='"', quoting=csv.QUOTE_MINIMAL)
            csvwriter.writerow([''.join(batch[1:]), output])
            

if __name__=='__main__':
    batch = Batches()
    batch.set_text()
    batch.create_batches()
    if param_IAgen['mode'] == "manuel":
        batch.write_batches()
    if param_IAgen['mode'] == "api":
        print(batch.request_api())