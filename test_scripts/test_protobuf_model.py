import os
import glob
import asyncio
import httpx
import requests

from io import BytesIO
from typing import Union
from PIL import Image
from PIL.PngImagePlugin import PngInfo

from image_pb2 import Image as ImageContainer


def image_to_buf(image: Image.Image) -> bytes:
    buf = BytesIO()
    metadata = PngInfo()
    for k, v in image.info.items():
        metadata.add_text(k, v)
    image.save(buf, format="PNG", pnginfo=metadata)
    return buf.getvalue()


def image_to_container(
    image: Image.Image, serialize: bool = False
) -> Union[ImageContainer, bytes]:
    buf = image_to_buf(image)
    container = ImageContainer(image_data=buf, height=image.height, width=image.width)
    if serialize:
        return container.SerializeToString()
    else:
        return container


def container_bytes_to_image(serialized: bytes) -> Image.Image:
    container = ImageContainer()
    container.ParseFromString(serialized)
    return Image.open(BytesIO(container.image_data))


async def test_ts(pred_url: str, data: bytes) -> bytes:
    headers = {"Content-Type": "application/protobuf"}
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            res = await client.post(pred_url,headers=headers, content=data)
            res.raise_for_status()
            return res.content
        except httpx.HTTPError as e:
            raise e

def test_ts_sync(pred_url: str, data: bytes):
    headers = {"Content-Type": "application/protobuf"}
    res = requests.post(pred_url, headers=headers, data=data)
    res.raise_for_status()
    return res.content

async def main(raw_args=None):
    model_name = "protobuf_model"
    host = "172.20.41.45"
    port = 8080
    pred_url = f"http://{host}:{port}/predictions/{model_name}"

    parent_dir = os.path.dirname(os.path.abspath(__file__))
    assets_dir = os.path.join(parent_dir, "assets")
    output_dir = os.path.join(parent_dir, "output")
    os.makedirs(output_dir, exist_ok=True)
    image_fns = glob.glob(os.path.join(assets_dir, "*.png"))

    for fn in image_fns:
        fn_only = os.path.basename(fn)
        print(fn_only)

        image = Image.open(fn)
        serialized = image_to_container(image, serialize=True)

        # ret = test_ts_sync(pred_url, serialized)
        ret = await test_ts(pred_url, serialized)
        print(type(ret))
        image_ret = container_bytes_to_image(ret)
        print(image_ret.info)
        print()
        image_ret.save(os.path.join(output_dir, f"{fn_only}_out.png"))
        return
    # print(ret)
    return


if __name__ == "__main__":
    asyncio.run(main())
