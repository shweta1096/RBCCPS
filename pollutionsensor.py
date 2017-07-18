# 1. Read from the microphone for a predetermined duration
# 2. Find an estimate of the loudness of that audio sample
# 3. Read from the serial to which a CO2 sensor has been connected
# 4. JSONencode these readings into a nice format
# 5. Push the JSON string into a serial port where an FTDI connector has been attached
# 6. Do this in intervals of 60s
import csv
import json
import alsaaudio #to handle the audio recording
import serial #for communication
import sys, time #for delays and argument handling
import numpy as np #for loudness estimation

#step 1: set up all the inputs and peripherals (mic, co2 sensor, ftdi etc..)

#microphone
FORMAT = alsaaudio.PCM_FORMAT_S16_LE
CHANNELS = 1
RATE = 44100
CHUNK = 1024

def readMicLoudness(len):


        inp = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, device='default')
        inp.setchannels(CHANNELS)
        inp.setrate(RATE)
        inp.setformat(FORMAT)
        inp.setperiodsize(CHUNK/2)

        frames = []

        while(len>0):
                len -= 1
                l, data = inp.read()

                if l:
                        frames.append(data)
        frames = (b''.join(frames))
        #print len(frames)
        frames = np.fromstring(frames, dtype = 'int16')
        #frames = frames/32767 #basic normalisation
        return int(np.sqrt(np.mean(np.square(frames)))) #seems to be a more reliable way to find the loudness than rms
        inp.stop_stream()
        inp.close()
        alsaaudio.terminate()

def jsonString(a,b,c,l):
        retstring = json.dumps({"c" : str(a) , "p2" : str(b), "pm10" :str(c), "db" : str(l)})
        return retstring

def main():
        #filename and duration - execute the file as <filename>.py name duration
        name = str(sys.argv[1])
        dur = int(sys.argv[2])
        len = int(dur * (RATE) * 2)
        #co2 sensor (arduino)
        sensor = serial.Serial('/dev/ttyACM0',9600,timeout=1)
        sensor.readline() #to discard the first value that comes


        #ftdi board - assuming the rx, tx and ground connections are made
        #yp05 = serial.Serial('/dev/ttyUSB0', 9600, timeout = 1)
        f = open("./archived/"+ name, 'w')

        g = open('./archived/'+ name+'.csv', 'wt');
        #Initialize the CSV writer to write data into file
        writer = csv.writer(g,dialect = csv.excel)

        while (1):
                        loudnessValue = readMicLoudness(len) #the microphone recording and processing using a function, just to keep things clean
                        t = sensor.readline()
                        co2, pm25 ,pm10 = t.strip().split(",")
                        output = jsonString(co2 , pm25, pm10,loudnessValue) #making the json string a function
                        print(output)
                        #yp05.write(output)
                        f.write(output + "\n")
                        data = [str(co2), str(pm25), str(pm10), str(loudnessValue)]
                        #print data
                        writer.writerow(data)
                        time.sleep(5)




if __name__== "__main__":
        main()
