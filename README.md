# README #

Version : 1.0

## Utilisation

Il faut brancher chaque dalle sur un réseau local unique relié à un ordinateur par ethernet.

L’ordinateur contrôle les dalles et doit faire tourner le driver disponible sur ce dépôt : [LedWall Spout Driver](https://github.com/TelecomSoundAndMagic/ledwallspoutdriver)

Le sous-réseau doit avoir pour adresse `192.168.1.0/24`


## Fonctionnement

Chaque dalle démarre automatiquement sur le mode shownumber. Si la dalle est branchée au PC et que ce dernier exécute le driver, la dalle affiche directement la vidéo. Elles peuvent recevoir plusieurs commande :



*   shownumber : affiche le numéro de la dalle
*   showversion : affiche la version du logiciel
*   live : repasse en mode d’affichage vidéo
*   restart : redémarre le programme
*   reboot : redémarre la dalle entièrement
*   shutdown : éteint la dalle


## Développement

	Connexion SSH : `ssh ledwall@192.168.1.XX”`(avec XX = numéro de la dalle + 50 (ex : dalle 3 → 192.168.1.53)

* user/password : ledwall/ledwall

* password sudo : ledwall

**TODO :** 


1. ~~nettoyer le dépot git~~
2. ~~Permettre un reset et un reboot via commande udp~~← À tester
3. ~~Vider le buffer à chaque reconnexion pour gérer la connexion à chaud~~ ← À tester
4. ~~Afficher version de la dalle au démarrage~~← À tester
5. ~~Eviter le bug quand les fichier log n’existent pas encore~~← À tester
6. ~~réparer la mise à jour automatique~~  ← À tester
7. ~~Corriger la commandes “restart”~~
8. Faire une commande “update”
9. S’assurer que le numero de dalle transmis par le PC est dans la bonne plage 
10. Couper les plots de reset sur les orangePi
11. Revoir correction gamma
12. corriger les fichier de test (client) pour intégrer la syncro UDP
13. Supprimer l’ancien dossier ledwall

## Flasher une carte Mini SD pour le Mur de LED

### Flasher sans image disque :

* Installer armbian

* Cloner le nouveau dépot git 

* Créer le fichier .slab avec le numéro de la dalle

* Installer les dépendances de pillow : `sudo apt-get install libjpeg-dev`

* Installer pillow (en cas d’erreur, modifier la date locale : si elle n’est pas bonne le certificat SSL n’est pas accepté) :`sudo pip3 install pillow`

* Installer spidev : `sudo pip3 install spidev`

* Il faut donner à l'utilisateur l'accès aux ports SPI

* Cloner le dépôt Git à la racine ou copiez le dossier depuis un ordinateur avec `scp` dans `~/ledwallslab`

* Modifier le chemin de start.sh dans init.d/ledwall pour mettre celui contenu dans `~/ledwallslab`

### Flasher avec image disque :

(Disponible sur le drive, à dézipper avant: v1.0 numéro de dalle 10)

[Comment flasher et sauver une image disque (en anglais)](https://beebom.com/how-clone-raspberry-pi-sd-card-windows-linux-macos/)

Sur Ubuntu, utiliser le gestionnaire “Disques”



*   Si le numéro affiché par la commande shownumber est différent de celui de la dalle
   *   Se connecter en SSH à la dalle : `ssh ledwall@192.168.1.X`  avec X = numéro affiché par la commande shownumber + 50 (ex : numéro 3 → 192.168.1.53)
    *   Changer le numéro de la dalle dans le fichier .slab
    *   Changer l’adresse IP pour mettre celle correspondant à la dalle
        *   Modifier l’adresse IP dans le fichier `/etc/network/interfaces` en tant qu’administrateur
    *   Redémarrer ou éteindre la dalle avec `sudo reboot`

* Si la version n'est pas la bonne, effectuez un `git pull` ou copiez le dossier depuis un ordinateur avec `scp`

### Qui contacter ? ###

Vous pouvez contacter lemaire@eurecom.fr, jarasse@eurecom.fr,  pwolski@enst.fr ou romain.guilloteau@telecom-paris.fr.