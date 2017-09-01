from PneumaticBoard import *

board = PneumaticBoard(port='COM4', actuators=8)
board.on()
board.setPWMList([25, 25, 25, 25, 25, 25, 25, 25])
sleep(500)
board.off()
board.close()
