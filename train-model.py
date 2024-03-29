import shutil
from ultralytics import YOLO
import argparse
import json
import debugpy

# Valohai: Use argparse to parse the arguments
def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--epochs', type=int, default=2)
    parser.add_argument('--optimizer', type=str, default='SGD')
    parser.add_argument('--debug', type=int, default=0)
    return parser.parse_args()

# Define a method that prints out key metrics from the trainer
# yolov8 includes (B) for object detection and (M) for segmentation
def print_valohai_metrics(trainer):
    metadata = {
        "epoch": trainer.epoch,
        "mAP50-95": trainer.metrics["metrics/mAP50-95(B)"],
        "mAP50": trainer.metrics["metrics/mAP50(B)"],
        "precision": 0 # TODO: Include precision metric
    }

    print(json.dumps(metadata))

args = parse_args()

if args.debug == 1:
    # Listen on port 5678
    debugpy.listen(5678)

    # The script is halted here, until a debugger is attached
    debugpy.wait_for_client()

# Load a model
model = YOLO("yolov8n.pt")  # load a pretrained model (recommended for training)
# Valohai: Add a callback function, every time an epoch ends, print the metrics
model.add_callback("on_train_epoch_end", print_valohai_metrics)

# Use the model
# Valohai: Use the epoch value from argparse
# train the model
model.train(data="coco128.yaml", epochs=args.epochs, optimizer=args.optimizer, verbose=False)

exported_model = model.export(format="onnx")  # export the model to ONNX format

# Valohai: Copy the exported model to the Valohai outputs directory
shutil.copy(exported_model, '/valohai/outputs/model.onnx')