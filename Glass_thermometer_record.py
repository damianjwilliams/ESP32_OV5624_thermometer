import urllib.request
import cv2
import numpy as np
import time
import csv
from datetime import datetime

font = cv2.FONT_HERSHEY_SIMPLEX
bottomLeftCornerOfText = (10,600)
fontScale = 1
fontColor = (0,0,0)
thickness = 2
lineType = 2

url = 'http://192.168.4.1/capture'

# Calibration left thermometer
#temperature value 1
t1_F1 = 70
#pixel location of temperature in y axis 1
t1_P1 = 245
#temperature value 2
t1_F2 = 40
#pixel location of temperature in y axis 2
t1_P2 = 552

# Calibration right thermometer (if used)
t2_F1 = 70
t2_P1 = 229
t2_F2 = 40
t2_P2 = 535

# range of blue colors that will be detected based on blue image acquired before
img = cv2.imread("/Users/damianwilliams/Desktop/blue.jpg")
hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
mu, sig = cv2.meanStdDev(hsv)

#--------------------------##------------Range of blue_values______________##

a = 15
#--------------------------##----------------------------------------------##


#--------------------------##------------threshold for rectangle size defined as liquid column size (ignores small
# area)______________##

minArea = 2000
#--------------------------##-------------------------------------------------------------------------------------------------------------##


change_resolution= urllib.request.urlopen("http://192.168.4.1/a?ql=6", timeout=5)
time.sleep(2)
change_resolution.close()

def CalculateTemp(temp1, temp2, pixel1, pixel2, yval):
    pix_per_deg = (pixel2 - pixel1) / (temp2 - temp1)
    pixels_diff = yval - pixel2
    delta_fah = pixels_diff / pix_per_deg
    fahrenheit = temp2 + delta_fah
    celcius = ((fahrenheit - 32) * (5 / 9))
    temps = [celcius,fahrenheit]
    return temps



idx = 0

while True:

    with open("/Users/damianwilliams/Desktop/test_data.csv", "a") as f:
        writer = csv.writer(f, delimiter=",")

    try:

        imgResp = urllib.request.urlopen(url, timeout=10)
        print(imgResp)

        imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
        img = cv2.imdecode(imgNp, -1)

        #Crop image
        img = img[400:1000 + 50, 600:1500 + 100]
        #cv2.imshow("orig_thresh", img)

        Image_for_detection = img
        Thermometer_image = img

        height_image, width_image, channels_image = Image_for_detection.shape
        print(f'image dimensions (pixels):, height =  {height_image}, width = {width_image}')

        # Mask for blue color
        therm_hsv = cv2.cvtColor(Image_for_detection, cv2.COLOR_BGR2HSV)
        therm_hsv = cv2.inRange(therm_hsv, mu - a * sig, mu + a * sig)

# --------------------------##------------Parameters that will fill any small gaps in the color mask that
        # encompasses the thermometer-------##


        kernel = np.ones((3, 3), np.uint8)
        dilated_image = cv2.dilate(therm_hsv, kernel, iterations=1)

# --------------------------##----------------------------------------------##

        mask_image = cv2.cvtColor(dilated_image, cv2.COLOR_GRAY2RGB)
        contours, hierarchy = cv2.findContours(image=dilated_image, mode=cv2.RETR_TREE, method=cv2.CHAIN_APPROX_NONE)

        number_regions_found = 0

        for cnt in contours:
            x, y, w, h = cv2.boundingRect(cnt)
            area = cv2.contourArea(cnt)

            if area > minArea:



                #defines area where left thermometer would be found
                if x < 500:

                    ##########################################################################################
                    Thermometer_image = cv2.rectangle(Thermometer_image, (x, y), (x + w, y + h), (0, 255, 0), 1)
                    mask_image = cv2.rectangle(mask_image, (x, y), (x + w, y + h), (0, 255, 0), 1)
                    ##########################################################################################

                    therm_reading_1 = CalculateTemp(t1_F1, t1_F2, t1_P1, t1_P2, y)
                    therm_1_stringC = "%.1f" % round(therm_reading_1[0], 1)
                    print("Therm 1 Calculated_value: " + therm_1_stringC)
                    therm_1_stringF = "%.1f" % round(therm_reading_1[1], 1)
                    print("Therm 1 Calculated_value: " + therm_1_stringF)
                    number_regions_found = 1

                else:
                    #################################################################################################
                    Thermometer_image = cv2.rectangle(Thermometer_image, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    mask_image = cv2.rectangle(mask_image, (x, y), (x + w, y + h), (0, 0, 255), 1)
                    #################################################################################################

                    therm_reading_2 = CalculateTemp(t2_F1, t2_F2, t2_P1, t2_P2, y)
                    therm_2_stringC = "%.1f" % round(therm_reading_2[0], 1)
                    print("Therm 2 Calculated_value C: " + therm_2_stringC)
                    therm_2_stringF = "%.1f" % round(therm_reading_2[1], 1)
                    print("Therm 2 Calculated_value C: " + therm_2_stringF)

                    number_regions_found = number_regions_found + 1

                if (number_regions_found == 2):

                    vis = np.concatenate((mask_image, Thermometer_image), axis=1)

                    #######################################################################
                    cv2.imshow("Image used for detection", vis)
                    #######################################################################

                    # Save data in csv file
                    now = datetime.now()
                    dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
                    current_time = time.time()
                    for_log = [current_time, dt_string, therm_1_stringC, therm_2_stringC, therm_1_stringF,
                    therm_2_stringF]


                    #######################################################################
                    with open("/Users/damianwilliams/Desktop/test_data.csv", "a") as f:
                        writer = csv.writer(f, delimiter=",")
                        writer.writerow(for_log)
                    ######################################################################

                    # Create image with annotation
                    place = (f"{dt_string} \n"
                             f"{therm_1_stringF} F, {therm_1_stringC} C\n"
                             f"{therm_2_stringF} F, {therm_2_stringC} C\n")

                    position = (30, 30)
                    text = place
                    font_scale = 0.75
                    color = (255, 0, 0)
                    thickness = 2
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    line_type = cv2.LINE_AA
                    text_size, _ = cv2.getTextSize(text, font, font_scale, thickness)
                    line_height = text_size[1] + 5
                    x, y0 = position
                    for i, line in enumerate(text.split("\n")):
                        y = y0 + i * line_height
                        img = cv2.putText(img,
                                    line,
                                    (x, y),
                                    font,
                                    font_scale,
                                    color,
                                    thickness,
                                    line_type)

                    #######################################################################################

                    #Save_name = "/Users/damianwilliams/Desktop/Image_set/thermometer_" + str(idx) + ".jpg"
                    #cv2.imwrite(Save_name, img)
                    #cv2.imshow('Thermometer_images', img)
                    ########################################################################################


                    print(idx)
                    idx = idx + 1





    except Exception as e:
        print(e)
        print("reset")
    pass

    cv2.waitKey(1000)
    cv2.destroyAllWindows()


