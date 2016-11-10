#!/usr/bin/python

import wave
import sys
import struct

if len(sys.argv) < 3:
	print "Usage: python", sys.argv[0], "<source> <destination>"
	sys.exit()

sourcefile = wave.open(sys.argv[1], 'r')
destinationfile = wave.open(sys.argv[2], 'w')

# Use the same wave params for the fixed file as for the original file
destinationfile.setparams(sourcefile.getparams())

print "Samplewidth: ", sourcefile.getsampwidth()
print "Framerate: ", sourcefile.getframerate()
print "Frames in total: ", sourcefile.getnframes()

# Silence: Everything below this threshold
silence = 1000

# Silence/Noise: 9ms
try:
	annoyingNoise = int(sys.argv[3])
except IndexError:
	annoyingNoise = 9

print "Annoying noise length (ms):", annoyingNoise
# First calculate frames per millisecond
framesPerMs = sourcefile.getframerate() / 1000
print "Frames per MS: ", framesPerMs

annoyingNoiseFrames = annoyingNoise * framesPerMs

silenceFrameCorridor = 0.15
silenceFrameLowerCorridor = int(round(annoyingNoiseFrames * (1 - silenceFrameCorridor), 0))
silenceFrameUpperCorridor = int(round(annoyingNoiseFrames * (1 + silenceFrameCorridor), 0))

print "Annoyance frame length corridor:", silenceFrameLowerCorridor, "-", silenceFrameUpperCorridor

print "Fixing..."

framepos = 0
lastnframessilent = 0
lastnframesByteContent = ""
fixedFileContent = ""

framereadsize = 1

while framepos < sourcefile.getnframes():
	current_frame = sourcefile.readframes(framereadsize)
	lastnframesByteContent += current_frame

	unpacked_frame = struct.unpack("<h", current_frame)
	volume = abs(unpacked_frame[0])

	if volume < silence:
		lastnframessilent += 1
	else:

		if silenceFrameLowerCorridor <= lastnframessilent <= silenceFrameUpperCorridor:
			lastnframesByteContent = ""

		lastnframessilent = 0

		destinationfile.writeframes(lastnframesByteContent)
		lastnframesByteContent = ""
		# destinationfile.writeframes(current_frame)

	framepos += 1

sourcefile.close()
destinationfile.close()

print "All done"