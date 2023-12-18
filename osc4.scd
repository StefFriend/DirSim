(
OSCdef(\tapTempoBPM, { |msg|
    var currentTime = SystemClock.seconds;
    var timeDiff, tappedBPM;
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port

    // Check if this is not the first tap
    if (~lastTapTime.notNil) {
        // Calculate the time difference in seconds
        timeDiff = currentTime - ~lastTapTime;

        // Check if time difference is less than or equal to two seconds
        if (timeDiff <= 2) {
            // Convert time difference to BPM and round it
            //tappedBPM = (60 / timeDiff).round.asInteger;
			tappedBPM = (60 / timeDiff);
            "BPM: %".format(tappedBPM).postln;
            ~lastBPM = tappedBPM; // Update the last BPM value

            // Send BPM via OSC
            oscTarget.sendMsg('/tempo/raw', tappedBPM);

			/*
            // Adjust playback rate
            if (~currentSynth.notNil) {
                ~currentSynth.set(\rate, ~lastBPM / ~originalBPM);
            };
			*/
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



// New OSCdef for handling /track1 messages
OSCdef(\forwardTrack1, { |msg|
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port

    "Forwarding /track1 message".postln;
    oscTarget.sendMsg(*msg); // Forward the entire message as received
}, '/track1');


// New OSCdef for handling /track2 messages
OSCdef(\forwardTrack2, { |msg|
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port

    "Forwarding /track2 message".postln;
    oscTarget.sendMsg(*msg); // Forward the entire message as received
}, '/track2');

// New OSCdef for handling /track3 messages
OSCdef(\forwardTrack3, { |msg|
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port

    "Forwarding /track3 message".postln;
    oscTarget.sendMsg(*msg); // Forward the entire message as received
}, '/track3');

// New OSCdef for handling /pauseNext messages
OSCdef(\pauseNext, { |msg|
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port

    "Forwarding /pauseNext message".postln;
    oscTarget.sendMsg(*msg); // Forward the entire message as received
}, '/pauseNext');

// New OSCdef for handling /volume1 messages
OSCdef(\volume1, { |msg|
    var oscTarget = NetAddr("localhost", 57121); // Set the target IP and port

    "Forwarding /volume1 message".postln;
    oscTarget.sendMsg(*msg); // Forward the entire message as received
}, '/volume1');
)