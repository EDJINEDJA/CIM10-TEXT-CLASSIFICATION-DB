#!/bin/bash

echo "Bienvenue .."

# Chemin vers le dossier contenant le script Python et le fichier Pipfile.lock
SCRIPT_PATH = /home/lnit/icd10-db-4-icd10taskclassification/


echo "Enable environnement .."
# Activer l'environnement virtuel Pipenv
cd $SCRIPT_PATH && pipenv shell
#pipenv install -r /home/lnit/icd10-db-4-icd10taskclassification/requirements.txt

# Exécuter le script Python à l'aide de pipenv run
pipenv run python3 /home/lnit/icd10-db-4-icd10taskclassification/app.py

# Désactiver l'environnement virtuel Pipenv
exit