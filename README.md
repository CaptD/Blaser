# blaser

## How to run file

1. one-step calibration:
```
roslaunch foxbot foxbot.launch
roslaunch foxbot keyboard.launch
roslaunch foxbot dance.launch
rosrun visp_hand2eye_calibration visp_hand2eye_calibration_calibrator 
roslaunch ueye_cam camera_blue.launch 
roslaunch ueye_cam calibration_blue.launch 
```
