# ens_projet_reseau

##How to use 
Pour lancer le serveur :
* -p : port
* -d : une donnée optionnelle (forcément une chaine UTF-8)
``` 
python3 trump.py -p 5124 -d "Hello!" 
```

Pour envoyer des ordres au serveur :
* -p    : port du serveur 
* -host : adresse du serveur
* -a    : action [insert|delete] (pour ajouter, supprimer les données)
* -d    : la donnée une chaine UTF-8 (utile pour l'insertion)
* -id   : id de la donnée ajoutée/supprimée

``` 
python3 hillary.py -host 127.0.0.1 -p 5124 -a insert -d "Hello!" 0x0
```

Pour visionner les logs de l'éxecution de trump.py en live
``` 
tail -f trump.log
```




