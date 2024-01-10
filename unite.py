import cv2, imutils
import cv2, imutils, socket
import numpy as np
import time
import base64
import threading, wave, pyaudio,pickle,struct
import sys
import queue
import os


# For details visit pyshine.com
q = queue.Queue(maxsize=10)

filename = 'video.mp4'
# reading video
vid = cv2.VideoCapture(filename)
FPS = vid.get(cv2.CAP_PROP_FPS)
global TS
TS = (0.5/FPS)
BREAK=False
print('FPS:',FPS,TS)
totalNoFrames = int(vid.get(cv2.CAP_PROP_FRAME_COUNT))
durationInSeconds = float(totalNoFrames) / float(FPS)
d=vid.get(cv2.CAP_PROP_POS_MSEC)
print(durationInSeconds,d) 

def video_stream_gen():
   
    WIDTH=800
    c = 0
    sttt = time.time()
    while(vid.isOpened()):
        try:
            _,frame = vid.read()
            frame = imutils.resize(frame, width=WIDTH)
            q.put(frame)
            c = c + 1
            if c == 600:
                sedd = time.time()
                # print()
                print(f"Time taken for put{sedd-sttt}")
        except:
            os._exit(1)
    print('Player closed')
    BREAK=True
    vid.release()


def video_stream():
    global TS
    fps,st,frames_to_count,cnt = (0,0,1,0)
    cv2.namedWindow('TRANSMITTING VIDEO')        
    cv2.moveWindow('TRANSMITTING VIDEO', 10,30)
    c = 0
    sttt = time.time()
    while(True):
        
        # print(sttt)
        frame = q.get()
        c = c + 1
       
        if c == 600:
            sedd = time.time()
            # print()
            print(f"Time taken fpr gget{sedd-sttt}")
        
        encoded,buffer = cv2.imencode('.jpeg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
        message = base64.b64encode(buffer)
        frame = cv2.putText(frame,'FPS: '+str(round(fps,1)),(10,40),cv2.FONT_HERSHEY_SIMPLEX,0.7,(0,0,255),2)
        if cnt == frames_to_count:
            try:
                fps = (frames_to_count/(time.time()-st))
                st=time.time()
                cnt=0
                if fps>FPS:
                    TS+=0.001
                elif fps<FPS:
                    TS-=0.001
                else:
                    pass
            except:
                pass
        cnt+=1
        
        
        
        # print('TRANSMITTING VIDEO')
        cv2.imshow('TRANSMITTING VIDEO', frame)
        key = cv2.waitKey(int(1000*TS)) & 0xFF
        if key == ord('q'):
            os._exit(1)
            TS=False
            break
                

def audio_stream():

    # open the file for reading.
    wf = wave.open('audio.wav', 'rb')
    # create an audio object
    p = pyaudio.PyAudio()
    # length of data to read.
    chunk = 1024
    # open stream based on the wave object which has been input.
    stream = p.open(format =
                    p.get_format_from_width(wf.getsampwidth()),
                    channels = wf.getnchannels(),
                    rate = wf.getframerate(),
                    output = True)

    # read data (based on the chunk size)
    data = wf.readframes(chunk)

    # play stream (looping from beginning of file to the end)
    while data:
        # writing to the stream is what *actually* plays the sound.
        stream.write(data)
        data = wf.readframes(chunk)
        # print(data)


    # cleanup stuff.
    wf.close()
    stream.close()    
    p.terminate()
                
from concurrent.futures import ThreadPoolExecutor
with ThreadPoolExecutor(max_workers=3) as executor:
    executor.submit(audio_stream)
    executor.submit(video_stream_gen)
    executor.submit(video_stream)