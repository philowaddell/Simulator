import numpy as np
import cv2
import os

cap = cv2.VideoCapture('scen_1011-000000.avi')

# Params for ShiTomasi corner detection
feature_params = dict( maxCorners = 4,
                       qualityLevel = 0.3,
                       minDistance = 7,
                       blockSize = 7 )

# Parameters for lucas kanade optical flow
lk_params = dict( winSize  = (15,15),
                  maxLevel = 2,
                  criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

# Define colour and filter threshhold
color = (255,255,255)
thresh = 150

# Take first frame and find corners in it
ret, old_frame = cap.read()
old_gray = old_frame[:,:,0]
old_gray[old_gray < thresh] = 0
old_pts = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)

# Create a mask image for drawing purposes
mask = np.zeros_like(old_frame)
    
while(1):

    # Get next frame
    ret, frame = cap.read()
    
    # Check for end of video
    if frame is None:
        break
    
    # Greyscale and filter G/R colour channels
    frame_gray = frame[:,:,0]
    frame_gray[frame_gray < thresh] = 0
    
    # If some trackable points found
    if old_pts is not None:
    
        # If not max trackable points found
        if len(old_pts) < feature_params.get('maxCorners'):
            old_pts = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)
            
        
        # Calculate optical flow
        new_pts, status, err = cv2.calcOpticalFlowPyrLK(old_gray, frame_gray, old_pts, None, **lk_params)

        # Select good points
        good_new = new_pts[status==1]
        good_old = old_pts[status==1]

        # Draw the tracks
        for i,(new, old) in enumerate(zip(good_new, good_old)):
            a,b = new.ravel()
            c,d = old.ravel()
            # Optical flow of tracked point
            mask = cv2.line(mask, (a,b),(c,d), color, 1)
            # Current location of tracked point
            #frame = cv2.circle(frame,(a,b),5,color[i].tolist(),-1)
        
        # Add mask to current frame
        img = cv2.add(frame,mask)

        # Show optical flow ontop of current frame
        cv2.imshow('frame', img)
        
        # Show optical flow only
        # cv2.imshow('frame', mask)
        
        # Wait 1ms for any key press before continuing
        k = cv2.waitKey(1) & 0xff
        
        # Update previous points array
        old_pts = good_new.reshape(-1,1,2)
    
    else:
      old_pts = cv2.goodFeaturesToTrack(old_gray, mask = None, **feature_params)  

    # Update the previous frame
    old_gray = frame_gray.copy()

print('Press any key to exit.')
os.system('pause')    

cv2.destroyAllWindows()
cap.release()