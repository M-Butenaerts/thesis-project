docker rm -f tx-runner-DK 2>/dev/null || true
docker rm -f tx-runner-RSA 2>/dev/null || true

docker network disconnect -f fabric_test tx-runner-DK 2>/dev/null || true
docker network disconnect -f fabric_test tx-runner-RSA 2>/dev/null || true
docker build -t tx-runner:latest -f Dockerfile .

docker compose down 
docker compose build --no-cache  
docker compose up -d 
docker network connect fabric_test tx-runner-DK || true 
docker network connect fabric_test tx-runner-RSA || true 
