#/bin/bash
set -e
IMAGE=dockerhub_username/somapi
VERSION=v1.0.6
echo "Building $IMAGE:$VERSION"
# python3 manage.py test
# git push origin main
docker build -t $IMAGE:$VERSION.arm . --platform=linux/arm64

do_push() {
  echo "Publishing image.."
  docker build -t $IMAGE:$VERSION . --platform=linux/amd64
  docker tag  $IMAGE:$VERSION  $IMAGE:latest
  docker push $IMAGE:$VERSION
}

# Loop through the arguments
for arg in "$@"; do
  case $arg in
    --push)
      do_push
      ;;
  esac
done
