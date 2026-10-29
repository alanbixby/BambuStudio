#!/bin/bash
# Actual native harness from /tmp/bambu-wx-native-font/run-dip.sh, linked
# directly against the newly installed archive (no replacement window object).
set -euo pipefail
cd /home/bxb/.local/state/bambu-scaling/build-02.08.04.57
source ./env.sh
wx_build="$BAMBU_BUILD_ROOT/deps-build/dep_wxWidgets-prefix/src/dep_wxWidgets-build"
wx_source="$BAMBU_BUILD_ROOT/deps-build/dep_wxWidgets-prefix/src/dep_wxWidgets"
read -r -a gtk_flags <<< "$(pkg-config --cflags gtk+-3.0)"
read -r -a dep_libs <<< "$(pkg-config --libs gtk+-3.0 libsecret-1 libpng libjpeg libtiff-4 fontconfig pangoft2 x11 xext sm ice)"
common=(-std=c++11 -O0 -DwxDEBUG_LEVEL=0 -D__WXGTK3__ -D__WXGTK__ -pthread -Wno-deprecated-declarations -I"$wx_build/lib/wx/include/gtk3-unicode-static-3.1" -I"$wx_source/include" "${gtk_flags[@]}")
libs=("$BAMBU_BUILD_ROOT/deps-build/destdir/usr/local/lib/libwx_gtk3u_core-3.1.a" "$BAMBU_BUILD_ROOT/deps-build/destdir/usr/local/lib/libwx_baseu-3.1.a" "$BAMBU_BUILD_ROOT/deps-build/destdir/usr/local/lib/libwxregexu-3.1.a" "$BAMBU_BUILD_ROOT/deps-build/destdir/usr/local/lib/libpng.a" "${dep_libs[@]}" -ldl)
export TMPDIR="$BAMBU_BUILD_ROOT/tmp"
mkdir -p logs/polished-probes
c++ "${common[@]}" -E -P /tmp/bambu-polish-20261028/implementation/build/range-probe-before-options-off-guard.cpp > tmp/range-before-options-off-guard.i
c++ "${common[@]}" -E -P probes/polished-native-dip-range-measurement.cpp > tmp/range-after-options-off-guard.i
cmp tmp/range-before-options-off-guard.i tmp/range-after-options-off-guard.i
sha256sum tmp/range-before-options-off-guard.i tmp/range-after-options-off-guard.i
