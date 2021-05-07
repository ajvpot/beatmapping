import gzip
import json
import sys
import xml.etree.ElementTree as ET
from collections import namedtuple

# read file
with open('Info.dat', 'r') as infodat:
	songInfo=json.loads(infodat.read())

globalBPM = float(songInfo['_beatsPerMinute'])

input = gzip.open('voulezvous.als', 'r')
tree = ET.parse(input)
root = tree.getroot()

TimeSignature = namedtuple('TimeSiguature', ['numerator', 'denominator'])
ts = TimeSignature(None, None)
for xts in tree.iter('RemoteableTimeSignature'):
	ts = TimeSignature(int(xts.find('Numerator').get('Value')), int(xts.find('Denominator').get('Value')))
	break

changes = []

# calculate BPM changes from marker locations
for clip in tree.iter('AudioClip'):
	#print(clip.find('Name').get('Value'))
	lastMarker = None
	for marker in sorted(clip.iter('WarpMarker'), key=lambda y: float(y.get('SecTime'))):
		beatTime = float(marker.get('BeatTime'))
		secTime = float(marker.get('SecTime'))
		#print(beatTime, secTime)

		beatDelta = beatTime - (-ts.numerator if lastMarker is None else float(lastMarker.get('BeatTime')))
		secDelta = secTime - (0 if lastMarker is None else float(float(lastMarker.get('SecTime'))))

		bpm = (beatDelta / secDelta) * 60

		bpmChange = {
			'_BPM': float(bpm),
			'_secTime': float(secTime) if lastMarker is not None else 0,
			'_beatsPerBar': ts.numerator,  # todo: ??
			'_metronomeOffset': 1  # todo: ??
		}
		bpmChange['_time'] = (globalBPM / 60) * bpmChange['_secTime']
		#print(bpmChange)

		changes.append(bpmChange)
		lastMarker = marker
	break

print(json.dumps(changes))