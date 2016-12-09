# soft-snake-locomotion

The motion capture processing script creates an animated view of a 2-actuator snake system from motion capture data. It also calculates curvature of each half of the body and visualizes the curvature value on the animate plot.

The arduino code creates a serial interface for controlling solenoids on fluidic control board. 
To interact with it from Matlab, we can use the following commands. We might decide to change them, but they work now as a proof-of-concept that we can turn the valves on/off and change the PWM duty cycling rate.

// first check which port the arduino has been mapped to 

s = serial('COM3', 'BaudRate', 9600)

fopen(s)

// issue as many of these commands as you want

fprintf(s, 'y') // y = turn all valves on (will not do anything until the rate is set with command below)

fprintf(s, 'v 0 50') //  set valve 0 to 50% 

fprintf(s, 'v 1 20') // set valve 1 to 20%

fprintf(s, 'v 2 30')

fprintf(s, 'v 3 60')

fprintf(s, 'n') // turn off all valves

// close stream before exiting program

fclose(s)
