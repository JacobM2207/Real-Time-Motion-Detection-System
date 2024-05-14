# Real-Time-Motion-Detection-System

Using the ESP32 Feather board and the Adafruit MPU-6050 sensor board, a Real-Time Motion Detection System was created. This system was integrated with the ThingSpeak IoT platform and IFTTT service (If-This-Then-That), so the system can be armed using Google Assistant and notifications of motion can be sent to your smartphone. 

# Overview

The system is put in an Armed state via Google Assistant voice commands, and the ESP32 will start detecting motion using the accelerometer sensor. As soon as any motion is detected, the system sends an IFTTT notification to your phone (on the IFTTT app), thereby alerting you of any motion. The system is also put in the disarmed stat via Google Assistant voice commands where no notification will be sent to your device. Below is the high-level overview of the system:

![image](https://github.com/JacobM2207/Real-Time-Motion-Detection-System/assets/122327307/8a61ffdc-e264-42e9-b3a1-8a43306dbc60)
