import urllib.request
import cv2
import numpy as np
import time

#Camera URL (from arduino serial monitor)
url = 'http://192.168.4.1/capture'

#ql value sent to the camera changes the resolution 5 = 1600 x 1200
Change_pic_resolution = urllib.request.urlopen("http://192.168.4.1/a?ql=5", timeout=2)
time.sleep(2)
Change_pic_resolution.close()



while True:

        try:

            #Command to get image send from server
            imgResp = urllib.request.urlopen(url, timeout=5)
            print(imgResp)

            imgNp = np.array(bytearray(imgResp.read()), dtype=np.uint8)
            img = cv2.imdecode(imgNp, -1)
            cv2.imshow('Thermometer_images', img)

            #Crop the image so the ideal region of thermometer is displayed
            img = img[400:1000 + 50, 600:1500 + 100]

            Save_name = "/Users/damianwilliams/Desktop/thermometer.jpg"
            cv2.imwrite(Save_name, img)
            print("image saved!")

            break


        except Exception as e:
            print(e)
            print("no image")
        pass

        cv2.waitKey(1000)
        cv2.destroyAllWindows()
