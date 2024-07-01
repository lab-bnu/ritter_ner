# batches 
import re
import json
import pandas as pd
import ast
import json
import glob
import csv
import typer
from transformers import AutoModelForCausalLM, AutoTokenizer
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix, classification_report
from pathlib import Path
from typing import Optional
import sys
import warnings
from params import param_general, param_IAgen

class Batches:
    doc = []
    batches = []
    
   
    def set_template(self, templatepath:Path): 
        if Path(templatepath).suffix != '.txt':
            warnings.warn("Doc template doit être format .txt")
            sys.exit()
        with open(templatepath, 'r', encoding='utf8') as f: 
            self.template = '\n'.join([line for line in f])
            return self.template
    
    def set_text(self, textdir:Path): 
        files = [file for file in glob.glob(f"{textdir}/*.txt")]
        if len(files) == 0:
            warnings.warn('Nein')
        for file in files:
            page = []
            with open(file, 'r', encoding='utf8') as f: 
                page_content = [line for line in f]
                self.doc.append('\n'.join(page_content))
    
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
    

    def write_batches(self, outdir:Path):     
        for batch in self.batches: 
            with open(f"{outdir}/batch_{self.batches.index(batch)}.txt", "w", encoding="UTF-8") as f:
                f.write(" ".join(batch))


def start(templatedoc:Path, txtdir:Path, outdir:Path):
    batch = Batches()
    batch.set_template(templatedoc)
    batch.set_text(txtdir)
    batch.write_batches(outdir)

if __name__=='__main__':
    typer.run(start)