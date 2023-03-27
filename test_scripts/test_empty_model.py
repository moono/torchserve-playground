import asyncio
import httpx


async def test_ts(pred_url: str, sleep_s: int, n_req: int):
    data = {"sleep_s": sleep_s}
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            tasks = [client.post(pred_url, data=data) for ii in range(n_req)]
            responses = await asyncio.gather(*tasks)
            return [res.json() for res in responses]
        except httpx.HTTPError as e:
            raise e


async def main(raw_args=None):
    model_name = "empty_model"
    host = "172.20.41.45"
    port = 8080
    pred_url = f"http://{host}:{port}/predictions/{model_name}"

    n_req = 20
    sleep_s = 3

    ret = await test_ts(pred_url, sleep_s=sleep_s, n_req=n_req)
    print(ret)
    return


if __name__ == "__main__":
    asyncio.run(main())
