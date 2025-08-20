# Comment se servir du logiciel ?

## Comment l'éxécuter la première fois ?

1) Exécuter le fichier "installer.bat" qui va s'occuper de tout installer. Si tous fonctionne correctement, il devrait vous lancer l'installateur de Tesseract, vous pouvez cliquer sur suiant jusqu'à terminer l'installation.
2) Si tout est bon vous pouvez appuyer sur entrée dans la console, et le logiciel se lancera alors.
3) Vous aurez des raccourcis sur votre bureau pour le lancer plus rapidement les prochaines fois !

## Si échec lors du lancement de l'installation

1) Vérifier que python est bien installé.
2) Regarder si les fichiers ont bien été cloné dans votre dossier.
3) Vérifier que tesseract est bien installé.
3) Essayer de lancer le raccourci sur votre bureau et regardé l'erreur qui apparait.

## Comment fonctionne le logiciel

Il vous affiche les fichier et essaye de les lires pour remplir automatiquement les 3 champs du milieux.
Je vous conseil de remplir les champs vous même pour ce qui est écrit à la main.
Le logiciel calcul à l'avance les fichiers suivants : laissez le donc tourner au moins 20s avant de commencer à l'utiliser pour qu'il puisse pré-charger.
Vous pouvez switch entre les champs avec tab et les flèches du clavier, copier coller la case en entier avec ctrl+c et ctrl+v, switcher entre les pages avec les flèches lorsqu'aucun champ n'est sélectionné et avec les bouton suivant et précédent.
Vous pouvez appuyez sur le bouton SAVE ou sur entrée pour sauvegardé. Le fichier sera alors renommé avec le nom dans le champ tout en haut et déplacer dans le bon dossier.
Vous pouvez appuyez sur SKIP pour déplacer le documents dans un dossier spécial (dans le cas où vous ne savez pas comment le renommer)
Vous pouvez également appuyez sur RETURN pour revenir en arrière et récupérer le dernier fichier, le logiciel mettre quelques secondes avant de l'analyser.

## Configuration

Le raccourci "Auto Filter Configuration" sur votre bureau amène dans un fichier avec des fichier de configuration.
Le fichier path.py définit l'emplacement des éléments : le dossier où sont stocker les fichiers à scanner, le dossier où est installer tesseract, le dossier où placer les fichier lorsqu'on appuie sur skip et le dossier ou placer les fichier lorsqu'ils sont trier. Par défaut ces 2 derniers sont dans files/unreadable et files/filtered
Le fichier text.py définit les caractères à supprimer et à remplacer lors de la lecture automatique des documents.
Le fichier window.py définit la taille de la fenêtre, la résolution des documents scanné (par défaut 300 dpi sur une imprimante), le nombre d'image par seconde et le nombre de fichier à lire en avance


## Erreurs

En cas d'erreur que vous n'arrivez pas à résoudre contacter le service informatique et en dernier recours :

fagot.nicolas.45@gmail.com


# How to code

## Python (pip)

Use proxy proxy_amer.safran:9009
```terminal
pip install <library> --proxy proxy_amer.safran:9009
```
Or the bat script with space between libraries if you want to install multiple libraries

You can also use this :
```terminal
pip install <library>  --proxy=http://11.56.30.169:3142 --trusted-host pypi.org --trusted-host files.pythonhost
```

## Git

Use proxy proxy_emea.safran:8080
```terminal
git config --global http.proxy proxy_emea.safran:8080
```


