""" This modules contains the preprocessing pipelines. A preprocessing pipeline should
accept a sample from a dataset and return a tensor that can be used as input for the
network. The preprocessing pipeline should also store intermediate results in the
intermediate_results dictionary. These results can be used in the end for closer evauation
and debugging.
Since a pipeline is not used in backpropagation it is not necessary to implement it as
a torch.nn.Module.
A pipeline should consist out of multiple submodules that are called in a specific order.
For clarity it should be avoided to have logic inthe pipeline itself. Instead the logic
should be implemented in the submodules. The pipeline itself should only manage the
flow of information through the submodules. If a pipeline has no or only a single
submodule it might be more suitable to implement it as a submodule instead of a pipeline
for improved reusability. It is also good practice to have the pipeline accept (multiple)
submodules as arguments. This way the pipeline can be used with different submodules
which increases modularity.
Somteimes it might be useful to have a subpipeline that is used in multiple pipelines.
This subpipeline will output an intermediate result that is used in multiple pipelines
but not the final result. Keep in mind that you need to manage the intermediate result 
of the subpipeline yourself.
"""

from abc import abstractmethod, ABC
from typing import Any, Dict

from nptyping import NDArray, Shape, Float, Int

from contact_graspnet.datatypes import (
    DatasetSample,
    YCBSimulationDataSample,
    OrigExampleDataSample,
)
from . import custom_transforms as CT


class PreprocessorBase(ABC):
    def __init__(self):
        super().__init__()
        self.intermediate_results: Dict[str, Any] = {}

    @abstractmethod
    def __call__(self, sample: DatasetSample) -> NDArray[Shape["N,3"], Float]:
        pass


class OrigExampleDataPreprocessor(PreprocessorBase):
    def __init__(
        self,
        segmenter: CT.SegmenterPixel,
        # depth2points_converter: CT.OrigDepth2Points,
        img2cam_converter: CT.Img2CamCoords,
        z_clipper: CT.ZClipper,
    ):
        super().__init__()

        self.segmenter = segmenter
        self.img2cam_converter = img2cam_converter
        self.z_clipper = z_clipper

    def __call__(self, sample: OrigExampleDataSample) -> NDArray[Shape["N,3"], Float]:
        points_img, points_colors = self.segmenter(
            sample.segmentation, sample.depth, sample.rgb
        )

        points_cam = self.img2cam_converter(points_img, sample.cam_intrinsics)

        points, points_colors = self.z_clipper(points_cam, points_colors)

        self.intermediate_results["pointcloud_colors"] = points_colors

        return points


# class YCBSimulationPreprocessor(PreprocessorBase):
#     def __init__(self, z_clipper: CT.ZClipper, segmenter: CT.YCBSegmenter = None):
#         super().__init__()

#         self.z_clipper = z_clipper
#         self.segmenter = segmenter

#     def __call__(self, sample: YCBSimulationDataSample) -> NDArray[Shape["N,3"], Float]:
#         points = sample.points
#         points_color = sample.points_color

#         if self.segmenter is not None:
#             points, points_color = self.segmenter(sample)

#         if self.z_clipper is not None:
#             points, points_color = self.z_clipper(points, points_color)

#         self.intermediate_results["pointcloud_colors"] = points_color

#         return points


# other preprocessors for other datasets or with completely different preprocessing pipelines ...
