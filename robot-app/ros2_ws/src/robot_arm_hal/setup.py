"""Setup script for robot_arm_hal."""
from glob import glob

from setuptools import setup

PACKAGE_NAME = "robot_arm_hal"

setup(
    name=PACKAGE_NAME,
    version="0.1.0",
    packages=[PACKAGE_NAME],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + PACKAGE_NAME]),
        ("share/" + PACKAGE_NAME, ["package.xml"]),
        ("share/" + PACKAGE_NAME + "/urdf", glob("urdf/*.xacro")),
        ("share/" + PACKAGE_NAME + "/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools", "paho-mqtt>=2.0"],
    zip_safe=True,
    maintainer="robot-logic",
    maintainer_email="robot-logic@local",
    description="HAL abstraction for forklift and gripper drivers (SIM/REAL dual-mode)",
    license="MIT",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "arm_hal_stub_node = robot_arm_hal.stub:main",
            "forklift_driver = robot_arm_hal.forklift_driver:main",
            "gripper_driver = robot_arm_hal.gripper_driver:main",
        ],
    },
)