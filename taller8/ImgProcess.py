import numpy as np
import matplotlib.pyplot as plt

def negative(img):
    return 255 - img

def red_channel(img):
    imgCopy = img.copy()
    imgCopy[:, :, 1] = imgCopy[:, :, 2] = 0
    return imgCopy

def green_channel(img):
    imgCopy = img.copy()
    imgCopy[:, :, 0] = imgCopy[:, :, 2] = 0
    return imgCopy

def blue_channel(img):
    imgCopy = img.copy()
    imgCopy[:, :, 0] = imgCopy[:, :, 1] = 0
    return imgCopy

def magenta(img):
    imgCopy = img.copy()
    imgCopy[:, :, 1] = 0
    return imgCopy