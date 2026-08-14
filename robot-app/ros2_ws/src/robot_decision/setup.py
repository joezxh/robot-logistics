"""Setup script for robot_decision."""
from glob import glob

from setuptools import setup

PACKAGE_NAME = "robot_decision"

setup(
    name=PACKAGE_NAME,
    version="0.1.0",
    packages=[PACKAGE_NAME, f"{PACKAGE_NAME}.planning"],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + PACKAGE_NAME]),
        ("share/" + PACKAGE_NAME, ["package.xml"]),
        ("share/" + PACKAGE_NAME + "/config", glob("config/*.yaml")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="joezxh",
    maintainer_email="joezxh@qq.com",
    description="MoveIt motion planning node (Phase 5 M3)",
    license="Apache-2.0",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "motion_planner_node = robot_decision.motion_planner:main",
            "task_coordinator_node = robot_decision.task_coordinator_node:main",
        ],
    },
)
