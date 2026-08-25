#ifndef RCS_MJIK_H
#define RCS_MJIK_H

#include <Eigen/Eigen>
#include <Eigen/Geometry>
#include <memory>
#include <optional>
#include <string>
#include <vector>

#include "Pose.h"
#include "Kinematics.h"
#include "utils.h"

// Forward declarations of MuJoCo types (avoid pulling the full header here).
struct mjModel_;
typedef mjModel_ mjModel;
struct mjData_;
typedef mjData_ mjData;

namespace rcs {
namespace common {

// MuJoCo-native implementation of the Kinematics interface.
//
// Unlike `Pin` (which depends on pinocchio and a separate URDF/MJCF model),
// `MjIK` operates directly on the live MuJoCo model/data. This keeps the core
// buildable without pinocchio while providing Cartesian<->joint conversion via
// MuJoCo's built-in Jacobian utilities (mj_jacSite / mj_forward).
class MjIK : public Kinematics {
 private:
  const double eps = 1e-4;
  const int IT_MAX = 1000;
  const double DT = 1e-1;
  const double damp = 1e-6;

  const mjModel* m;
  mjData* d_scratch;  // private scratch data, never touches the live sim
  int site_id;        // attachment site (TCP reference)
  int base_id;        // robot base body
  std::vector<int> dof_adr;  // qpos address for each controlled joint
  std::vector<int> vel_adr;  // dof (qvel) address for each controlled joint
  int dof;            // number of controlled joints

  // Run one DLS iteration on the given qpos buffer (length m->nq).
  double _step(const Pose& target_site_pose, Eigen::VectorXd& q) const;

 public:
  // `joint_names` are the robot's actuated joints; `site_name` is the TCP
  // attachment site; `base_name` is the robot base body.
  MjIK(const mjModel* model, mjData* data, const std::vector<std::string>& joint_names,
       const std::string& site_name, const std::string& base_name);
  ~MjIK() override;

  std::optional<VectorXd> inverse(
      const Pose& pose, const VectorXd& q0,
      const Pose& tcp_offset = Pose::Identity()) override;

  Pose forward(const VectorXd& q0, const Pose& tcp_offset) override;
};

}  // namespace common
}  // namespace rcs

#endif  // RCS_MJIK_H
