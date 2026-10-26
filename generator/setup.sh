#!/usr/bin/env bash
# Instala todo lo que necesita el generador de reels de Salió caro (idempotente, cachea en ~/.cache/saliocaro)
set -euo pipefail
C="$HOME/.cache/saliocaro"; mkdir -p "$C/fonts"
python3 -m pip install -q --break-system-packages kokoro-onnx soundfile pillow numpy imageio-ffmpeg wordfreq 2>/dev/null \
  || python3 -m pip install -q kokoro-onnx soundfile pillow numpy imageio-ffmpeg wordfreq
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s "$C/$f" ] || curl -sSL --retry 3 -o "$C/$f" "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
cd "$C/fonts"
get_font () {  # $1 paquete npm  $2 fichero dentro del paquete  $3 nombre destino
  [ -s "$3" ] && return 0
  rm -rf package && npm pack -s "$1" >/dev/null && tar xzf ./*.tgz && cp "package/files/$2" "$3" && rm -rf package ./*.tgz
}
get_font @fontsource/anton@5.0.20 anton-latin-400-normal.woff Anton.woff
get_font @fontsource/inter@5.0.20 inter-latin-700-normal.woff Inter-Bold.woff
get_font @fontsource/inter@5.0.20 inter-latin-500-normal.woff Inter-Medium.woff
get_font @fontsource/montserrat@5.0.19 montserrat-latin-900-normal.woff MontBlack.woff
get_font @fontsource/montserrat@5.0.19 montserrat-latin-800-normal.woff MontXB.woff
python3 - <<'EOF'
import os
from PIL import ImageFont
C = os.path.expanduser("~/.cache/saliocaro")
for f in ["fonts/MontBlack.woff", "fonts/MontXB.woff", "fonts/Anton.woff", "fonts/Inter-Bold.woff", "fonts/Inter-Medium.woff", "kokoro-v1.0.onnx", "voices-v1.0.bin"]:
    p = os.path.join(C, f); assert os.path.getsize(p) > 1000, p
ImageFont.truetype(os.path.join(C, "fonts/Anton.woff"), 40)
print("setup OK")
EOF
