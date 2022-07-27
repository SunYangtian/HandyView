pyinstaller -D handyview/handyviewer.py \
  -i icon.ico \
  --add-data="handyview;handyview" \
  --add-data="icons;icons" \
  --add-data="icon.png;." \
  --add-data="icon.ico;." \
  --add-data="VERSION;." \
  --windowed \
  --noconfirm \
  --hidden-import="PIL.Image" \
  --hidden-import="PIL.ImageDraw" \
  --hidden-import="PyQt5.QtMultimedia" \
  --hidden-import="PyQt5.QtMultimediaWidgets" \
  --hidden-import="imagehash"
