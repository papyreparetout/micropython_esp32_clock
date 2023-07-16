"""

Horloge basée sur le module TTGO T-Display de LILYGO équipé d'un écran TFT  ST7789 et de 2 boutons
l'horloge est programmée en micropython.
Le driver de l'écran TFT est ici: https://penfold.owt.com/st7789py

les boutons du TTGO sont sur GPIO0 (bouton 1) et GPIO35 (bouton 2)

L'horloge tire sa référence d'un module DS3231
La gestion du DS3231 se fait via la library DS3231 trouvée ici:
https://github.com/pangopi/micropython-DS3231-AT24C32
Une heure d'alarme peut être définie (action limitée à un changement de couleur de fond de l'écran)
L'heure de référence étant en UTC le décalage entre l'heure UTC est l'heure locale peut être modifié

Toutes ces actions se font à l'aide des 2 boutons:
- bouton 1: changement de mode;
- bouton 2: modification des valeurs

"""
from machine import Pin, SoftSPI, RTC, SoftI2C
import st7789 as st7789
import vga1_16x16 as font1
import vga2_8x8 as font2
import utime
import network
# import ntptime
import sys
from ds3231 import DS3231
from time import *
"""
# Pour connexion ultérieure en tant que serveur
try:
    import usocket as socket # pour faire un web server
except:
    import socket
"""    
#
#  initialisation des variables
#

background = st7789.BLACK
backprec = st7789.BLACK
bout1 = True
bout2 = True
valeur = ""
textaffich = ''
#
#  connexion pour l'afficheur
#
spi = SoftSPI(
    baudrate=20000000,
    polarity=1,
    phase=0,
    sck=Pin(18),
    mosi=Pin(19),
    miso=Pin(13))

tft = st7789.ST7789(
    spi,
    135,
    240,
    reset=Pin(23, Pin.OUT),
    cs=Pin(5, Pin.OUT),
    dc=Pin(16, Pin.OUT),
    backlight=Pin(4, Pin.OUT),
    rotation=1)
#
i2c = SoftI2C(sda=Pin(21), scl=Pin(22))
#        
# declaration des boutons 
#
button1 = Pin(0, Pin.IN)
button2 = Pin(35, Pin.IN)
#
# sous programmes
#
def affiche(font, tft, col, lig ,textaffich, background):
    col_max = tft.width - font.WIDTH*6
    row_max = tft.height - font.HEIGHT
    tft.text(font,textaffich,col,lig,st7789.WHITE,background)

def wifi_connect(tft,box,password):
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    attempt = 4
    wlan.config(reconnects=attempt)
    if not wlan.isconnected():
        print('essai connection wifi...')
        wlan.connect(box, password)
        iessai = 0
        while not wlan.isconnected() and (iessai < attempt):
            iessai = iessai +1
            utime.sleep(2)
            pass
    if wlan.isconnected():
        print('réseau', wlan.ifconfig()[0])
        print(wlan.ifconfig()[0][-2:])
#        affiche(tft,100,100,wlan.ifconfig()[0][-2:], background)
        return wlan
    else:
        print (iessai)
        print("erreur connection réseau")
        affiche(font1,tft,20,40,"erreur connexion",background)

def disconnect(wlan):
    if wlan.active() == True:
        wlan.active(False)
        print("Déconnexion")
    if wlan.isconnected() == False:
        print("Disconnected")
        
def testbout(bouton1, bouton2):
    val = ""
    if bouton1:
        if not(button1.value()):
            bouton1 = False
            val = "1L"
    else:
        if button1.value():
            bouton1 = True
            val = "1H"
    if bouton2:
        if not(button2.value()):
            bouton2 = False
            val = "2L"
    else:
        if button2.value():
            bouton2 = True
            val = "2H"
    return val, bouton1, bouton2

def lancalarm(evala):
    tft.fill(st7789.RED)
    evala = False
    backg = st7789.RED
    return evala, backg

def afficheur(seconde,minute,heure,background):
# affichage heure, il faut completer si <10 pour eviter erreur affichage
    tabmois = ["jan","fev","mar","avr","mai","jun","jul","aou","sep","oct","nov","dec"]
    col1 =25
    col2 = 50
    lig1 = 30
    lig2 = 70
    affhorl = complz(heure) +" : "+ complz(minute) + " : "+ complz(seconde)
    affiche(font1,tft,col1, lig1, affhorl, background)
#    affichage jour
    affhor2 = complz(jour) +"   "+ tabmois[(mois-1)]
    affiche(font1,tft,col2, lig2, affhor2, background)
# affichage reseau pour eventuelle connexion
#    affiche(font2,tft,20,110,"sync_IP", background)
#    affiche(font2,tft,150,110,reseau.ifconfig()[0][-2:], background)
    return

def complz(chiffre):
    res =str(chiffre)
    if chiffre <= 9: res ="0"+res
    return res
#
# Programme principal
#
# initialisation reseau Wifi
#reseau = wifi_connect(tft,"Livebox-08B6","jrfeajroguin1978")
#utime.sleep(2) # pour attendre l'établissement de la connexion Wifi
# initialisation de l'horloge interne RTC
ds = DS3231(i2c)
rtc = RTC()
# decalage heure UTC _ heure locale
decalh = 0
# heure alarme par defaut
halarm = 0
malarm = 0
evalarm =False # par defaut pas d'alarme
misheur = True # pour synchro reguliere
finalarm = True
alarm = (0,0)
#
# initialisation etat
etat = 0

