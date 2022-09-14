# readUID-python

Suivre l'installion des dépendances via ce site : https://pimylifeup.com/raspberry-pi-rfid-rc522/

Installer mqtt : 
```
sudo pip3 install paho-mqtt
```

Installer dotenv :
```
sudo pip install python-dotenv
```



# Une fois les dépendances installées

On récupère mon code : 

```
cd ~
mkdir read-python
cd read-python
git clone https://github.com/Nathan08240/readUID-python
```

On se créer un fichier .env, il y a un ficher .env.exemple pour vous aider


Et on lance avec la commande :

```
sudo python3 read.py
```

Vous êtes prêts !

Pensez à inclure vos coordonnées de connexion pour MQTT dans les variables USERNAME, PASSWORD et HOST

# Si cela ne fonctionne pas à la fin, suivre les instructions suivantes :

Télécharger le dépot suivant : https://github.com/pimylifeup/MFRC522-python

via la commande suivant : 

```
cd ~
cd read-python
git clone https://github.com/pimylifeup/MFRC522-python
```

Ensuite : 

```
cd MFRC522-python
python setup.py install
```

Normalement tout devrait fonctionner ! 
