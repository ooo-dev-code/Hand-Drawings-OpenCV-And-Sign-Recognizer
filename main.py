import cv2 as cv
import numpy as np
import mediapipe as mp
from panel import Panel
import threading

# Initialize the webcam
cap = cv.VideoCapture(0)
drawing_points = []
# Set the frame rate
fps = 320
cap.set(cv.CAP_PROP_FPS, fps)

# Initialize mediapipe
mp_hands = mp.solutions.hands
hands = mp_hands.Hands()
mp_drawing = mp.solutions.drawing_utils

def adjust_frame(frame):
    frame = cv.flip(frame, 1)
    rgb_frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)
    return frame, results

def add_fingers_name(hand_landmarks, frame):
    finger_names = ['Wrist','Thumb', 'Index', 'Middle', 'Ring', 'Pinky']
    point_coor_list = []
    
    for i, landmark in enumerate(hand_landmarks.landmark):
        x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
        
        if i % 4 == 0:
            finger_name = finger_names[(i // 4)]
            
            cv.putText(frame, finger_name, (x, y), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv.LINE_AA)
            cv.circle(frame, (x, y), 5, (255, 120, 120), -1)

        point_coor_list.append([x, y])

    return point_coor_list

def calc_distance(p1, p2):
    return int(np.linalg.norm(np.array(p1) - np.array(p2)))

def hand_signs(coors):
    state = "Not Recognized"
    possible_states = {"High-Five": 0, "Fist": True, "OK": True}

    # Index Up for drawings
    if coors[8][1] < coors[6][1] and all(coors[i][1] > coors[i - 2][1] for i in [12, 16, 20]):
        return "Draw"
    
    # Calculate thumb-index distance
    thumb_index_dist = calc_distance(coors[4], coors[8])

    # OK detection first
    if thumb_index_dist < 40:  # You can adjust this threshold based on camera resolution
        state = "OK"
        return state

    for i in range(len(coors)):
        if i % 4 == 0 and i != 0:
            if coors[i][1] < coors[i-3][1] and possible_states["High-Five"]:
                state = "High-Five"
            else:
                possible_states["High-Five"] += 1

        if i % 4 == 0 and i != 0 and i != 4:
            if coors[i][1] > coors[i-3][1] and possible_states["Fist"]:
                state = "Fist"
            else:
                possible_states["Fist"] = False

        if i == 4 and possible_states["Fist"]:
            if coors[4][1] < coors[5][1] and coors[8][1] < coors[20][1] and possible_states["High-Five"] != 0:
                state = "Thumb Up"
                return state
            elif coors[4][1] > coors[17][1] and coors[8][1] > coors[20][1]:
                state = "Thumb Down"
                return state

    return state

def cases(state, frame, coors):
    cv.putText(frame, state, (100, 100), cv.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2, cv.LINE_AA)
    
    if state == "Draw":
        index_tip = coors[8]
        drawing_points.append(index_tip)

    # Draw all points
    for i in range(1, len(drawing_points)):
        cv.line(frame, drawing_points[i - 1], drawing_points[i], panel.get_color(), 3)
        
    if state == "Fist":
        drawing_points.clear()

def run():
    while cap.isOpened():
        ret, frame = cap.read()
        frame, results = adjust_frame(frame)

        # If there is a hand, draw the hand
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                
                coors = add_fingers_name(hand_landmarks, frame)
                state = hand_signs(coors)
                cases(state, frame, coors)
 
        cv.imshow('Hand Tracking', frame)
        if cv.waitKey(5) & 0xFF ==ord('d'):
            break

    cap.release()
    cv.destroyAllWindows()

def start_app():
    global panel
    panel = Panel(drawing_points)

    # Start OpenCV loop in a separate thread
    threading.Thread(target=run, daemon=True).start()

    # Now safely run the Tkinter mainloop in the main thread
    panel.root.mainloop()

if __name__ == "__main__":
    start_app()
