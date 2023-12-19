import numpy as np
import cv2 as cv
import glob
import os


"""
Find checkerboard corners, object points, and image points
"""
dir = os.path.dirname(os.path.realpath(__file__))
chessboardSize = (9,6)
frameSize = (640,480)
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# Prepare object points
objp = np.zeros((chessboardSize[0] * chessboardSize[1], 3), np.float32)
objp[:,:2] = np.mgrid[0:chessboardSize[0],0:chessboardSize[1]].T.reshape(-1,2)
objpoints = [] 
imgpointsL = [] 
imgpointsR = [] 

imagesLeft = glob.glob(os.path.join(dir, 'images', 'Left', '*.png'))
imagesRight = glob.glob(os.path.join(dir, 'images', 'Right', '*.png'))

for imgLeft, imgRight in zip(imagesLeft, imagesRight):
    imgL = cv.imread(imgLeft)
    imgR = cv.imread(imgRight)
    grayL = cv.cvtColor(imgL, cv.COLOR_BGR2GRAY)
    grayR = cv.cvtColor(imgR, cv.COLOR_BGR2GRAY)

    # Find chessboard corners
    retL, cornersL = cv.findChessboardCorners(grayL, chessboardSize, cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_FAST_CHECK + cv.CALIB_CB_NORMALIZE_IMAGE)
    retR, cornersR = cv.findChessboardCorners(grayR, chessboardSize, cv.CALIB_CB_ADAPTIVE_THRESH + cv.CALIB_CB_FAST_CHECK + cv.CALIB_CB_NORMALIZE_IMAGE)

    if retL and retR and len(cornersL)==len(cornersR) and len(cornersL) == 9*6 and len(cornersR) == 9*6:
        objpoints.append(objp)
        cornersL = cv.cornerSubPix(grayL, cornersL, (11,11), (-1,-1), criteria)
        imgpointsL.append(cornersL)
        cornersR = cv.cornerSubPix(grayR, cornersR, (11,11), (-1,-1), criteria)
        imgpointsR.append(cornersR)

        # Draw and display the corners
        cv.drawChessboardCorners(imgL, chessboardSize, cornersL, retL)
        cv.imshow('img left', imgL)
        cv.drawChessboardCorners(imgR, chessboardSize, cornersR, retR)
        cv.imshow('img right', imgR)
        cv.waitKey(1000)

cv.destroyAllWindows()


"""
Return calibration matrices
"""

retL, cameraMatrixL, distL, rvecsL, tvecsL = cv.calibrateCamera(objpoints, imgpointsL, frameSize, None, None)
heightL, widthL, channelsL = imgL.shape
newCameraMatrixL, roi_L = cv.getOptimalNewCameraMatrix(cameraMatrixL, distL, (widthL, heightL), 1, (widthL, heightL))

retR, cameraMatrixR, distR, rvecsR, tvecsR = cv.calibrateCamera(objpoints, imgpointsR, frameSize, None, None)
heightR, widthR, channelsR = imgR.shape
newCameraMatrixR, roi_R = cv.getOptimalNewCameraMatrix(cameraMatrixR, distR, (widthR, heightR), 1, (widthR, heightR))


"""
Stereo vision calibration and rectification
"""
# Calibration
flags = 0
flags |= cv.CALIB_FIX_INTRINSIC
criteria_stereo= (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
retStereo, newCameraMatrixL, distL, newCameraMatrixR, distR, rot, trans, essentialMatrix, fundamentalMatrix = cv.stereoCalibrate(objpoints, imgpointsL, imgpointsR, newCameraMatrixL, distL, newCameraMatrixR, distR, grayL.shape[::-1], criteria_stereo, flags)

# Rectification
rectifyScale= 1
rectL, rectR, projMatrixL, projMatrixR, Q, roi_L, roi_R= cv.stereoRectify(newCameraMatrixL, distL, newCameraMatrixR, distR, grayL.shape[::-1], rot, trans, rectifyScale,(0,0))
stereoMapL = cv.initUndistortRectifyMap(newCameraMatrixL, distL, rectL, projMatrixL, grayL.shape[::-1], cv.CV_16SC2)
stereoMapR = cv.initUndistortRectifyMap(newCameraMatrixR, distR, rectR, projMatrixR, grayR.shape[::-1], cv.CV_16SC2)

def save_coefficients(mtxL, distL, mtxR, distR, path, rot, trans, Q):
    """ Save the camera matrix and the distortion coefficients to given path/file. """
    cv_file = cv.FileStorage(path, cv.FILE_STORAGE_WRITE)

    # Left
    cv_file.write("KL", mtxL)
    cv_file.write("DL", distL)

    # Right
    cv_file.write("KR", mtxR)
    cv_file.write("DR", distR)

    cv_file.write("rot", rot)
    cv_file.write("trans", trans)

    # Map
    cv_file.write('sLX',stereoMapL[0])
    cv_file.write('sLY',stereoMapL[1])
    cv_file.write('sRX',stereoMapR[0])
    cv_file.write('sRY',stereoMapR[1])

    cv_file.write('Q', Q)
    cv_file.release()

path = dir + '/calibrationCoefficients.yaml'
save_coefficients(newCameraMatrixL, distL, newCameraMatrixR, distR, path, rot, trans, Q)
print(f"Parameters saved in {dir}!")