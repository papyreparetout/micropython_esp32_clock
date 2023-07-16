# micropython_esp32_clock
Micropython TTGO T Display based clock

Horloge basée sur le module TTGO T-Display de LILYGO équipé d'un écran TFT  ST7789 et de 2 boutons
l'horloge est programmée en micropython.
Le driver de l'écran TFT est ici: https://penfold.owt.com/st7789py
les boutons du TTGO sont sur GPIO0 (bouton 1) et GPIO35 (bouton 2)
Une heure d'alarme peut être définie (action limitée à un changement de couleur de fond de l'écran)
Toutes ces actions se font à l'aide des 2 boutons:
- bouton 1: changement de mode;
- bouton 2: modification des valeurs

1  Version avec synchronisation via internet:

Gestion du temps tiré de:
https://www.engineersgarage.com/micropython-esp8266-esp32-rtc-utc-local-time/
L'horloge tire sa référence d'une connexion internet (synchronisation journalière)
L'heure de référence étant en UTC le décalage entre l'heure UTC et l'heure locale peut être modifié.

2  Version avec module DS3231 pour conserver la référence temporelle (synchronisation journalière):

Le module est relié via I2C à l'ESP et met à jour l'horloge interne de l'ESP
Le décalage entre l'heure conservée par le DS3231 et l'heure locale peut être modifié
