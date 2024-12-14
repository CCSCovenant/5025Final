import configparser
import os
import numpy as np
import trimesh
from data import renderObj
from data.renderObj import rotate_trimesh
from cal_curvature2 import cal_curvature2

config = configparser.ConfigParser()
config.read('config.ini')
Thingi10K = config['SETTING']['DataPath']
sample_path = config['SETTING']['NpzOutPath']
SampleStep = (int)(config['SETTING']['SampleStep'])
maxNumSamplePreObj = (int)(config['SETTING']['maxNumSamplePreObj'])

def cal2(objPth):
    fov_list = [4]
    mesh = None
    try:
        mesh = trimesh.load(objPth,force='mesh')
    except:
        pass
    if mesh is not None:
        for fov in fov_list:
            c_mesh = mesh.copy()
            c_mesh = renderObj.normalize_mesh(c_mesh, np.pi / fov)
            c_mesh.remove_degenerate_faces()
            for i in range(maxNumSamplePreObj):
                abspath = os.path.dirname(objPth)
                relative_path = os.path.relpath(abspath, Thingi10K)
                sample_save_path = os.path.join(sample_path, relative_path)
                filename = str(fov) + '_' + str(i) + 'npz'
                os.makedirs(sample_save_path, exist_ok=True)
                sample_save_path = os.path.join(sample_save_path, filename)
                if not os.path.exists(sample_save_path):
                    c1 = None
                    rotate_angle = np.random.rand(3) * 360
                    rotatedMesh = rotate_trimesh(c_mesh, [0, 1, 0], rotate_angle[0])
                    rotatedMesh = rotate_trimesh(rotatedMesh, [1, 0, 0], rotate_angle[1])
                    rotatedMesh = rotate_trimesh(rotatedMesh, [0, 0, 1], rotate_angle[2])
                    c1, c2, B, valid_map,apparent_angle, vertex_3d = cal_curvature2(rotatedMesh, np.pi / fov,sample=SampleStep)
                    if c1 is not None:
                        np.savez(sample_save_path, c1=c1, c2=c2, contours=B,valid_map=valid_map, rotations=rotate_angle, angle=apparent_angle,
                                 vertex_3d=vertex_3d)
                else:
                    pass

