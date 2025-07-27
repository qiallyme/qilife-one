import os
import openai
import cloudinary
import cloudinary.uploader
import pandas as pd
import requests
from time import sleep
from pathlib import Path
from dotenv import load_dotenv

# --- Load Environment Variables ---
dotenv_path = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=dotenv_path)

openai_api_key = os.getenv("OPENAI_API_KEY")
cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
cloud_api_key = os.getenv("CLOUDINARY_API_KEY")
cloud_api_secret = os.getenv("CLOUDINARY_API_SECRET")

if not openai_api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in environment variables.")

if not cloud_name:
    raise ValueError("❌ CLOUDINARY_CLOUD_NAME not found in environment variables.")

client = openai.OpenAI(api_key=openai_api_key)

cloudinary.config(
    cloud_name=cloud_name,
    api_key=cloud_api_key,
    api_secret=cloud_api_secret,
    secure=True
)

print("☁️ Cloudinary Name:", cloud_name)

# --- Paths ---
csv_path = "src/tools/others/services_with_prompts.csv"
output_csv = "services_with_images.csv"
image_folder = Path("generated_images")
image_folder.mkdir(exist_ok=True)

try:
    df = pd.read_csv(csv_path)
except FileNotFoundError:
    print(f"❌ CSV file not found at path: {csv_path}")
    exit()

if "serviceSlug" in df.columns:
    df["serviceSlug"] = df["serviceSlug"].fillna("").astype(str).str.strip()
else:
    df["serviceSlug"] = ""

# --- Generate Slug using GPT ---
def generate_slug(service_name):
    prompt = f"Create a short, lowercase, hyphen-separated slug for this service name: '{service_name}'. Only return the slug. No punctuation, no quotes."
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You generate clean slugs from service names."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=20,
            temperature=0.3
        )
        content = response.choices[0].message.content
        if content:
            slug = content.strip().replace(" ", "-").replace("--", "-").lower()
            slug = ''.join(c for c in slug if c.isalnum() or c == "-")
            return slug
        else:
            print(f"❌ GPT did not return a slug for '{service_name}'")
            return f"service-{hash(service_name) & 0xfffffff}"
    except Exception as e:
        print(f"❌ GPT slug error for '{service_name}': {e}")
        return f"service-{hash(service_name) & 0xfffffff}"

# --- Generate DALL·E Image ---
def generate_image(prompt, filename):
    try:
        print(f"🎨 Generating image: {filename}")
        response = client.images.generate(
            model="dall-e-3",
            prompt=prompt,
            size="1024x1024",
            quality="standard",
            n=1
        )
        if not response or not getattr(response, "data", None):
            print(f"❌ No image data returned for prompt: {prompt}")
            return None
        image_url = response.data[0].url if response.data and len(response.data) > 0 else None
        if not image_url:
            print(f"❌ Image URL is None for prompt: {prompt}")
            return None
        image_data = requests.get(image_url).content
        filepath = image_folder / filename
        with open(filepath, "wb") as f:
            f.write(image_data)
        return filepath
    except Exception as e:
        print(f"❌ Image generation failed: {e}")
        return None

# --- Upload to Cloudinary ---
def upload_to_cloudinary(filepath, public_id):
    try:
        print(f"☁️ Uploading {filepath.name} to Cloudinary...")
        upload_result = cloudinary.uploader.upload(
            str(filepath),
            public_id=f"service-icons/{public_id}",
            overwrite=True,
            resource_type="image"
        )
        return upload_result["secure_url"]
    except Exception as e:
        print(f"❌ Cloudinary upload failed: {e}")
        return None

# --- Main Logic ---
df["imageUrl"] = ""
existing_slugs = set()

for index, row in df.iterrows():
    service_name = row["serviceName"]
    image_prompt = row["imagePrompt"]
    slug = row.get("serviceSlug")
    if pd.isna(slug) or not isinstance(slug, str) or not slug.strip():
        slug = generate_slug(service_name)

    original_slug = slug
    count = 1
    while slug in existing_slugs:
        slug = f"{original_slug}-{count}"
        count += 1
    existing_slugs.add(slug)

    filename = f"{slug}.png"
    image_path = generate_image(image_prompt, filename)
    if not image_path:
        continue

    image_url = upload_to_cloudinary(image_path, slug)
    if not image_url:
        continue

    df.at[index, "serviceSlug"] = slug
    df.at[index, "imageUrl"] = image_url
    print(f"✅ {service_name} → {slug} → {image_url}")
    sleep(1)

# --- Save Output ---
df.to_csv(output_csv, index=False)
print(f"\n📦 All done! Updated catalog saved to: {output_csv}")