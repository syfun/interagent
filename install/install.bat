mkdir config
copy null ./config/device.json


curl -URi http://47.99.92.189:6789/media/.env -OutFile .env
curl -URi http://47.99.92.189:6789/media/docker-compose.yaml -OutFile docker-compose.yaml
curl -URi http://47.99.92.189:6789/media/nginx.conf -OutFile nginx.conf
curl -URi http://47.99.92.189:6789/media/startgame.bat -OutFile startgame.bat

mkdir media
docker-compose up -d backend
docker-compose up -d
