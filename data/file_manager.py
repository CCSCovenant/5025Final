#data/file_manager.py

import json
import os

class StrokeFileManager:
    def __init__(self, stroke_manager_2d, stroke_manager_3d):
        self.stroke_manager_2d = stroke_manager_2d
        self.stroke_manager_3d = stroke_manager_3d

    def save_strokes(self, filepath, camera_rot, camera_dist):
        """
        将当前的camera信息 + 2D和3D笔画保存到JSON文件
        """
        data = {}
        data["camera"] = {
            "rot_x": camera_rot[0],
            "rot_y": camera_rot[1],
            "distance": camera_dist
        }

        # 保存2D
        strokes_2d_data = []
        for stroke2d in self.stroke_manager_2d.get_all_strokes():
            stroke_dict = {
                "stroke_id": stroke2d.stroke_id,
                "points_2d": stroke2d.points_2d,
                "camera_rot": list(stroke2d.camera_rot) if hasattr(stroke2d,"camera_rot") else [0.0,0.0],
                "camera_dist": stroke2d.camera_dist if hasattr(stroke2d,"camera_dist") else 3.0
            }
            strokes_2d_data.append(stroke_dict)
        data["strokes_2d"] = strokes_2d_data

        # 保存3D
        strokes_3d_data = []
        for stroke3d in self.stroke_manager_3d.get_all_strokes():
            coords_list = stroke3d.coords_3d.tolist()  # numpy -> list
            stroke_dict = {
                "stroke_id": stroke3d.stroke_id,
                "coords_3d": coords_list
            }
            strokes_3d_data.append(stroke_dict)
        data["strokes_3d"] = strokes_3d_data

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"Strokes saved to {filepath}.")

    def load_strokes(self, filepath):
        """
        加载JSON文件, 并分别写回 stroke_manager_2d / stroke_manager_3d 的数据结构。
        同时返回camera参数(给外部设置camera用)。
        """
        if not os.path.exists(filepath):
            print("File not found:", filepath)
            return None, None

        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 清空manager旧数据
        self.stroke_manager_2d.strokes_2d.clear()
        self.stroke_manager_3d.strokes_3d.clear()

        camera_data = data.get("camera", {})
        camera_rot = (camera_data.get("rot_x",0.0), camera_data.get("rot_y",0.0))
        camera_dist = camera_data.get("distance", 3.0)

        # 加载2D
        strokes_2d_data = data.get("strokes_2d", [])
        for s2d_dict in strokes_2d_data:
            from data.stroke_2d import Stroke2D
            stroke_id = s2d_dict["stroke_id"]
            points_2d = s2d_dict["points_2d"]
            st = Stroke2D(stroke_id, points_2d)

            # 如果需要恢复当时的camera信息到笔画，可做：
            st.camera_rot = tuple(s2d_dict.get("camera_rot",(0.0,0.0)))
            st.camera_dist = s2d_dict.get("camera_dist", 3.0)

            self.stroke_manager_2d.add_stroke(st)

        # 加载3D
        strokes_3d_data = data.get("strokes_3d", [])
        for s3d_dict in strokes_3d_data:
            from data.stroke_3d import Stroke3D
            stroke_id = s3d_dict["stroke_id"]
            coords_3d = s3d_dict["coords_3d"]
            import numpy as np
            coords_3d_array = np.array(coords_3d, dtype=np.float32)
            st3d = Stroke3D(coords_3d_array, stroke_id=stroke_id)
            self.stroke_manager_3d.add_stroke(st3d)

        print(f"Strokes loaded from {filepath}.")
        return camera_rot, camera_dist
