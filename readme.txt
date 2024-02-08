La structure des fichiers :

project/
|-- docker-compose.yml
|-- readme.txt
|-- db/
|-- insert_data/
|   |__ data/  
| 	|   |-- airports.json
| 	|   |-- airlines.json
| 	|   |-- cities.json
| 	|   |-- countries.json
| 	|   |-- fleets.json
| 	|   |-- flight_delay.json
| 	|   |-- flight_info.json
| 	|   |-- routes.json
| 	|   |-- schedules.json
|   |-- Dockerfile
|   |-- insert_data.py
|   |-- requirements.txt
|-- fastapi_app/
|   |-- Dockerfile
|   |-- api_airline.py
|   |-- requirements.txt
|   |-- dash_airline.py


Les étapes à installer sur la machine virtuelle de Datascientest ou n'importe quelle machine :

Etape 1 : créer la structure des fichiers comme ci-dessus (les fichiers *.json seront transférer via SSH)
	mkdir project
	cd project
	mkdir install_manuel
	mkdir db
	mkdir insert_data
	mkdir fastapi_app
	cd insert_data
	mkdir data

Etape 2 : transférer les fichiers *.json à la machine virtuelle /project/insert_data/data. 
	Ouvrir un autre terminal, entrer dans le répertoire où il y a le fichier data_enginering_machine.pem. 
	Remplacer l'@ IP par l'@ IP de la machine virtuelle et puis copier ces lignes et exécuter :

	scp -i "data_enginering_machine.pem" airports.json ubuntu@176.34.137.217:/home/ubuntu/project/insert_data/data
	scp -i "data_enginering_machine.pem" airlines.json ubuntu@176.34.137.217:/home/ubuntu/project/insert_data/data
	scp -i "data_enginering_machine.pem" cities.json ubuntu@176.34.137.217:/home/ubuntu/project/insert_data/data
	scp -i "data_enginering_machine.pem" countries.json ubuntu@176.34.137.217:/home/ubuntu/project/insert_data/data
	scp -i "data_enginering_machine.pem" fleets.json ubuntu@176.34.137.217:/home/ubuntu/project/insert_data/data
	scp -i "data_enginering_machine.pem" flight_delay.json ubuntu@176.34.137.217:/home/ubuntu/project/insert_data/data
	scp -i "data_enginering_machine.pem" flight_info.json ubuntu@176.34.137.217:/home/ubuntu/project/insert_data/data
	scp -i "data_enginering_machine.pem" routes.json ubuntu@176.34.137.217:/home/ubuntu/project/insert_data/data
	scp -i "data_enginering_machine.pem" schedules.json ubuntu@176.34.137.217:/home/ubuntu/project/insert_data/data

Etape 3 : Créer l'image Mongo . 
	Entrer install_manuel (cd install_manuel) et puis créer le fichier docker-compose.yml.

	version: "3.3"
	services:
	  mongodb:
	    image : mongo:5.0
	    container_name: my_mongo
	    volumes:
	    - ./sample_training:/data/db
	    ports:
	    - 27017:27017

Etape 4 : Lancer l'image Mongodb en exécuatnt : docker-compose up -d 

Etape 5 : pip install pymongo

Etape 6 : insérer les données dans la base de mongo 

		créer le fichier /project/insert_data/insert_data.py 
		exécuter : /project/insert_data/python3 insert_data.py 

Etape 7 : Vérification des données dans la base de données Mongo
	Ouvrir une autre terminal, entrer dans le containeur my_mongo : docker exec -it my_mongo bash et puis appeler mongosh
	Vérifier si l'insertion des données est bien passée en passant la requête dans mongosh : use airlabs
	et puis : db.airports.find({"country_code": "FR" })

Etape 8 : Installer FastAPI 
	pip3 install fastapi httptools==0.1.* uvloop uvicorn
    sudo apt install uvicorn
    pip install pandas

Etape 9 : Créer le fichier /project/fastapi_app/api_airline.py 
    nano /project/fastapi_app/api_airline.py 
    copier et coller le contenu du fichier api_airline.py

Etape 10 : Lancer le service fastapi
 	/project/fastapi_app/uvicorn api_airline:api --reload --host 0.0.0.0

Etape 11 : Tester FastAPI via la machine virtuelle 
	par ex : http://18.200.243.129:8000/docs#/

Etape 12 : Installer DASH
	pip install dash

Etape 13 : Créer le fichier /project/fastapi_app/dash_airline.py
	Copier et coller le contenu du fichier dash_airline.py

Etape 14 : exécuter le fichier /project/fastapi_app/python3 dash_airline.py

Etape 15 : Lancer l'interface Dash via le navigateur 
	Par ex en remplacant l'@IP de la machine virtuelle : http://176.34.137.217:7777/
