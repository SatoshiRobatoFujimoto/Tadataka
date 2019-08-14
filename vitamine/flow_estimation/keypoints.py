from autograd import numpy as np

from skimage.feature import (match_descriptors, corner_peaks, corner_harris,
                             BRIEF)
from skimage import transform

from vitamine.coordinates import yx_to_xy


brief = BRIEF(
    descriptor_size=512,
    patch_size=64,
    mode="uniform",
    sigma=0.1
)


def extract_brief(image):
    keypoints = corner_peaks(corner_harris(image), min_distance=5)
    brief.extract(image, keypoints)
    keypoints = keypoints[brief.mask]
    descriptors = brief.descriptors
    return yx_to_xy(keypoints), descriptors


def extract_orb(image):
    from skimage.feature import ORB
    orb = ORB(n_keypoints=100)
    orb.detect_and_extract(image)
    return yx_to_xy(orb.keypoints), orb.descriptors


extract_keypoints = extract_brief


def match(descriptors0, descriptors1):
    return match_descriptors(descriptors0, descriptors1,
                             metric="hamming", cross_check=False)


class MatchOneToMany(object):
    def __init__(self, base_image):
        self.keypoints0, self.descriptors0 = extract_keypoints(base_image)
        self.base_image = base_image

    def compute(self, images):
        n_images = images.shape[0]
        n_keypoints = self.keypoints0.shape[0]

        keypoints = np.full((n_images, n_keypoints, 2), np.nan)
        for i, image in enumerate(images):
            keypoints1, descriptors1 = extract_keypoints(image)
            matches01 = match(self.descriptors0, descriptors1)
            keypoints[i, matches01[:, 0]] = keypoints1[matches01[:, 1]]
        return keypoints
