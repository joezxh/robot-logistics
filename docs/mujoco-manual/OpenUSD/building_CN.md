> [🌐 English](building.md) | 中文

# 构建

> **警告**
>
> OpenUSD 支持目前仍处于实验阶段，可能会频繁变动。

MuJoCo 必须链接到一个预先构建好的 USD 库，我们提供了一个工具来完成这件事，但你也可以自带 USD 库。

以下说明假设你已经将 MuJoCo 克隆到 `~/mujoco`，并且在 `~/mujoco/build` 处有一个构建目录。

## 构建 USD

如果你已经有一个预先构建好的 USD 库，可以跳过本节。

MuJoCo 提供了一个 CMake 工程，用于简化构建 USD 的过程。它会下载并以仅启用必要特性的方式构建 USD。

    cd ~/mujoco
    cmake -Bcmake/third_party_deps/openusd/build cmake/third_party_deps/openusd
    cmake --build cmake/third_party_deps/openusd/build

如果你想自定义构建过程，可以使用 USD 的 `build_usd.py` 脚本。建议使用一个位于克隆仓库目录之外的独立安装目录。

    git clone https://github.com/PixarAnimationStudios/OpenUSD
    python OpenUSD/build_scripts/build_usd.py /path/to/my_usd_install_dir

## 启用 USD

如果 USD 是通过 third_party_deps/openusd CMake 工程构建的，你可以使用 MUJOCO_WITH_USD 标志来启用 USD 支持。

    cd ~/mujoco
    cmake -Bbuild -S. -DMUJOCO_WITH_USD=True
    cmake --build build -j 64

否则，如果你使用的是预先构建好的 USD 库，你还必须传入 pxr_DIR 标志。

    cd ~/mujoco
    cmake -Bbuild -S. -DMUJOCO_WITH_USD=True -Dpxr_DIR=/path/to/my_usd_install_dir
    cmake --build build -j 64

如果现在运行 [simulate.cc](https://mujoco.readthedocs.io/en/stable/OpenUSD/programming/samples.md#sasimulate)，我们就能够拖放 USD 文件了。

    simulate
