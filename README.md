# padsys.py
Python-based implementation of Padsys by Electronics (https://github.com/electronics/padsys)

## Usage:

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

