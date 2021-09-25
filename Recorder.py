
from config import _FPS

import cv2
import threading
import time
import numpy as np

from pathlib import Path
from PIL import Image 

class Recorder(object):
    def __init__(self, resolution):
        self.filename = ''
        self.root = 'data/'
        self.img_dir = self.root + 'img/'
        self.vid_dir = self.root + 'vid/'
        self.classes = ('0-Good', '1-Bad')
        self.fileSetup()
        self.workers = 2
        self.worker_flags = [True]*self.workers
        self.resolution = resolution
        self.frame_buffer = [] # List of frames for current recording
        self.video_buffer = [] # Queue of videos to be rendered
        
        # Parameters for optical flow extraction
        # Params for ShiTomasi corner detection
        self.feature_params = dict( maxCorners = 4,
                               qualityLevel = 0.3,
                               minDistance = 3,
                               blockSize = 5 )

        # Parameters for lucas kanade optical flow
        self.lk_params = dict( winSize  = (15,15),
                          maxLevel = 2,
                          criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        # Define flow plot colour
        self.flow_colour = (255,255,255)

        # Threads and associated locks for rendering in background
        self.lock = threading.Lock()
  
        for thread_id in range(self.workers):
            threading.Thread(target=self.renderer, daemon=True, args=(thread_id,)).start() 
            
    def fileSetup(self):
        for myclass in self.classes:
            Path(self.img_dir + myclass).mkdir(parents=True, exist_ok=True)
            Path(self.vid_dir + myclass).mkdir(parents=True, exist_ok=True)
        
    
    # Add current tick frame to buffer
    def add(self, bytes_view):
        self.frame_buffer.append(bytes_view)
    
    # Stop recording
    def stop(self):
        self.lock.acquire()
        self.video_buffer.append((self.filename, self.frame_buffer))
        self.frame_buffer = []
        self.lock.release()
    
    # Video Renderer
    def renderer(self, thread_id):
        while True:
        
            while True:
                self.lock.acquire()
                video_count = len(self.video_buffer)
                self.lock.release()
                
                if video_count == 0:
                    self.worker_flags[thread_id] = True
                    time.sleep(1)
                else:
                    self.worker_flags[thread_id] = False
                    break
            
            self.lock.acquire() 
            
            filename, frame_list = self.video_buffer[0]
            del self.video_buffer[0]
            
            self.lock.release()
            
            # Delete leaked frame
            del frame_list[0]
            
            print('INFO: Recorder %d: Exporting \'%s\' (%d frames)..' % (thread_id, filename, len(frame_list)))
            
            self.export(filename, frame_list)
            frame_list = []
            
            print('INFO: Recorder %d: Saved \'%s\' successfully.' % (thread_id, filename))
            
    def export(self, filename, frame_list):
    
        # Setup output video
        out = cv2.VideoWriter(self.vid_dir + filename + '.avi', cv2.VideoWriter_fourcc('F','F','V','1'), _FPS, self.resolution) 
        
        # Locate corners in first frame
        bytes_view = frame_list[0]
        old_frame = np.flip(np.array(Image.frombytes("RGB", self.resolution, bytes_view)), 2)
        old_gray = old_frame[:,:,0]
        old_pts = cv2.goodFeaturesToTrack(old_gray, mask = None, **self.feature_params)
        
        # Write first frame to video
        out.write(old_frame)
            
        # Create a mask image for drawing optical flow
        mask = np.zeros_like(old_frame)
            
        for bytes_view in frame_list[1:]:
            
            # Convert from bytes view
            frame = np.flip(np.array(Image.frombytes("RGB", self.resolution, bytes_view)), 2)
            
            # Write frame to video
            out.write(frame)
            
            # Greyscale and filter G/R colour channels
            frame_gray = frame[:,:,0]
            
            # If some trackable points found
            if old_pts is not None:
            
                # If not max trackable points found
                if len(old_pts) < self.feature_params.get('maxCorners'):
                    old_pts = cv2.goodFeaturesToTrack(old_gray, mask = None, **self.feature_params)
                    
                # Calculate optical flow
                new_pts, status, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, old_pts, None, **self.lk_params)

                # Select good points
                good_new = new_pts[status==1]
                good_old = old_pts[status==1]

                # Draw the tracks
                for i,(new, old) in enumerate(zip(good_new, good_old)):
                    a,b = new.ravel()
                    c,d = old.ravel()
                    # Optical flow of tracked point
                    mask = cv2.line(mask, (a,b),(c,d), self.flow_colour, 1)
                
                # Update previous points array
                old_pts = good_new.reshape(-1,1,2)
            
            else:
              old_pts = cv2.goodFeaturesToTrack(old_gray, mask = None, **self.feature_params)  
            
            # Update the previous frame
            old_gray = frame_gray.copy()
            
        # Release video
        out.release()
        
        # Write optical flow mask to disk
        cv2.imwrite( self.img_dir + filename + '.png', mask )
        
    def clear(self):
        self.frame_buffer = []
        
    def openNew(self, scenarioID):
        scen_class = self.classes[int(scenarioID[0])]
        p = Path(self.img_dir + scen_class).glob('*' + scenarioID + '-*.png')
        n_entries = len([x for x in p if x.is_file()])
        filenumber = str(n_entries).zfill(6)
        self.filename = scen_class + '/' + 'scen_' + scenarioID + '-' + filenumber
        open(self.vid_dir + self.filename + '.avi',"w+")
        open(self.img_dir + self.filename + '.png',"w+")
        
    def isRecording(self):
        if self.frame_buffer == [] and self.video_buffer == [] and all(self.worker_flags):
            return False
        else:
            return True
