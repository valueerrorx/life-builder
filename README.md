# life-builder

LiFE-Builder is an Subapplication for the LiFE KDE System http://www.life-edu.eu/. 
It relies on https://launchpad.net/ubuntu/+source/casper and therefore will NOT work on Linux Systems other than **ubuntu* derivates





This application is based on **remastersys** and creates an ISO file from the running system.
The GUI is written in Python and QT.

It allows to include the complete user configuration (backup mode) in the live system and use the live system as installer device.
The finalised ISO Image can be tested directly in KVM or "burned" to a USB device.
LiFE-Usbcreator is included in this application.

*Tested with Kubuntu 20.04*

### HowTo run this application:

```python3 main.py```

The Bash Script ```lifebuilder``` can be used independently.(in that case you need to manually edit the config file)

### Python Dependencies:
pyqt5
ipaddress


#
The application also removes private information like ssh keys, password store files, browserhistory, bashhistory, klipper contents, recent documents and unused kernels and packages...

![Image of life-builder](http://life-edu.eu/images/life-builder1.png)
![Image of life-builder](http://life-edu.eu/images/life-builder3.png)
![Image of life-builder](http://life-edu.eu/images/life-usbcreator.png)

