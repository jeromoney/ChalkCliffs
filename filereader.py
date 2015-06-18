import numpy as np
from math import cos,sin,pi
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


def createImage(directory = '/Users/justinmatis/Documents/chalkcliffdata/',saveFile='save.p',image='image.tif'):
    data = pickle.load(open(directory+saveFile ,'r'))
    NCOLS  = data.shape[0]
    NROWS =  data.shape[1]
    # f = open(directory + image,'w')
    # f.write('NCOLS ' + NCOLS + '\n')
    # f.write('NROWS ' + NROWS + '\n')
    # f.write('XLLCORNER 0\n') #No specific corner since map is vertical
    # f.write('YLLCORNER -'+ NROWS+'\n')
    # f.write('CELLSIZE 1\n')
    # f.write('NODATA_VALUE 0\n')
    # for i in range(int(NROWS)):
    #     line = ' '.join([str(int(x)) for x in data[i]]) + '\n'
    #     f.write(line)
    format = "GTiff"
    driver = gdal.GetDriverByName( format )
    metadata = driver.GetMetadata()
    dst_ds = driver.Create( directory + image, NROWS,NCOLS, 1, gdal.GDT_Byte )
    #dst_ds.SetGeoTransform( [ 444720, 1, 0, 3751320, 0, 1 ] )
    srs = osr.SpatialReference()
    srs.SetUTM( 11, 1 )
    srs.SetWellKnownGeogCS( 'NAD27' )
    dst_ds.SetProjection( srs.ExportToWkt() )
    dst_ds.GetRasterBand(1).WriteArray( data )









createImage()



