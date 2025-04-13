import warnings
import numpy as np
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=RuntimeWarning)

from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout
from PyQt5.Qt3DExtras import Qt3DWindow, QOrbitCameraController, QPhongMaterial
from PyQt5.Qt3DCore import QEntity, QTransform
from PyQt5.Qt3DRender import QMesh
from PyQt5.QtGui import QVector3D, QQuaternion, QColor
from PyQt5.QtCore import QUrl, Qt

from urdfpy import URDF
from pathlib import Path
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
    quat = trimesh.transformations.quaternion_from_matrix(T)
    return translation, quat

def convert_dae_to_stl(dae_path: Path, stl_dir: Path) -> Path:
    stl_path = stl_dir / (dae_path.stem + ".stl")
    if not stl_path.exists():
        mesh = trimesh.load(dae_path, force='mesh')
        mesh.export(stl_path)
    return stl_path

def compute_link_transforms(robot, joint_values):
    transforms = {'panda_link0': np.eye(4)}  # gốc
    for joint in robot.joints:
        parent = joint.parent
        child = joint.child
        T = joint.origin if joint.origin is not None else np.eye(4)

        if joint.joint_type == 'revolute':
            axis = np.array(joint.axis)
            axis = axis / np.linalg.norm(axis) if np.linalg.norm(axis) > 0 else np.array([0, 0, 1])
            angle = joint_values.get(joint.name, 0.0)
            R = trimesh.transformations.rotation_matrix(angle, axis)
            T = T @ R

        transforms[child] = transforms[parent] @ T
    return transforms

def create_link_entity(name, T_link, visual, mesh_path, root_entity):
    entity = QEntity(root_entity)

    mesh = QMesh()
    mesh.setSource(QUrl.fromLocalFile(str(mesh_path)))

    T_visual = visual.origin if visual.origin is not None else np.eye(4)
    T_total = T_link @ T_visual

    pos, quat = to_pose(T_total)
    transform = QTransform()
    transform.setTranslation(to_qt_vector(pos))
    transform.setRotation(to_qt_quaternion(quat))

    material = QPhongMaterial(root_entity)
    material.setDiffuse(QColor("lightgray"))

    entity.addComponent(mesh)
    entity.addComponent(transform)
    entity.addComponent(material)

    return entity

class CameraController(QWidget):
    def __init__(self, view):
        super().__init__()
        self.view = view
        self.setLayout(QHBoxLayout())
        self.layout().addWidget(QWidget.createWindowContainer(view))
        self.setFocusPolicy(Qt.StrongFocus)
        self.last_pos = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.last_pos = event.pos()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.MiddleButton and self.last_pos:
            delta = event.pos() - self.last_pos
            camera = self.view.camera()
            pos = camera.position()
            center = camera.viewCenter()
            direction = pos - center
            up = camera.upVector()

            right = QVector3D.crossProduct(direction, up).normalized()
            up = QVector3D.crossProduct(right, direction).normalized()

            move = (-delta.x() * right + delta.y() * up) * 0.002
            camera.setPosition(pos + move)
            camera.setViewCenter(center + move)

            self.last_pos = event.pos()

    def wheelEvent(self, event):
        delta = event.angleDelta().y() / 120
        camera = self.view.camera()
        pos = camera.position()
        center = camera.viewCenter()
        direction = (center - pos).normalized()
        zoom_amount = 0.2 * delta
        camera.setPosition(pos + direction * zoom_amount)

def main():
    urdf_path = Path('/home/duy/ws_moveit2/src/moveit_resources/panda_description')
    urdf_file = urdf_path / 'urdf/panda.urdf'

    with open(urdf_file, 'r') as f:
        urdf_text = f.read()

    urdf_text = urdf_text.replace(
        'package://moveit_resources_panda_description',
        str(urdf_path)
    )

    with tempfile.NamedTemporaryFile(mode='w', suffix='.urdf', delete=False) as tmp:
        tmp.write(urdf_text)
        tmp_path = tmp.name

    robot = URDF.load(tmp_path)
    stl_tmp_dir = Path(tempfile.mkdtemp(prefix="stl_meshes_"))

    joint_values = {j.name: 0.0 for j in robot.joints if j.joint_type == 'revolute'}
    link_transforms = compute_link_transforms(robot, joint_values)

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
        if mesh_path.suffix.lower() == ".dae":
            mesh_path = convert_dae_to_stl(mesh_path, stl_tmp_dir)

        T_link = link_transforms.get(link.name, np.eye(4))
        create_link_entity(link.name, T_link, visual, mesh_path, root_entity)

    camera = view.camera()
    camera.lens().setPerspectiveProjection(45.0, 16 / 9, 0.1, 1000.0)
    camera.setPosition(QVector3D(1.5, 1.5, 1.5))
    camera.setViewCenter(QVector3D(0, 0, 0))

    controller = QOrbitCameraController(root_entity)
    controller.setCamera(camera)

    view.setRootEntity(root_entity)

    widget = CameraController(view)
    widget.resize(1024, 768)
    widget.setWindowTitle("Robot Viewer - Panda Arm")
    widget.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
