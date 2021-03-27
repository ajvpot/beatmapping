import gzip
import json
import sys
import xml.etree.ElementTree as ET
from collections import namedtuple

input = gzip.open('voulezvous.als', 'r')
tree = ET.parse(input)
root = tree.getroot()

TimeSignature = namedtuple('TimeSiguature', ['numerator', 'denominator'])
ts = TimeSignature(None, None)
for xts in tree.iter('RemoteableTimeSignature'):
	ts = TimeSignature(int(xts.find('Numerator').get('Value')), int(xts.find('Denominator').get('Value')))
	break

#print(ts)

tempoHandleID = 0
for tempoHandle in tree.iter('Tempo'):
	tempoHandleID = tempoHandle.find('AutomationTarget').get('Id')

changes = []


for envelope in tree.iter('AutomationEnvelope'):
	if envelope.find('EnvelopeTarget').find('PointeeId').get('Value') != tempoHandleID:
		continue

	for bpmChangeEvent in envelope.find('Automation').find('Events').iter('FloatEvent'):
		if float(bpmChangeEvent.get('Time')) <= 0:
			continue

		bpmChange = {
			'_BPM': round(float(bpmChangeEvent.get('Value')),3),
			'_time': int(float(bpmChangeEvent.get('Time'))),
			'_beatsPerBar': ts.numerator,  # todo: ??
			'_metronomeOffset': ts.denominator  # todo: ??
		}

		changes.append(bpmChange)

	break

print(json.dumps(changes))
sys.exit(0)



changes = []

# calculate BPM changes from marker locations
for clip in tree.iter('AudioClip'):
	#print(clip.find('Name').get('Value'))
	lastMarker = None
	for marker in sorted(clip.iter('WarpMarker'), key=lambda y: float(y.get('SecTime'))):
		beatTime = float(marker.get('BeatTime'))
		secTime = float(marker.get('SecTime'))

		beatDelta = beatTime - (0 if lastMarker is None else float(lastMarker.get('BeatTime')))
		secDelta = secTime - (0 if lastMarker is None else float(float(lastMarker.get('SecTime'))))

		bpm = (beatDelta / secDelta) * 60

		bpmChange = {
			'_BPM': bpm,
			'_time': secTime,
			'_beatsPerBar': ts.numerator,  # todo: ??
			'_metronomeOffset': ts.denominator  # todo: ??
		}

		changes.append(bpmChange)
		lastMarker = marker
	break

print(json.dumps(changes))
