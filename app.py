import modal

image = (
    modal.Image.from_registry(
        "nvidia/cuda:12.8.0-devel-ubuntu22.04",
        add_python="3.12",
    )
    .entrypoint([])
    .apt_install("libgl1", "libglib2.0-0", "unzip", "wget", "git")
    .uv_pip_install(
        "torch==2.8.0",
        "huggingface_hub[hf_transfer]==0.35.0",
        "flashinfer-python==0.3.1",
        "addict",
        "pillow",
    )
    .pip_install(
        "vllm",
        pre=True,
        extra_options="--extra-index-url https://wheels.vllm.ai/nightly",
        )
    .env({"HF_HUB_ENABLE_HF_TRANSFER": "1"})  # faster model transfers
)


app = modal.App(
    name="modal-deepseek-ocr",
    image=image,
)

FAST_BOOT = True
MODEL_NAME = "deepseek-ai/DeepSeek-OCR"
MODEL_REVISION = "ee668a444ce026b7a23944f36692df1cdba54de9"  # avoid nasty surprises when repos update!
GPU = "t4"

hf_cache_vol = modal.Volume.from_name("huggingface-cache", create_if_missing=True)
vllm_cache_vol = modal.Volume.from_name("vllm-cache", create_if_missing=True)

@app.function(image=image, gpu=GPU, scaledown_window=60*5)
@modal.concurrent(max_inputs=3)
@modal.asgi_app(requires_proxy_auth=True)
def ocrapp():
    from vllm import LLM, SamplingParams
    from vllm.model_executor.models.deepseek_ocr import NGramPerReqLogitsProcessor
    from fastapi import FastAPI, Request
    from PIL import Image

    class Provider: 
        llm: LLM
        sampling_params: SamplingParams

    provider = Provider()
    
    def lifespan(wapp: FastAPI):
        print("starting")
        provider.llm = LLM(
            model="deepseek-ai/DeepSeek-OCR",
            enable_prefix_caching=False,
            mm_processor_cache_gb=0,
            logits_processors=[NGramPerReqLogitsProcessor]
        )

        provider.sampling_params = SamplingParams(
            temperature=0.0,
            max_tokens=8192,
            extra_args=dict(# ngram logit processor args
                            ngram_size=30,
                            window_size=90,
                            whitelist_token_ids={128821, 128822},  # whitelist: <td>, </td>
                            ),
            skip_special_tokens=False,
        )

        yield
        print("stopping")

    web_app = FastAPI(lifespan=lifespan)

    @web_app.post("/api/v1/describe")
    async def describe(req: Request):
        data = await req.json()
        import base64
        filename = data["file_name"]
        img_data = data["image"]
        bytes = base64.b64decode(img_data)
        with open(filename, "wb") as f:
            _ = f.write(bytes)
        image = Image.open(filename).convert("RGB")
        prompt = "<image>\nDescribe this image in detail."
        model_input = [
            {
                "prompt": prompt,
                "multi_modal_data": {"image": image}
            },
        ]
        model_outputs = provider.llm.generate(model_input, provider.sampling_params)
        full = ""
        for output in model_outputs:
            full += output.outputs[0].text
        return {"output": full}

    
    @web_app.post("/api/v1/locate")
    async def locate(req: Request):
        data = await req.json()
        import base64
        filename = data["file_name"]
        ref_text = data["ref_text"]
        img_data = data["image"]
        bytes = base64.b64decode(img_data)
        with open(filename, "wb") as f:
            _ = f.write(bytes)
        image = Image.open(filename).convert("RGB")
        prompt = "<image>\nFree OCR."
        prompt = f"<image>\nLocate <|ref|>{ref_text.strip()}<|/ref|> in the image."
        model_input = [
            {
                "prompt": prompt,
                "multi_modal_data": {"image": image}
            },
        ]
        model_outputs = provider.llm.generate(model_input, provider.sampling_params)
        full = ""
        for output in model_outputs:
            full += output.outputs[0].text
        return {"output": full}

    @web_app.post("/api/v1/locate-text")
    async def locate_text(req: Request):
        data = await req.json()
        import base64
        filename = data["file_name"]
        ref_text = data["ref_text"]
        img_data = data["image"]
        bytes = base64.b64decode(img_data)
        with open(filename, "wb") as f:
            _ = f.write(bytes)
        image = Image.open(filename).convert("RGB")
        prompt = f"<image>\nLocate <|ref|>{ref_text.strip()}<|/ref|> in the image."
        model_input = [
            {
                "prompt": prompt,
                "multi_modal_data": {"image": image}
            },
        ]
        model_outputs = provider.llm.generate(model_input, provider.sampling_params)
        full = ""
        for output in model_outputs:
            full += output.outputs[0].text
        return {"output": full}

    @web_app.post("/api/v1/custom")
    async def custom(req: Request):
        data = await req.json()
        import base64
        filename = data["file_name"]
        img_data = data["image"]
        prompt = data["prompt"]
        bytes = base64.b64decode(img_data)
        with open(filename, "wb") as f:
            _ = f.write(bytes)
        image = Image.open(filename).convert("RGB")
        model_input = [
            {
                "prompt": prompt,
                "multi_modal_data": {"image": image}
            },
        ]
        model_outputs = provider.llm.generate(model_input, provider.sampling_params)
        full = ""
        for output in model_outputs:
            full += output.outputs[0].text
        return {"output": full}


    return web_app
