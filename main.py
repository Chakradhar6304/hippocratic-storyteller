import os
import re
import base64
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ----------------------------------------
# Utilities
# ----------------------------------------

def clean_story_text(story):
    """Remove markdown (**text**) and remove 'Panel X:' lines."""
    
    # Remove markdown bold syntax **like this**
    story = re.sub(r"\*\*(.*?)\*\*", r"\1", story)

    # Remove “Panel 1:”, “Panel 2”, “Panel X”
    story = re.sub(r"Panel\s*\d+\:?", "", story, flags=re.IGNORECASE)

    # Remove extra blank lines left behind
    story = re.sub(r"\n\s*\n\s*\n+", "\n\n", story)

    return story.strip()


# ----------------------------------------
# Generate Story
# ----------------------------------------
def generate_story(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a comic-style children's storyteller. "
                    "Write in fun paragraphs but DO NOT use markdown like **bold**, "
                    "DO NOT label panels (no 'Panel 1:' etc). "
                    "Just write a smooth, clean story."
                )
            },
            {
                "role": "user",
                "content": f"Write a fun comic-style bedtime story for ages 5–10 based on: {prompt}. "
                           "Use 8–10 short paragraphs."
            }
        ],
        max_tokens=900
    )
    
    story_raw = response.choices[0].message.content
    return clean_story_text(story_raw)


# ----------------------------------------
# Generate Images (2 different prompts)
# ----------------------------------------
def generate_images(prompt):
    images = []

    # Page 1 image
    img1 = client.images.generate(
        model="gpt-image-1",
        prompt=f"comic book illustration, page 1 scene for: {prompt}",
        size="1024x1024"
    )

    # Page 2 image
    img2 = client.images.generate(
        model="gpt-image-1",
        prompt=f"comic book illustration, page 2 scene continuing: {prompt}",
        size="1024x1024"
    )

    # Helper to extract URLs or base64
    def extract(imgobj):
        output_list = []
        for x in imgobj.data:
            if getattr(x, "url", None):
                output_list.append(x.url)
            elif getattr(x, "b64_json", None):
                output_list.append("data:image/png;base64," + x.b64_json)
        return output_list

    images.extend(extract(img1))
    images.extend(extract(img2))

    # Guarantee at least 2 images
    if len(images) < 2:
        images.append(images[0])

    return images[:2]


# ----------------------------------------
# Judge Story
# ----------------------------------------
def judge_story(story):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a children's story safety judge. Be brief, positive, and clear."
            },
            {"role": "user", "content": story}
        ],
        max_tokens=300
    )
    
    return response.choices[0].message.content


# ----------------------------------------
# Final combined wrapper
# ----------------------------------------
def generate_final_story(prompt):

    story = generate_story(prompt)

    images = generate_images(prompt)

    judge = judge_story(story)

    return story, images, judge
