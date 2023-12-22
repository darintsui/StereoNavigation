
# Stereoscopic Surgical Navigation

This repository contains code for the paper:

_"A low-cost, open-source based optical surgical
navigation system using stereoscopic vision"_, Darin Tsui, Capalina Melentyev, Kirsten Ramos, Ananya Rajan, Matthew Tam, Mitsuhiro Jo, Frank E. Talke.

### Calibration

The following instructions describe how to calibration your own stereoscopic camera system.

1. From the command line:
```
cd Calibration
```

2. Run the script:
```
python calibration_images.py
```
The script will look for two cameras connected to your computer. Upon detection, it will label the first camera as Left `cv2.VideoCapture(0)` and the second as Right `cv2.VideoCapture(1)`. You may need to change the numbering depending on your setup. 

Place your calibration checkerboard in the frame and press 's'. Pressing the 's' key will have both cameras take an image.

3. Extract camera parameters:
```
python stereo_calibration.py
```
The script will go into `/images/Left/` and `/images/Right/` and iterate through the camera images. The script will then look for the checkerboard corners and extract camera parameters. Final parameters will be placed in `calibrationCoefficients.yaml`.
