import os
import logging
import importlib
import torch
import numpy as np

from io import BytesIO
from logging.config import dictConfig
from typing import List, Dict, Any, Tuple
from zipfile import ZipFile
from PIL import Image
from ts.context import Context

from log_config import gen_log_config

# set logging config
dictConfig(
    gen_log_config(__name__, level=os.environ.get("MY_TS_MODEL_LOG_LEVEL", "DEBUG"))
)
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
        # self.zip_file = "some_model.zip"
        self.model = None
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

    def initialize(self, context: Context) -> None:
        properties = context.system_properties
        self.map_location, self.device = self._check_device(properties)
        self.manifest = context.manifest
        model_dir = properties.get("model_dir")
        logger.info(f"Using backend {self.device}!")

        # prepare files
        # logger.info(f"Unzipping {self.zip_file} ...")
        # if not os.path.isfile(self.zip_file):
        #     raise RuntimeError(f"{self.log_prefix} Missing {self.zip_file} file")
        # with ZipFile(self.zip_file, "r") as zip_ref:
        #     zip_ref.extractall(model_dir)
        # logger.info(f"Unzipping {self.zip_file} ... DONE !!")

        # initialize model
        # from model_initialization import initialize as model_init

        # safety_checks_module = importlib.import_module("safety_checks")
        # self.check_safety = getattr(safety_checks_module, "check_safety")
        # self.model, self.sampler, self.wm_encoder = model_init(self.opt, self.device)

        self.initialized = True
        logger.info(f"Model initialization ... DONE !!")
        return

    def preprocess(self, data: List[Dict[str, Any]]) -> List[str]:
        def _print(item: Any):
            for k, v in item.items():
                if isinstance(v, dict):
                    _print(v)
                else:
                    logger.debug(f"{k}: {type(v)}")
            return
        inputs = list()
        for row in data:
            _print(row)
            inputs.append("inputs ...")
        return inputs

    def inference(self, data: List[str]) -> List[str]:
        batch_size = len(data)
        logger.debug(f"batch_size: {batch_size}")
        return data

    def postprocess(data: List[str]) -> List[str]:
        # image_bytes = list()
        # for img in images:
        #     buf = BytesIO()
        #     img.save(buf, format="JPEG")
        #     image_bytes.append(buf.getvalue())
        #     buf.close()
        return data

    # must have: Torchserve
    def handle(self, data: List[Dict[str, Any]], context: Context):
        # It can be used for pre or post processing if needed as additional request
        # information is available in context

        self.context = context
        # metrics = self.context.metrics

        # run
        batch_size = len(data)
        logger.info(f"Received batch size of {batch_size} !!!")

        data1 = self.preprocess(data)
        # data2 = self.inference(data1)
        # output = self.postprocess(data2)
        # logger.debug(f"output type: {type(output)}")
        # return output
        return [{"output": "output_sample"} for _ in range(batch_size)]