toutv-fs
========

Le problème
-----------
Je possède un lecteur de médias [WDTV Live](http://wdc.com/en/products/products.aspx?id=330) qui répond assez bien à mes besoins. Toutefois, comme il n'a pas vraiment été conçu avec une mentalité _open_, ses fonctionnalitées ne peuvent pas être étendues à l'aide de plugins. J'aimerais énormément pouvoir consulter et visionner des émissions sur Tou.TV directement sur ma télévision avec ce gadget. Évidemment, on peut consulter un paquets de services américains, mais il n'y a rien pour Tou.TV.

La solution
-----------
La solution saute aux yeux: créer un système de fichier FUSE offrant une vue sur le contenu de Tou.TV et le monter via NFS (ou CIFS). une émission ou une série correspond à un dossier dans la racine et un épisode correspond à un fichier dans le dossier correspndant à l'émission. La lecture d'un fichier est implémentée en _streamant_ celui-ci en temps réel.

Je me base sur la [librairie python pour Tou.TV](https://github.com/bvanheu/Tou.tv-console-application) écrite par Benjamin Vanheuverzwijn.

État du projet
--------------
Preuve de concept. Le _layout_ du système de fichier est présent ([output de la commande _tree_](http://paste.ubuntu.com/1444583/)). Avec quelques configurations (HowTo à venir), il est possible de naviguer dans les fichiers à partir du WDTV.
