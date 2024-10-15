from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import ollama
from diffusers import StableDiffusionPipeline
import torch
from torch import autocast
from PIL import Image, ImageDraw, ImageFont
import json
import textwrap
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os


app = FastAPI()

# Add CORS middleware to allow frontend requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for testing purposes (adjust in production)
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods (GET, POST, OPTIONS, etc.)
    allow_headers=["*"],  # Allow all headers (Content-Type, Authorization, etc.)
)

# Serve static files (for generated images)
app.mount("/static", StaticFiles(directory="generated_storybook"), name="static")

# Ensure the generated storybook directory exists
if not os.path.exists("generated_storybook"):
    os.makedirs("generated_storybook")

# Initialize Ollama client
client = ollama.Client()

# Replace with your Hugging Face authentication token
HF_AUTH_TOKEN = "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"  # Update this with your Hugging Face token

# Load the Stable Diffusion Pipeline
device = "cuda" if torch.cuda.is_available() else "cpu"
model_id = "CompVis/stable-diffusion-v1-4"

# Initialize the pipeline with the correct parameters
pipe = StableDiffusionPipeline.from_pretrained(
    model_id,
    revision="fp16",
    torch_dtype=torch.float16 if device == "cuda" else torch.float32,
    use_auth_token=HF_AUTH_TOKEN
)
pipe.to(device)


class StoryPrompt(BaseModel):
    """Input schema for text prompt"""
    story: str


@app.post("/generate_storybook")
async def generate_storybook(prompt: StoryPrompt):
    """
    Enhances the given story using `ollama`, generates cartoon-style images with text, and returns a storybook.
    """
    try:
        # Step 1: Enhance the story
        response = client.chat(
            model='llama2',
            messages=[{'role': 'user', 'content': f"Enhance the following story to be more vivid, descriptive, and engaging:\n\n{prompt.story}"}]
        )
        story = response['message']['content']

        # Step 2: Format the enhanced story as structured JSON
        enhanced_story = get_enhanced_story(story)

        # Step 3: Generate the cartoon-style images with text based on the enhanced story
        generated_images = generate_images_with_text(enhanced_story)

        # Step 4: Construct the final storybook response
        storybook = {
            "original_story": prompt.story,
            "enhanced_story": enhanced_story,
            "images": generated_images
        }

        return storybook

    except Exception as e:
        # Print the detailed exception for debugging
        print(f"Error generating storybook: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


def get_enhanced_story(prompt_text):
    """
    Enhance the input story text and structure it as JSON.
    """
    try:
        request_content = (
            f"Create a structured JSON output for a storybook. Split the story into appropriate sections and create image prompts for each. "
            f"The JSON should follow this structure: [{{'section_number': 1, 'text': 'Story text for this section', 'prompt': 'Image generation prompt based on the text'}}]. "
            f"Here is the story: {prompt_text}"
        )

        # Request enhancement from Llama2
        response = client.chat(
            model='llama2',
            messages=[{'role': 'user', 'content': request_content}]
        )

        # Extract and parse the JSON correctly
        content = response['message']['content']
        start_idx = content.find("[")
        end_idx = content.rfind("]") + 1
        json_content = content[start_idx:end_idx].replace('\n', ' ').replace('\r', '')

        # Parse the JSON
        return json.loads(json_content)

    except json.JSONDecodeError as json_err:
        raise Exception(f"Failed to decode JSON: {json_err}")
    except Exception as e:
        raise Exception(f"Error during text enhancement: {e}")


def generate_images_with_text(enhanced_story):
    """
    Generate cartoon-style images with text using the prompts and properties from the enhanced story.
    """
    generated_images = []
    for idx, message in enumerate(enhanced_story):
        prompt_text = message["text"]
        image_prompt = message.get("prompt", prompt_text)

        # Modify the prompt for a cartoon style
        cartoon_prompt = f"{image_prompt}, cartoon style, vibrant colors, whimsical details"

        # Use the Stable Diffusion pipeline to generate the image
        with autocast(device):
            image = pipe(cartoon_prompt, guidance_scale=8.5).images[0]

        # Format text to be placed below the image
        wrapped_text = format_text_for_image(prompt_text, width=60)

        # Combine the image with formatted text
        final_image = combine_image_with_text(image, wrapped_text, image_width=image.width)

        # Save the image and store the path
        image_path = f"generated_storybook/generated_storybook_page_{idx}.png"
        final_image.save(image_path)

        # Add generated image details to the list
        generated_images.append({
            "section_number": message["section_number"],
            "text": prompt_text,
            "image_prompt": image_prompt,
            "image_path": f"/static/generated_storybook_page_{idx}.png"
        })

    return generated_images


def format_text_for_image(text, width=60):
    """Wrap the text into a specified width for better layout in images."""
    return "\n".join(textwrap.wrap(text, width=width))


def combine_image_with_text(image, text, image_width, padding=20, font_size=24):
    """
    Combine the given image with text below, formatted as a storybook page.
    """
    text_height = (text.count("\n") + 1) * font_size + 2 * padding
    total_height = image.height + text_height
    combined_image = Image.new("RGB", (image_width, total_height), color=(255, 255, 255))

    # Paste the generated image on the canvas
    combined_image.paste(image, (0, 0))

    # Draw text below the image
    draw = ImageDraw.Draw(combined_image)
    font = ImageFont.truetype("arial.ttf", font_size)
    draw.text((padding, image.height + padding), text, font=font, fill=(0, 0, 0))

    return combined_image


# Run the FastAPI application using Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
