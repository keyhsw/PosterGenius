import numpy as np
from PIL import Image
# all_result_imgs = []
# all_result_imgs.append(np.zeros((1280,300,3)))
# all_result_imgs.append(np.zeros((1280,300,3)))
# all_result_imgs.append(np.zeros((1280,720,3)))
# all_result_imgs.append(np.zeros((1280,720,3)))
# all_result_imgs.append(np.zeros((300,720,3)))
# all_result_imgs.append(np.zeros((300,720,3)))
# w1 = 300
# w2 = 1280
# w3 = 720
# w_set = w1*2 + w3*2 + 50*3 + 20*2
# h_set = w1*2 + w2 + 50*2 + 20*2
# set_image = np.ones((h_set,w_set,3))
set_image = np.ones((1280,720,3))
set_image[:,:,0] = 220
set_image[:,:,1] = 220
set_image[:,:,2] = 180
# set_image[20+w1+50:20+w1+50+w2,20:20+w1] = np.array(all_result_imgs[0])
# set_image[20+w1+50:20+w1+50+w2,20+w1+50+w3+50:20+w1+50+w3+50+w1] = np.array(all_result_imgs[1])
# set_image[20+w1+50:20+w1+50+w2,20+w1+50:20+w1+50+w3] = np.array(all_result_imgs[2])
# set_image[20+w1+50:20+w1+50+w2,20+w1+50+w3+50+w1+50:20+w1+50+w3+50+w1+50+w3] = np.array(all_result_imgs[3])
# set_image[20:20+w1,20+ w1+50:20+ w1+50+w3] = np.array(all_result_imgs[4])
# set_image[20+w1+50+w2+50:20+w1+50+w2+50+w1,20+ w1+50:20+ w1+50+w3] = np.array(all_result_imgs[5])
set_image = Image.fromarray(np.uint8(set_image))
set_image.save("canvas_v.jpg")
#all_result_imgs.append(Image.fromarray(set_image))
