import cv2
import os


"""
Take images of calibration checkerboard
- Pressing the key "s" takes a picture with two cameras and saves it to /images/Left and /images/Right.
"""
cap = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

num = 0
dir = os.path.dirname(os.path.realpath(__file__))
while cap.isOpened():

    succes1, img = cap.read()
    succes2, img2 = cap2.read()

    k = cv2.waitKey(5)
    if k == 27:
        break
    elif k == ord('s'): # wait for 's' key to save and exit
        cv2.imwrite(dir + '/images/Left/L' + str(num) + '.png', img)
        cv2.imwrite(dir + '/images/Right/R' + str(num) + '.png', img2)
        print("images saved!")
        num += 1

    cv2.imshow('Left img',img)
    cv2.imshow('Right img',img2)
