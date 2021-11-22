import cv2
import time
srcPiCam = 'libcamerasrc ! video/x-raw,width=640,height=480 ! videoflip method=clockwise ! videoconvert ! appsink'
cap = cv2.VideoCapture(srcPiCam)

srcUSBCam = 'v4l2src ! video/x-raw,width=640,height=480 ! videoconvert ! appsink'

cap2 = cv2.VideoCapture(srcUSBCam)

#cap.set(3,640)
#cap.set(4,360)

#cap2.set(3,640)
#cap2.set(4,360)

count_pics = 0

while True:
    success, img = cap.read()
    success2, img2 = cap2.read()
    time.sleep(1)
    cv2.imwrite("Results/imPi"+str(count_pics)+".png",img)
    cv2.imwrite("Results/imUSB" + str(count_pics) + ".png", img2)
    count_pics = count_pics+1
    print(f"Pic Captured :{count_pics}")
    if count_pics == 10:
        print("Completed")
        break