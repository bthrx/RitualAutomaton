# RitualAutomaton
An interactive python script to quickly set up an Emulated Android device for proxying traffic.
#Setup
1. Create a device with avdmanager, Android Studio, or Intelli J.
2. The API must be less than 34 (Android 14) and DOES NOT have the Play Store in order for this script to work.
3. ```git clone https://github.com/bthrx/RitualAutomaton```
4. ```cd RitualAutomaton```
5. ```python RitualAutomaton.py```
6. The interactive script will run if you enter no arguments.
7. Enter the name of the device you created with avdmanager.
8. When the emulated device launches, wait for the device to completely load and press enter again so it asks you the file path for your certificate.
9. Enter the path for your certificate.
10. The device is now ready to proxy traffic. Set up a listener on 127.0.0.1:8888 and set the proxy on the device to 127.0.0.1:8888. It uses adb reverse to tunnel the traffic.
11. ????
12. profit!!
