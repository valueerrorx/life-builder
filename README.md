# life-builder
This apptlication is based on "remastersys" and creates an ISO file from the running system.
The GUI is written in Python and QT.
The Bash Script can also be used without GUI.

It allows to include the complete user configuration (backup mode) in the live system and use the live system as installer device.
The finalised ISO Image can be tested directly in KVM or "burned" to a USB device.
life-usbcreator is included in this application.

Tested with Kubuntu 20.04 (but should work with most Ubuntu derivates).

HowTo run this application:

```python3 main.py```



Python Dependencies:
pyqt5
ipaddress


#
The application also removes private information like ssh keys, password store files, browserhistory, bashhistory, klipper contents, recent documents and unused kernels and packages...

![Image of life-builder](http://life-edu.eu/images/life-builder1.png)
![Image of life-builder](http://life-edu.eu/images/life-builder3.png)
![Image of life-builder](http://life-edu.eu/images/life-usbcreator.png)

