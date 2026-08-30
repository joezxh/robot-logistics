cmake_minimum_required(VERSION 3.18)
project(rcs_sim_core LANGUAGES CXX)

# The RCS sources upstream target C++20: they use designated initializers
# (`.field = value`) and the alternative tokens `and` / `or` / `not`.
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

if(MSVC)
  # /permissive-  : conformance mode, required for the `and`/`or`/`not` tokens
  # /Zc:__cplusplus : make __cplusplus report the real standard
  # /bigobj       : pybind11 translation units exceed the default section limit
  add_compile_options(/permissive- /Zc:__cplusplus /bigobj)
endif()

# ---------------------------------------------------------------------------
# Dependencies
#   mujoco   : physics engine (C API)            [required]
#   pybind11  : Python bindings                  [required]
#   Eigen3    : linear algebra (header-only)     [required]
#   Boost     : Interprocess (shared-memory GUI) [header-only, optional]
#   pinocchio : optional IK backend (RCS_HAVE_PINOCCHIO)
#   EGL / GL  : offscreen rendering (RCS_HAVE_EGL)
# ---------------------------------------------------------------------------

find_package(pybind11 CONFIG REQUIRED)

if(DEFINED ENV{MUJOCO_ROOT})
  set(MUJOCO_ROOT "$ENV{MUJOCO_ROOT}")
endif()

# --- 1) Find the `mujoco` Python package ------------------------------------
# The MuJoCo PyPI wheel is our only source of headers/lib on Windows.
# IMPORTANT: scikit-build-core builds in an *isolated* env whose python does NOT
# have `mujoco` installed, so querying "python" blindly fails. Try the target
# interpreter first, then fall back to whatever is on PATH.
set(_mujoco_python_candidates "")
foreach(_py IN ITEMS "${Python_EXECUTABLE}" "${PYTHON_EXECUTABLE}" python3 python)
  if(_py)
    list(APPEND _mujoco_python_candidates "${_py}")
  endif()
endforeach()
list(REMOVE_DUPLICATES _mujoco_python_candidates)
list(FILTER _mujoco_python_candidates EXCLUDE REGEX "^$")

set(_tool_python "python")   # any interpreter works for the helper script
if(_mujoco_python_candidates)
  list(GET _mujoco_python_candidates 0 _tool_python)
endif()

set(MUJOCO_PKG_DIR "")
foreach(_py IN LISTS _mujoco_python_candidates)
  execute_process(
    COMMAND "${_py}" -c "import mujoco, os, sys; sys.stdout.write(os.path.dirname(mujoco.__file__))"
    OUTPUT_VARIABLE _pkg_dir
    ERROR_QUIET
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE _pkg_rc)
  if(_pkg_rc EQUAL 0 AND _pkg_dir)
    set(MUJOCO_PKG_DIR "${_pkg_dir}")
    break()
  endif()
endforeach()
message(STATUS "MuJoCo: package dir = '${MUJOCO_PKG_DIR}'")

# --- 2) Headers -------------------------------------------------------------
# Layout differs by MuJoCo version:
#   <= 3.11 : <pkg>/include/mujoco/mujoco.h      -> include dir = <pkg>/include
#   >= 3.12 : <pkg>/include/mujoco/mujoco/*.h    -> include dir = <pkg>/include/mujoco
# Listing the newer layout first makes find_path pick the right include root.
# Listing the newer layout first makes find_file pick the right header; the
# include root is then two levels up from the header itself.
find_file(MUJOCO_HEADER
  NAMES mujoco/mujoco/mujoco.h mujoco/mujoco.h
  HINTS ${MUJOCO_ROOT}/include ${MUJOCO_PKG_DIR}/include)
set(MUJOCO_INCLUDE_DIR "")
if(MUJOCO_HEADER)
  # header = <root>/mujoco/<mujoco.h>  -> include root = <root>
  get_filename_component(_mj_hdr_dir "${MUJOCO_HEADER}" DIRECTORY)
  get_filename_component(MUJOCO_INCLUDE_DIR "${_mj_hdr_dir}" DIRECTORY)
endif()
message(STATUS "MuJoCo: include dir = '${MUJOCO_INCLUDE_DIR}'")

# --- 3) Library -------------------------------------------------------------
find_library(MUJOCO_LIBRARY
  NAMES mujoco
  HINTS ${MUJOCO_ROOT}/lib ${MUJOCO_ROOT}/bin ${MUJOCO_PKG_DIR}/lib ${MUJOCO_PKG_DIR})

# Windows: the wheel ships mujoco.dll but NO import .lib, and the MSVC linker
# cannot link against a .dll directly. Derive mujoco.lib from the DLL's export
# table (dumpbin -> .def -> lib.exe); see cmake/gen_mujoco_import_lib.py.
if(NOT MUJOCO_LIBRARY AND WIN32)
  find_file(MUJOCO_DLL
    NAMES mujoco.dll
    HINTS ${MUJOCO_PKG_DIR} ${MUJOCO_PKG_DIR}/bin ${MUJOCO_PKG_DIR}/lib)
  if(MUJOCO_DLL)
    set(_gen_lib "${CMAKE_CURRENT_BINARY_DIR}/mujoco_import_lib/mujoco.lib")
    # dumpbin/lib live next to the compiler we are already using.
    get_filename_component(_msvc_bin_dir "${CMAKE_CXX_COMPILER}" DIRECTORY)
    message(STATUS "MuJoCo: no import .lib found; generating one from ${MUJOCO_DLL}")
    execute_process(
      COMMAND "${_tool_python}"
              "${CMAKE_CURRENT_SOURCE_DIR}/cmake/gen_mujoco_import_lib.py"
              --dll "${MUJOCO_DLL}" --out "${_gen_lib}"
              --dumpbin "${_msvc_bin_dir}/dumpbin.exe"
              --lib "${_msvc_bin_dir}/lib.exe"
      RESULT_VARIABLE _gen_rc)
    if(_gen_rc EQUAL 0 AND EXISTS "${_gen_lib}")
      set(MUJOCO_LIBRARY "${_gen_lib}")
    else()
      message(WARNING "MuJoCo: failed to generate an import library (rc=${_gen_rc})")
    endif()
  endif()
