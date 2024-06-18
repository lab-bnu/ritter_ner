# Documentation : OCRisation du Ritter

Toute cette partie est disponible dans le dossier [ocr](../ocr/)

## eScriptorium
[eScriptorium](https://escriptorium.unistra.fr/) est un logiciel de retranscription dont une instance est hébergée par l'unistra à des fins de recherche et notamment pour l'entrainement de modèles d'OCR et d'HTR. 




### Ressources pour eScriptorium



## Programme d'évaluation des modèles 

Pour faire fonctionner le programme [evaluation_ocr.py](../ocr/evaluation_ocr.py) entrer en ligne de commande :

```
pip install -r requirements.txt
cd ocr/
```

Puis :
```
python evaluation_ocr.py <doc_vérité_de_terrain> <doc/dir_transcription> <document_sortie> <OPTION: --auto>
```

**doc_vérité_de_terrain** chemin du document au format txt contenant la vérité de terrain

**doc/dir transcription** : En mode par défaut : évaluation d'une seule transcription donc chemin vers la transcription au format txt faite par le modèle. En mode "auto" : évaluation de toutes les transcriptions présentes dans le dossier 
**document_sortie** : document au format csv qui contiendra les résultats 
**OPTION: --auto** permet d'effectuer l'évaluation de plusieurs transcriptions dans le dossier donné en 2e argument.

Attention aux formats des documents : les transcriptions sont en ```txt``` et le document de sortie en ```csv```. 

### Modèles comparés

- [CATMuS-Print Large](https://zenodo.org/records/10592716)
- [CATMuS-Print Tiny](https://zenodo.org/records/10602357)
- [ManuMcFondue](https://zenodo.org/records/10886224)
- [Transcription model for Paul d'Estournelles de Constant French typewritten letters (pec)](https://zenodo.org/records/10556673)

### Méthodologie

1. Sélection aléatoire de 21 pages du Ritter [(dir)](../ocr/ground_truth/tif)
2. Retranscription manuelle des 922 lignes [(dir)](../ocr/ground_truth/txt/)
3. Retranscription automatique par les 4 modèles.
4. Evaluation avec les métriques CER et WER.

### CER et WER

_Character Error Rate_ et _Word Error Rate_

[Word Error Rate](https://en.wikipedia.org/wiki/Word_error_rate)

*Character Error Rate*  : The Character Error Rate (CER) compares, for a given page, the total number of characters (n), including spaces, to the minimum number of insertions (i), substitutions (s) and deletions (d) of characters that are required to obtain the Ground Truth result. The formula to calculate CER is as follows: CER = [ (i + s + d) / n ]*100 ([source](https://oecd.ai/en/catalogue/metrics/character-error-rate-%28cer%29))

Les valeurs vont de 0 à 1 pour ces deux métriques et correspondent à des pourcentages d'erreur. On considère qu'au dessus de 10% d'erreur pour le CER une OCRisation n'est plus vraiment exploitable (demanderait une correction manuelle). 


### Résultats

modèle|CER|WER
----|----|---
|[catmus_large](../ocr/catmus/)|0.035|0.12|
[pec](../ocr/pec/)|0.435|0.902
[mcfondue](../ocr/mcfondue/)|0.231|0.688
[catmus_tiny](../ocr/catmus_tiny)|0.048|0.181


Le modèle CATMuS Large est de loin le meilleur avec 3% d'erreur pour le CER. On note cependant qu'il ne reconnait pas le pipe "|", ni les caractères spéciaux "ů" et le guillemet allemand " „ ". 

Je recommande un prétraitement simple sur ces caractères pour nettoyer la sortie. 