# boucle infinie

while True:
# debut et remise en synchro
    if etat == 0:
        # datetime: tuple (année, mois, jour, jourdesemaine, heure, minute, seconde, ssseconde
        # initialisation de l'horloge et de l'écran
#        (year, month, day, weekday, hours, minutes, seconds, subseconds) = rtc.datetime()
        rtc.datetime(ds.datetime())
        (year, month, day, weekday, hours, minutes, seconds, subseconds) = rtc.datetime()
        print ("UTC Time: ")
        print((year, month, day, hours, minutes, seconds))
        secondprec = seconds
# couleur de fond initiale (avant alarme)
        tft.fill(background)
        etat =1
# affichage heure
    if etat == 1:
    #    gestion des boutons
        valeur, bout1, bout2 = testbout(bout1, bout2)
#        if valeur != "": print(valeur)
        if valeur == "1H": # 1ere pression sur bouton 1 on bascule sur reglage alarme
            tft.fill(background)
            etat = 2
        else:
        # recuperation de l'heure UTC donnee par l'horloge interne de l'ESP   
            (heure,minute,seconde) = (rtc.datetime()[4],rtc.datetime()[5],rtc.datetime()[6])
            (mois, jour) = (rtc.datetime()[1],rtc.datetime()[2])
        # mise à l'heure locale par décalage par rapport à l'UTC
            heure = (heure + decalh)%24 #  modulo 24
        # affichage toutes les secondes uniquement
            if (seconde > secondprec) or (seconde == 0) : 
                secondprec = seconde
        # gestion alarme    
                if (heure, minute) == alarm :
                    if evalarm == True: # pour ne pas lancer le ssprog plusieurs fois
                        backprec = background
                        evalarm, background = lancalarm(evalarm)
                if ((heure, minute) == (alarm[0],alarm[1] +1)) and finalarm:
                    tft.fill(backprec) 
                    background = backprec
                    finalarm = False

        # synchronisation reguliere à minuit
                if (heure, minute) == (0,0) :
                    if misheur == True: # pour ne pas lancer le ssprog plusieurs fois
#                        ntptime.settime() # initialisation horloge interne
                        rtc.datetime(ds.datetime())
                        print("synchronisation journalière")
                        misheur = False
                if (heure, minute) == (0,1) : # pour relancer la synchro le jour suivant
                    misheur = True

        # affichage heure
                afficheur(seconde,minute,heure,background)
                
    elif etat == 2: # alarme ou non
        affiche(font1,tft,20,40,"    Alarme", background)
        affiche(font1,tft,40,70,str(evalarm), background)
        valeur, bout1, bout2 = testbout(bout1, bout2)
#            if valeur != "": print(valeur)
        if valeur == "1H": # suite, soit heure alarme, soit decalage
            tft.fill(background)
            if evalarm:
                etat = 3
            else: etat = 5
        elif valeur == "2H":
            tft.fill(background)
            evalarm = not(evalarm)
            print("choix alarme: "+str(evalarm))
                

    elif etat == 3: # reglage minute alarme
        affiche(font1,tft,20,40,"    Alarme", background)
        affiche(font1,tft,40,70,complz(halarm) +" : "+complz(malarm), background)
        valeur, bout1, bout2 = testbout(bout1, bout2)
#            if valeur != "": print(valeur)
        if valeur == "1H": # heure alarme
            tft.fill(background)
            etat = 4
        elif valeur == "2H":
            malarm = (malarm +5)%60
            print("minute alarme: "+str(malarm))
                
    elif etat == 4: # reglage heure alarme
        affiche(font1,tft,20,40,"    Alarme", background)
        affiche(font1,tft,40,70,complz(halarm) +" : "+complz(malarm), background)
        valeur, bout1, bout2 = testbout(bout1, bout2)
#            if valeur != "": print(valeur)
        if valeur == "1H": # decalage
            alarm = (halarm, malarm)
            tft.fill(background)
            etat = 5
        elif valeur == "2H":
            halarm = (halarm +1)%24
            print("heure alarme: "+str(halarm))
                
    elif etat == 5:
#        reglage decalage par appui sur bouton 1: +1 heure à chaque fois
        affiche(font1,tft,20,40,"Reglage UTC", background)
        affiche(font1,tft,40,70,complz(decalh), background)
    # recuperation de l'heure UTC donnee par l'horloge interne de l'ESP
    # pour ne pas etre bloqué en revenant à l'affichage de l'heure courante
        (heure,minute,seconde) = (rtc.datetime()[4],rtc.datetime()[5],rtc.datetime()[6])
        secondprec = seconde
        valeur, bout1, bout2 = testbout(bout1, bout2)
#            if valeur != "": print(valeur)
        if valeur == "1H": # affichage heure
            tft.fill(background)
            etat = 1
        elif valeur == "2H":
            decalh = (decalh +1)%24
            print("décalage: "+str(decalh))


# deconnexion du reseau wifi    
disconnect(reseau)
sys.exit("fin")

    
