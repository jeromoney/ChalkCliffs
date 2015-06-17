import numpy as np
from math import cos,sin,pi



filename = 'points.txt'
chunkSize = 10000 #number of points to read into memory at one go
directory = '/Users/justinmatis/Documents/chalkcliffdata/'
pinholeMatrix = np.concatenate((np.identity(3),np.zeros((3,1))),axis=1)
roll  = 0  #parameters used to describe rotation from flat world plane to house window pane
pitch = 0
yaw   =  (0.5) * pi

rollMatrix = np.array( [\
    (cos(roll), -sin(roll), 0), \
    (sin(roll),  cos(roll), 0), \
    (        0,          0, 1) \
])



pitchMatrix = np.array( [\
    (cos(pitch)  , 0 , sin(pitch)), \
    (           0, 1 ,         0), \
    (-sin(pitch) , 0 , cos(pitch)) \
])

yawMatrix =  np.array( [\
    (1 ,        0 ,         0), \
    (0 , cos(yaw) , -sin(yaw)), \
    (0 , sin(yaw) ,  cos(yaw)) \
])


rotationMatrix = yawMatrix



with open(directory+filename) as infile:
    infile.readline()   #Skip header row
    for line in infile:
        dataPoint = line.split(',')[:3]
        dataPoint = np.array([float(x) for x in dataPoint]) #Chose to store data as float. Not sure what is most memory efficient choice
                                                  #I could normalize the data to save memory
        dataPoint = np.dot(rotationMatrix , dataPoint)
        dataLine = ','.join([str(abs(x)) for x in dataPoint]) + '\n' #Bit clunky adding absolute function here

        print dataLine

        # dataPoint = (dataPoint/dataPoint[2])[:2] #Normalizing by dividing by z coordinate
