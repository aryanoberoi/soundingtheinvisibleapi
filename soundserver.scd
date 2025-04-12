// Boot the server
s.boot;

// Boot the server if not already booted
s.waitForBoot({
	// Uncomment the next line to use sounds from the folder name specified in quotes
	// Folder must exist in the same level as this supercollider patch
	~sampleDir = thisProcess.nowExecutingPath.dirname +/+ "RevisedFrequencies_March282025";
	// Uncomment the next line to use sounds from the default pollutant folder on RasPi
	//~sampleDir = "/home/nandi/Documents/Pollutants";

	~pollutantGroup = Group.new;
	// These are some groups that will be used to divide sounds between different tanks
	~tank1Group = Group.new;
	~tank2Group = Group.new;
	~tank3Group = Group.new;

	{
		SynthDef(\bpfbuf, {
			arg buf = 0, rate = 1, gate = 1, atk = 0.01,
			sus = 1, rel = 1, amp = 0.5, out = 0,
			startPos, hpeqf = 20, lpeqf = 20000;
			var env, sig, filt;
			env = EnvGen.kr(Env.asr(atk, sus, rel), gate, doneAction: Done.freeSelf); // ASR envelope with gate control
			sig = PlayBuf.ar(2, buf, rate * BufRateScale.ir(buf), startPos: startPos, doneAction: Done.freeSelf);
			sig = BLowPass.ar(sig, lpeqf, 1); // Low pass eq
			sig = BHiPass.ar(sig, hpeqf, 1); // Hi pass eq
			sig = sig * env * amp;
			Out.ar(out, sig); // Stereo output
		}).add;

		0.5.wait;

		// Run through all the sounds in the directory
		~pollutants = PathName.new(~sampleDir).entries.do({
			arg path, i;
			var pad = "\pad" ++ i, addr = "/2/push" ++ (i+1);
			path.postln;
			// Add the current file as a buffer
			~pollutantSounds = ~pollutantSounds.add(Buffer.read(s, path.fullPath));
			// Add an OSC definition for the current sound
			OSCdef.new(pad.asSymbol, {
				arg msg;
				case { msg[1] == 1} {
					msg[0].postln;
					Synth("bpfbuf", [\buf, ~pollutantSounds.at(i)], ~pollutantGroup); }
			}, addr.asString, nil, 57120);
		});

		// Add an OSC definition to stop all sounds in the group
		OSCdef.new(\stopSounds, {
			arg msg;
			case { msg[1] == 1} {
				"Turn off sounds".postln;
				~pollutantGroup.freeAll;
			};
		}, '/2/push16', nil, 57120);
		OSCdef.new(\tank1Level, {
			arg msg;
			~tank1Group.set(\amp, msg[1]);
		}, '/1/fader1', nil, 57120);
		OSCdef.new(\tank2Level, {
			arg msg;
			~tank2Group.set(\amp, msg[1]);
		}, '/1/fader2', nil, 57120);
		OSCdef.new(\tank3Level, {
			arg msg;
			~tank3Group.set(\amp, msg[1]);
		}, '/1/fader3', nil, 57120);
	}.fork;
	"SuperCollider is ready to receive OSC messages!".postln;
});
