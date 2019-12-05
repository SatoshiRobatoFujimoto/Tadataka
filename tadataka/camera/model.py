from tadataka.camera.normalizer import Normalizer
from tadataka.camera.parameters import CameraParameters
from tadataka.camera.distortion import FOV


def parse_(string):
    params = string.split(' ')
    distortion_type = params[0]
    params = [float(v) for v in params[1:]]
    camera_parameters = CameraParameters.from_params(params[0:4])
    if distortion_type == "FOV":
        distortion_model = FOV.from_params(params[4:])
    else:
        ValueError("Unknown distortion model: " + distortion_type)
    return CameraModel(camera_parameters, distortion_model)


class CameraModel(object):
    def __init__(self, camera_parameters, distortion_model):
        self.normalizer = Normalizer(camera_parameters)
        self.camera_parameters = camera_parameters
        self.distortion_model = distortion_model

    def undistort(self, keypoints):
        return self.distortion_model.undistort(
            self.normalizer.normalize(keypoints)
        )

    def distort(self, normalized_keypoints):
        return self.normalizer.inverse(
            self.distortion_model.undistort(normalized_keypoints)
        )

    def __str__(self):
        distortion_type = type(self.distortion_model).__name__
        params = self.camera_parameters.params + self.distortion_model.params
        return ' '.join([distortion_type] + [str(v) for v in params])

    @staticmethod
    def fromstring(string):
        return parse_(string)
