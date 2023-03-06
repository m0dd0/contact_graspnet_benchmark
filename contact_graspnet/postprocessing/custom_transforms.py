"""This module contains the custom transforms that are used in the postprocessing pipelines.
They should be as concise as possible and only contain the logic that is necessary to
execute a singe transformation step.
They might also be used directly in a Compose to make a descriptive pipeline.
"""
from typing import List

from nptyping import NDArray, Shape, Float
import numpy as np

from contact_graspnet.datatypes import GraspCam


class TopScoreFilter:
    def __init__(self, top_k: int = 1):
        self.top_k = top_k

    def __call__(self, grasps: List[GraspCam]) -> List[GraspCam]:
        if len(grasps) <= self.top_k:
            return grasps

        return sorted(grasps, key=lambda grasp: grasp.score, reverse=True)[: self.top_k]


class Cam2WorldCoordConverter:
    def __init__(self):
        pass

    def __call__(
        self,
        p_cam: NDArray[Shape["3"], Float],
        cam_pos: NDArray[Shape["3"], Float],
        cam_rot: NDArray[Shape["3, 3"], Float],
    ) -> NDArray[Shape["3"], Float]:
        p_cam = p_cam.reshape(3, 1)
        cam_pos = cam_pos.reshape(3, 1)
        cam_rot_inv = np.linalg.inv(cam_rot)

        p_world = cam_rot_inv @ p_cam + cam_pos

        p_world = p_world.flatten()

        return p_world


class Cam2WorldOrientationConverter:
    def __init__(self):
        pass

    def __call__(
        self,
        orientation: NDArray[Shape["3, 3"], Float],
        cam_rot: NDArray[Shape["3, 3"], Float],
    ) -> NDArray[Shape["3, 3"], Float]:
        cam_rot_inv = np.linalg.inv(cam_rot)

        orientation_world = cam_rot_inv @ orientation

        return orientation_world
