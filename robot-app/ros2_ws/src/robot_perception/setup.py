from setuptools import setup


package_name = "robot_perception"


setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="robot-logic",
    maintainer_email="robot-logic@local",
    description="Perception nodes for Top 3 scenarios",
    license="MIT",
    entry_points={
        "console_scripts": [
            "pallet_detector = robot_perception.pallet_detector:main",
            "gripper_monitor = robot_perception.gripper_monitor:main",
            "collision_avoidance = robot_perception.collision_avoidance:main",
        ],
    },
)