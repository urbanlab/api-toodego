# Prediction interface for Cog ⚙️
# https://cog.run/python

from cog import BasePredictor, Input, Path
import os
import spacy
import requests
import json
from base64 import b64decode
from pdf2image import convert_from_path
import time
import cv2
import easyocr
import numpy as np
import re
from difflib import SequenceMatcher

AUTH_TOKEN = os.getenv('AUTH_TOKEN')
TOODEGO_LOGIN = os.getenv("TOODEGO_LOGIN")
TOODEGO_PASSWORD = os.getenv("TOODEGO_PASSWORD")

class Predictor(BasePredictor):
    def setup(self) -> None:
        """Load the model into memory to make running multiple predictions efficient"""
        # self.model = torch.load("./weights.pth")
        self.nlp = spacy.load("fr_core_news_md")

    def convert_pdf_to_images(self,pdf_path):
        images = convert_from_path(pdf_path)
        return images
    
    def extract_text(self,image_path):
        # Initialiser le lecteur EasyOCR
        reader = easyocr.Reader(['fr'])

        # Effectuer l'OCR sur l'image
        result = reader.readtext(image_path)

        # Concaténer le texte extrait de toutes les détections
        extracted_text = ""
        for detection in result:
            extracted_text += detection[1] + " "

        # Retourner le texte extrait complet
        return extracted_text


    def extract_text_from_image(self,image):
        img = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        _, image_binaire = cv2.threshold(gray_img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        texte_extrait = self.extract_text(image_binaire)
        texte_nettoye = re.sub(r'\s+', ' ', texte_extrait)
        return texte_nettoye

    def extract_text_from_pdf_or_image(self,file_path):
        if file_path.endswith('.pdf'):
            images = self.convert_pdf_to_images(file_path)
            extracted_text = ''
            for image in images:
                extracted_text += self.extract_text_from_image(image)
            return extracted_text
        elif file_path.endswith(('.png', '.jpg', '.jpeg')):
            image = cv2.imread(file_path)
            return self.extract_text_from_image(image)
            
        else:
            return "Format de fichier non pris en charge."

    def search_existence_probability(self,name, text):
        # Convertir le nom, l'adresse, le numéro et le texte en minuscules et diviser en mots
        name_words = set(name.lower().split())
    
        text_words = set(text.lower().split())

        # Compter le nombre de mots du nom, de l'adresse et du numéro présents dans le texte
        matching_words_count = sum(1 for word in name_words if word in text_words)
        

        # Calculer la probabilité d'existence du nom, de l'adresse et du numéro dans le texte
        total_words = len(name_words) 
        probability = matching_words_count / total_words if total_words > 0 else 0

        return probability
    
    def spacy_phrase_match(self,texte, phrases):
        doc = self.nlp(texte)
        total_phrases = len(phrases)
        counts = [0] * total_phrases
        
        for i, phrase in enumerate(phrases):
            for token in doc:
                if token.text == phrase:
                    counts[i] += 1
                    
        total_found = sum(1 for count in counts if count > 0)
        percentage = (total_found / total_phrases) * 100
        return percentage
    
    def prob_phrase_exist(self,phrase, texte):
        """
        Calcule la probabilité que la phrase existe dans le texte donné.

        Arguments :
        texte -- Le texte dans lequel on cherche la phrase.
        phrase -- La phrase à rechercher.

        Retourne :
        La probabilité que la phrase existe dans le texte.
        """
    
        if not texte or not phrase:
            raise ValueError("Le texte ou la phrase ne peut pas être vide.")
        
        texte = texte.lower()
        phrase = phrase.lower()
    
        len_phrase = len(phrase)

        max_score = 0

        for i in range(len(texte) - len_phrase + 1):
            score = SequenceMatcher(None, phrase, texte[i:i+len_phrase]).ratio()
            max_score = max(max_score, score)

        return max_score
    def extraire_nom_prenom_utilisateur(self,json_data):
        nom_usager = json_data["fields"]["nom_usager"]
        prenom_usager = json_data["fields"]["prenom_usager"]
        adresse_usager_raw = json_data["fields"]["adresse_usager_raw"]
        adresse_usager = json_data["fields"]["adresse_usager"]
        numero_adresse = json_data["fields"]["adresse_usager_structured"]["display_name"]
        voie_adresse = json_data["fields"]["adresse_usager_structured"]["display_name"]
        commune_adresse = json_data["fields"]["commune_adresse"]
        fichier_just = json_data["fields"]["justificatif_domicile"]["content"]
        name = json_data["fields"]["justificatif_domicile"]["filename"]
        
        
        return nom_usager, prenom_usager, adresse_usager_raw, adresse_usager, numero_adresse, voie_adresse, commune_adresse, fichier_just,name

    def predict(
        self,
        apiUrl: str = Input(description="API URL", default="https://demarches.guichet-recette.grandlyon.com/api/forms"),
        formSlug: str = Input(description="Form slug", default="poc-automatisation"),
        formId: str = Input(description="Form ID"),
        authToken: str = Input(description="Auth Token"),
    ) -> dict:
        if authToken != AUTH_TOKEN:
            return {"error": "Invalid auth token"}
        """Run a single prediction on the model"""

        api_url=f"{apiUrl}/{formSlug}/{formId}"        
        response = requests.get(api_url, auth=(TOODEGO_LOGIN, TOODEGO_PASSWORD))

        chemin_fichier_entree = "fichier.txt"
        chemin_fichier_sortie = "resul.txt"

        # Écrivez le contenu de la réponse dans le fichier d'entrée
        with open(chemin_fichier_entree, "w", encoding="utf-8") as fichier:
            fichier.write(response.text)

        # Ouvrez le fichier et chargez le contenu JSON
        with open(chemin_fichier_entree, "r", encoding="utf-8") as fichier:
            contenu_json = json.load(fichier)

        # Assurez-vous que le fichier contient la clé "fields"
        if "fields" in contenu_json:
            # Appelez la fonction pour extraire le nom et prénom de l'utilisateur
            nom, prenom, adresse_raw, adresse, numero_adresse, voie_adress,commune,fichier_ju,n = self.extraire_nom_prenom_utilisateur(contenu_json)

            # Écrivez le nom et prénom dans le fichier de sortie
            with open(chemin_fichier_sortie, "w", encoding="utf-8") as fichier_sortie:
            
                fichier_sortie.write(f"{fichier_ju}")
                

            #Ajoutez ces informations à la réponse de l'API
            contenu_json["nom_usager"] = nom
            contenu_json["prenom_usager"] = prenom
            with open('resul.txt', 'r') as file:
                b64 = file.read()

            # Décodez la chaîne Base64, en vous assurant qu'elle ne contient que des caractères valides
            bytes = b64decode(b64, validate=True)

            # Effectuez une validation de base pour vous assurer que le résultat est un fichier PDF valide
            # Attention ! Le numéro magique (signature de fichier) n'est pas une solution fiable à 100 % pour valider les fichiers PDF
            # De plus, si vous obtenez la Base64 à partir d'une source non fiable, vous devez désinfecter les contenus PDF
            if bytes[0:4] != b'%PDF':
                raise ValueError('Signature de fichier PDF manquante')

            # Écrire le contenu PDF dans un fichier local
            with open('fil.pdf', 'wb') as f:
                f.write(bytes)

            
            dossier="fil.pdf"
        
            time.sleep(8)
            h = self.extract_text_from_pdf_or_image(dossier)
            adresse_recherchee = voie_adress
            

            
            similarite_nom = self.search_existence_probability(nom, h)
            similarite_adresse = self.spacy_phrase_match(adresse_recherchee, h)
            similarite_prenom = self.search_existence_probability(prenom, h)
            similarite_adresse_2= self.prob_phrase_exist(adresse_recherchee, h)
            similarite_adresse_2= self.prob_phrase_exist(adresse_recherchee, h)
            similarite_adresse_3= self.search_existence_probability(adresse_recherchee, h)

            donnees = {
                "data": {
                    "score_nom": similarite_nom,
                    "score_prenom": similarite_prenom,
                    "score_adresse1": similarite_adresse,
                    "score_adress2": similarite_adresse_2,
                    "score_adress3":similarite_adresse_3
                    
                }
            }

            # remove the file after processing
            os.remove("fil.pdf")
            os.remove("fichier.txt")
            os.remove("resul.txt")

            # envoyer_resultats_api(slug_du_formulaire,identifiant_du_formulaire, donnees,authentification)
            return donnees

        
        
        else:
            return {"error": "Aucun fichier trouvé."}



