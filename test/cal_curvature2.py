import numpy
import shapely
from shapely.geometry import polygon
from trimesh.intersections import mesh_plane
import numpy as np
from shapely import Polygon, union_all
import networkx as nx

def normalize(v):
    # 计算向量的长度（范数）
    norm = np.linalg.norm(v)
    # 避免除以0
    if norm == 0:
       return v
    # 返回归一化的向量
    return v / norm

def compute_camera_matrices(fov, camera_position):
    # 首先，定义图像平面的大小
    img_width = 480
    img_height = 480

    # 计算焦距
    f = img_width / (2 * np.tan(fov / 2))

    # 内参矩阵
    K = np.array([[f, 0, img_width / 2],
                  [0, f, img_height / 2],
                  [0, 0, 1]])

    # 外参矩阵
    # 我们假设相机看向 -Z 方向，并且相机的 "上" 方向是 +Y 方向。
    R = np.array([[1, 0, 0],
                  [0, 1, 0],
                  [0, 0, -1]])

    T = -R @ camera_position

    RT = np.hstack([R, T.reshape(3, 1)])

    return K, RT
def perspective_matrix(fov, aspect, near, far):
    # fov 应该是以度为单位，将其转换为弧度
    fov_rad = np.deg2rad(fov)

    # 计算透视投影矩阵的元素
    f = 1 / np.tan(fov_rad / 2)
    range_recip = 1 / (near - far)

    # 创建投影矩阵
    projection_matrix = np.array([
        [f / aspect, 0, 0, 0],
        [0, f, 0, 0],
        [0, 0, (near + far) * range_recip, 2 * near * far * range_recip],
        [0, 0, -1, 0],
    ])

    return projection_matrix
def calculate_angle(vec1, vec2):
    # 计算两个向量的点积
    dot_product = np.dot(vec1, vec2)

    # 计算两个向量的模
    vec1_norm = np.linalg.norm(vec1)
    vec2_norm = np.linalg.norm(vec2)

    # 计算两个向量的夹角
    cos_theta = dot_product / (vec1_norm * vec2_norm)
    angle_in_radians = np.arccos(np.clip(cos_theta, -1.0, 1.0))

    return angle_in_radians
def projected(mesh,
              normal,
              matrix,
              **kwargs):
    from trimesh.path import Path2D
    from trimesh.exchange.load import load_path

    projection = projected(
        mesh=mesh, normal=normal,matrix=matrix,**kwargs)
    if projection is None:
        return Path2D()
    return load_path(projection)
def perspective_projected(mesh,
              K,RT,):

    vertices_2D = map_points_to_image(mesh.vertices,K,RT)
    polygons = []
    '''
    fig, ax = plt.subplots(dpi=1000)
    debug
    '''
    for face in mesh.faces:
        vlist = [vertices_2D[face[0]],vertices_2D[face[1]],vertices_2D[face[2]]]
        trig = Polygon(vlist)
        polygons.append(trig)
        '''
        draw_trig = [vertices_2D[face[0]],vertices_2D[face[1]],vertices_2D[face[2]],vertices_2D[face[0]]]
        draw_trig = np.asarray(draw_trig)
        ax.plot(draw_trig[:,0],draw_trig[:,1],linewidth=0.1)
        '''
    '''
    ax.scatter(vertices_2D[:,0],vertices_2D[:,1],s=0.1,edgecolors='none')
    ax.axis('equal')
    plt.title('projected triangles')
    plt.show()
    '''
    final = union_all(polygons)

    return final,mesh.edges_sorted,vertices_2D
def map_points_to_image(points_3d, K, RT):
    # 把点从世界坐标系变换到相机坐标系
    points_cam = points_3d @ RT[:, :3].T + RT[:, 3]

    # 把点从相机坐标系映射到图像平面
    points_2d = points_cam @ K.T

    # 进行透视除法，使得点的坐标是归一化的齐次坐标
    div = points_2d[:, 2, np.newaxis]
    points_2d = points_2d / div

    return points_2d[:, :2]  # 只返回x和y坐标
def project_point_to_plane(point, plane_point, plane_normal):
    # 标准化法向量
    plane_normal = plane_normal / np.linalg.norm(plane_normal)
    # 计算点到平面的距离
    d = np.dot(np.subtract(point, plane_point), plane_normal)
    # 计算投影点
    projected_point = np.subtract(point, np.multiply(d, plane_normal))
    return projected_point



