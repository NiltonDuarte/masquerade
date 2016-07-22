#!/root/wishful/dev/bin/python
# -*- coding: utf-8 -*-


from wishful_module_wifi_wmp import *



if __name__ == "__main__":
	wmpm = WmpModule()
	args = {'interface' : 'wlan0', UPI_R.CSMA_CW : 15, UPI_R.CSMA_CW_MIN : 15, UPI_R.CSMA_CW_MAX : 15}
	result = wmpm.setParameterLowerLayer(args)
	print(wmpm)
	print ("hello wmp")