from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from typing import List,Optional
import pandas as pd
import numpy as np
from pydantic import BaseModel
import pymongo
from pymongo import MongoClient
from bson import ObjectId

api = FastAPI()

# Identifiants pour l'authentification basique
credentials_db = {
    "admin": "4dm1N",
    "vadang":"datascientest"
}

class DayRouteRequest(BaseModel):
    days: List[str]

def connexionMongo() :
    client = MongoClient("mongodb://localhost:27017/")  
    return client
def innsertMongo(nameC, datas):
    client = connexionMongo()
    collections = client["airlabs"][nameC]
    collections.insert_many(datas)
def getDatasMongo(nameC,query):
    client = connexionMongo()
    collections = client["airlabs"][nameC]
    resultat = collections.find(query)
    return resultat
# Authentification basique
security = HTTPBasic()

# Point de terminaison pour vérifier que l'API est fonctionnelle
@api.get("/")
def read_root():
    return {"message": "API is functional"}

# Point de terminaison pour récupérer l'aéroport d'un pays
@api.get("/airports/")
def get_airport(
    country_code: str
):
#
#    Obtenez les aéroport en fonction du pays
#    Args:
#    - `country_code` (str): Code ISO pays 
#
#    Returns:
#    - Liste des aéroports du pays correspondant.
#
    query = {"country_code": country_code}
    try:
        resultats = getDatasMongo("airports",query)
        # Traiter les résultats
        datas = []
        for item in resultats:
            # Convertir ObjectId en str si présent
            item_dict = {key: str(value) if key == "_id" and isinstance(value, ObjectId) else value for key, value in item.items()}
            datas.append(item_dict)

        return datas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données : {str(e)}")

# Point de terminaison pour récupérer la route des vols
@api.post("/routes/")
def get_route(
    dep_iata: str,
    arr_iata: str,
    days_request: DayRouteRequest = None,
    airline_iata: str = None,
):
#
#    Obtenez les routes en fonction des aéroports de départ et d'arrivée, et éventuellement de l'aéroline.

#    Args:
#    - `dep_iata` (str): Code IATA de l'aéroport de départ.
#    - `arr_iata` (str): Code IATA de l'aéroport d'arrivée.
#    - `days_request` (array, optional): la liste des jours : mon : lundi, tue: mardi, wed: mercredi, thu: jeudi, fri: friday, sat: samedi, sun: dimanche (facultatif).
#    - `airline_iata` (str, optional): Code IATA de la compagnie aérienne (facultatif).
#
#    Returns:
#    - Liste des routes correspondantes.
#
    days = days_request.days
    query = {"dep_iata": dep_iata, 
            "arr_iata": arr_iata
            }
    
    if airline_iata and airline_iata.strip():
        query["airline_iata"] = airline_iata
    if days :
        query['days'] = {"$in": days}
    try:
        resultats = getDatasMongo("routes",query)
        # Traiter les résultats
        datas = []
        for item in resultats:
            # Convertir ObjectId en str si présent
            item_dict = {key: str(value) if key == "_id" and isinstance(value, ObjectId) else value for key, value in item.items()}
            datas.append(item_dict)

        return datas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données : {str(e)}")

# Point de terminaison pour récupérer l'information du vols
@api.get("/flight_info/")
def get_flightInfo(
    flight_iata: str,
    
):
#
#    Obtenez l'information du vols

#    Args:
#    - `flight_iata` (str): Code IATA du vol.
#
#    Returns:
#    - L'information du vols
#

    query = {"flight_iata": flight_iata}
    
    try:
        resultats = getDatasMongo("flight_info",query)
        # Traiter les résultats
        datas = []
        for item in resultats:
            # Convertir ObjectId en str si présent
            item_dict = {key: str(value) if key == "_id" and isinstance(value, ObjectId) else value for key, value in item.items()}
            datas.append(item_dict)

        return datas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données : {str(e)}")

# Point de terminaison pour récupérer l'information du vols de retard
@api.get("/flight_delay/")
def get_flightDelay(
    dep_iata: str,
    arr_iata: str,
    
):
#
#    Obtenez l'information du vols

#    Args:
#    - `flight_iata` (str): Code IATA du vol.
#
#    Returns:
#    - L'information du vols
#

    query = {"dep_iata": dep_iata,
            "arr_iata" : arr_iata
            }
    
    try:
        resultats = getDatasMongo("flight_delay",query)
        # Traiter les résultats
        datas = []
        for item in resultats:
            # Convertir ObjectId en str si présent
            item_dict = {key: str(value) if key == "_id" and isinstance(value, ObjectId) else value for key, value in item.items()}
            datas.append(item_dict)

        return datas
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération des données : {str(e)}")

@api.post("/schedules/")
def get_schedules(
    dep_iata: str,
    arr_iata: str,
    flight_iata: str = None,
    credentials: HTTPBasicCredentials = Depends(security),
):
#
#    Obtenez les schedules en fonction des aéroports de départ et d'arrivée, et éventuellement de la référence du vols.

#    Args:
#    - `dep_iata` (str): Code IATA de l'aéroport de départ.
#    - `arr_iata` (str): Code IATA de l'aéroport d'arrivée.
#    - `flight_iata` (str, optional): Code IATA du vol (facultatif).
#
#    Returns:
#    - Liste des routes correspondantes.
#

    # Vérification des identifiants admin
    if credentials.username != "admin" or credentials.password != credentials_db["admin"]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Only admin can add a new question",
            headers={"WWW-Authenticate": "Basic"},
        )

    # Ajout de la nouvelle question à la base de données (à adapter selon votre modèle de >
    try:
        query = {"dep_iata": dep_iata,
                "arr_iata" : arr_iata
                }
        if flight_iata and flight_iata.strip():
            query["flight_iata"] = flight_iata

        resultats = getDatasMongo("schedules",query)
        # Traiter les résultats
        datas = []
        for item in resultats:
            # Convertir ObjectId en str si présent
            item_dict = {key: str(value) if key == "_id" and isinstance(value, ObjectId) else value for key, value in item.items()}
            datas.append(item_dict)

        return datas
    except Exception as e:
        # Gestion des erreurs
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to add question: {str(e)}")

