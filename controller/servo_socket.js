var app = require('http').createServer(handler)
  , io = require('/usr/lib/node_modules/socket.io').listen(app)
  , fs = require('fs')

app.listen(80);

// Initialise server and send index file
// Initialise server and send index file
// Initialise server and send index file

function handler (req, res) {
	fs.readFile(__dirname + '/index.html',
	function (err, data) {
		if (err) {
			res.writeHead(500);
			return res.end('Error loading index.html');
    		}
    		res.writeHead(200);
    		res.end(data);
	});
}

// get servo_config
// get servo_config
// get servo_config

var servo_config;

fs.readFile(__dirname + '/servo_config.json', function (err, data) {
                if (err) {
                        res.writeHead(500);
                        return res.end('Error loading servo_config.json');
                }
		// save into json here???
                res.writeHead(200);
                res.end(data);
});

function write_config() {

	// save json back to file system


}


// Set up pwm
// Set up pwm
// Set up pwm

var PwmDriver, pwm, servoLoop, servoMax, servoMin, setHigh, setLow, setServoPulse, sleep;

PwmDriver = require('/usr/lib/node_modules/adafruit-i2c-pwm-driver');
pwm = new PwmDriver(0x40);

setServoPulse = function(channel, pulse) {
	var pulseLength;
	pulseLength = 1000000;
	pulseLength /= 60;
	print("%d us per period" % pulseLength);
	pulseLength /= 4096;
	print("%d us per bit" % pulseLength);
	pulse *= 1000;
	pulse /= pulseLength;
	return pwm.setPWM(channel, 0, pulse);
};

pwm.setPWMFreq(60);

io.sockets.on('connection', function (socket) {

	socket.of('/control').on('set_position', function (data) {
        
       		if (data['percentage'] > 1)
                	data['percentage'] = 1;
        	else if (data['percentage'] < 0)
                	data['percentage'] = 0;

        	if (servo_config['min'][ data['port'] ]) {
                	var position = ((servo_config['max'][ data['port'] ] - servo_config['min'][ data['port'] ]) * data['percentage'] ) + servo_config['min'][ data['port'] ]                	
			pwm.setPWM( data['port'], 0, position );
			socket.emit('success', {
				position: position
			});
        	} else {
			socket.emit('error', {
                                port: false
                        });
		}

        }).on('set_max', function (data) {

		if (servo_config['max'][ data['port'] ]) {
                	servo_config['max'][ data['port'] ] = data['max']
                	write_config();
                	
			socket.emit('success', {
                                max: data['max']
                        });

                } else {
                        socket.emit('error', {
                                max: false
                        });
		}
	}).on('set_min', function (data) {

                if (servo_config['min'][ data['port'] ]) {
                        servo_config['min'][ data['port'] ] = data['min']
                        write_config();

                        socket.emit('success', {
                                min: data['min']
                        });

                } else {
                        socket.emit('error', {
                                min: false
                        });
                }
        }).on('set_start', function (data) {

                if (servo_config['start'][ data['port'] ]) {
                        servo_config['start'][ data['port'] ] = data['start']
                        write_config();

                        socket.emit('success', {
                                start: data['start']
                        });

                } else {
                        socket.emit('error', {
                                start: false
                        });
                }
        }).on('get_config', function (data) {

                if (servo_config['max'][ data['port'] ]) {
                        
                        socket.emit('success', {
                                max: servo_config['max'][ data['port'] ],
                                min: servo_config['min'][ data['port'] ],
                                start: servo_config['start'][ data['port'] ]
			});

                } else {
                        socket.emit('error', {
                                port: false
                        });
                }
        });
});






// Clean up
// Clean up
// Clean up

process.on('SIGINT', function() {
	console.log("\nGracefully shutting down from SIGINT (Ctrl-C)");
	pwm.stop();
	return process.exit();
});

