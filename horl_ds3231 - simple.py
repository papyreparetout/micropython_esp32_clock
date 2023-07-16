"""
Test module DS3231 pour réaliser une horloge
sur la base de la library micropython:
https://github.com/pangopi/micropython-DS3231-AT24C32

"""
# import machine
from machine import Pin, SoftI2C, RTC
from ds3231 import DS3231
from time import *

i2c = SoftI2C(sda=Pin(21), scl=Pin(22))
# Lookup table for names of days (nicer printing).

days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
tabmois = ["jan","fev","mar","avr","mai","jun","jul","aou","sep","oct","nov","dec"]
ds = DS3231(i2c)
# Simple demo of reading and writing the time for the DS3231 real-time clock.
rtc = RTC()
#
# pour mise à l'heure initiale du DS3231
#

if False:  # change to True if you want to set the time!
    #                     year, mon, date, hour, min, sec, wday, yday, isdst
    t = (2023, 7, 15, 21, 47, 30, 5, 2, 0)
    # you must set year, mon, date, hour, min, sec and weekday
    # yearday is not supported, isdst can be set but we don't do anything with it at this time
    print("Setting time to:", t)  # uncomment for debugging
    ds.datetime(t)
    rtc.datetime(ds.datetime())
    print()

# Main loop: affichage du jour et de l'heure

while True:
#    t = rtc.datetime()
#    (year, month, day, weekday, hours, minutes, seconds, subseconds) = rtc.datetime()
    (year, month, day, weekday, hours, minutes, seconds, subseconds) = ds.datetime()
#    print(t)     # uncomment for debugging
    print("The date is {} {}/{}/{}".format(days[int(weekday)],day, month, year))
    print("The time is {}:{:02}:{:02}".format(hours, minutes, seconds))

    sleep_ms(1000)  # wait a second