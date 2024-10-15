auth_token="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"

import torch
from torch import autocast
from diffusers import StableDiffusionPipeline 



prompt = "Image of beautiful mountain veiw with a river flowing bottom to top"

modelid = "CompVis/stable-diffusion-v1-4"
device = "cuda"
pipe = StableDiffusionPipeline.from_pretrained(modelid, revision="fp16", torch_dtype=torch.float16, use_auth_token=auth_token) 
pipe.to(device) 

def generate(): 
    with autocast(device): 
        image = pipe(prompt, guidance_scale=8.5).images[0]
    
    image.save('generatedimage.png')
generate()