#!/usr/bin/env python3

import hp9800 

acmeter_port = 'COM4'

 #####################################################################
 #                      Main programm
 #####################################################################
if __name__ == "__main__":
  acmeter_device = hp9800.acmeter(port = acmeter_port)
  
  # power_ac = round(acmeter_device.getPower(),1)
  power_ac = acmeter_device.getPower()
  print("Power consumtion: " + str(power_ac) + "W")

  power_ac = acmeter_device.getVoltage()