def cal_curvature2(rotatedMesh, fov,sample=2):
    mesh = rotatedMesh
    mesh.merge_vertices()
    mesh.remove_duplicate_faces()
    camera_pose = np.array([0, 0, 1]) #look at 0,0,0
    K, RT = compute_camera_matrices(fov, camera_pose)
    valid_polygon = True

    try:
        path2d, edges, vertices_2D = perspective_projected(mesh, K, RT)
    except:
        valid_polygon = False
    if valid_polygon:
        # contours = edge_to_contours(vertices_2D,edges)
        if isinstance(path2d, shapely.Polygon):
            path2d = polygon.orient(path2d, sign=1.0)
            A = np.array(vertices_2D)
            B = np.array(path2d.exterior.xy)
            B = B.T
            A1 = A[:, 0]
            B1 = B[:, 0]
            sort_idx_1 = A1.argsort()
            x_index = sort_idx_1[np.searchsorted(A1, B1, sorter=sort_idx_1)]
            x_final = np.zeros_like(x_index)
            mesh_vertex_faces = mesh.vertex_faces
            mesh_vertex_3d = mesh.vertices
            mesh_faces = mesh.faces
            mesh_vertex_normals = mesh.vertex_normals
            coutour_filter = []
            for i, x in enumerate(x_index):
                point = A[x]
                contour_point = B[i]
                if i == len(x_index)-1:
                    break
                if np.allclose(point, contour_point):
                    x_final[i] = x
                    coutour_filter.append(True)
                else:
                    x_final[i] = -1
                    coutour_filter.append(False)
            coutour_filter.append(False)
            coutour_filter = np.asarray(coutour_filter)
            B = B[coutour_filter]
            x_final = x_final[coutour_filter]
            z_axis = np.array([0, 0, -1])
            curvature_apparent = []
            curvature_normal = []
            apparent_angle = []
            valid_map = []
            vertex_3d = mesh_vertex_3d[x_final]
            for idx, i in enumerate(x_final):
                vertex = mesh_vertex_3d[i]
                view_vector = vertex - camera_pose
                vertex_normal = mesh_vertex_normals[i]
                N_plane_normal = np.cross(view_vector, vertex_normal)
                '''
                plane P:
                defined by point P and normal at view vector 
                plane N:
                defined by point P and normal at N_plane_normal
                '''
                arclen = 0

                local_sample = int(max(min(sample, len(B) / 2 - 1), 1))

                for j in range(idx-local_sample,idx+local_sample):
                    '''
                    p0 = B[j % len(B)]
                    p1 = B[(j+1) % len(B)]
                    v = p1 - p0
                    v = [v[0], v[1], 0]
                    v = np.asarray(v)
                    v = v/480
                    '''
                    p0 = vertex_3d[j % len(x_final)]
                    p0_ = project_point_to_plane(p0,vertex,view_vector)
                    p1 = vertex_3d[(j+1) % len(x_final)]
                    p1_ = project_point_to_plane(p1,vertex,view_vector)
                    v = p1_-p0_
                    v = np.asarray(v)
                    arclen += np.linalg.norm(v)


                p1_idx = (idx - local_sample) % len(B)
                p2_idx = (idx - local_sample + 1) % len(B)
                p3_idx = (idx + local_sample - 1) % len(B)
                p4_idx = (idx + local_sample) % len(B)


                p1 = B[p1_idx]
                p2 = B[p2_idx]
                p3 = B[p3_idx]
                p4 = B[p4_idx]
                V1 = p2 - p1
                V2 = p4 - p3

                V1 = [V1[0],V1[1],0]
                V2 = [V2[0],V2[1],0]

                V1 = normalize(V1)
                V2 = normalize(V2)

                normal = [0, 0, 1]
                a1 = np.cross(V1, V2).dot(normal)
                a2 = np.dot(V1, V2)
                angle = np.arctan2(a1, a2)
                apparent_angle.append(angle)
                apparent_value = angle / (arclen / local_sample*2)

                curvature_apparent.append(apparent_value)
                '''valid_map
                RMS distance of the point 
                '''

                '''
                find intersection of groundtruth 3d mesh with plane N
                '''
                if i == -1:
                    raise RuntimeError("wrong index")
                else:

                    vertex = np.asarray(mesh_vertex_3d[i])
                    G = nx.Graph()
                    lines = mesh_plane(mesh=rotatedMesh, plane_normal=N_plane_normal, plane_origin=vertex)
                    lines = lines * 1e14
                    lines = lines.astype(numpy.int64)
                    vertex = vertex * 1e14
                    vertex = vertex.astype(numpy.int64)
                    vertex = tuple(vertex)

                    num_edge = G.number_of_edges()
                    for line in lines:
                        p1 = tuple(line[0])
                        p2 = tuple(line[1])
                        G.add_edge(p1,p2)
                    arclen = 0
                    V0 = [0,0,0]
                    V1 = [0,0,0]
                    visited_point = []
                    local_sample = max(min(sample,num_edge/2-1),1)
                    try:
                        if vertex in G:
                            v_neighbors = [n for n in G.neighbors(vertex)]
                            degree = G.degree(vertex)
                            visited_point.append(vertex)
                            if len(v_neighbors) == 2:
                                root_1 = vertex
                                next_v1 = v_neighbors[0]
                                root_2 = vertex
                                next_v2 = v_neighbors[1]
                                visited_point.append(next_v1)
                                visited_point.append(next_v2)
                                for i in range(local_sample):
                                    V0 = np.asarray(next_v1)/1e14 - np.asarray(root_1)/1e14
                                    arclen = arclen + np.linalg.norm(V0)
                                    if i == sample - 1:
                                        break
                                    neighbors = [neighbor for neighbor in G.neighbors(next_v1) if neighbor != root_1]
                                    if len(neighbors) != 1:
                                        raise ValueError('bad slice')
                                    root_1 = next_v1
                                    next_v1 = neighbors[0]

                                for i in range(local_sample):
                                    V1 = np.asarray(next_v2)/1e14 - np.asarray(root_2)/1e14
                                    arclen = arclen + np.linalg.norm(V1)
                                    if i == sample - 1:
                                        break
                                    neighbors = [neighbor for neighbor in G.neighbors(next_v2) if neighbor != root_2]
                                    if len(neighbors) != 1:
                                        raise ValueError('bad slice')
                                    root_2 = next_v2
                                    next_v2 = neighbors[0]
                            else:
                                raise ValueError('bad slice')
                        else:
                            raise ValueError('bad slice')
                        V1 = -V1
                        V0 = normalize(V0)
                        V1 = normalize(V1)
                        angle = np.pi - calculate_angle(V0, V1)
                        normal_value = angle / (arclen / sample * 2)
                        curvature_normal.append(normal_value)
                        valid_map.append(True)
                    except ValueError:
                        curvature_normal.append(0)
                        valid_map.append(False)
                        debug = True
                        if debug:
                            pass



            return curvature_apparent, curvature_normal, B, valid_map,apparent_angle,vertex_3d
        else:
            return None, None, None, None, None,None
    else:
        return None, None, None, None, None,None