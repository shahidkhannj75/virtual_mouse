import cv2
import numpy as np
import pyautogui
import HandTrackingModule as htm
import time

# Initialize the hand detector
detector = htm.handDetector(maxHands=1)
cap = cv2.VideoCapture(0)

# Get screen size
screen_width, screen_height = pyautogui.size()

# Timing variables
click_hold_time = 0.5  # Time to hold fingers for a click (in seconds)
last_click_time = 0

while True:
    success, frame = cap.read()
    if not success:
        print("Failed to grab frame")
        break

    # Flip the frame horizontally for a later selfie-view display
    frame = cv2.flip(frame, 1)
    
    # Find hands in the frame
    frame = detector.findHands(frame)
    lmList = detector.findPosition(frame, draw=False)

    if lmList:
        # Get the tips of the fingers
        thumb_tip = lmList[4][1:]
        index_tip = lmList[8][1:]
        middle_tip = lmList[12][1:]
        ring_tip = lmList[16][1:]
        pinky_tip = lmList[20][1:]

        # Get the positions of the lower parts of each finger (to check if they are down)
        index_mcp = lmList[5][1:]   
        middle_mcp = lmList[9][1:] 
        ring_mcp = lmList[13][1:]  # Metacarpophalangeal joint of ring finger
        pinky_mcp = lmList[17][1:] 

        # Check if only the index finger is raised
        if (index_tip[1] < index_mcp[1] and  # Index finger is raised
            middle_tip[1] > middle_mcp[1] and  # Middle finger is down
            ring_tip[1] > ring_mcp[1] and      # Ring finger is down
            pinky_tip[1] > pinky_mcp[1]):      # Pinky finger is down
            
            # Map the hand coordinates to screen coordinates and move cursor
            screen_x = np.interp(index_tip[0], [0, frame.shape[1]], [0, screen_width])
            screen_y = np.interp(index_tip[1], [0, frame.shape[0]], [0, screen_height])
            pyautogui.moveTo(screen_x, screen_y)

            # Draw a yellow circle at the tip of the index finger
            cv2.circle(frame, (index_tip[0], index_tip[1]), 10, (0, 255, 255), -1)

            current_time = time.time()
            
            if last_click_time == 0:
                # Start timing the hold
                last_click_time = current_time
            elif current_time - last_click_time >= click_hold_time:
                # Simulate a mouse click
                pyautogui.click()
                # Reset click timer
                last_click_time = 0
        else:
            # Reset click timer if fingers are not in the desired state
            last_click_time = 0
            # Optional: Draw a different indicator when not moving the cursor
            cv2.circle(frame, (index_tip[0], index_tip[1]), 10, (0, 255, 0), -1)

    # Display the frame
    cv2.imshow("Virtual Mouse", frame)

    # Break the loop on pressing 'Esc'
    if cv2.waitKey(1) & 0xFF == 27:
        break

# Release the capture and close windows
cap.release()
cv2.destroyAllWindows()


