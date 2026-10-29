#!/bin/bash
# Actual native harness from /tmp/bambu-wx-native-font/run-dip.sh, linked
# directly against the newly installed archive (no replacement window object).
set -euo pipefail
cd /home/bxb/.local/state/bambu-scaling/build-02.08.04.57
source ./env.sh
wx_build="$BAMBU_BUILD_ROOT/wx-system-options-off"
wx_source="$BAMBU_BUILD_ROOT/deps-build/dep_wxWidgets-prefix/src/dep_wxWidgets"
read -r -a gtk_flags <<< "$(pkg-config --cflags gtk+-3.0)"
read -r -a dep_libs <<< "$(pkg-config --libs gtk+-3.0 libsecret-1 libpng libjpeg libtiff-4 fontconfig pangoft2 x11 xext sm ice)"
common=(-std=c++11 -O0 -DwxDEBUG_LEVEL=0 -D__WXGTK3__ -D__WXGTK__ -pthread -Wno-deprecated-declarations -I"$wx_build/lib/wx/include/gtk3-unicode-static-3.1" -I"$wx_source/include" "${gtk_flags[@]}")
libs=("$BAMBU_BUILD_ROOT/wx-system-options-off-prefix/lib/libwx_gtk3u_core-3.1.a" "$BAMBU_BUILD_ROOT/wx-system-options-off-prefix/lib/libwx_baseu-3.1.a" "$BAMBU_BUILD_ROOT/wx-system-options-off-prefix/lib/libwxregexu-3.1.a" "$BAMBU_BUILD_ROOT/deps-build/destdir/usr/local/lib/libpng.a" "${dep_libs[@]}" -ldl)
export TMPDIR="$BAMBU_BUILD_ROOT/tmp"
mkdir -p logs/polished-probes
nice -n 19 c++ "${common[@]}" probes/polished-native-dip-range-measurement.cpp "${libs[@]}" -o probes/polished-options-off-range
for scale in 1 2; do
 for dpi in 96 120 144 192 dynamic; do
  log="logs/polished-probes/options-disabled-scale${scale}-${dpi}.log"
  xvfb-run -a -s '-screen 0 1280x800x24 -dpi 96' env -u WXGTK_DIP_SCALE -u wx_gtk_window_font_dpi_scaling -u LD_PRELOAD -u LD_LIBRARY_PATH GDK_BACKEND=x11 GDK_SCALE="$scale" GDK_DPI_SCALE=1 ./probes/polished-options-off-range "$dpi" "$scale" 1 > "$log" 2>&1
  if rg -q 'FAIL|WARNING|CRITICAL' "$log"; then cat "$log"; exit 1; fi
  echo "PASS actual separately installed wxUSE_SYSTEM_OPTIONS=0 archive requested-option=1 scale=$scale dpi=$dpi"
 done
done
