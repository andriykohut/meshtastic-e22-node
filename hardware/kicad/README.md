# KiCad schematic

Net-label style — every pin carries a label on its connection point instead of routed wires.
Written for the KiCad 6 file format; 7 and later will open it and offer to upgrade.

Symbols are plain rectangles from an embedded `meshnode` library that isn't installed anywhere,
so KiCad will flag them as not found and fall back to the cached definitions in the file. It
renders and nets fine; rescue or remap them if the warnings are annoying.

Pin numbers are the same strings as pin names, which keeps the netlist readable but isn't what
you want for board layout. Going to a PCB needs real footprints and numeric pin mapping — treat
this as documentation and a netlist source.

`netlist.txt` in the parent directory is the same connectivity as plain text. Export KiCad's
netlist and diff against it if you want to be sure.

Regenerate with `python3 gen_kicad.py` (needs `pip install kiutils`).
