(
OSCdef(\tapTempoBPM, { |msg|
    var currentTime = SystemClock.seconds;
    var timeDiff, tappedBPM;
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port
	// Initialize ~lastBPM if it is nil
    if (~lastBPM.isNil) { ~lastBPM = 90.0; }; // default value

    // Check if this is not the first tap
    if (~lastTapTime.notNil) {
        // Calculate the time difference in seconds
        timeDiff = currentTime - ~lastTapTime;

        // Check if time difference is less than or equal to two seconds
        if (timeDiff <= 2) {
            // Convert time difference to BPM
            tappedBPM = 60 / timeDiff;

            // Set BPM to a random value within a range based on whether it's greater or less than the last BPM
            if (tappedBPM > ~lastBPM) {
                // If new BPM is greater, set to random BPM between 90 and 100
                ~lastBPM = rrand(92.0, 100.0);
            } {
                // If new BPM is less, set to random BPM between 80 and 90
                ~lastBPM = rrand(80.0, 92.0);
            };

            "BPM: %".format(~lastBPM).postln;

            // Send BPM via OSC
            oscTarget.sendMsg('/tempo/raw', ~lastBPM);
        };
    };

    // Update the last tap time
    ~lastTapTime = currentTime;
}, '/tapTempo');











/*
//  OSCdef for receiving BPM values
OSCdef(\receiveBPM, { |msg|
    var receivedBPM = msg[1].asInteger; // Assuming BPM is sent as an integer in the second element of the message
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port

    "Received BPM: %".format(receivedBPM).postln;
    ~lastBPM = receivedBPM; // Update the last BPM value

    // Send BPM via OSC
    oscTarget.sendMsg('/tempo/raw', receivedBPM);

    // Adjust playback rate
    if (~currentSynth.notNil) {
        ~currentSynth.set(\rate, ~lastBPM / ~originalBPM);
    };
}, '/BPM');
*/


/*
OSCdef(\reaperTransport, { |msg, time, addr, recvPort|
    // msg is an array where the first element is the address pattern
    // and the second element is the value (0 or 1 in this case)
    if (msg[0].asString == "/play") {
        if (msg[1].asFloat == 1.0) {
            "Reaper is playing".postln;
        } {
            "Reaper is stopped".postln;
        };
    };
}, '/play'); // Adjust IP and port as needed
*/


//  OSCdef for handling /track1 messages
OSCdef(\forwardTrack1, { |msg|
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port

    "Forwarding /track1 message".postln;
    oscTarget.sendMsg(*msg); // Forward the entire message as received
}, '/track1');


//  OSCdef for handling /track2 messages
OSCdef(\forwardTrack2, { |msg|
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port

    "Forwarding /track2 message".postln;
    oscTarget.sendMsg(*msg); // Forward the entire message as received
}, '/track2');

//  OSCdef for handling /track3 messages
OSCdef(\forwardTrack3, { |msg|
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port

    "Forwarding /track3 message".postln;
    oscTarget.sendMsg(*msg); // Forward the entire message as received
}, '/track3');

//  OSCdef for handling /pauseNext messages
OSCdef(\pauseNext, { |msg|
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port

    "Forwarding /pauseNext message".postln;
    oscTarget.sendMsg(*msg); // Forward the entire message as received
}, '/pauseNext');

//  OSCdef for handling /play messages
OSCdef(\play, { |msg|
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port

    "Forwarding /play message".postln;
    oscTarget.sendMsg(*msg); // Forward the entire message as received
	oscTarget.sendMsg('/tempo/raw', 85);
}, '/play');

//  OSCdef for handling /stop messages
OSCdef(\stop, { |msg|
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port

    "Forwarding /stop message".postln;
    oscTarget.sendMsg(*msg); // Forward the entire message as received
}, '/stop');


//  OSCdef for handling /volume1 messages
OSCdef(\volume1, { |msg|
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port

    "Forwarding /volume1 message".postln;
    oscTarget.sendMsg(*msg); // Forward the entire message as received
}, '/volume1');
)