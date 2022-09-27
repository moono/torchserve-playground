import os
import glob
import base64
import asyncio
import httpx
import numpy as np


async def test_ts_inputs(pred_url: str):
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    txt_file = os.path.join(parent_dir, "sample_text.txt")
    img_file = os.path.join(parent_dir, "sketch-mountains-input.jpg")
    files = {
        "txt": ("sample_text.txt", open(txt_file, "rb"), "text/plain"),
        "img": ("sketch-mountains-input.jpg", open(img_file, "rb"), "image/jpeg"),
    }
    async with httpx.AsyncClient() as client:
        try:
            res = await client.post(pred_url, files=files)
            res.raise_for_status()
            return res.json()
        except httpx.HTTPError as e:
            raise e
    return


async def main(raw_args=None):
    model_name = "gpu_model"
    host = "172.20.41.45"
    port = 18080
    pred_url = f"http://{host}:{port}/predictions/{model_name}"
    
    ret = await test_ts_inputs(pred_url)
    print(ret)
    return


if __name__ == '__main__':
    asyncio.run(main())
