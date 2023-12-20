import logging
import traceback
import torch

from io import BytesIO
from typing import List, Dict, Any, Tuple, Union, Optional
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from ts.context import Context

from grpc_model_pb2 import MixedInput, MixedOutput

logger = logging.getLogger(__name__)


class MyTSModel(object):
    def __init__(self) -> None:
        self.model = None
        self.mapping = None
        self.device = None
        self.initialized = False
        self.context = None
        self.manifest = None
        self.map_location = None

        # model specific
        self.model = None
        self.is_protobuf = None
        return

    @staticmethod
    def _check_device(properties: Dict[str, Any]) -> Tuple[str, torch.device]:
        # default is "cpu"
        map_location = "cpu"
        device = torch.device("cpu")
        if torch.cuda.is_available() and properties.get("gpu_id") is not None:
            map_location = "cuda"
            device = torch.device(map_location + ":" + str(properties.get("gpu_id")))
        return (map_location, device)

    # must have: Torchserve
    def initialize(self, context: Context) -> None:
        properties = context.system_properties
        self.map_location, self.device = self._check_device(properties)
        self.manifest = context.manifest
        model_dir = properties.get("model_dir")
        logger.info(f"Using backend {self.device}!")

        self.initialized = True
        logger.info(f"Model initialization ... DONE !!")
        return

    @staticmethod
    def deserialize(serialized: Union[bytes, bytearray]) -> Optional[Image.Image]:
        if isinstance(serialized, bytearray):
            buf = bytes(serialized)
        else:
            buf = serialized
        container = MixedInput()
        container.ParseFromString(buf)

        print(type(container))
        if not container.image_data:
            print("Empty input image")
            image = None
        else:
            image = Image.open(BytesIO(container.image_data))
        print(f"image: {type(container.image_data)} / {container.image_data}")
        print(f"prompt: {type(container.prompt)} / {container.prompt}")
        print(f"height: {type(container.height)} / {container.height}")
        print(f"width: {type(container.width)} / {container.width}")
        print(f"task: {type(container.task)} / {container.task}")
        print(f"lora_names: {type(container.lora_names)} / {container.lora_names}")

        return image

    def preprocess(self, row: Dict[str, Any]) -> Optional[Image.Image]:
        image = self.deserialize(row["data"])
        return image

    def postprocess(self, image: Optional[Image.Image]) -> bytes:
        model_name = "myModel"
        if image is not None:
            buf = BytesIO()
            metadata = PngInfo()
            for k, v in image.info.items():
                if isinstance(v, str):
                    metadata.add_text(k, v)
            image.save(buf, format="PNG", pnginfo=metadata)

            container = MixedOutput(
                generated_image=buf.getvalue(), model_name=model_name
            )
        else:
            container = MixedOutput(model_name=model_name)
        return container.SerializeToString()

    # must have: Torchserve
    def handle(self, data: List[Dict[str, Any]], context: Context):
        # It can be used for pre or post processing if needed as additional request
        # information is available in context

        self.context = context
        # metrics = self.context.metrics

        if len(data) != 1:
            raise ValueError("Only batch size 1 supported !!")

        output = list()
        try:
            # check header
            req_headers = self.context.get_all_request_header(idx=0)
            for k, v in req_headers.items():
                if k.lower() == "content-type":
                    print(f"content-type: {v.lower()}")

            # run
            inputs = self.preprocess(data[0])
            out = self.postprocess(inputs)
            output.append(out)
        except Exception as e:
            logger.error(f"Error in nutshell: {type(e).__name__}: {e}")
            logger.error(f"Error in detailed: ...")
            full_traceback = traceback.format_exc().split("\n")
            for tr in full_traceback:
                logger.error(tr)
            raise e
        return output
