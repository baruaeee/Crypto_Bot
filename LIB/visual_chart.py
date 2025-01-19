import pyautogui
import cv2
import numpy as np

canvas = (675, 150, 293, 733)
screenshot = pyautogui.screenshot(region=canvas)
screenshot = np.array(screenshot)
sceeenshot = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
cv2.imshow('test', screenshot)
cv2.waitKey(5000)
cv2.destroyAllWindows()

print('Done')
