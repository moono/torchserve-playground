import os
import grpc
import inference_pb2
import inference_pb2_grpc

from io import BytesIO
from grpc_model_pb2 import MixedInput, MixedOutput
from PIL import Image
# import management_pb2
# import management_pb2_grpc


def get_inference_stub():
    channel = grpc.insecure_channel("172.20.41.45:7070")
    stub = inference_pb2_grpc.InferenceAPIsServiceStub(channel)
    return stub


def deserialize_output(serialized: bytes):
    container = MixedOutput()
    container.ParseFromString(serialized)
    
    if not container.generated_image:
        print("Empty input image")
    else:
        image = Image.open(BytesIO(container.generated_image))
        print(f"image info: {image.info}")
        print(f"image size: {image.size}")
    print(f"model_name: {container.model_name}")
    return

def infer(stub, model_name, fn1, metadata):
    with open(fn1, "rb") as f:
        image1 = f.read()

    data = MixedInput()
    data.image_data = image1
    data.prompt = "hello world"
    data.height = 768
    # data.width = 512
    data.task = MixedInput.Task.IMG2IMG
    
    data.lora_names.extend(["lora_01", "lora_02"])
    
    
    input_data = {"data": data.SerializeToString()}
    response = stub.Predictions(
        inference_pb2.PredictionsRequest(model_name=model_name, input=input_data),
        metadata=metadata,
    )

    try:
        # prediction = response.prediction.decode("utf-8")
        # print(prediction)
        prediction = response.prediction
        
        deserialize_output(prediction)
    except grpc.RpcError as e:
        exit(1)


def main(raw_args=None):
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(parent_dir, "assets")
    image_fn1 = os.path.join(assets_dir, "512x512_02.png")
    # image_fn2 = os.path.join(assets_dir, "512x512_03.png")
    model_name = "grpc_model"
    metadata = (("protocol", "gRPC"), ("session_id", "12345"))
    infer(get_inference_stub(), model_name, image_fn1, metadata)
    return


if __name__ == "__main__":
    main()
