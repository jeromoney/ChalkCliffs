import numpy as np
from math import cos,sin,pi,sqrt
from osgeo import gdal
import pickle, osr

def rotatePoints():
    filename = 'points.txt'
    outfilename = 'out_pounts.txt'
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



    with open(directory+filename , 'r') as infile , open(directory+outfilename,'w') as outfile:
        infile.readline()   #Skip header row
        for line in infile:
            dataPoint = line.split(',')[:3]
            dataPoint = np.array([float(x) for x in dataPoint]) #Chose to store data as float. Not sure what is most memory efficient choice
                                                      #I could normalize the data to save memory
            dataPoint = np.dot(rotationMatrix , dataPoint)
            dataLine = ','.join([str(abs(x)) for x in dataPoint]) + '\n' #Bit clunky adding absolute function here
            outfile.write(dataLine)

            # dataPoint = (dataPoint/dataPoint[2])[:2] #Normalizing by dividing by z coordinate

def fileInfo(filename = 'out_pounts.csv',directory = '/Users/justinmatis/Documents/chalkcliffdata/'):
        with open(directory+filename , 'r') as infile:
            xMin,yMin = 999999,999999
            xMax,yMax = -999999,-999999
            for line in infile:
                x , y = [float(x) for x in line.split(',')[:2]]
                xMin = min(xMin,x)
                yMin = min(yMin,y)
                xMax = max(xMax,x)
                yMax = max(yMax,y)
        return xMin,xMax,yMin,yMax

def createTif(filename = 'out_pounts.csv',directory = '/Users/justinmatis/Documents/chalkcliffdata/',saveFile='save.p'):
    xMin,xMax,yMin,yMax = fileInfo()
    data = np.zeros((xMax-xMin + 1,yMax-yMin + 1))
    with open(directory+filename , 'r') as infile:
            for line in infile:
                x , y , z = [float(x) for x in line.split(',')]
                data[x-xMin,y-yMin] = z

    pickle.dump( data, open( directory+saveFile, "wb" ) )



def noDataFill((x,y),data):

    defaultFillSize = 3
    xMax = data.shape[0]
    yMax = data.shape[1]
    average = 0.
    distAverage = 0. #Used for tracking inverse distance weighted sum
    flag = False #Used to check if search actually finds one cell with data
    i = 1
    while not (i > defaultFillSize and not flag):
        xRange = range(-i,i+1)
        yRange = range(-i,i+1)
        for xDelta in xRange:
            for yDelta in yRange:
                if (abs(xDelta) > i-1 or abs(yDelta) > i-1):   #Checking point is out on outer ring
                    if 0<=xDelta+x<=xMax and 0<=yDelta+y<=yMax: #Making sure point is within boundaries
                        if data[xDelta+x,yDelta+y] <> 0:
                            flag = True
                            average += data[xDelta+x,yDelta+y] / sqrt(xDelta**2 + yDelta **2)
                            distAverage += 1/sqrt(xDelta**2 + yDelta **2)
        data[x,y] = average/distAverage
        i += 1



def loadData(directory = '/Users/justinmatis/Documents/chalkcliffdata/',saveFile='save.p'):
    data = pickle.load(open(directory+saveFile ,'r'))


    zMax = 0
    zMin = 999999999
     #Filling in nodata points
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            if data[x,y] == 0:
                fillNo = noDataFill((x,y),data)
                print fillNo
                data[x,y] = fillNo

    #Normalizing Data
    data = (data - zMin)/(zMax - zMin) * (2**32)
    return data



def createImage(data,directory = '/Users/justinmatis/Documents/chalkcliffdata/',image='image.tif'):
    NCOLS  = data.shape[0]
    NROWS =  data.shape[1]
    format = "GTiff"
    driver = gdal.GetDriverByName( format )
    metadata = driver.GetMetadata()
    dst_ds = driver.Create( directory + image, NROWS,NCOLS, 1, gdal.GDT_Int32 )
    dst_ds.SetGeoTransform( [ 444720, 1, 0, 3751320, 0, 1 ] )
    srs = osr.SpatialReference()
    srs.SetUTM( 11, 1 )
    srs.SetWellKnownGeogCS( 'NAD27' )
    dst_ds.SetProjection( srs.ExportToWkt() )
    dst_ds.GetRasterBand(1).WriteArray( data )

createTif()
data = loadData()
createImage(data)



