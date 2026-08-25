#ifndef RCS_KINEMATICS_H
#define RCS_KINEMATICS_H

#include <Eigen/Eigen>
#include <Eigen/Geometry>
#include <memory>
#include <optional>
#include <string>

#include "Pose.h"
#include "utils.h"

namespace rcs {
namespace common {

// Abstract Cartesian<->joint kinematics interface.
//
// Two implementations are provided:
//   * MjIK  (rcs/MjIK.h)  - MuJoCo-native, no external deps (default in sim)
//   * Pin   (rcs/Pin.h)   - pinocchio-based, only compiled when
//                           RCS_HAVE_PINOCCHIO is defined (set by CMake when the
//                           pinocchio library is found)
class Kinematics {
 public:
  virtual ~Kinematics(){};
  virtual std::optional<VectorXd> inverse(
      const Pose& pose, const VectorXd& q0,
      const Pose& tcp_offset = Pose::Identity()) = 0;
  virtual Pose forward(const VectorXd& q0, const Pose& tcp_offset) = 0;
};

}  // namespace common
}  // namespace rcs

#endif  // RCS_KINEMATICS_H
