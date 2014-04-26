#!/usr/bin/python

# ===========================================================================
# Initialise Socket Server
# Gratefully copied from http://www.binarytides.com/python-socket-server-code-example/
# And http://picamera.readthedocs.org/en/release-0.8/recipes1.html#capturing-to-a-network-stream
# ===========================================================================

import socket
import io
import struct
import time
import picamera
import sys

HOST = ''   # Symbolic name meaning all available interfaces
PORT = 8889 # Arbitrary non-privileged port

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

print 'Video socket created'
 
#Bind socket to local host and port
try:
    s.bind((HOST, PORT))
except socket.error as msg:
    print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
     
print 'Socket bound'
 
#Start listening on socket
s.listen(10)
print 'Socket listening'

def send_video_stream (connection):
	with picamera.PiCamera() as camera:
	        camera.resolution = (320, 240)
	        # Start a preview and let the camera warm up for 2 seconds
        	camera.start_preview()
        	time.sleep(2)

        	# Note the start time and construct a stream to hold image data
        	# temporarily (we could write it directly to connection but in this
        	# case we want to find out the size of each capture first to keep
        	# our protocol simple)
        	start = time.time()
        	stream = io.BytesIO()
        	for foo in camera.capture_continuous(stream, 'jpeg'):
			# Write the length of the capture to the stream and flush to
            		# ensure it actually gets sent
            		#connection.write(struct.pack('<L', stream.tell()))
            		#connection.flush()
            		# Rewind the stream and send the image data over the wire
            		stream.seek(0)
        	    	connection.sendall(stream.read())
            		# If we've been capturing for more than 30 seconds, quit
	            	if time.time() - start > 30:
                		break
            	# Reset the stream for the next capture
            	stream.seek(0)
            	stream.truncate()
	# Write a length of zero to the stream to signal we're done
    	connection.write(struct.pack('<L', 0))


#now keep talking with the client
while 1:
    #wait to accept a connection - blocking call
	conn, addr = s.accept()
	print 'Connected with ' + addr[0] + ':' + str(addr[1])
	print 'Sending images...'

	send_video_stream(conn)


 
s.close()

