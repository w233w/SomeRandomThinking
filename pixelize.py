import cv2
from matplotlib import pyplot as plt
import numpy as np

def pixelize(image, density):
    img = cv2.imread(image)
    h, w, path = img.shape
    if np.gcd(h, w)%density!=0:
        print(h, w, np.gcd(h,w))
        raise ValueError("Image's height and width must be dividable by density")
    raw = cv2.split(img)
    n_h, n_w = h//density, w//density
    new_img = []
    for layer in range(path):
        color = np.zeros((n_h, n_w), dtype=np.int16)
        for i in range(n_h):
            for j in range(n_w):
                block = raw[layer][i*density:i*density+density, j*density:j*density+density]
                pixel = np.round(block.mean(), 0)
                color[i][j] = pixel
        new_img.append(color)
    b, g, r = new_img
    pixel_img = cv2.merge([r, g, b])
    plt.imshow(pixel_img)
    plt.show()
                

if __name__ == "__main__":
    pixelize("test.jpg", 10)
