import os
import json
from PIL import Image
import tarfile

# --- Configuration ---
images_folder = "/home/node/academic/lcm/flickr30k_images/images"
captions_file = "/home/node/academic/lcm/flickr30k_images/results.csv"
output_folder = "/home/node/academic/lcmlora/flickr8k_wds"
output_tar_file = "/home/node/academic/lcmlora/000000.tar"
keep_first_caption_only = True  # Set to False to keep all captions

# --- Helper Functions ---
def create_output_files(image_path, caption, new_file_name, output_folder):
    """Copies and renames image, creates caption and JSON files."""
    # Copy and rename image
    new_image_path = os.path.join(output_folder, f"{new_file_name}.jpg")
    with Image.open(image_path) as img:
        img.save(new_image_path, "JPEG")

    # Create caption file
    caption_path = os.path.join(output_folder, f"{new_file_name}.txt")
    with open(caption_path, "w") as caption_f:
        caption_f.write(caption)

    # Create JSON file with image resolution
    with Image.open(new_image_path) as img:
        width, height = img.size
    json_data = {"width": width, "height": height}
    json_path = os.path.join(output_folder, f"{new_file_name}.json")
    with open(json_path, "w") as json_f:
        json.dump(json_data, json_f)

# --- Main Processing ---

os.makedirs(output_folder, exist_ok=True)  # Ensure output folder exists

image_counter = 1
processed_images = set()

with open(captions_file, "r") as f:
    for line in f:
        parts = line.strip().split("|")

        # Ensure we have at least 2 parts (image name and caption)
        if len(parts) >= 2:
            image_name = parts[0]
            caption = parts[-1]  # Get the last part as the caption
        else:
            print(f"Skipping invalid line: {line}")  # Log invalid lines
            continue  # Move to the next line

        # Skip if keeping only the first caption and this image is processed
        if keep_first_caption_only and image_name in processed_images:
            continue
        
        # Construct image path
        image_path = os.path.join(images_folder, image_name)
        
        # Check if the image file exists
        if os.path.exists(image_path):
            # Create new file name
            new_file_name = f"{image_counter:09d}"

            # Create output files for the image with the caption
            create_output_files(image_path, caption.strip(), new_file_name, output_folder)

            # Update counter and processed images set
            image_counter += 1
            processed_images.add(image_name)

            if image_counter % 1000 == 0:
                print(f"Processed {image_counter} images...")

# --- Create Tar Archive ---
with tarfile.open(output_tar_file, "w") as tar:
    tar.add(output_folder, arcname=os.path.basename(output_folder))

print(f"Finished processing {image_counter - 1} images.")
