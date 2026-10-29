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
for name in native-dip-range-measurement dip-probe native-label-measurement; do
 extra=()
 if [[ "$name" == native-label-measurement ]]; then extra=(-Wl,--wrap=gtk_style_context_invalidate); fi
 nice -n 19 c++ "${common[@]}" "probes/polished-$name.cpp" "${libs[@]}" "${extra[@]}" -o "probes/polished-$name"
done
for mode in unset 0 1; do
 for scale in 1 2; do
  for dpi in 72 96 120 144 192 dynamic; do
   log="logs/polished-probes/range-option${mode}-scale${scale}-${dpi}.log"
   xvfb-run -a -s '-screen 0 1280x800x24 -dpi 96' env -u WXGTK_DIP_SCALE -u wx_gtk_window_font_dpi_scaling -u LD_PRELOAD -u LD_LIBRARY_PATH GDK_BACKEND=x11 GDK_SCALE="$scale" GDK_DPI_SCALE=1 ./probes/polished-native-dip-range-measurement "$dpi" "$scale" "$mode" > "$log" 2>&1
   if rg -q 'FAIL|WARNING|CRITICAL' "$log"; then cat "$log"; exit 1; fi
   echo "PASS actual installed archive option=$mode scale=$scale dpi=$dpi"
  done
 done
 log="logs/polished-probes/no-frame-option${mode}.log"
 xvfb-run -a -s '-screen 0 1280x800x24 -dpi 96' env -u WXGTK_DIP_SCALE -u wx_gtk_window_font_dpi_scaling -u LD_PRELOAD -u LD_LIBRARY_PATH GDK_BACKEND=x11 GDK_SCALE=1 GDK_DPI_SCALE=1 ./probes/polished-dip-probe "$mode" > "$log" 2>&1
 if rg -q 'FAIL|WARNING|CRITICAL' "$log"; then cat "$log"; exit 1; fi
 echo "PASS actual installed archive no-frame option=$mode"
done
for dpi in 96 144; do
 log="logs/polished-probes/label-${dpi}.log"
 xvfb-run -a -s "-screen 0 1280x800x24 -dpi $dpi" env -u LD_PRELOAD -u LD_LIBRARY_PATH -u WXGTK_DIP_SCALE GDK_BACKEND=x11 GDK_SCALE=1 GDK_DPI_SCALE=1 ./probes/polished-native-label-measurement "$dpi" > "$log" 2>&1
 if rg -q 'FAIL|WARNING|CRITICAL' "$log"; then cat "$log"; exit 1; fi
 cat "$log"
done
