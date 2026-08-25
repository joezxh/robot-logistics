cmake_minimum_required(VERSION 3.18)
project(rcs_sim_core LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)

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
find_path(MUJOCO_INCLUDE_DIR NAMES mujoco/mujoco.h HINTS ${MUJOCO_ROOT}/include)
find_library(MUJOCO_LIBRARY NAMES mujoco HINTS ${MUJOCO_ROOT}/lib ${MUJOCO_ROOT}/bin)
if(NOT MUJOCO_LIBRARY)
  execute_process(
    COMMAND ${Python3_EXECUTABLE} -c "import mujoco, os; print(os.path.join(os.path.dirname(mujoco.__file__), 'lib'))"
    OUTPUT_VARIABLE MUJOCO_LIB_DIR OUTPUT_STRIP_TRAILING_WHITESPACE)
  find_library(MUJOCO_LIBRARY NAMES mujoco HINTS ${MUJOCO_LIB_DIR})
endif()

find_package(Eigen3 QUIET)

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
