#ifndef GUI_H
#define GUI_H
#include <mujoco/mujoco.h>

#include <optional>
#include <string>

namespace rcs {
namespace sim {

static constexpr mjtState MJ_PHYSICS_SPEC = mjSTATE_FULLPHYSICS;

#ifdef RCS_HAVE_BOOST
// --- Full implementation: Boost.Interprocess shared-memory bridge ----------
#include <bitset>
#include <boost/interprocess/managed_shared_memory.hpp>
#include <boost/interprocess/sync/named_sharable_mutex.hpp>
#include <boost/interprocess/sync/named_upgradable_mutex.hpp>

using namespace boost::interprocess;
static const char* INFO_BYTE = "I";
static const char* STATE = "S";
static const char* MODEL = "M";
static const std::string STATE_LOCK_POSTFIX = "_state_lock";
static const std::string INFO_LOCK_POSTFIX = "_info_lock";

static size_t calculate_state_size(mjModel const* m) {
  return mj_stateSize(m, MJ_PHYSICS_SPEC);
}
static size_t calculate_mdl_size(mjModel const* m) { return mj_sizeModel(m); }
static size_t calculate_shm_size(mjModel const* m, mjData const* d) {
  size_t const extra_info_size = 1;
  size_t const total_required_size = extra_info_size + calculate_mdl_size(m) +
                                     calculate_state_size(m) * sizeof(mjtNum);
  size_t const estimated_overhead = total_required_size * 0.1;
  return total_required_size + estimated_overhead;
}

struct shm {
  struct {
    mjtNum* ptr = nullptr;
    size_t size = 0;
  } state;
  struct {
    char* ptr = nullptr;
    size_t size = 0;
  } model;
  bool* info_byte = nullptr;
  managed_shared_memory manager;
  named_sharable_mutex state_lock;
  named_upgradable_mutex info_lock;
};

class GuiServer {
 public:
  GuiServer(mjModel* m, mjData* d, const std::string& id);
  ~GuiServer();
  void publish_state();
  void publish_state_if_requested();
  void update_mjdata_callback();

 private:
  const std::string id;
  struct shm shm;
  mjModel* m;
  mjData* d;
};

class GuiClient {
 public:
  GuiClient(const std::string& id);
  std::string get_model_bytes() const;
  void set_model_and_data(mjModel* m, mjData* d);
  void sync();

 private:
  mjModel* m;
  mjData* d;
  const std::string id;
  struct shm shm;
};

#else
// --- Stub implementation: Boost headers unavailable on this build host ------
// The shared-memory GUI bridge is disabled; Sim still works headless, and
// rendering/callbacks function normally. Rebuild with Boost.Interprocess to
// enable the independent MuJoCo Viewer bridge.
class GuiServer {
 public:
  GuiServer(mjModel*, mjData*, const std::string&) {}
  ~GuiServer() {}
  void publish_state() {}
  void publish_state_if_requested() {}
  void update_mjdata_callback() {}
  const std::string id;  // kept for API symmetry
};

class GuiClient {
 public:
  explicit GuiClient(const std::string&) {}
  std::string get_model_bytes() const { return ""; }
  void set_model_and_data(mjModel*, mjData*) {}
  void sync() {}
};

#endif  // RCS_HAVE_BOOST
}  // namespace sim
}  // namespace rcs
#endif
