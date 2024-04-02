from machine import Pin, ADC, RTC
import time

rtc = RTC()     # init on-board RTC
rtc.datetime((2024, 4, 2, 1, 0, 0, 0, 0)) # set a specific date and time for the RTC (year, month, day, weekday, hours, minutes, seconds, subseconds)
print(rtc.datetime())

message = "hello world2"
message = message.strip()  # Remove leading and trailing whitespaces
with open("log2.txt", "a") as file:
    timestamp = rtc.datetime()		# Timeregistration
    timestring = "%04d-%02d-%02d %02d:%02d:%02d.%03d" % timestamp[:7] 
    file.write(timestring + "," + message + "\n")		# Write time and message to the file
    file.flush()  # Write the data immediately to the file
        
        
