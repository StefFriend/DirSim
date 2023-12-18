(
OSCdef(\tapTempoBPM, { |msg|
    var currentTime, timeDiff, tappedBPM;
	var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port
    currentTime = SystemClock.seconds;



    // Initialize lastBPMChangeTime and lastTapTime if they are nil
    if (~lastBPMChangeTime.isNil) { ~lastBPMChangeTime = 0; };
    if (~lastTapTime.isNil) { ~lastTapTime = 0; };

    // Calculate the time difference in seconds
    timeDiff = currentTime - ~lastTapTime;

    // Check if time difference is less than or equal to two seconds
    if (timeDiff <= 2) {
        // Convert time difference to BPM
        tappedBPM = 60 / timeDiff;

        // Ensure BPM is not changed more than once every 2 seconds
        if (currentTime - ~lastBPMChangeTime > 2) {
            // Compare with the last BPM and adjust accordingly
            if (tappedBPM > ~lastBPM) {
                // If computed BPM is greater than actual, set to random BPM between 90 and 100
                tappedBPM = rrand(90.0, 100.0);
            };
            if (tappedBPM < ~lastBPM) {
                // If computed BPM is less than actual, set to random BPM between 80 and 90
                tappedBPM = rrand(80.0, 90.0);
            };

            "BPM: %".format(tappedBPM).postln;
            ~lastBPM = tappedBPM; // Update the last BPM value
            ~lastBPMChangeTime = currentTime; // Update the time of last BPM change

            // Send BPM via OSC
            oscTarget.sendMsg('/tempo/raw', tappedBPM);
        };
    };

    // Update the last tap time
    ~lastTapTime = currentTime;
}, '/tapTempo');







/*
// New OSCdef for receiving BPM values
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