import cv2
import numpy as np
from serial import Serial
import threading
import time
ser = Serial('COM3',9600) 

GENDER_MODEL = 'genderDetection/deploy_gender.prototxt'
GENDER_PROTO = 'genderDetection/gender_net.caffemodel'
MODEL_MEAN_VALUES = (78.4263377603, 87.7689143744, 114.895847746)
GENDER_LIST = ['Male','Female']
GENDER_LIST_CHAR = ["M","F"]
FACE_PROTO = "faceDetection/deploy.prototxt"
FACE_MODEL = "faceDetection/res10_300x300_ssd_iter_140000_fp16.caffemodel"
face_net = cv2.dnn.readNetFromCaffe(FACE_PROTO, FACE_MODEL)
gender_net = cv2.dnn.readNetFromCaffe(GENDER_MODEL, GENDER_PROTO)
gender_dict = {"Male":(255,0,0),"Female":(255,0,203)}
webfeed = cv2.VideoCapture(0)
applicantEnabled = False
def enableApplicant():
    global applicantEnabled
    time.sleep(5)
    applicantEnabled = True
    
applicantThread = threading.Thread(target=enableApplicant, name="ApplicantThread")
applicantThread.start()
    

def get_faces(frame, confidence_threshold=0.5):
    blob = cv2.dnn.blobFromImage(frame, 1.0, (300, 300), (104, 177.0, 123.0))
    face_net.setInput(blob)
    output = np.squeeze(face_net.forward())
    faces = []
    for i in range(output.shape[0]):
        confidence = output[i, 2]
        if confidence > confidence_threshold:
            box = output[i, 3:7] * np.array([frame.shape[1], frame.shape[0], frame.shape[1], frame.shape[0]])
            start_x, start_y, end_x, end_y = box.astype(np.int_)
            start_x, start_y, end_x, end_y = start_x - 10, start_y - 10, end_x + 10, end_y + 10
            
            start_x = max(0, start_x)
            start_y = max(0, start_y)
            end_x = min(frame.shape[1], end_x)
            end_y = min(frame.shape[0], end_y)
            
            faces.append((start_x, start_y, end_x, end_y))
            return faces
    
def applicantStatus(gender):
    if gender == "Male":
        cv2.putText(image,"APPLICATION ACCEPTED",(0,100),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2)
        return
    #Female
    cv2.putText(image,"APPLICATION DENIED",(0,100),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255), 2)

   
    

def get_gender(frame,confidence_threshold=0.5):
    global applicantEnabled
    faces = get_faces(frame)
    if faces == None or applicantEnabled == False:
        sendToArduino("N")
        return
    for i, (start_x,start_y,end_x,end_y) in enumerate(faces):
        faceframe = frame[start_y: end_y, start_x: end_x]
        blob = cv2.dnn.blobFromImage(image=faceframe, scalefactor=1.0, size=(
            227, 227), mean=MODEL_MEAN_VALUES, swapRB=False, crop=False)
        gender_net.setInput(blob)
        gender_preds = gender_net.forward()
        i = gender_preds[0].argmax()
        gender = GENDER_LIST[i]
        genderChar = GENDER_LIST_CHAR[i]
        applicantStatus(gender)
        sendToArduino(str(genderChar))
        gender_confidence_score = gender_preds[0][i]
        if(gender_confidence_score > confidence_threshold):
            cv2.putText(frame,gender,(start_x,end_y),cv2.FONT_HERSHEY_SIMPLEX, 1, gender_dict[gender], 2)
            cv2.rectangle(frame, (start_x, start_y), (end_x, end_y), gender_dict[gender], 2)
            cv2.putText(frame,f"",(start_x,start_y),cv2.FONT_HERSHEY_SIMPLEX, 1, gender_dict[gender], 2)
        
def sendToArduino(gender):
    ser.write(gender.encode())
        
    
while True:
    success, image = webfeed.read()
    get_gender(image)
    cv2.putText(image,"CorruptCorp Interview Application",(0,30),cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,0), 2)
    cv2.imshow("System", image)
    cv2.waitKey(1)