import logging
import traceback
import torch

from io import BytesIO
from typing import List, Dict, Any, Tuple, Union
from PIL import Image
from PIL.PngImagePlugin import PngInfo
from ts.context import Context

from image_pb2 import Image as ImageContainer

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
    def serialize(image: Image.Image) -> bytes:
        buf = BytesIO()
        metadata = PngInfo()
        for k, v in image.info.items():
            metadata.add_text(k, v)
        image.save(buf, format="PNG", pnginfo=metadata)
        container = ImageContainer(
            image_data=buf.getvalue(), height=image.height, width=image.width
        )
        return container.SerializeToString()

    @staticmethod
    def deserialize(serialized: Union[bytes, bytearray]) -> Image.Image:
        if isinstance(serialized, bytearray):
            buf = bytes(serialized)
        else:
            buf = serialized
        container = ImageContainer()
        container.ParseFromString(buf)
        return Image.open(BytesIO(container.image_data))

    def preprocess(self, row: Dict[str, Any], is_protobuf: bool) -> Image.Image:
        if is_protobuf:
            return self.deserialize(row["body"])
        else:
            raise NotImplementedError("Not implemented yet !!")

    def run(self, image: Image.Image) -> bytes:
        return self.serialize(image)

    def _is_protobuf(
        self, idx: int = 0, content_type: str = "application/protobuf"
    ) -> bool:
        if not self.context:
            raise ValueError("Error parsing context !!")

        req_headers = self.context.get_all_request_header(idx=idx)
        for k, v in req_headers.items():
            if k.lower() == "content-type":
                if v.lower() == content_type:
                    return True
                else:
                    return False
        return False

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
            is_protobuf = self._is_protobuf(idx=0)

            # run
            image = self.preprocess(data[0], is_protobuf)
            out = self.run(image)
            output.append(out)
        except Exception as e:
            logger.error(f"Error in nutshell: {type(e).__name__}: {e}")
            logger.error(f"Error in detailed: ...")
            full_traceback = traceback.format_exc().split("\n")
            for tr in full_traceback:
                logger.error(tr)
            raise e
        return output
