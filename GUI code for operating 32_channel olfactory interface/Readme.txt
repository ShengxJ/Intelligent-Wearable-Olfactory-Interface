# --------------------------------------------------------
# This is the GUI source code for wirelessly manipulating the wearable 32-channel olfactory interface
# --------------------------------------------------------

1. System requirements
- Python >= 3.10 installed with python modules: Matplotlib, Tkinter, Serial, Numpy

2. Installation guide
- All software is open-source and, therefore, can be downloaded and installed on personal computers through Python PIP install.


3. Demo and Instructions for use
- To run the GUI, real-time data, including three different parameters, time, temperature, and magnetic voltage output values, must be sent from the corresponding device. By handling the GUI, the command for adjusting OG operating factors can be adjusted, while once the heater is selected, the device automatically sends data in a specific data format (e.g. [time, temperature, magnetic power]). Then, the data is split based on the letter "[", ",", and "]" and saved in different list arrays for graphical display.
	
	3.1 Connect a device using USB-to-UART TTL for direct communication or USB dongle for BLE application to PC.
	3.2 Set up the proper comport line in the GUI source code by checking USB-to-UART TTL or USB dongle comport in your PC at the source code line 56: s = sr.Serial('COM5',115200).
	3.3 Run the software.
	3.4 Set up the heater.
	3.5 The corresponding heater data will be ploted automatically.

