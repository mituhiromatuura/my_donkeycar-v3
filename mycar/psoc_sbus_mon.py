import struct

ch3 = 0
ch4 = 0
ch5 = 0
ch6 = 0
ch7 = 0

ch9 = 0
ch10 = 0
ch11 = 0
ch12 = 0

ch13 = 0
ch14 = 0
ch15 = 0
ch16 = 0

uart = open("/dev/hidPsoc",'rb')
while True:
	d = uart.read(16)
	d0, d1, d2, L, H, d4, d5, d6, d7 = struct.unpack('HHHBBHHHH', d)
	if H == 3:
		ch3 = L - 100
	elif H == 4:
		ch4 = L - 100
	elif H == 5:
		ch5 = L - 100
	elif H == 6:
		ch6 = L - 100
	elif H == 7:
		ch7 = L - 100
	elif H == 7+1:
		ch9 = L - 100
	elif H == 7+2:
		ch10 = L - 100
	elif H == 7+3:
		ch11 = L - 100
	elif H == 7+4:
		ch12 = L - 100
	elif H == 7+5:
		ch13 = L - 100
	elif H == 7+6:
		ch14 = L - 100
	elif H == 7+7:
		ch15 = L - 100
	elif H == 7+8:
		ch16 = L - 100

	print(d0,d1,d2,ch3,ch4,ch5,ch6,ch7,ch9,ch10,ch11,ch12,ch13,ch14,ch15,ch16)
