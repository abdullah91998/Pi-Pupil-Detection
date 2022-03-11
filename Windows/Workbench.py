import cv2 as cv
import numpy as np
import random as rng
import os
import logging

# create a logger with name of the file
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

ch = logging.FileHandler("../log_ellipse_fitting.log")
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

logger.addHandler(ch)

logger.info("*"*50)
logger.info("EXPERIMENT START")

'''Trackbar titles'''
median_blur = 'kernel_size'
median_blur_value = 13
median_blur_value_max = 50

morph_operations_kernel_size = 'morph_kernel'
morph_value = 1
morph_value_max = 10

canny_threshold = 'threshold_canny'
canny_threshold_value = 17
canny_threshold_value_max = 60


def filter_contour(contours):
    """TODO filter contours to get ellipses based on area and circularity
    DOCUMENTATION : Why we need to do a convex hull operation on the contour instead of finding the circularity directly
    from contour ?
    ANS: Since pixels of contour leads to a higher value of circularity > 200. Doing a convex hull leads to a lower
    value since we don't deal with discritised pixels """
    contours_filtered = []
    print("Initial Contours : {}".format(len(contours)))
    print("Filtered Contours:")
    for i, c in enumerate(contours):
        try:
            convex_hull = cv.convexHull(c)
            area_hull = cv.contourArea(convex_hull)
            # print("{} area convex hull {}".format(i, area_hull))
            if 600 < area_hull:  # filtering based on area
                circumference_hull = cv.arcLength(convex_hull, True)
                circularity_hull = (4 * np.pi * area_hull) / circumference_hull ** 2
                if 0.8 < circularity_hull:  # filtering based on circularity
                    print("convex hull :{} Circularity :{} Area : {}".format(i, circularity_hull, area_hull))
                    contours_filtered.append(convex_hull)
        except ZeroDivisionError:
            print("Division by zero for contour {}".format(i))
    return contours_filtered




def draw_ellipse(drawing, contours_filtered):
    minEllipse = [None] * len(contours_filtered)
    for i, c in enumerate(contours_filtered):

        color = (rng.randint(0, 256), rng.randint(0, 256), rng.randint(0, 256))
        minEllipse[i] = cv.fitEllipse(c)
        cv.drawContours(drawing, contours_filtered, i, color)
        (x, y), (MA, ma), angle = minEllipse[i]
        area_contour_hull = cv.contourArea(c)
        area_ellipse = (np.pi / 4) * MA * ma
        print("Area Ellipse :{} Area Contour Hull :{}".format(area_ellipse, area_contour_hull))
        cv.ellipse(drawing, minEllipse[i], color, 2)


def morphology_operations(val):
    """Get Trackbar positions"""

    roi = src_image[220:640, 0:480]
    output = roi.copy()
    src_gray_original = cv.cvtColor(roi, cv.COLOR_BGR2GRAY)
    src_gray = src_gray_original.copy()

    # Blur Operation
    median_blur_th = cv.getTrackbarPos(median_blur, window_name)
    if median_blur_th % 2 == 0:
        median_blur_th += 1
        cv.setTrackbarPos(median_blur, window_name, median_blur_th)
        src_gray = cv.medianBlur(src_gray, median_blur_th)
    else:
        src_gray = cv.medianBlur(src_gray, median_blur_th)

    # Opening operation
    kernel_size_th = cv.getTrackbarPos(morph_operations_kernel_size, window_name)
    if kernel_size_th % 2 == 0:
        kernel_size_th += 1
        kernel = np.ones((kernel_size_th, kernel_size_th), np.uint8)
        cv.setTrackbarPos(morph_operations_kernel_size, window_name, kernel_size_th)
        opening = cv.morphologyEx(src_gray, cv.MORPH_OPEN, kernel)
    else:
        kernel = np.ones((kernel_size_th, kernel_size_th), np.uint8)
        opening = cv.morphologyEx(src_gray, cv.MORPH_OPEN, kernel)

    # Canny
    canny_threshold_th = cv.getTrackbarPos(canny_threshold, window_name)
    canny_output = cv.Canny(opening, canny_threshold_th, canny_threshold_th * 2)

    # Contour
    contours, _ = cv.findContours(canny_output, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    contours_filtered = filter_contour(contours)

    # blank canvas
    drawing = np.zeros((canny_output.shape[0], canny_output.shape[1], 3), dtype=np.uint8)
    draw_ellipse(drawing, contours_filtered)

    cv.imshow("source", output)
    cv.imshow("drawing", drawing)
    cv.imshow(result_window, canny_output)
    print("*" * 30)
    print(
        "Values: Median Blur Kernel Size : {} Opening Kernel Size : {} Canny : {}".format(median_blur_th,
                                                                                          kernel_size_th,
                                                                                          canny_threshold_th))
    print("*" * 30)
    return len(contours_filtered)


window_name = "Trackbars"
cv.namedWindow(window_name)
cv.resizeWindow(window_name, 700, 200)

cv.createTrackbar(canny_threshold, window_name, canny_threshold_value, canny_threshold_value_max, morphology_operations)

cv.createTrackbar(median_blur, window_name, median_blur_value, median_blur_value_max, morphology_operations)

cv.createTrackbar(morph_operations_kernel_size, window_name, morph_value, morph_value_max, morphology_operations)

result_window = "results"

#src_image = cv.imread(
#    r"C:\Users\Ankur\Desktop\Uni Siegen\SEM5\Eye Detection\Project-code-Ankur\master-thesis-eye-tracking\Results\Hough21_01_2022_16_01_18\hough_circle360.png")

folder_path = r"C:\Users\Ankur\Desktop\Uni Siegen\SEM5\Eye Detection\Project-code-Ankur\master-thesis-eye-tracking\Results\Hough21_01_2022_16_01_18"
#folder_path = r"C:\Users\Ankur\Desktop\Uni Siegen\SEM5\Eye Detection\Project-code-Ankur\master-thesis-eye-tracking\Results\infrared"
logger.info("Folder Name :{}".format(folder_path))
ellipse_detected = 0
total_images = len(os.listdir(folder_path))
for path in os.listdir(folder_path):
    src_image_name = os.path.join(folder_path, path)
    print("Image Name {}".format(src_image_name))
    src_image = cv.imread(src_image_name)
    key = cv.waitKey(10)
    ellipse_detected += morphology_operations(0)

    if key == 27:
        break

logger.info("Ellipse Detected {}, Total Images {}, Percentage {}".format(ellipse_detected,total_images,ellipse_detected/total_images))

cv.waitKey(1)
cv.destroyAllWindows()
logger.info("EXPERIMENT END")
logger.info("*"*50)
