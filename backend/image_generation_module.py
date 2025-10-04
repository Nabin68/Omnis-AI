import asyncio
from random import randint
from PIL import Image
import requests
from dotenv import load_dotenv
import os
from time import sleep
from io import BytesIO

class ImageGenerationModule:
    def __init__(self):
        """Initialize the Image Generation Module"""
        # Load environment variables
        load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))
        
        # Set API URL and headers
        self.MODEL_ID = "black-forest-labs/FLUX.1-dev"
        self.API_URL = f"https://api-inference.huggingface.co/models/{self.MODEL_ID}"
        self.headers = {"Authorization": f"Bearer {os.getenv('HUGGINGFACE_API_KEY')}"}
        
        # Define the path for saving images
        self.GENERATED_IMAGES_PATH = os.path.join(os.path.dirname(__file__), '..', 'Data', 'GeneratedImage')
        
        # Ensure the GeneratedImage folder exists
        if not os.path.exists(self.GENERATED_IMAGES_PATH):
            os.makedirs(self.GENERATED_IMAGES_PATH)
    
    def open_images(self, prompt):
        """Open all generated images for the given prompt"""
        prompt = prompt.replace(" ", "_")
        files = [f"{prompt}{i}.jpg" for i in range(1, 3)]

        for jpg_file in files:
            image_path = os.path.join(self.GENERATED_IMAGES_PATH, jpg_file)

            try:
                img = Image.open(image_path)
                print(f"Opening image: {image_path}")
                img.show()
                sleep(1)

            except IOError:
                print(f"Unable to open {image_path}. Ensure the image file exists and is valid.")

    async def query(self, payload):
        """Query the Hugging Face API"""
        try:
            response = await asyncio.to_thread(requests.post, self.API_URL, headers=self.headers, json=payload)
            response.raise_for_status()  # Raise an error for HTTP failures
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"Error querying API: {e}")
            return None

    async def generate_images_async(self, prompt: str):
        """Generate 4 images asynchronously"""
        tasks = []
        for i in range(2):
            seed = randint(0, 1000000)
            payload = {
                "inputs": f"{prompt}, quality=4k, sharpness=maximum, Ultra High details, high resolution, seed={seed}"
            }
            task = asyncio.create_task(self.query(payload))
            tasks.append(task)

        responses = await asyncio.gather(*tasks)

        for i, response_content in enumerate(responses):
            if response_content:
                try:
                    # The API returns raw image bytes (PNG format)
                    # Convert to JPG using PIL
                    
                    # Open the PNG image from bytes
                    img = Image.open(BytesIO(response_content))
                    
                    # Convert RGBA to RGB if necessary (JPG doesn't support transparency)
                    if img.mode == 'RGBA':
                        img = img.convert('RGB')
                    
                    # Save as JPG
                    file_path = os.path.join(self.GENERATED_IMAGES_PATH, f"{prompt.replace(' ', '_')}{i + 1}.jpg")
                    img.save(file_path, 'JPEG', quality=95)
                    print(f"✅ Image {i + 1} saved as {file_path}")
                    
                except Exception as e:
                    print(f"❌ Error saving image {i + 1}: {e}")

    def generate(self, prompt: str, open_after_generation: bool = True):
        """
        Main function to generate images
        
        Args:
            prompt (str): The text prompt for image generation
            open_after_generation (bool): Whether to open images after generation (default: True)
        """
        print(f"Generating images for prompt: '{prompt}'")
        asyncio.run(self.generate_images_async(prompt))
        
        if open_after_generation:
            self.open_images(prompt)
        
        print("✅ Image generation complete!")


# Example usage
if __name__ == "__main__":
    # Create an instance of the module
    image_gen = ImageGenerationModule()
    
    # Generate images with a prompt
    image_gen.generate("Iron Man,thor and spider man flying in sky while fighting with alliens")
    
    # Or generate without opening images automatically
    # image_gen.generate("a beautiful sunset over mountains", open_after_generation=False)