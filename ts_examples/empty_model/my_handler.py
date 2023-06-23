import os
import time
import traceback
import torch

from typing import List, Dict, Any, Tuple
from ts.context import Context

from log_config import get_logger
from my_models import ModelStatus

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
        self.model_status = ModelStatus.not_ready
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

    # parse boolean env variable: default False
    @staticmethod
    def _parse_env_boolean(key: str) -> bool:
        v = False
        if key in os.environ:
            env_val = os.environ.get(key).lower()
            assert env_val in ("true", "false")
            v = True if env_val == "true" else False
        return v

    def initialize(self, context: Context) -> None:
        properties = context.system_properties
        self.map_location, self.device = self._check_device(properties)
        self.manifest = context.manifest
        model_dir = properties.get("model_dir")
        logger.info(f"Using backend {self.device}!")

        simulate_error = self._parse_env_boolean("SIMULATE_ERROR")
        if simulate_error:
            sleep_s = 10
            logger.info(f"sleeping {sleep_s}s ... ")
            time.sleep(sleep_s)
            logger.info(f"sleeping {sleep_s}s ... DONE")
            logger.info(f"Invoking error on initialization on purpose !!!")
            raise ValueError("Initialization Error!!")
        self.initialized = True
        self.model_status = ModelStatus.ready
        logger.info(f"Model initialization ... DONE !!")
        return

    def run(self, row: Dict[str, Any], log_extra: Dict[str, str]):
        sleep_s = int(row.get("sleep_s", 1))
        simulate_crash = row.get("simulate_crash", None)
        simulate_long_req = row.get("simulate_long_req", None)

        logger.debug({"msg": f"sleeping {sleep_s}s ... "}, extra=log_extra)
        time.sleep(sleep_s)
        logger.debug({"msg": f"sleeping {sleep_s}s ... DONE "}, extra=log_extra)

        if simulate_crash is not None:
            logger.debug({"msg": f"simulating crash by zero division"}, extra=log_extra)
            # zero division
            ret = 0 / 0

        if simulate_long_req is not None:
            logger.debug({"msg": f"simulating long response time "}, extra=log_extra)
            # default response timeout: 120
            time.sleep(int(simulate_long_req))
        return

    def _is_describe(self):
        if self.context and self.context.get_request_header(0, "describe"):
            if self.context.get_request_header(0, "describe") == "True":
                return True
        return False

    def describe_handle(self):
        logger.info("Collect customized metadata")
        return {"status": self.model_status}

    # must have: Torchserve
    def handle(self, data: List[Dict[str, Any]], context: Context):
        # It can be used for pre or post processing if needed as additional request
        # information is available in context

        self.context = context
        # metrics = self.context.metrics

        if self._is_describe():
            output = [self.describe_handle()]
            return output

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
