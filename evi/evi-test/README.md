## Overview

Docker Compose:
1) `docker compose build`
2) `docker compose up`


Docker:


```hume-api-examples git:(my_hume) ✗ sudo docker run -it \       
   --device /dev/snd \
   -e PULSE_SERVER=unix:${XDG_RUNTIME_DIR}/pulse/native \
   -v ${XDG_RUNTIME_DIR}/pulse/native:${XDG_RUNTIME_DIR}/pulsee/native \
   -v ~/.config/pulse/cookie:/root/.config/pulse/cookie \
   -v /run/user/$(id -u):/run/user/$(id -u) \
   --group-add audio \
   hume-app bash```
