from numpy import ndarray
from aicssegmentation.core.pre_processing_utils import image_smoothing_gaussian_3d

class MppModel:

    def smooth_image(self, image_data) -> ndarray:
        return image_smoothing_gaussian_3d(image_data, sigma=3.0)
