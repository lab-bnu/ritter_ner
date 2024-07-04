---
Autrice: Alexia Schneider
Github: alexiaschn
Date de création: 2024-07
Titre: NER_Ritter
Licence: CC BY-SA
Description: Dépôt avec ressources logicielles et données pour la Reconnaissance d'Entités Nommées adaptée à des notices bibliographiques
---

# La Reconnaissance d'Entités Nommées : le Ritter augmenté comme cas d'usage

Dépôt et tutoriel pour la reconnaissance d'Entités Nommées (EN) à partir des données du Répertoire bibliographique des imprimés d'Alsace des XVe et XVIe siècles de François Ritter aka le Ritter.

Le tutoriel suit la [documentation](documentation/) avec les différentes étapes : [Présentation des données](documentation/1.Les_donnees.md), [OCRisation](documentation/2.OCR.md), [Création des jeux de données, de l'annotation manuelle au formatage pour l'utilisation d'algorithmes](documentation/3.Creation_jeux_de_donnees.md), puis [Présentation des différentes stratégies pour la Reconnaissance d'EN](documentation/4.Strategie_NER.md), ce qui offre la possibilité d'[Entrainer un modèle avec spaCy](documentation/5.Entrainement_modele_avec_spacy.md) ou d'[Utiliser des modèles génératifs](documentation/6.Modeles_generatif.md).

Les programmes principaux sont : 

programme|commentaire
--|--
params.py|gère tous les paramètres pour les programmes principaux, se référer à la documentation poru les étapes concernées
creation_dataset.py|convertit les pages XML en tableurs CSV (et en document .spacy pour l'entrainement) en fonction des paramètres
hf_ner|produit les prédictions à partir du fichier csv en fonction du modèle disponible sur HF donné en paramètre, effectue aussi l'évaluation du modèle
regex_ner|à partir du csv généré par creation_dataset effectue la prédiction par regex depuis la _Liste alphabétique des noms de personnes_ du Ritter : ne fonctionne qu'avec ces données. 
generative_models_ner| Divise en batch de texte avec le prompt en fonction du nombre de token maximal donné en paramètre
alignement_encodage_xml|Cherche l'URI IdRef de chaque EN de personne et encode en XML le document final en XML par div ou par page

Les étapes fondamentales sont aussi divisées dans des programmes courts standalone qui peuvent être utiles pour l'application sur d'autres jeux de données :

|programme|arguments|options|commentaire
|--|--|--|--|
evaluation_ocr.py|*ground_truth* : chemin du document en txt contenant la transcription correcte. *model_output* :chemin vers le document txt contenant la transcription produite par le modèle *output_doc* : chemin vers le document .csv dans lequel les mesures d'évaluation seront enregistrées.|*--auto* : argument optionnel pour faire l'évaluation de toutes les transcriptions présentes dans le dossier model_output | enregistre les mesures CER et WER du document OCRisé |
extract_names.py|*doc*: document .csv de sortie de creation_dataset.py avec annotation manuelle *outdoc* : document dans lequel sera écrit la liste des noms de personnes|| Extrait du doc avec les données tokenisées et les étiquettes correctes les tokens correspondants à des noms de personnes
train_test_split.py|    *doc* : sortie en csv du programme creation_dataset.py contenant les données tokenisées et alignées avec leur étiquette correcte *outdir* : dossier où seront écrits les jeux d'entrainement et de test en format csv || Créé les csv contenant les jeux d'entrainement et de test
testing_hf_ner.py| *document* : document en .txt contenant le texte brut sur lequel on veut faire de la NER. *model* : nom du modèle disponible via Hugging Face.| *--outpath* : sauvegarde des EN extraits dans le document donné. | Permet de visualiser la tâche de NER à partir d'un simple document txt. 
spacy_ner.py|*document* : document en .txt contenant le texte brut sur lequel on veut faire de la NER. *model* : nom du modèle de spaCy  |*--outpath* : sauvegarde des EN extraits. | Tâche de NER simple à partir d'un modèle de spaCy. 
training_llm.ipynb|||Notebook pour l'affinage de modèles Transformers. 
create_batches.py|_template.txt_ : document .txt contenant l'instruction de base à ajouter à chaque batch. _txtdir_ : dossier contenant le/s texte/s en format .txt _outdir_ : dossier de sortie des batches au format .txt||divise le contenu d'un ensemble de documents txt en fonction de la fenêtre contextuelle maximale du modèle employé : permet d'insérer le contenu manuellement dans le prompt via l'interface web.  |
alignement.py|"nom d'une personne"|--sparql : fait une requête via l'endpoint SPARQL et non Sru | requête www.idref.fr pour obtenir l'URI d'un nom