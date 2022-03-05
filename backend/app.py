import io
import cv2
import time
import json
import base64
import numpy as np
import face_recognition

from PIL import Image
from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from engineio.payload import Payload

app = Flask(__name__)
socket_ = SocketIO(app, cors_allowed_origins='*')

# time in seconds 
eyes_closed_time_threshold = 10
ear_threshold = 0.29
time_limit_reached = False
start_time = None
eyes_closed = False
plot = ('left_eye','right_eye')

Payload.max_decode_packets = 500

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


# extract the frame from the base64 encoded data for opencv to process
def extract_frame(base64_string):
	idx = base64_string.find('base64,')
	base64_string  = base64_string[idx+7:]
	sbuf = io.BytesIO()
	sbuf.write(base64.b64decode(base64_string, ' /'))
	pimg = Image.open(sbuf)

	return cv2.cvtColor(np.array(pimg), cv2.COLOR_RGB2BGR)


# encode the frame back into a base64 string to send to the client
def serializeFrame(frame):
	imgencode = cv2.imencode('.jpeg', frame, [cv2.IMWRITE_JPEG_QUALITY,1000])[1]
	stringData = base64.b64encode(imgencode).decode('utf-8')
	b64_src = 'data:image/jpeg;base64,'

	return b64_src + stringData
 

# when a frame arrives from the client 
@socket_.on('frame', namespace='/')
def frameEvent(base64_string):
	global start_time, eyes_closed, eyes_closed_time_threshold, plot, time_limit_reached
	
	# extract frame from base64 encoded string
	frame = extract_frame(base64_string)
	# get the facial landmark points 
	face_landmark_list = face_recognition.face_landmarks(frame[:,:,1])

	# draw the facial landmarks on the image 
	if(len(face_landmark_list) > 0):
		for i in face_landmark_list[0].keys():
			if i in plot: 
				landmark = face_landmark_list[0][i]

				for coords in landmark:     
					x,y = coords
					cv2.circle(frame, (x,y), radius=2, color=(0,0,255), thickness=-1)
	
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

		# check if eyes are closed 
		if ear_avg < ear_threshold: 
			print("Eyes closed!")

			eyes_closed = True

			if start_time == None: 
				start_time = time.time()
		else: 
			start_time = None
			eyes_closed = False
			time_limit_reached = False

		# if the time the eyes have remained closed has crossed the time limit  
		if start_time != None and eyes_closed and time.time() - start_time >= eyes_closed_time_threshold: 
			time_limit_reached = True
			emit('time_limit_reached', json.dumps({ 'limit_reached': 1 }))
			print(f'Eyes closed for more than {eyes_closed_time_threshold} seconds!')
		
	# serialize the frame to be sent to the client
	stringData = serializeFrame(frame)

	# emit the events to the client 
	emit('time_limit_reached', json.dumps({ 'limit_reached': 0 }))
	emit('response_back', stringData)


if __name__ == '__main__':
	socket_.run(app, debug=True)