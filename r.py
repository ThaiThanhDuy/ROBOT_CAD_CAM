from PyQt5.QtWidgets import QApplication
from PyQt5.Qt3DExtras import Qt3DWindow, QOrbitCameraController, QPhongMaterial
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DRender import QMesh
from PyQt5.QtGui import QVector3D, QQuaternion, QColor
from PyQt5.QtCore import QUrl

from urdfpy import URDF
from pathlib import Path
import numpy as np
import sys
import os
import tempfile
import trimesh

def to_qt_vector(vec):
    return QVector3D(*vec)

def to_qt_quaternion(quat):
    return QQuaternion(quat[3], quat[0], quat[1], quat[2])  # w, x, y, z

def to_pose(T):
    translation = T[:3, 3]
    rotation = T[:3, :3]
    quat = trimesh.transformations.quaternion_from_matrix(T)
    return translation, quat

def convert_dae_to_stl(dae_path: Path, stl_dir: Path) -> Path:
    stl_path = stl_dir / (dae_path.stem + ".stl")
    if not stl_path.exists():
        mesh = trimesh.load(dae_path, force='mesh')
        mesh.export(stl_path)
    return stl_path

def create_link_entity(name, visual, mesh_path, root_entity):
    entity = QEntity(root_entity)

    mesh = QMesh()
    mesh.setSource(QUrl.fromLocalFile(str(mesh_path)))

    T = visual.origin if visual.origin is not None else np.eye(4)
    pos, quat = to_pose(T)

    transform = QTransform()
    transform.setTranslation(to_qt_vector(pos))
    transform.setRotation(to_qt_quaternion(quat))

    material = QPhongMaterial(root_entity)
    material.setDiffuse(QColor("lightgray"))

    entity.addComponent(mesh)
    entity.addComponent(transform)
    entity.addComponent(material)

    return entity

def main():
    urdf_path = Path('/home/duy/ws_moveit2/src/moveit_resources/panda_description')
    urdf_file = urdf_path / 'urdf/panda.urdf'

    with open(urdf_file, 'r') as f:
        urdf_text = f.read()

    # Sửa các đường dẫn `package://` thành đường dẫn tuyệt đối
    urdf_text = urdf_text.replace(
        'package://moveit_resources_panda_description',
        str(urdf_path)
    )

    # Ghi ra file tạm
    with tempfile.NamedTemporaryFile(mode='w', suffix='.urdf', delete=False) as tmp:
        tmp.write(urdf_text)
        tmp_path = tmp.name

    robot = URDF.load(tmp_path)

    # Thư mục tạm chứa mesh STL
    stl_tmp_dir = Path(tempfile.mkdtemp(prefix="stl_meshes_"))

    app = QApplication(sys.argv)
    view = Qt3DWindow()
    view.defaultFrameGraph().setClearColor(QColor("black"))
    root_entity = QEntity()

    for link in robot.links:
        if not link.visuals:
            continue

        visual = link.visuals[0]
        mesh_file = visual.geometry.mesh.filename
        if mesh_file.startswith("package://"):
            mesh_file = mesh_file.replace("package://moveit_resources_panda_description", str(urdf_path))

        mesh_path = Path(mesh_file)
        if not mesh_path.exists():
            print(f"[WARN] Mesh file not found: {mesh_path}")
            continue

        # Chuyển DAE sang STL
        if mesh_path.suffix.lower() == ".dae":
            mesh_path = convert_dae_to_stl(mesh_path, stl_tmp_dir)

        create_link_entity(link.name, visual, mesh_path, root_entity)

    camera = view.camera()
    camera.lens().setPerspectiveProjection(45.0, 16/9, 0.1, 1000.0)
    camera.setPosition(QVector3D(1.5, 1.5, 1.5))
    camera.setViewCenter(QVector3D(0, 0, 0))

    controller = QOrbitCameraController(root_entity)
    controller.setCamera(camera)

    view.setRootEntity(root_entity)
    view.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
