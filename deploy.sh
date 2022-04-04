LAYER_DIR="layer"
SRC_DIR="lambda"

rm ${LAYER_DIR} -f -r
mkdir ${LAYER_DIR}

pip install -r ${SRC_DIR}/requirements.txt -t ${LAYER_DIR}/python/