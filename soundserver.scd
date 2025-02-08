// Boot the server
s.boot;

// Boot the server if not already booted
s.waitForBoot({

    // Define a simple Synth (a sine wave with frequency and amplitude controls)
    SynthDef(\exampleSynth, {
        |freq = 440, amp = 0.5|
        var sig;
        sig = SinOsc.ar(freq) * amp;
        Out.ar(0, sig);
    }).add;

    // Create an OSC listener that listens for messages from Flask
    OSCdef(\triggerSynth, { |msg|
        var freq, amp;
        freq = msg[1];  // Get frequency from OSC message
        amp = msg[2];   // Get amplitude from OSC message

        // Play the sound with received parameters
        Synth(\exampleSynth, [\freq, freq, \amp, amp]);

        // Print the received message in the Post window
        ("Received OSC message: " + msg).postln;
    }, '/triggerSynth');  // Listen for messages on this OSC address

    "SuperCollider is ready to receive OSC messages!".postln;
});
