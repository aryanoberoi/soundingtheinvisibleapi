// Boot the server
s.boot;

// Boot the server if not already booted
s.waitForBoot({

	~sampleDir = thisProcess.nowExecutingPath.dirname +/+ "RevisedFrequencies_March282025";
    ~pollutants = PathName.new(~sampleDir).entries.do({
      arg path;
      ~pollutantSounds = ~pollutantSounds.add(Buffer.read(s, path.fullPath););
    });

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

	{

		 SynthDef(\bpfbuf, {
            arg buf = 0, rate = 1, gate = 1, atk = 0.01, sus = 1, rel = 1, amp = 0.5, out = 0, startPos, lpff = 20, lpfm = 0;
            var env, sig, filt;
            env = EnvGen.kr(Env.asr(atk, sus, rel), gate, doneAction: Done.freeSelf); // ASR envelope with gate control
            sig = PlayBuf.ar(2, buf, rate * BufRateScale.ir(buf), startPos: startPos, doneAction: Done.freeSelf);
            sig = LPF.ar(sig, XLine.kr(lpff,4000,20));
            sig = sig * env * ampq;
            Out.ar(out, sig); // Stereo output
        }).add;

        0.5.wait; // Wait so that samples are all loaded up and synthdefs are ready to be played

		OSCdef.new(\pad1, {
			arg msg;
			case { msg[1] == 1} { Synth("bpfbuf", [\buf, ~pollutantSounds.at(0)]); }
		}, '/2/push1', nil, 57120);
		OSCdef.new(\pad2, {
			arg msg;
			case { msg[1] == 1} { Synth("bpfbuf", [\buf, ~pollutantSounds.at(1)]); }
		}, '/2/push2', nil, 57120);
		OSCdef.new(\pad3, {
			arg msg;
			case { msg[1] == 1} { Synth("bpfbuf", [\buf, ~pollutantSounds.at(2)]); }
		}, '/2/push3', nil, 57120);
		OSCdef.new(\pad4, {
			arg msg;
			case { msg[1] == 1} { Synth("bpfbuf", [\buf, ~pollutantSounds.at(3)]); }
		}, '/2/push4', nil, 57120);
		OSCdef.new(\pad5, {
			arg msg;
			case { msg[1] == 1} { Synth("bpfbuf", [\buf, ~pollutantSounds.at(4)]); }
		}, '/2/push5', nil, 57120);
		OSCdef.new(\pad6, {
			arg msg;
			case { msg[1] == 1} { Synth("bpfbuf", [\buf, ~pollutantSounds.at(5)]); }
		}, '/2/push6', nil, 57120);
		OSCdef.new(\pad7, {
			arg msg;
			case { msg[1] == 1} { Synth("bpfbuf", [\buf, ~pollutantSounds.at(6)]); }
		}, '/2/push7', nil, 57120);
		OSCdef.new(\pad8, {
			arg msg;
			case { msg[1] == 1} { Synth("bpfbuf", [\buf, ~pollutantSounds.at(7)]); }
		}, '/2/push8', nil, 57120);
		OSCdef.new(\pad9, {
			arg msg;
			case { msg[1] == 1} { Synth("bpfbuf", [\buf, ~pollutantSounds.at(8)]); }
		}, '/2/push9', nil, 57120);
		OSCdef.new(\pad10, {
			arg msg;
			case { msg[1] == 1} { Synth("bpfbuf", [\buf, ~pollutantSounds.at(9)]); }
		}, '/2/push10', nil, 57120);
		OSCdef.new(\pad10, {
			arg msg;
			case { msg[1] == 1} { Synth("bpfbuf", [\buf, ~pollutantSounds.at(9)]); }
		}, '/2/push10', nil, 57120);
    }.fork;
    "SuperCollider is ready to receive OSC messages!".postln;
});
