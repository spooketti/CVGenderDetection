import cv2

webfeed = cv2.VideoCapture(0)
while True:
    
    success, image = webfeed.read()
    cv2.imshow("System", image)
    cv2.waitKey(1)