
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
path = r"C:\Users\SYX\Pictures\未标题-1.png"

img = np.array(Image.open(path).convert('L'))

rows, cols = img.shape
for i in range(rows):
    for j in range(cols):
        if (img[i, j] <= 128):
            img[i, j] = 0
        else:
            img[i, j] = 1

plt.figure("lena")
# fig=plt.figure(figsize=(400,400))

plt.imshow(img, cmap='gray')
plt.axis('off')
# plt.savefig("ok.png")
print(img.shape)
plt.savefig("okk.png")
plt.show()

