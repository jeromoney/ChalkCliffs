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
    assert False



def fillNoData(directory = '/Users/justinmatis/Documents/chalkcliffdata/',saveFile='oldsave.p'):
    data = pickle.load(open(directory+saveFile ,'r'))


    zMax = 0
    zMin = 999999999
     #Filling in nodata points with vertical extrapolation
    for x in range(data.shape[0]):
        topCellwData    = None
        bottomCellwData = None
        for y in range(data.shape[1]):
            if data[x,y] != 0:
                zMax = max(zMax,data[x,y])
                zMin = min(zMin,data[x,y])
                #When we find the first cell with data, we need to fill in all the above values
                if topCellwData == None:
                    data[x,:y] = data[x,y]


                bottomCellwData = (y,data[x,y])


                #The meat of the algorithm: linear extrapolation between two known points
                if topCellwData is not None and data[x,max(y-1,0)] == 0: #Max function protects against out of range references

                    linearFunction = lambda x: topCellwData[1] + \
                                               (bottomCellwData[1] - topCellwData[1]) * (float(x)/float(bottomCellwData[0] - topCellwData[0]))
                    linExtrap = map( linearFunction,range(bottomCellwData[0]-topCellwData[0]))
                    data[x,topCellwData[0]:bottomCellwData[0]] = linExtrap



                topCellwData = (y,data[x,y])

        #We fill in the bottom nodata values with the last data point.
        data[x,bottomCellwData[0]:] = bottomCellwData[1]


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







data = fillNoData()
createImage(data)



