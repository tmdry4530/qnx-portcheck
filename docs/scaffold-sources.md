# Scaffold template sources

The templates reproduce functional interfaces needed by QNX recursive make. Upstream has no license file, so generated templates do not copy its comment prose; explanatory comments are newly written. All entries refer to `https://github.com/qnx-ports/build-files` at commit `79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5`.

| Upstream file | Generated file | Deliberate deviations |
|---|---|---|
| [ports/cJSON/Makefile](https://github.com/qnx-ports/build-files/blob/79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5/ports/cJSON/Makefile) | Makefile | Recursive stub retained; no upstream prose copied. |
| [ports/cJSON/common.mk](https://github.com/qnx-ports/build-files/blob/79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5/ports/cJSON/common.mk) | CMake common.mk | Generic name and install settings; QNX_PROJECT_ROOT defaults to `$(PROJECT_ROOT)/../..`; removes project-specific options. |
| [ports/cJSON/qnx.nto.toolchain.cmake](https://github.com/qnx-ports/build-files/blob/79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5/ports/cJSON/qnx.nto.toolchain.cmake) | qnx.nto.toolchain.cmake | Removes VSOMEIP_EXTERNAL_DEPS_INSTALL and uses generic QNX roots. |
| [ports/cJSON/nto-aarch64-le/Makefile](https://github.com/qnx-ports/build-files/blob/79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5/ports/cJSON/nto-aarch64-le/Makefile) | nto-aarch64-le/Makefile | Include line retained. |
| [ports/cJSON/nto-x86_64-o/Makefile](https://github.com/qnx-ports/build-files/blob/79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5/ports/cJSON/nto-x86_64-o/Makefile) | nto-x86_64-o/Makefile | Include line retained. |
| [ports/fribidi/common.mk](https://github.com/qnx-ports/build-files/blob/79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5/ports/fribidi/common.mk) | Meson common.mk | `MESON ?= meson` is overridable; project-specific options are omitted. |
| [ports/fribidi/qnx_cross.txt.in](https://github.com/qnx-ports/build-files/blob/79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5/ports/fribidi/qnx_cross.txt.in) | qnx_cross.txt.in | Generic cross file, with project-specific settings omitted. |
| [ports/libffi/common.mk](https://github.com/qnx-ports/build-files/blob/79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5/ports/libffi/common.mk) | Autotools common.mk | QNX_PROJECT_ROOT default adapted; uses correctly spelled RANLIB; autoreconf only when configure is absent. |
| [ports/bzip2/common.mk](https://github.com/qnx-ports/build-files/blob/79d94bd6f1d66e524b17c1f26379ac0ef9bd24c5/ports/bzip2/common.mk) | Make common.mk | Generic all/install targets have a TODO for project adaptation. |

All templates use the same upstream repository URL and commit SHA shown above. The QNX SDP was not available, so generated files were not built with the SDP and were not run on a QNX target.
