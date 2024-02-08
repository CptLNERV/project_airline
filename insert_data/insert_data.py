import os
import json
from pymongo import MongoClient

def insert_all_files_in_directory(directory_path, db_name):
    # Connexion à la base de données MongoDB
    client = MongoClient("mongodb://localhost:27017/")  
    db = client['airlabs']
    # Parcourir tous les fichiers dans le répertoire
    for filename in os.listdir(directory_path):
        if filename.endswith(".json"):
            collection_name = os.path.splitext(filename)[0]  # Utilisez le nom du fichier sans extension
            file_path = os.path.join(directory_path, filename)

            # Lecture des données depuis le fichier JSON
            with open(file_path, 'r') as file:
                data = json.load(file)

            # Insertion des données dans la collection
            collection = db[collection_name]
            collection.insert_many(data)

# Utilisation de la fonction pour insérer des données depuis tous les fichiers du répertoire "db"
insert_all_files_in_directory('data', 'airlabs')
