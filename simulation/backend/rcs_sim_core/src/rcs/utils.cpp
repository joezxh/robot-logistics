#include "rcs/utils.h"

#include <iostream>

#ifdef RCS_HAVE_EGL
#include <EGL/egl.h>

namespace rcs {
namespace common {
static PFNEGLMAKECURRENTPROC g_makeCurrent = nullptr;
static EGLDisplay g_display = EGL_NO_DISPLAY;
static EGLSurface g_surface = EGL_NO_SURFACE;
static EGLContext g_context = EGL_NO_CONTEXT;

void bootstrap_egl(uintptr_t fn_addr, uintptr_t dpy, uintptr_t ctx) {
  g_makeCurrent = reinterpret_cast<PFNEGLMAKECURRENTPROC>(fn_addr);
  g_display = reinterpret_cast<EGLDisplay>(dpy);
  g_context = reinterpret_cast<EGLContext>(ctx);
}

void ensure_current() {
  if (g_makeCurrent == nullptr || g_display == EGL_NO_DISPLAY ||
      g_context == EGL_NO_CONTEXT) {
    throw std::runtime_error(
        "EGL rendering was requested, but EGL was not bootstrapped. "
        "This usually means libEGL or the MuJoCo EGL context is unavailable. "
        "Run without cameras/viewers if you do not need rendering, or install "
        "the required system EGL/OpenGL runtime libraries.");
  }
  if (!g_makeCurrent(g_display, g_surface, g_surface, g_context))
    throw std::runtime_error("eglMakeCurrent failed");
}
}  // namespace common
}  // namespace rcs
#else
namespace rcs {
namespace common {
void bootstrap_egl(uintptr_t, uintptr_t, uintptr_t) {}
void ensure_current() {
  throw std::runtime_error("EGL rendering not available in this build.");
}
}  // namespace common
}  // namespace rcs
#endif

