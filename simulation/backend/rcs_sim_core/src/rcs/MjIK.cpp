#include "rcs/MjIK.h"

#include <algorithm>
#include <stdexcept>

#include "mujoco/mjdata.h"
#include "mujoco/mjmodel.h"
#include "mujoco/mujoco.h"

namespace rcs {
namespace common {

MjIK::MjIK(const mjModel* model, mjData* data,
           const std::vector<std::string>& joint_names,
           const std::string& site_name, const std::string& base_name)
    : m(model), d_scratch(nullptr), site_id(-1), base_id(-1), dof(0) {
  if (model == nullptr || data == nullptr) {
    throw std::runtime_error("MjIK: model/data must not be null");
  }
  site_id = mj_name2id(m, mjOBJ_SITE, site_name.c_str());
  if (site_id == -1) {
    throw std::runtime_error("MjIK: no site named " + site_name);
  }
  base_id = mj_name2id(m, mjOBJ_BODY, base_name.c_str());
  if (base_id == -1) {
    throw std::runtime_error("MjIK: no body named " + base_name);
  }
  dof = static_cast<int>(joint_names.size());
  dof_adr.reserve(dof);
  vel_adr.reserve(dof);
  for (const auto& jname : joint_names) {
    int jid = mj_name2id(m, mjOBJ_JOINT, jname.c_str());
    if (jid == -1) {
      throw std::runtime_error("MjIK: no joint named " + jname);
    }
    dof_adr.push_back(m->jnt_qposadr[jid]);
    vel_adr.push_back(m->jnt_dofadr[jid]);
  }
  // private scratch copy so IK never perturbs the live simulation state
  d_scratch = mj_makeData(m);
  mj_copyData(d_scratch, m, data);
}

MjIK::~MjIK() {
  if (d_scratch) mj_deleteData(d_scratch);
}

double MjIK::_step(const Pose& target_site_pose, Eigen::VectorXd& q) const {
  // write current guess into scratch
  for (int i = 0; i < dof; ++i) d_scratch->qpos[dof_adr[i]] = q[i];
  mj_forward(m, d_scratch);

  // current site pose
  Eigen::Vector3d cur_pos =
      Eigen::Map<const Eigen::Vector3d>(d_scratch->site_xpos + 3 * site_id);
  // MuJoCo stores xmat as a 9-element ROW-major array. Eigen::Map defaults to
  // ColMajor, so RowMajor must be requested explicitly or we read the transpose.
  Eigen::Matrix3d cur_rot =
      Eigen::Map<const Eigen::Matrix<double, 3, 3, Eigen::RowMajor>>(
          d_scratch->site_xmat + 9 * site_id);
  Pose cur(cur_rot, cur_pos);

  // spatial error (position + orientation)
  Pose err_pose = target_site_pose * cur.inverse();
  Eigen::Vector3d p_err = err_pose.translation();
  Eigen::AngleAxisd aa(err_pose.quaternion());
  Eigen::Vector3d r_err = aa.angle() * aa.axis();
  Vector6d err;
  err << r_err, p_err;

  // full Jacobian at the site (6 x nv)
  Eigen::Matrix<double, 6, Eigen::Dynamic> Jfull(6, m->nv);
  Jfull.setZero();
  Eigen::Matrix<double, 3, Eigen::Dynamic> Jpos(3, m->nv);
  Eigen::Matrix<double, 3, Eigen::Dynamic> Jrot(3, m->nv);
  mj_jacSite(m, d_scratch, Jpos.data(), Jrot.data(), site_id);
  Jfull.topRows(3) = Jrot;
  Jfull.bottomRows(3) = Jpos;

  // restrict to controlled dofs
  Eigen::Matrix<double, 6, Eigen::Dynamic> J(6, dof);
  for (int c = 0; c < dof; ++c) J.col(c) = Jfull.col(vel_adr[c]);

  // damped least squares
  Eigen::MatrixXd JJt = J * J.transpose();
  JJt.diagonal().array() += damp;
  Eigen::VectorXd dq = J.transpose() * JJt.ldlt().solve(-err);

  // integrate (use full qpos so free joints stay consistent)
  Eigen::VectorXd qnew(m->nq);
  for (int i = 0; i < m->nq; ++i) qnew[i] = d_scratch->qpos[i];
  for (int i = 0; i < dof; ++i) qnew[dof_adr[i]] += dq[i] * DT;
  double serr = err.norm();
  // Read back through dof_adr: the controlled joints are NOT necessarily the
  // first `dof` entries of qpos (other bodies may have joints/actuators too).
  for (int i = 0; i < dof; ++i) q[i] = qnew[dof_adr[i]];
  return serr;
}

std::optional<VectorXd> MjIK::inverse(const Pose& pose, const VectorXd& q0,
                                      const Pose& tcp_offset) {
  Pose target = pose * tcp_offset.inverse();
  Eigen::VectorXd q(dof);
  q.setZero();
  if (q0.size() == dof) q = q0;

  double norm = 1e9;
  for (int i = 0; i < IT_MAX; ++i) {
    norm = _step(target, q);
    if (norm < eps) return q;
  }
  // return best-effort solution even if not fully converged
  return q;
}

Pose MjIK::forward(const VectorXd& q0, const Pose& tcp_offset) {
  for (int i = 0; i < dof; ++i) d_scratch->qpos[dof_adr[i]] = q0[i];
  mj_forward(m, d_scratch);

  Eigen::Vector3d site_pos =
      Eigen::Map<const Eigen::Vector3d>(d_scratch->site_xpos + 3 * site_id);
  Eigen::Matrix3d site_rot =
      Eigen::Map<const Eigen::Matrix<double, 3, 3, Eigen::RowMajor>>(
          d_scratch->site_xmat + 9 * site_id);
  Pose site_pose(site_rot, site_pos);

  // transform site pose into robot base coordinates
  Eigen::Map<const Eigen::Vector3d> base_pos(d_scratch->xpos + 3 * base_id);
  Eigen::Map<const Eigen::Vector4d> base_quat(d_scratch->xquat + 4 * base_id);
  Eigen::Quaterniond base_rot(base_quat[0], base_quat[1], base_quat[2],
                              base_quat[3]);
  Pose base_pose(base_rot, base_pos);
  Pose tcp = base_pose.inverse() * site_pose * tcp_offset.inverse();
  return tcp;
}

}  // namespace common
}  // namespace rcs
