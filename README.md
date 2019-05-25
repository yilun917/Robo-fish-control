# Robo-fish-control
This is an controlling program for our robotic fish, which includes read of RC signals and control of servos using Raspberry Pi.

The whole project is aimed at designing, manufracturing and testing a robotic fish used for underwater exploration with concealment. So 
that observation of marine creatures can be conducted without disturbance.

This github repository contains the controlling code for the controller of the robotic fish. One version is for the Arduino which uses C++.
The other version for Raspberry Pi uses Python.

# Supported Python Version
Python 3

# What you need
A Raspberry Pi or Arduino
A RC transmitter
A RC controller
Several servos
RPi.GPIO libraey instsalled on Raspberry Pi

# How to Use
The program is designed for Arduino/Raspberry Pi. A corresponding RC transmitter is need to connect to the controller on specified pin (written in code comments) to read in the signal. And then process through the controller to output signal to the servos. The connection between servo and controller is also included in the code comment.

# Issues
The raspberry pi does not support hardware PWM as I know. Thus, without external chips, the controlling of servo is very poor.

# License
The contents of this repository are covered under the MIT [Liscense](./LISCENSE).
