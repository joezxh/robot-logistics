> [中文](index_CN.md) | English

# Programming

## Introduction

This chapter is the MuJoCo programming guide. A separate chapter contains the [API Reference](https://mujoco.readthedocs.io/en/stable/programming/APIreference/index.md) documentation. MuJoCo is a dynamic library compatible with Windows, Linux and macOS, which requires a processor with AVX instructions. The library exposes the full functionality of the simulator through a compiler-independent shared-memory C API. It can also be used in C++ programs.

The MuJoCo codebase is organized into subdirectories corresponding to different major areas of functionality:

Engine
    

The simulator (or physics engine) is written in C. It is responsible for all runtime computations.

Parser
    

The XML parser is written in C++. It can parse MJCF models and URDF models, converting them into an internal mjCModel C++ object which is exposed to the user via mjSpec.

Compiler
    

The compiler is written in C++. It takes an mjCModel C++ object constructed by the parser, and converts it into an mjModel C structure used at runtime.

Thread
    

The threading framework is written in C++ and exposed in C. It provides a thread pool interface to process tasks asynchronously. To enable use in MuJoCo, call `mju_threadpool`.

Rendering
    

There are two rendering libraries provided by MuJoCo. The [classic rendering](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#openglrendering) library is written in C and uses OpenGL 1.5. It provides a simple and efficient way to visualize MuJoCo models. The [filament rendering](https://mujoco.readthedocs.io/en/stable/programming/programming/visualization.md#filamentrendering) library is written in C++ and uses the externally-devloped Filament rendering engine. It provides more modern and feature-rich real-time rendering capabilities.

Abstract visualizer
    

The abstract visualizer is written in C. It generates a list of abstract geometric entities representing the simulation state, with all information needed for rendering with the Classic renderer. It also provides abstract mouse hooks for camera and perturbation control.

UI framework
    

The UI framework is written in C and is designed to work with the [classic OpenGL renderer](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#openglrendering). UI elements are rendered in OpenGL. It has its own event mechanism and abstract hooks for keyboard and mouse input. The code samples use it with GLFW, but it can also be used with other window libraries.

## Getting started

MuJoCo is an open-source project. Pre-built dynamic libraries are available for x86_64 and arm64 machines running Windows, Linux, and macOS. These can be downloaded from the [GitHub Releases page](https://github.com/google-deepmind/mujoco/releases). Users who do not intend to develop or modify core MuJoCo code are encouraged to use our pre-built libraries, as these come bundled with the same versions of dependencies that we regularly test against, and benefit from build flags that have been tuned for performance. Our pre-built libraries are almost entirely self-contained and do not require any other library to be present, outside the standard C runtime. We also hide all symbols apart from those that form MuJoCo’s public API, thus ensuring that it can coexist with any other libraries that may be loaded into the process (including other versions of libraries that MuJoCo depends on).

The pre-built distribution is a single .zip on Windows, .dmg on macOS, and .tar.gz on Linux. There is no installer. On Windows and Linux, simply extract the archive in a directory of your choice. From the `bin` subdirectory, you can now run the precompiled code samples, for example:
    
    
    Windows:           simulate ..\model\humanoid\humanoid.xml
    Linux and macOS:   ./simulate ../model/humanoid/humanoid.xml
    

The directory structure is shown below. Users can re-organize it if needed, as well as install the dynamic libraries in other directories and set the path accordingly. The only file created automatically is MUJOCO_LOG.TXT in the executable directory; it contains error and warning messages, and can be deleted at any time.
    
    
    bin     - dynamic libraries, executables, MUJOCO_LOG.TXT
    doc     - README.txt and REFERENCE.txt
    include - header files needed to develop with MuJoCo
    model   - model collection
    sample  - code samples and CMakeLists.txt needed to build them
    

After verifying that the simulator works, you may also want to re-compile the code samples to ensure that you have a working development environment. We provide a cross-platform [CMake](https://github.com/google-deepmind/mujoco/blob/main/sample/CMakeLists.txt) setup that can be used to build sample applications independently of the MuJoCo library itself.

On macOS, the DMG disk image contains `MuJoCo.app`, which you can double-click to launch the `simulate` GUI. You can also drag `MuJoCo.app` into the `/Applications` on your system, as you would to install any other app. As well as the `MuJoCo.app` [Application Bundle](https://developer.apple.com/go/?id=bundle-structure), the DMG includes the `mujoco.framework` subdirectory containing the MuJoCo dynamic library and all of its public headers. If you are using Xcode, you can import it as a framework dependency on your project. (This also works for Swift projects without any modification). If you are building manually, you can use `-F` and `-framework mujoco` to specify the header search path and the library search path respectively.

## Building from source

To build MuJoCo from source, you will need CMake and a working C++17 compiler installed. The steps are:

  1. Clone the `mujoco` repository: `git clone https://github.com/google-deepmind/mujoco.git`

  2. Create a new build directory and `cd` into it.

  3. Run `cmake $PATH_TO_CLONED_REPO` to configure the build.

  4. Run `cmake --build .` to build.




MuJoCo’s build system automatically fetches dependencies from upstream repositories over the Internet using CMake’s [FetchContent](https://cmake.org/cmake/help/latest/module/FetchContent.html) module.

The main CMake setup will build the MuJoCo library itself along with all sample applications, but the Python bindings are not built. Those come with their own build instructions, which can be found in the [Python](https://mujoco.readthedocs.io/en/stable/programming/python.md) section of the documentation.

Additionally, the CMake setup also implements an installation phase which will copy and organize the output files to a target directory.

  1. Select the directory: `cmake $PATH_TO_CLONED_REPO -DCMAKE_INSTALL_PREFIX=<my_install_dir>`

  2. After building, install with `cmake --install .`

  3. If desired, proceed to building the Python bindings - see [Building from source](https://mujoco.readthedocs.io/en/stable/programming/python.md#pybuild).




**Notes:**

  * To optimize runtime performance build with `-DCMAKE_BUILD_TYPE=Release`.

  * When building on Windows with MSVC, use Visual Studio 2019 or later and make sure Windows SDK version 10.0.22000 or later is installed (see [issue #862](https://github.com/google-deepmind/mujoco/issues/862) for more details).

  * We’ve found that performance on Windows is best when building with Clang, rather than MSVC.




Tip

As a reference, a working build configuration can be found in MuJoCo’s [continuous integration setup](https://github.com/google-deepmind/mujoco/blob/main/.github/workflows/build.yml) on GitHub.

## Building the docs

If you wish to build the documentation locally, for example to test pull-requests that improve it, do:

  1. Clone the `mujoco` repository: `git clone https://github.com/google-deepmind/mujoco.git`

  2. Go to the `doc/` directory: `cd mujoco/doc`

  3. Install the dependencies: `pip install -r requirements.txt`   
Note that the MuJoCo Warp API documentation is autogenerated and requires additional dependencies. See [.readthedocs.yml](https://github.com/google-deepmind/mujoco/blob/main/.readthedocs.yml) for details.

  4. Build the HTML: `make html`

  5. Open `_build/html/index.html` in your browser of choice.




## Header files

The distribution contains several header files which are identical on all platforms. They are also available from the links below, to make this documentation self-contained.

[mujoco.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mujoco.h)
    

This is the main header file and must be included in all programs using MuJoCo. It defines all API functions and global variables, and includes all other header files except mjxmacro.h and mjspecmacro.h.

[mjmodel.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjmodel.h)
    

Defines the C structure [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel) which is the runtime representation of the model being simulated.

[mjdata.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjdata.h)
    

Defines the C structure [mjData](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjdata) which is the workspace where all computations read their inputs and write their outputs.

[mjvisualize.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjvisualize.h)
    

Defines the primitive types and structures needed by the abstract visualizer.

[mjrender.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjrender.h)
    

Defines the primitive types and structures needed by the OpenGL renderer.

[mjrfilament.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjrfilament.h)
    

Defines the primitive types and structures needed by the filament renderer.

[mjui.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjui.h)
    

Defines the primitive types and structures needed by the UI framework.

[mjtype.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjtype.h)
    

Defines primitive types and enums, including the `mjtNum` floating-point type to be either `double` or `float` (see [mjtNum](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtnum)).

[mjspec.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjspec.h)
    

Defines enums and structs used for [procedural model editing](https://mujoco.readthedocs.io/en/stable/programming/programming/modeledit.md).

[mjplugin.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjplugin.h)
    

Defines data structures required by [engine plugins](https://mujoco.readthedocs.io/en/stable/programming/programming/extension.md#explugin).

[mjmacro.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjmacro.h)
    

Defines C macros that are useful in user code.

[mjxmacro.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjxmacro.h)
    

This file is optional and is not included by mujoco.h. It defines [X Macros](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#tyxmacro) that can automate the mapping of mjModel and mjData into scripting languages, as well as other operations that require accessing all fields of mjModel and mjData.

[mjspecmacro.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjspecmacro.h)
    

This file is optional and is not included by mujoco.h. It defines [X Macros](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#tyxmacro) that can automate the mapping of mjSpec and its element structs into scripting languages, as well as other operations that require accessing all fields of mjSpec during procedural model editing.

[mjexport.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjexport.h)
    

Macros used for exporting public symbols from the MuJoCo library. This header should not be used directly by client code.

[mjsan.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjsan.h)
    

Definitions required when building with sanitizer instrumentation.

[mjassert.h](https://github.com/google-deepmind/mujoco/blob/main/include/mujoco/mjassert.h)
    

Compile-time size assertions verifying MuJoCo ABI stability across C and C++ compilers.

## Versions and compatibility

MuJoCo has been used extensively since 2010 and is quite mature (even though our version numbering scheme is quite conservative). Nevertheless it remains under active development, and we have many exciting ideas for new features and are also making changes based on user feedback. This leads to unavoidable changes in both the modeling language and the API. While we encourage users to upgrade to the latest version, we recognize that this is not always feasible, especially when other developers release software that relies on MuJoCo. Therefore we have introduced simple mechanisms to help avoid version conflicts, as follows.

The situation is more subtle if existing code was developed with a certain version of MuJoCo, and is now being compiled and linked with a different version. If the definitions of the API functions used in that code have changed, either the compiler or the linker will generate errors. But even if the function definitions have not changed, it may still be a good idea to assert that the software version is the same. To this end, the main header (mujoco.h) defines the symbol [mjVERSION_HEADER](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#glnumericversion) and the library provides the function [mj_version](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-version). Thus the header and library versions can be compared with:
    
    
    // recommended version check
    if (mjVERSION_HEADER != mj_version())
      complain();
    

Note that only the main header defines this symbol. We assume that the collection of headers released with each software version will stay together and will not be mixed between versions. To avoid complications with floating-point comparisons, the above symbol and function use integers rather than floating-point numbers. See [VERSIONING.md](https://github.com/google-deepmind/mujoco/blob/main/VERSIONING.md) for the encoding formula and version semantics.

## Naming convention

All symbols defined in the API start with the prefix “mj”. The character after “mj” in the prefix determines the family to which the symbol belongs. First we list the prefixes corresponding to type definitions.

`mj`
    

Core simulation data structure (C struct), for example [mjModel](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjmodel). If all characters after the prefix are capital, for example [mjMIN](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mjmin), this is a macro or a symbol (#define).

`mjt`
    

Primitive type, for example [mjtNum](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtnum) and [mjtGeom](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjtgeom). Most types in this family are enums.

`mjf`
    

Callback function type, for example [mjfGeneric](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjfgeneric).

`mjs`
    

Data structure related to [procedural model editing](https://mujoco.readthedocs.io/en/stable/programming/programming/modeledit.md), for example [mjsJoint](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjsjoint).

`mjv`
    

Data structure related to abstract visualization, for example [mjvCamera](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjvcamera).

`mjrf`
    

Data structure related to filament rendering, for example [mjrfContext](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjrfcontext).

`mjr`
    

Data structure related to OpenGL rendering, for example [mjrContext](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjrcontext).

`mjui`
    

Data structure related to UI framework, for example [mjuiSection](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APItypes.md#mjuisection).

Next we list the prefixes corresponding to function definitions. Note that function prefixes always end with underscore.

`mj_`
    

Core simulation function, for example [mj_step](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mj-step). Almost all such functions have pointers to mjModel and mjData as their first two arguments, possibly followed by other arguments. They usually write their outputs to mjData.

`mju_`
    

Utility function, for example [mju_mulMatVec](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mju-mulmatvec). These functions are self-contained in the sense that they do not have mjModel and mjData pointers as their arguments.

`mjv_`
    

Function related to abstract visualization, for example [mjv_updateScene](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjv-updatescene).

`mjrf_`
    

Function related to filament rendering, for example [mjrf_render](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjrf-render).

`mjr_`
    

Function related to OpenGL rendering, for example [mjr_render](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjr-render).

`mjui_`
    

Function related to UI framework, for example [mjui_update](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjui-update).

`mjcb_`
    

Global callback function pointer, for example [mjcb_control](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIglobals.md#mjcb-control). The user can install custom callbacks by setting these global pointers to user-defined functions.

`mjd_`
    

Functions for computing derivatives, for example [mjd_transitionFD](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjd-transitionfd).

`mjs_`
    

Functions for [procedural model editing](https://mujoco.readthedocs.io/en/stable/programming/programming/modeledit.md), for example [mjs_addJoint](https://mujoco.readthedocs.io/en/stable/programming/APIreference/APIfunctions.md#mjs-addjoint).
