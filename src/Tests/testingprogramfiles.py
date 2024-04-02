import machine
import utime

# RTC initialisatie en instellen op 1 januari 2024
rtc = machine.RTC()
rtc.datetime((2024, 1, 1, 0, 0, 0, 0, 0))

# Potentiometer initialisatie
potentiometer = machine.ADC(machine.Pin(27))

# Openen van het bestand "log.txt" om te schrijven
with open("log.txt", "w") as file:
    while True:
        # Timeregistration
        timestamp = rtc.datetime()
        timestring = "%04d-%02d-%02d %02d:%02d:%02d" % timestamp[:6]

        # Lees de waarde van de potentiometer
        pot_value = potentiometer.read_u16()
        
        # Data om te loggen
        LogData = pot_value
        
        # Schrijven van tijd en data naar bestand
        file.write(timestring + "," + str(LogData) + "\n")
        file.flush()  # Schrijf de gegevens onmiddellijk naar het bestand
        
        # Wacht voor een bepaalde tijd voordat de volgende meting wordt uitgevoerd
        utime.sleep(1)  # Bijvoorbeeld elke seconde
