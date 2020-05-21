import cv2
import numpy as np

"""
TODO:
    - Better names to variables
    - Refact function to a class
"""

def extractSignatures(adjustedImg, y = 1985, s1 = (0,520), s2 = (495, 1060), s3 = (1035, -1), centerArea = 40, threshold = 250):
    """
    Extract 3 signatures from a pre-proccess document page.

    Parameters
    ----------
    adjustedImg

    y : int, optional

    s1 : tuple, optional

    s2 : tuple optional

    s3 : tuple optional

    centerArea : int, optional

    threshold : int, optional


    Returns
    -------
    
    """
    
    # Crop
    sig1 = adjustedImg[y:, s1[0]:s1[1]]
    sig2 = adjustedImg[y:, s2[0]:s2[1]]
    sig3 = adjustedImg[y:, s3[0]:s3[1]]

    # Calculate the mean of the pixel values of the center to see if it's white (empty box)
    signatures = []
    center = [sig1.shape[0]//2, sig1.shape[1]//2]
    roi = sig1[center[0]-centerArea:center[0]+centerArea, center[1]-centerArea:center[1]+centerArea]
    mean = cv2.mean(cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY))
    if mean[0] < threshold:
        signatures.append(sig1)
    
    center = [sig2.shape[0]//2, sig2.shape[1]//2]
    roi = sig2[center[0]-centerArea:center[0]+centerArea, center[1]-centerArea:center[1]+centerArea]
    mean = cv2.mean(cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY))
    if mean[0] < threshold:
        signatures.append(sig2)

    center = [sig3.shape[0]//2, sig3.shape[1]//2]
    roi = sig3[center[0]-centerArea:center[0]+centerArea, center[1]-centerArea:center[1]+centerArea]
    mean = cv2.mean(cv2.cvtColor(roi, cv2.COLOR_RGB2GRAY))
    if mean[0] < threshold:
        signatures.append(sig3)

    return signatures
