This Raspberry Pi (RPi) hosted sprinkler controllerp uses the 
Waveshare Expansion Board 8 Channel Relay Expansion Board.

The sprinkler runs within a server running on the RPi.  The server supports multiple,
simultaneous, clients.

The following package needs to be installed on the RPi: YAML.

The following packages needs to be installed on the machine running the client: Kivy

Users control the sprinkler by connecting to the server with either the supplied a command
line client or the supplied GUI.

Connections require that the RPi is connected to wireless LAN.	Connections can be made
either directly over the LAN or over the inernet.

The GUI is implemented using the python Kivy package and, as such, can run on a PC, Mac, 
or Android phone.

Users can create their own styles watering schedules.  Schedule creation uses 
the YAML package.

Some of the sprinkler's code is common with another, second, project.  To prevent having to 
copy/paste changes/bug-fixes back and forth between projects, this common code resides 
in a third project. Copy the shared code into the root directory of this project.

The common code can be found here:
https://github.com/sgarrow/sharedClientServerCode

More information (including parts list, wiring diagrams, configuration and operation 
instructions) can be found in the docs folder.	Note that the links within the 
documentation don't seem to work when viewed within GitHub but they do work if the 
doc is downloaded to the local machine.
