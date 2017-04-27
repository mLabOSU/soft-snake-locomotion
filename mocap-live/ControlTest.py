from NatNetClient import NatNetClient
from CurvatureControl import CurvatureControl
from PneumaticBoard import PneumaticBoard
from collections import defaultdict

positions = [(0, 0, 0)] * 3
actuator = CurvatureControl()
pneumatic = PneumaticBoard(valves=4)

starttime = 0
timelist = [0, 5, 10, 15, 20, 25]
ktargets = [10, 15, 13, 17, 20, 10]
kindex = 0

# This is a callback function that gets connected to the NatNet client and called once per mocap frame.
def receiveNewFrame( frameNumber, markerSetCount, unlabeledMarkersCount, rigidBodyCount, skeletonCount,
                    labeledMarkerCount, latency, timecode, timecodeSub, timestamp, isRecording, trackedModelsChanged ):
	global starttime, kindex
			
	if frameNumber % 60 == 0:				
		k, valve0, newPWM0, valve1, newPWM1 = actuator.update(positions, ktargets[kindex % len(ktargets)])
		pneumatic.setPWM(newPWM0, valve0)
		pneumatic.setPWM(newPWM1, valve1)
		
		print (timestamp - starttime, ", ", k)
	
	if starttime == 0:
		starttime = timestamp
		
	if timestamp - starttime > timelist[(kindex + 1) % len(timelist)]:
		kindex = kindex + 1

# This is a callback function that gets connected to the NatNet client. It is called once per rigid body per frame
def receiveRigidBodyFrame( id, position, rotation ):
	positions[id-1] = position
    #print( "Received frame for rigid body", id )

pneumatic.on()	
	
# This will create a new NatNet client
streamingClient = NatNetClient()

# Configure the streaming client to call our rigid body handler on the emulator to send data out.
streamingClient.newFrameListener = receiveNewFrame
streamingClient.rigidBodyListener = receiveRigidBodyFrame

# Start up the streaming client now that the callbacks are set up.
# This will run perpetually, and operate on a separate thread.
streamingClient.run()
