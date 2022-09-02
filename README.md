# KFS-OTA
For doing OTA updates and storing key files

To prepare for update: Rename the latest version into "update.py" and upload into main folder.

In the program, set it to download the "update.py" file instead of "main.py". This is done so that in the event of connection problems, the main.py file won't be overwritten halfway and be corrupted.
