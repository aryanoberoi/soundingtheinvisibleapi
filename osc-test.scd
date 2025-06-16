(
	// n = NetAddr("localhost", 12345);
	n = NetAddr("MacBook-Pro-6.local", 12345);
	n = s.addr;
);

(
t = Task({
    loop {
        [1, 0].do({ |tog|
			tog.postln;
			n.sendMsg('/4/toggle4', tog);
            0.125.wait;
        });
    }
}).play;
);

// t.stop;
