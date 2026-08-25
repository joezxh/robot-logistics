#include <mujoco/mujoco.h>

#include <iostream>

#include "sim.h"
#include "sim/gui.h"

namespace rcs {
namespace sim {

#ifdef RCS_HAVE_BOOST

GuiClient::GuiClient(const std::string& id)
    : m{nullptr},
      d{nullptr},
      shm{.state{.size = 0},
          .model{.size = 0},
          .manager{open_only, id.c_str()},
          .state_lock{open_only, (id + STATE_LOCK_POSTFIX).c_str()},
          .info_lock{open_only, (id + INFO_LOCK_POSTFIX).c_str()}},
      id{id} {
  this->shm.state.ptr =
      this->shm.manager.find<mjtNum>(STATE).first;
  this->shm.state.size = this->shm.manager.find<mjtNum>(STATE).second;
  this->shm.model.ptr = this->shm.manager.find<char>(MODEL).first;
  this->shm.model.size = this->shm.manager.find<char>(MODEL).second;
  this->shm.info_byte = this->shm.manager.find<bool>(INFO_BYTE).first;
}

std::string GuiClient::get_model_bytes() const {
  return std::string(this->shm.model.ptr, this->shm.model.size);
}

void GuiClient::set_model_and_data(mjModel* m, mjData* d) {
  this->m = m;
  this->d = d;
  mj_loadModel(m, this->shm.model.ptr);
}

void GuiClient::sync() {
  this->shm.info_lock.lock_upgradable();
  if (not *this->shm.info_byte) {
    *this->shm.info_byte = true;
    this->shm.state_lock.lock_sharable();
    mj_setState(this->m, this->d, this->shm.state.ptr, MJ_PHYSICS_SPEC);
    this->shm.state_lock.unlock_sharable();
  }
  this->shm.info_lock.unlock_upgradable();
}

#endif  // RCS_HAVE_BOOST
}  // namespace sim
}  // namespace rcs