endif()
message(STATUS "MuJoCo: library = '${MUJOCO_LIBRARY}'")

# Eigen is header-only. Prefer the vendored copy in third_party/eigen3 so the
# build works out of the box on Windows (PyPI has no Eigen); fall back to a
# system/conda install when present.
find_path(EIGEN3_INCLUDE_DIR
  NAMES Eigen/Eigen Eigen/Dense
  HINTS ${CMAKE_CURRENT_SOURCE_DIR}/third_party/eigen3
        $ENV{EIGEN3_INCLUDE_DIR} $ENV{EIGEN_ROOT} $ENV{EIGEN3_ROOT}
        /usr/include/eigen3 /usr/local/include/eigen3
        /opt/homebrew/include/eigen3
)
set(Eigen3_FOUND FALSE)
if(EIGEN3_INCLUDE_DIR)
  set(Eigen3_FOUND TRUE)
  if(NOT TARGET Eigen3::Eigen)
    add_library(rcs_eigen INTERFACE)
    target_include_directories(rcs_eigen INTERFACE "${EIGEN3_INCLUDE_DIR}")
    add_library(Eigen3::Eigen ALIAS rcs_eigen)
  endif()
endif()
message(STATUS "Eigen3: found=${Eigen3_FOUND} include='${EIGEN3_INCLUDE_DIR}'")

# pinocchio is optional; when found we build the pinocchio-backed IK (Pin).
find_package(pinocchio QUIET)
if(pinocchio_FOUND)
  add_compile_definitions(RCS_HAVE_PINOCCHIO)
endif()

# Boost.Interprocess (shared-memory GUI) is optional, header-only.
find_path(BOOST_INCLUDE_DIR NAMES boost/interprocess/managed_shared_memory.hpp
          HINTS $ENV{BOOST_ROOT}/include)
if(BOOST_INCLUDE_DIR)
  add_compile_definitions(RCS_HAVE_BOOST)
endif()

# EGL is optional; MuJoCo bundles its own GL loader on Windows, but on Linux
# headless rendering needs libEGL/libGL.
find_path(EGL_INCLUDE_DIR NAMES EGL/egl.h)
if(EGL_INCLUDE_DIR)
  add_compile_definitions(RCS_HAVE_EGL)
endif()

# ---------------------------------------------------------------------------
# rcs common static lib (Pose / Robot / Kinematics / MjIK / utils)
# ---------------------------------------------------------------------------
add_library(rcs_common STATIC
  src/rcs/Pose.cpp
  src/rcs/Robot.cpp
  src/rcs/Kinematics.cpp
  src/rcs/MjIK.cpp
  src/rcs/utils.cpp
)
target_include_directories(rcs_common PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${MUJOCO_INCLUDE_DIR}
)
if(Eigen3_FOUND)
  target_link_libraries(rcs_common PUBLIC Eigen3::Eigen)
endif()
if(pinocchio_FOUND)
  target_link_libraries(rcs_common PUBLIC pinocchio::pinocchio)
endif()
if(EGL_INCLUDE_DIR)
  target_include_directories(rcs_common PRIVATE ${EGL_INCLUDE_DIR})
endif()

# ---------------------------------------------------------------------------
# Python extension: rcs._core  (submodules: common, sim)
# ---------------------------------------------------------------------------
pybind11_add_module(_core
  src/pybind/rcs.cpp
  src/sim/sim.cpp
  src/sim/SimRobot.cpp
  src/sim/SimGripper.cpp
  src/sim/SimTilburgHand.cpp
  src/sim/camera.cpp
  src/sim/renderer.cpp
  src/sim/gui_server.cpp
  src/sim/gui_client.cpp
)
target_include_directories(_core PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/include
  ${CMAKE_CURRENT_SOURCE_DIR}/src          # for "sim/sim.h" style includes
  ${MUJOCO_INCLUDE_DIR}
)
target_link_libraries(_core PRIVATE
  rcs_common
  ${MUJOCO_LIBRARY}
)
if(DEFINED ENV{BOOST_ROOT})
  target_include_directories(_core PRIVATE $ENV{BOOST_ROOT}/include)
endif()
if(BOOST_INCLUDE_DIR)
  target_include_directories(_core PRIVATE ${BOOST_INCLUDE_DIR})
endif()

if(WIN32)
  target_link_libraries(_core PRIVATE opengl32)
else()
  find_library(EGL_LIB NAMES EGL)
  find_library(GL_LIB NAMES GL)
  if(EGL_LIB)
    target_link_libraries(_core PRIVATE ${EGL_LIB} ${GL_LIB})
  endif()
endif()

set_target_properties(_core PROPERTIES
  OUTPUT_NAME "_core"
  PREFIX "${PYTHON_MODULE_PREFIX}"
  LIBRARY_OUTPUT_DIRECTORY "${CMAKE_CURRENT_BINARY_DIR}/rcs")

# Without an install() rule scikit-build-core has nothing to put in the wheel and
# `import rcs._core` fails with a circular-import error. DESTINATION must match
# the package name (see `wheel.packages = ["python/rcs"]` in pyproject.toml).
# RUNTIME is needed on Windows, where the .pyd is a DLL-like artifact.
install(TARGETS _core DESTINATION rcs)
