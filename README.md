# 📄 Toodego Ocr API

![Logo de Toodegoo avec le slogan "Facilitez vous la vi(ll)e"](./medias/platforms_large-image.jpeg)

[🇬🇧 English Documentation Here](README_EN.md)

Une api pour matcher l'identité d'une personne à partir d'un justificatif d'identité fourni sur la plateforme [Toodego](https://www.toodego.com/). projet experimental réalisé par les étudiants du Centrale Digital Lab

## Table des matières
- [📄 Toodego Ocr API](#-toodego-ocr-api)
  - [Table des matières](#table-des-matières)
  - [🗒 Prérequis](#-prérequis)
  - [🚀 Démarrage rapide](#-démarrage-rapide)
  - [🚴 Utilisation](#-utilisation)
  - [🚇 API](#-api)
    - [POST /predictions](#post-predictions)
      - [Webhook](#webhook)
  - [❤️ Contributeurices](#️-contributeurices)


## 🗒 Prérequis
- [Docker](https://www.docker.com/)
- [Python](https://www.python.org/)
- [pip](https://pip.pypa.io/en/stable/installation/)

## 🚀 Démarrage rapide
Copiez le fichier `.env.example` en `.env` et remplissez les variables d'environnement.

```bash
cp .env.example .env
```

Lancez docker-compose pour démarrer l'application.
```bash
docker-compose up
```

## 🚴 Utilisation

1. Soumettre le formulaire sur le [site de recette de toodego ](https://demarches.guichet-recette.grandlyon.com/poc-automatisation/) et récupérer l'identifiant du formulaire 

![url dans une barre de navigation avec rond jaune qui entoure la fin de l'url ou l'on voit le chiffre 31, il s'agit de l'id](./medias/get_id.png)

## 🚇 API

Il est possible de récupérer directement le résultat du score de confiance en utilisant l'api suivante

### POST /predictions

**Headers**

`Content-Type`: `application/json`


**Body**
```json
{
  "input": {
    "formId": "nombre",
    "authToken": "token",
    "apiUrl": "",
    "formSlug": "",
  }
}
```

Les champs apiUrl et formSlug sont optionnels.
Ils possedent par défaut les valeurs suivantes:
- apiUrl: https://demarches.guichet-recette.grandlyon.com/api/forms
- formSlug: 'poc-automatisation'

**Retourne:**


Retourne un json avec le score de confiance

```json
{
    "input": {
        "apiUrl": "https://demarches.guichet-recette.grandlyon.com/api/forms",
        "formSlug": "poc-automatisation",
        "formId": "32",
        "authToken": "token"
    },
    "output": {
        "data": {
            "score_nom": 1.0,
            "score_prenom": 1.0,
            "score_adresse1": 0.6060606060606061,
            "score_adress2": 0.9743589743589743,
            "score_adress3": 0.8333333333333334
        }
    },
    "id": null,
    "version": null,
    "created_at": null,
    "started_at": "",
    "completed_at": "",
    "logs": "",
    "error": null,
    "status": "succeeded",
    "metrics": {
        "predict_time": 38.96576
    },
    "output_file_prefix": null,
    "webhook": null,
    "webhook_events_filter": ["start", "output", "logs", "completed"]
}
```

#### Webhook

Il est possible de définir un webhook qui sera appelé à chaque événement spécifié (démarrage, sortie, logs et terminé). Le webhook doit être une URL valide vers laquelle le service POST les informations relatives au job. Les événements disponibles sont : "start", "output", "logs" et "completed".

**Headers**

`Content-Type`: `application/json`

`Prefer:` `respond-async`

**Body**
```json
{
  "input": {
    "formId": "nombre",
    "authToken": "token",
    "apiUrl": "",
    "formSlug": "",
  },
  "webhook": "url de callback",
  "webhook_events_filter": ["start", "output", "logs", "completed"],
}
```



## ❤️ Contributeurices
- [Freeinkstein](https://github.com/Freeinkstein)