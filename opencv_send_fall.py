import cv2
import numpy as np
import random

pile_obs = np.zeros([50], np.int16)
for _ in range(2000):
    p = int(random.normalvariate(24, 10))
    try:
        pile_obs[p] += 1
    except:
        pass

while True:
    for i in range(50):
        left = pile_obs[i - 1 : i]
        true_left = pile_obs[i]
        right = pile_obs[i + 1 : i + 2]
        true_right = pile_obs[i]
        if len(left) == 1:
            true_left = left[0]
        if len(right) == 1:
            true_right = right[0]
        if true_left > true_right:
            if pile_obs[i] - true_right > 1:
                pile_obs[i] -= 1
                pile_obs[i + 1] += 1
        elif true_left < true_right:
            if pile_obs[i] - true_left > 1:
                pile_obs[i] -= 1
                pile_obs[i - 1] += 1
        else:
            l = random.randint(0, 1)
            if l:
                if pile_obs[i] - true_left > 1:
                    pile_obs[i] -= 1
                    pile_obs[i - 1] += 1
            else:
                if pile_obs[i] - true_right > 1:
                    pile_obs[i] -= 1
                    pile_obs[i + 1] += 1

    image = np.zeros([400, 200])
    for x, v in enumerate(pile_obs):
        cv2.rectangle(image, [4 * x, 400 - 4 * v], [3 + 4 * x, 400], 1, -1)
    cv2.imshow("1", image)
    mykey = cv2.waitKey(1)
    # 按q退出循环,0xFF是为了排除一些功能键对q的ASCII码的影响
    if mykey & 0xFF == ord("q"):
        break

cv2.destroyAllWindows()
