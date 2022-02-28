import face_recognition
import cv2
import numpy as np
import time
from matplotlib.pyplot import plot

'''image = face_recognition.load_image_file("images/faceImage.py")
eyes_closed_image = face_recognition.load_image_file('images/two_people.jpg')
face_landmarks_list = face_recognition.face_landmarks(image)
face_landmarks_eyes_closed = face_recognition.face_landmarks(eyes_closed_image)
left_eye = face_landmarks_list[0]['left_eye']
right_eye = face_landmarks_list[0]['right_eye']
print("left eye: ", left_eye)
print('right eye: ', right_eye)'''

# to plot the landmarks on the image 
def plot_landmarks(image, plot=('left_eye','right_eye')): 
    face_landmarks_list = face_recognition.face_landmarks(image[:,:,1])

    if(len(face_landmarks_list) > 0):
        for i in face_landmarks_list[0].keys():
            if i in plot: 
                landmark = face_landmarks_list[0][i]

                for coords in landmark:     
                    x,y = coords

                    cv2.circle(image,(x,y), radius=2, color=(0,0,255), thickness=-1)
        
    cv2.imshow('left eye',image)

    return face_landmarks_list if len(face_landmarks_list) > 0 else []

# returns the aspect ratio of the vertical landmarks to the vertical landmarks (used to determine if the eyes are closed)
def eye_aspect_ratio(eye_coords):    
    left = np.array(eye_coords[0])
    right = np.array(eye_coords[3])
    
    top_left = np.array(eye_coords[1])
    bottom_left = np.array(eye_coords[5])

    top_right = np.array(eye_coords[2])
    bottom_right = np.array(eye_coords[4])

    A = np.linalg.norm(top_left - bottom_left)
    B = np.linalg.norm(top_right - bottom_right)
    C = np.linalg.norm(left - right)

    return (A + B) / (2 * C) 

# declare the video capture object 
video_capture = cv2.VideoCapture(0)
video_capture.set(cv2.CAP_PROP_FPS, 60)

eyes_closed_time_threshold = 10
ear_threshold = 0.29
start_time = None
eyes_closed = False

def detectEyesClosed(): 
    while True: 
        # read frames from webcam
        ret, frame = video_capture.read()

        # small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)

        # get the face landmark list 
        face_landmark_list = plot_landmarks(frame)

        # get individual features and check if the eyes are closed 
        if(len(face_landmark_list) > 0): 
            # get the landmarks for the left and the right eye
            left_eye = face_landmark_list[0]['left_eye']
            right_eye = face_landmark_list[0]['right_eye']

            # get the eye aspect ratios for the left and the right eyes 
            ear_left = eye_aspect_ratio(left_eye)
            ear_right = eye_aspect_ratio(right_eye)

            # average eye aspect ratio value for left and right eyes 
            ear_avg = (ear_left + ear_right) / 2

            if ear_avg < ear_threshold: 
                eyes_closed = True

                if start_time == None: 
                    start_time = time.time()
                
            else: 
                start_time = None
                eyes_closed = False

            if eyes_closed: 
                print("Eyes closed!")

            if start_time != None and eyes_closed and time.time() - start_time >= eyes_closed_time_threshold: 
                print(f'Eyes closed for more than {eyes_closed_time_threshold} seconds!')

        key = cv2.waitKey(50)

        if key == ord('q'):
            break

if __name__ == '__main__':
    detectEyesClosed()