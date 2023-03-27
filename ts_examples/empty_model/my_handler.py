import os
import time
import traceback
import torch

from typing import List, Dict, Any, Tuple
from ts.context import Context

from log_config import get_logger

logger = get_logger(
    name=__name__,
    level=os.environ.get("MY_TS_MODEL_LOG_LEVEL", "DEBUG"),
)


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
        return

    @staticmethod
    def parse_req_id(context: Context, idx: int) -> str:
        # X-Request-ID, X-Request-Id, x-request-id
        req_headers = context.get_all_request_header(idx=idx)
        req_id = None
        for k, v in req_headers.items():
            if k.lower() == "x-request-id":
                req_id = v
        if req_id is None:
            req_id = context.get_request_id(idx=idx)
        return req_id

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

        self.initialized = True
        logger.info(f"Model initialization ... DONE !!")
        return

    def run(self, row: Dict[str, Any], log_extra: Dict[str, str]):
        sleep_s = int(row.get("sleep_s", 1))

        logger.debug({"msg": f"sleeping {sleep_s}s ... "}, extra=log_extra)
        time.sleep(sleep_s)
        logger.debug({"msg": f"sleeping {sleep_s}s ... DONE "}, extra=log_extra)
        return

    # must have: Torchserve
    def handle(self, data: List[Dict[str, Any]], context: Context):
        # It can be used for pre or post processing if needed as additional request
        # information is available in context

        self.context = context
        # metrics = self.context.metrics

        output = list()
        for idx, row in enumerate(data):
            # parse request headers
            req_id = self.parse_req_id(context=context, idx=idx)
            log_extra = None if req_id is None else {"requestId": req_id}

            try:
                # run
                out = self.run(row, log_extra)
                output.append(out)
            except Exception as e:
                logger.error(
                    f"Error in nutshell: {type(e).__name__}: {e}", extra=log_extra
                )
                logger.error(f"Error in detailed: ...", extra=log_extra)
                full_traceback = traceback.format_exc().split("\n")
                for tr in full_traceback:
                    logger.error(tr, extra=log_extra)
                raise e
        # logger.info(f"Outputs batch size of {len(output)} !!!")
        return output
