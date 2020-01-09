import os
import time

import numpy as np
import torch

from hardware.camera import RealSenseCamera
from inference.post_process import post_process_output
from utils.data.camera_data import CameraData
from utils.dataset_processing.grasp import detect_grasps


class GraspGenerator:
    def __init__(self, saved_model_path, cam_id):
        self.saved_model_path = saved_model_path
        self.camera = RealSenseCamera(device_id=cam_id)

        self.saved_model_path = saved_model_path
        self.model = None
        self.device = None

        self.cam_data = CameraData(include_depth=True, include_rgb=True)

        # Connect to camera
        self.camera.connect()

        # Load camera pose and depth scale (from running calibration)
        self.cam_pose = np.loadtxt('saved_data/camera_pose.txt', delimiter=' ')
        self.cam_depth_scale = np.loadtxt('saved_data/camera_depth_scale.txt', delimiter=' ')

        homedir = os.path.join(os.path.expanduser('~'), "grasp-comms")
        self.grasp_request = os.path.join(homedir, "grasp_request.npy")
        self.grasp_available = os.path.join(homedir, "grasp_available.npy")
        self.grasp_pose = os.path.join(homedir, "grasp_pose.npy")

    def load_model(self):
        print('Loading model... ')
        self.model = torch.load(self.saved_model_path)
        self.device = torch.device("cuda:0")

    def generate(self):
        # Get RGB-D image from camera
        image_bundle = self.camera.get_image_bundle()
        rgb = image_bundle['rgb']
        depth = image_bundle['aligned_depth']
        x, depth_img, rgb_img = self.cam_data.get_data(rgb=rgb, depth=depth)

        # Predict the grasp pose using the saved model
        with torch.no_grad():
            xc = x.to(self.device)
            pred = self.model.predict(xc)

        q_img, ang_img, width_img = post_process_output(pred['pos'], pred['cos'], pred['sin'], pred['width'])
        grasp = detect_grasps(q_img, ang_img, width_img)[0]

        # Get grasp position from model output
        pos_z = depth[grasp.center[0]][grasp.center[1]] * self.cam_depth_scale
        pos_x = np.multiply(grasp.center[1] - self.camera.intrinsics[0][2], pos_z / self.camera.intrinsics[0][0])
        pos_y = np.multiply(grasp.center[0] - self.camera.intrinsics[1][2], pos_z / self.camera.intrinsics[1][1])
        if pos_z == 0:
            return
        target = np.asarray([pos_x, pos_y, pos_z])
        target.shape = (3, 1)

        # Convert camera to robot coordinates
        camera2robot = self.cam_pose
        target_position = np.dot(camera2robot[0:3, 0:3], target) + camera2robot[0:3, 3:]

        target_position = target_position[0:3, 0]
        grasp_pose = np.append(target_position, grasp.angle)

        np.save(self.grasp_pose, grasp_pose)

    def run(self):
        while True:
            if np.load(self.grasp_request):
                self.generate()
                np.save(self.grasp_request, 0)
                np.save(self.grasp_available, 1)
            else:
                time.sleep(0.1)
