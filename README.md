# padsys.py
Python-based implementation of Padsys by Electronics (https://github.com/electronics/padsys).

Padsys allows you to control Chamsys MagicQ Exec Pages over OSC using Novation Launchpads.
The current implementation was tested with two Launchpad MK2's (RGB), but theoretically even first generation launchpads, and launchpad mini's should work.
Currently, Launchpad Pro's don't work because they have lots of extra buttons. This may be updated in a future release.

## Getting Started

The first step is to create a 10x10 exec page in MagicQ. This can be on any page number, just note down which exec page it's on.

This 10x10 dimension includes the launchpad and a border at the left and top edges for adding groups and other non-launchpad-controlled items.

Make sure that OSC control is enabled (set to Tx and Rx) in MagicQ Setup under Network.

The next step is to install the requirements for padsys.py. Do this by running `pip3 install -r requirements.txt`, which will collect all the packages.

Then, connect a launchpad to your PC and run PadSys.py with the following arguments:

```
padsys.py -n 1 -e <EXEC_PAGE_NO> 
```

Now, assuming you have some blue hardware connected which unlocks OSC control, you should be able to push buttons on your Launchpad which control Chamsys, and active exec page items should mirror back to the launchpad with feedback.

In order to set colours of buttons, press `Record arm`, `Volume`, `User 2` and `Mixer` at the same time. This puts the launchpad into "edit" mode.

Cycle through colours with `User 2` and paint them onto the launchpad where you want them. Press `Mixer` when done to save.

The pad layout saves to a `json` file which is loaded if present at next startup so you don't have to re-make your layout every time.

## Multiple Launchpads

To use multiple launchpads, simply connect as many as you need to your system.

The `-n` flag states how many launchpads you have connected.

In its default mode, this will make launchpad 1 control the exec page passed by `-e`, launchpad 2 control (`-e + 1`), launchpad 3 control (`-e + 2`), etc.

The `-c` flag combines launchpads together in a horizontal row, so if you have two and pass `-c`, they will control a 20x10 exec page.

## Ports

At the moment, Padsys.py allows you to change the Chamsys OSC port for information sent to Chamsys, (referred to in setup as "OSC rx port"), but has a static listening port for feedback from Chamsys on Port 9000. This may be updated in future versions.

## Full Usage:

```
usage: padsys.py [-h] [-n PADS] [-e EXEC] [-c] [--host HOST] [--port PORT]
                 [-v]

PadSys.py: Use Novation Launchpads to control Chamsys MagicQ over OSC

optional arguments:
  -h, --help            show this help message and exit
  -n PADS, --pads PADS  Number of Launchpads (default: 1)
  -e EXEC, --exec EXEC  ChamSys Exec Page (default: 3), increments by pad
                        number by default, e.g. first LaunchPad maps to page3,
                        second LaunchPad to page4 etc.
  -c, --combine         Combine multiple pads onto same exec page (e.g. 2 pads
                        map to a 20x10 page)
  --host HOST           OSC Hostname (default: 127.0.0.1)
  --port PORT           OSC Port (default: 8000)
  -v, --verbose         Verbose logging
```

