from setuptools import setup

package_name = "mqtt_bridge"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", ["resource/" + package_name]),
        ("share/" + package_name, ["package.xml"]),
        ("share/" + package_name, ["mqtt_bridge/topic_mapping.yaml"]),
        ("share/" + package_name + "/launch", ["launch/mqtt_bridge.launch.py"]),
    ],
    install_requires=["setuptools", "paho-mqtt>=2.0", "PyYAML>=6.0"],
    zip_safe=True,
    maintainer="robot-logic",
    maintainer_email="robot-logic@local",
    description="ROS2 ↔ MQTT bidirectional bridge",
    license="MIT",
    entry_points={
        "console_scripts": [
            "mqtt_bridge_node = mqtt_bridge.mqtt_bridge_node:main",
        ],
    },
)