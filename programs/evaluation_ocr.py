import jiwer
import csv
import glob
from pathlib import Path
from typing_extensions import List
import typer
import os.path as os
from typing import Optional


class OCR_eval:
    ref = []
    eval = []

    def get_ref(self,ground_truth: Path)-> List[str]:
        # extraction des lignes de ground_truth
        with open(ground_truth, 'r', encoding='UTF-8') as ref:
                self.ref = [line for line in ref] 
        return self.ref

    def find_cer_wer(self, model_output:Path) -> List[float]:
        with open(model_output, 'r', encoding='UTF-8') as pred: 
                pred = [line for line in pred]
        out = jiwer.process_words(self.ref, pred)
        out_char = jiwer.process_characters(self.ref, pred)
        # visualisations
        print(jiwer.visualize_alignment(out))
        print(jiwer.visualize_alignment(out_char))
        
        self.eval.append([str(model_output), round(out_char.cer, 3), round(out.wer, 3)])
        return self.eval

    def write_cer(self, output_doc:Path):
        with open(f"{output_doc}", 'a', newline='', encoding='UTF-8') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if os.getsize(output_doc) == 0:
                writer.writerow(['model', 'CER', 'WER'])
            for eval in self.eval:
                writer.writerow(eval)
        
def evaluate(ground_truth:Path, model_output:Path, output_doc:Path, auto:Optional[bool]=False):
    """
    Evalue la transcription du doc txt --model-output par rapport au doc txt --ground-truth les écrit dans le doc csv --output-doc
    L'option --auto automatise l'évaluation de plusieurs transcription dans le même dossier --model-output
    """
    eval = OCR_eval()
    eval.get_ref(ground_truth)
    if auto == True:
        outputs = [output for output in glob.glob(f"{model_output}/*.txt")]
        for output in outputs:
            eval.find_cer_wer(output)
    else:
         eval.find_cer_wer(model_output)
    eval.write_cer(output_doc)

if __name__ == '__main__':
    typer.run(evaluate)