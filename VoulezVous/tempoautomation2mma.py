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
		if float(bpmChangeEvent.get('Time')) < 0:
			continue

		bpmChange = {
			'_BPM': float(bpmChangeEvent.get('Value')),
			'_time': float(bpmChangeEvent.get('Time')),
			'_beatsPerBar': ts.numerator,  # todo: ??
			'_metronomeOffset': ts.denominator  # todo: ??
		}
		#print(bpmChange)
		changes.append(bpmChange)

	break

print(json.dumps(changes))