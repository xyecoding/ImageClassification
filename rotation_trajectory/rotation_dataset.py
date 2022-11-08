# create the rotation dataset.
# output tensors whose dimension are [N, C, H, W]
# where N is the batch size and also the number of 
# angles within [0, 360].  

# Each batch contains an image rotated by N angles.

import numbers
import random
from torchvision import datasets, transforms
import os
import torch
import numpy as np
import math
from PIL import Image, ImageOps

class RandomRotate(object):
    def __init__(self, angle_range=(-180, 180), num_angles = 100, fill='black'):
        assert isinstance(angle_range, tuple) and len(angle_range) == 2 and angle_range[0] <= angle_range[1]
        assert isinstance(fill, numbers.Number) or isinstance(fill, str) or isinstance(fill, tuple)
        self.angle_range = angle_range
        self.num_angles = num_angles
        self.fill = fill

    def __call__(self, img):
        angle_min, angle_max = self.angle_range
        img_org = img
        img_out = None
        for i in range(self.num_angles):
            img = img_org.copy()
            angle = angle_min + i * (angle_max - angle_min) / self.num_angles
            theta = math.radians(angle)
            w, h = img.size
            diameter = math.sqrt(w * w + h * h)
            theta_0 = math.atan(float(h) / w)
            w_new = diameter * max(abs(math.cos(theta-theta_0)), abs(math.cos(theta+theta_0)))
            h_new = diameter * max(abs(math.sin(theta-theta_0)), abs(math.sin(theta+theta_0)))
            pad = math.ceil(max(w_new - w, h_new - h) / 2)
            img = ImageOps.expand(img, border=int(pad), fill=self.fill)
            img = img.rotate(angle, resample=Image.BICUBIC)
            img = np.asarray(img.crop((pad, pad, w + pad, h + pad)))
            if i == 0:
                img_out = img
            else:
                img_out = np.dstack((img_out, img))
        img_out = torch.from_numpy(np.expand_dims(img_out, axis = 1)).permute(3, 1, 0, 2)
        return  img_out


def crease_rot_dataset(use_cuda= True, batch_size = 1):
    kwargs = {'num_workers': 1, 'pin_memory': True} if use_cuda else {}
    data_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')

    test_loader = torch.utils.data.DataLoader(
    datasets.MNIST(data_path, train=False, transform=transforms.Compose([
                    transforms.Resize(32),
                    RandomRotate((-180, 180)),
                    transforms.ToTensor(),
                    transforms.Normalize((0.1307,), (0.3081,))
                ])),
    batch_size=batch_size, shuffle=True, **kwargs)
    return test_loader
