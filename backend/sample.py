import torch
from torch import autocast
from diffusers import StableDiffusionPipeline
from PIL import Image, ImageDraw, ImageFont
import json
import numpy as np

# Assuming you have an `ollama` function that enhances text and provides image prompts.
def ollama_text_enhancement(story):
    # Placeholder function. Replace with API call or text enhancement logic.
    enhanced_story = "Enhanced: " + story  # Enhance the story (Mockup)
    no_images = 3  # Assume 3 images needed based on story length
    return enhanced_story, no_images

# Generate image prompts based on the enhanced story and number of images required.
def generate_prompts(enhanced_story, no_images):
    segments = enhanced_story.split('.')  # Split story into segments by sentence.
    prompts = [segment.strip() for segment in segments if segment.strip()][:no_images]
    return [{"text": text, "prompt": f"Generate an image for: {text}"} for text in prompts]

# Function to add text to an image using Pillow
def add_text_to_image(image, text, position=(10, 10), font_size=24, font_color=(255, 255, 255)):
    draw = ImageDraw.Draw(image)
    # Load a font or use the default font
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except IOError:
        font = ImageFont.load_default()
    
    # Draw text on the image
    draw.text(position, text, fill=font_color, font=font)
    return image

# Image generation pipeline using Stable Diffusion, with text addition.
def generate_images_with_text(prompts, modelid="CompVis/stable-diffusion-v1-4", device="cuda", auth_token=None):
    # Initialize the Stable Diffusion pipeline
    pipe = StableDiffusionPipeline.from_pretrained(
        modelid, 
        revision="fp16", 
        torch_dtype=torch.float16, 
        use_auth_token=auth_token
    )
    pipe.to(device)

    generated_images = []
    for idx, prompt in enumerate(prompts):
        with autocast(device):
            image = pipe(prompt["prompt"], guidance_scale=8.5).images[0]

        # Convert to NumPy array and then to PIL image
        image = np.array(image)  # Convert the output to a NumPy array
        pil_image = Image.fromarray(image)

        text_to_add = prompt["text"]

        # Add text to image at a predefined position
        pil_image_with_text = add_text_to_image(
            pil_image, text_to_add, position=(50, pil_image.height - 100), font_size=28, font_color=(255, 255, 255)
        )

        # Save the image and store the path
        image_path = f'generated_image_with_text_{idx}.png'
        pil_image_with_text.save(image_path)
        
        generated_images.append({
            "text": prompt["text"],
            "image_path": image_path
        })
    
    return generated_images

# Full Story-to-Images generation pipeline
def story_creator_pipeline(story, auth_token=None):
    # Step 1: Enhance story using Ollama.
    enhanced_story, no_images = ollama_text_enhancement(story)
    
    # Step 2: Generate image prompts based on enhanced story.
    prompts = generate_prompts(enhanced_story, no_images)
    
    # Step 3: Generate images with text using the prompts.
    generated_images = generate_images_with_text(prompts, auth_token=auth_token)
    
    # Step 4: Return the final JSON format combining text and images.
    storybook = {
        "storytext": enhanced_story,
        "images": generated_images
    }
    return storybook

# Example Usage
if __name__ == "__main__":
    # Your story input
    story_input = "Once upon a time there lived a farmer in forest. he throwed his axe in river. An angel came with goled axe but he refused"

    # Insert your authentication token here for image generation.
    HF_AUTH_TOKEN = "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"

    # Run the story-to-images pipeline.
    result = story_creator_pipeline(story_input, auth_token=HF_AUTH_TOKEN)

    # Save or print the result.
    print(json.dumps(result, indent=4))
