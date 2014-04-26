#!/usr/bin/python

from Adafruit_PWM_Servo_Driver import PWM
import time

# ===========================================================================
# Initialise Servo Controller
# ===========================================================================

# Initialise the PWM device using the default address
# bmp = PWM(0x40, debug=True)
pwm = PWM(0x40, debug=True)

def setServoPulse(channel, pulse):
  pulseLength = 1000000                   # 1,000,000 us per second
  pulseLength /= 60                       # 60 Hz
  print "%d us per period" % pulseLength
  pulseLength /= 4096                     # 12 bits of resolution
  print "%d us per bit" % pulseLength
  pulse *= 1000
  pulse /= pulseLength
  pwm.setPWM(channel, 0, pulse)

pwm.setPWMFreq(60)                        # Set frequency to 60 Hz

# ===========================================================================
# Servo Controls
# ===========================================================================

import json

with open ("servo_config.json", "r") as json_file:
	servo_config = json.load( json_file )

def write_config():
	with open ("servo_config.json", "w") as json_file:
        	json_file.write( json.dumps( servo_config ) )

def get_servo_config(port):
	if (servo_config['min'][port]):
		return {"status":"ok","min":servo_config['min'][port],"max":servo_config['max'][port]}
	else:		
		return {"status":"error","message":"notfound"}

def set_servo_start(port, start):
        if (servo_config['start'][port]):
                servo_config['start'][port] = start
		write_config()
		return {"status":"ok"}
	else:
		return {"error":"notfound"}

def set_servo_min(port, min):
        if (servo_config['min'][port]):
                servo_config['min'][port] = min
		write_config()
		return {"status":"ok"}
	else:
		return {"error":"notfound"}

def set_servo_max(port, max):
        if (servo_config['max'][port]):
                servo_config['max'][port] = max
		write_config()
		return {"status":"ok"}
	else:
		return {"status":"error","message":"notfound"}

def set_servo_position(port, percentage):
	if percentage > 100:
		percentage = 100
	elif percentage < 0:
		percentage = 0

        if servo_config['min'][port]:
		print "-------------------"                
		print "port:"+str(port)
		print "percentage:"+str(percentage)
		position = int((servo_config['max'][port] - servo_config['min'][port]) * percentage ) + servo_config['min'][port]
		print "position:"+str(position)
		pwm.setPWM( port, 1, position )
		return {"status":"ok"}
	else:
		return {"status":"error","message":"notfound"}

# ===========================================================================
# Initialise Socket Server
# Gratefully copied from http://www.binarytides.com/python-socket-server-code-example/
# ===========================================================================

import socket
import re
import sys
from base64 import b64encode
from hashlib import sha1
from thread import *

HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8888 # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
print 'Socket created'
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bound'
 
#Start listening on socket
s.listen(1)
print 'Socket listening'

def handshake (client):
	print 'Handshaking...'
	text = client.recv(1024)

	websocket_answer = (
	    'HTTP/1.1 101 Switching Protocols',
	    'Upgrade: websocket',
	    'Connection: Upgrade',
	    'Sec-WebSocket-Accept: {key}\r\n\r\n',
	)

	GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"

	key = (re.search('Sec-WebSocket-Key:\s+(.*?)[\n\r]+', text)
		.groups()[0]
		.strip())

	#print "--/--" + key + "--/--"

	shake_key = b64encode(sha1(key + GUID).digest())
	shake = '\r\n'.join(websocket_answer).format(key=shake_key)

	return client.send(shake)


#Function for handling connections. This will be used to create threads
def clientthread(conn):
    #Sending message to connected client
    #conn.send('{"servoMin":'+servoMin+',"servoMax":'+servoMax+'}\n') #send only takes string
    	
	handshake(conn)
	print "Sending hello"

	conn.send('Howdie!') #send only takes string
	     
    #infinite loop so that function do not terminate and thread do not end.
	while True:
         
        	#Receiving from client
        	data = conn.recv(1024)
		
		print "Got something from client..."
		print "--:"+data
		
		conn.send('Thank you - thinking')

		if data[0:4] == "exit":
			conn.sendall('bye')
			break
	
		else:
			try: 
				json_data = json.loads( data )	
	
				if json_data['do'] == 'position':
					reply = set_servo_position(int(json_data['port']), float(json_data['percentage']))

				elif json_data['do'] == 'get_config':
					reply = get_servo_config(int(json_data['port']))

				elif json_data['do'] == 'set_max':
					reply = set_servo_max(int(json_data['port']), int(json_data['value']))

				elif json_data['do'] == 'set_min':
					reply = set_servo_min(int(json_data['port']), int(json_data['value']))

				elif json_data['do'] == 'set_start':
					reply = set_servo_start(int(json_data['port']), int(json_data['value']))
			
				else:
					reply = {"error":"eh?"}

	        		conn.sendall(json.dumps(reply))			

			except ValueError: 			
				reply = {"error":"invalid-request"}
         			conn.sendall(json.dumps(reply))

			except KeyError: 			
				reply = {"error":"missing-something-important"}
         			conn.sendall(json.dumps(reply))

	#came out of loop
	conn.close()
 
#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
    conn, addr = s.accept()
    print 'Connected with ' + addr[0] + ':' + str(addr[1])
     
    #start new thread takes 1st argument as a function name to be run, second is the tuple of arguments to the function.
    start_new_thread(clientthread ,(conn,))
 
s.close()

