#ifndef RCS_SIM_H
#define RCS_SIM_H
#include <mujoco/mjvisualize.h>

#include <functional>
#include <optional>
#include <string>
#include <unordered_map>
#include <vector>

// Boost.Interprocess is only needed by gui.h/gui_server (shared-memory GUI).
// It is unavailable on many Windows setups, so keep it optional.
#ifdef RCS_HAVE_BOOST
#include "boost/interprocess/managed_shared_memory.hpp"
#endif
#include "gui.h"
#include "mujoco/mujoco.h"
#include "rcs/utils.h"

namespace rcs {
namespace sim {
class Renderer {
 public:
  Renderer(mjModel* m);
  ~Renderer();
  void register_context(const std::string& id, size_t width, size_t height);
  mjrContext* get_context(const std::string& id);
  mjvScene scene;
  mjvOption opt;

 private:
  mjModel* m;
  std::unordered_map<std::string, mjrContext*> ctxs;
};

struct SimConfig {
  bool async_control = false;
  bool realtime = false;
  double frequency = 30;  // in Hz
  int max_convergence_steps = 500;
};

struct Callback {
  const std::function<void(void)> cb;
  mjtNum seconds_between_calls;  // in seconds
  mjtNum last_call_timestamp;
};

struct ConditionCallback {
  const std::function<bool(void)> cb;
  mjtNum seconds_between_calls;  // in seconds
  mjtNum last_call_timestamp;    // in seconds
  bool last_return_value;
};

struct RenderingCallback {
  const std::function<void(const std::string&, mjrContext&, mjvScene&,
                           mjvOption&)>
      cb;
  const std::string id;          // rendering context id in renderer class
  mjtNum seconds_between_calls;  // in seconds
  mjtNum last_call_timestamp;    // in seconds
};

struct DynamicJointSchema {
  std::vector<std::string> joint_names;
  std::vector<int> joint_types;
  std::vector<int> qpos_sizes;
  std::vector<int> qvel_sizes;
};

struct DynamicJointState {
  rcs::common::VectorXd qpos;
  rcs::common::VectorXd qvel;
};

class Sim {
 private:
  struct DynamicJointSpec {
    std::string name;
    int type;
    int qpos_adr;
    int qvel_adr;
    int qpos_size;
    int qvel_size;
  };

  SimConfig cfg;
  std::vector<Callback> callbacks;
  std::vector<ConditionCallback> any_callbacks;
  std::vector<ConditionCallback> all_callbacks;
  std::vector<RenderingCallback> rendering_callbacks;
  std::vector<DynamicJointSpec> dynamic_joint_specs;
  std::unordered_map<std::string, size_t> dynamic_joint_name_to_index;
  void invoke_callbacks();
  bool invoke_condition_callbacks();
  void invoke_rendering_callbacks();
  void init_dynamic_joint_specs();
  static int get_joint_qpos_size(int joint_type);
  static int get_joint_qvel_size(int joint_type);
  size_t convergence_steps = 0;
  bool converged = true;
  std::optional<GuiServer> gui;
  bool gui_callback_registered = false;
  bool owns_model_data = false;

 public:
  // TODO: hide m & d, pass as parameter to callback (easier refactoring)
  /// Renderer is created lazily (only when rendering is actually used) to avoid
  /// allocating a MuJoCo GL scene at construction time and freeing it during
  /// static teardown (which triggered a 0xc0000374 heap corruption on exit).
  rcs::sim::Renderer* renderer{nullptr};
  mjModel* m;
  mjData* d;
  Sim(mjModel* m, mjData* d);
  /// Construct directly from an MJCF/XMLA XML file path. Sim takes ownership of
  /// the resulting mjModel/mjData and frees them on destruction.
  explicit Sim(const std::string& xml_path, const SimConfig& cfg = SimConfig{});
  ~Sim();
  /// Release MuJoCo model/data/renderer explicitly. Safe to call multiple times
  /// and during normal operation (before interpreter finalization) to avoid
  /// late frees that corrupt the CRT heap at process exit.
  void close();
  /// Lazily construct (and return) the renderer; throws if the Sim was closed.
  rcs::sim::Renderer* get_renderer();
  bool set_config(const SimConfig& cfg);
  SimConfig get_config();
  bool is_converged();
  void step_until_convergence();
  void step(size_t k);
  /// Recompute forward dynamics (positions -> accelerations, body/site frames).
  /// Useful after teleporting qpos via SimRobot::set_joints_hard().
  void forward();
  /// Number of active contacts in the current mjData.
  int ncon() const;
  void reset_callbacks();
  void reset();
  /// Reset mjData to the qpos/qvel stored in a named <key> keyframe (e.g. the
  /// robot's "home" pose). Falls back to a plain mj_resetData if the keyframe
  /// does not exist. Used so reset() lands the robot in its collision-free home
  /// pose instead of the MJCF default (often all-zero qpos).
  void reset_key(const std::string& name);
  DynamicJointSchema get_dynamic_joint_schema() const;
  DynamicJointState get_dynamic_joint_state() const;
  void set_dynamic_joint_state(const DynamicJointSchema& schema,
                               const DynamicJointState& state);
  /* NOTE: IMPORTANT, the callback is not necessarily called at exactly the
   * the requested interval. We invoke a callback if the elapsed simulation time
   * since the last call of the callback is greater than the requested time.
   * The exact interval at which they are called depends on the models timestep
   * option (cf.
   * https://mujoco.readthedocs.io/en/stable/programming/simulation.html#simulation-loop
   */
  void register_cb(std::function<void(void)> cb, mjtNum seconds_between_calls);
  void register_any_cb(std::function<bool(void)> cb,
                       mjtNum seconds_between_calls);
  void register_all_cb(std::function<bool(void)> cb,
                       mjtNum seconds_between_calls);
  void register_rendering_callback(
      std::function<void(const std::string& id, mjrContext&, mjvScene&,
                         mjvOption&)>
          cb,
      const std::string& id, int frame_rate, size_t width, size_t height);
  void start_gui_server(const std::string& id);
  void stop_gui_server();
  void sync_gui();
};
}  // namespace sim
}  // namespace rcs
#endif
