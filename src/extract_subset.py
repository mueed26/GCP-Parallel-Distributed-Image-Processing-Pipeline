import os
import shutil
import random
import json

# Define your paths - CHANGE THESE TO MATCH YOUR SETUP
FOOD_101_PATH = "/Users/anishaaggarwal/Desktop/Y4, Sem 1/CST435/Assignment 2/food-101" 
SUBSET_OUTPUT_PATH = "images"  

# Number of categories to select
NUM_CATEGORIES = 75 
# Number of images per category (1-2)
MIN_IMAGES_PER_CATEGORY = 10
MAX_IMAGES_PER_CATEGORY = 10

# STEP 1.5: Get all food categories and randomly select some
def select_random_categories():
    """
    Gets all 101 food categories from Food-101 and randomly selects NUM_CATEGORIES of them.
    Returns a list of selected category names.
    """
    # Get the path to the images folder
    images_path = os.path.join(FOOD_101_PATH, "images")
    
   # Get all folder names (these are the 101 food categories)
   # Filter out files like .DS_Store - only keep actual folders
    all_categories = [f for f in os.listdir(images_path) if os.path.isdir(os.path.join(images_path, f))]
    
    # Randomly select NUM_CATEGORIES from the list
    selected_categories = random.sample(all_categories, NUM_CATEGORIES)
    
    print(f"✓ Selected {len(selected_categories)} categories from {len(all_categories)} total")
    print(f"Sample categories: {selected_categories[:5]}")  # Show first 5 as preview
    
    return selected_categories

# STEP 2: Randomly select categories and create their folder structure
def create_subset_structure(categories_list):
    """
    Creates the folder structure for all selected categories.
    For each category, creates: images/category_name/
    """
    # Create the main subset folder if it doesn't exist
    if not os.path.exists(SUBSET_OUTPUT_PATH):
        os.makedirs(SUBSET_OUTPUT_PATH)
        print(f"✓ Created main subset folder: {SUBSET_OUTPUT_PATH}")
    
    # Create a subfolder for each selected category
    for category in categories_list:
        category_folder = os.path.join(SUBSET_OUTPUT_PATH, category)
        if not os.path.exists(category_folder):
            os.makedirs(category_folder)
    
    print(f"✓ Created {len(categories_list)} category subfolders")
    return categories_list

# STEP 3A: Select random images from a category
def select_images_from_category(category_path, min_images=1, max_images=2):
    """
    Randomly selects 10 images from a food category folder.
    
    Args:
        category_path: Full path to the category folder (e.g., food-101/images/apple_pie)
        min_images: Minimum number of images to select (default 1)
        max_images: Maximum number of images to select (default 2)
    
    Returns:
        List of selected image filenames
    """
    # Get all files in the category folder
    all_files = os.listdir(category_path)
    
    # Filter to only image files (jpg, jpeg, png)
    image_extensions = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    image_files = [f for f in all_files if f.lower().endswith(image_extensions)]
    
    # Randomly decide: pick 1 or 2 images
    num_to_select = random.randint(min_images, max_images)
    
    # Make sure we don't try to select more images than exist
    num_to_select = min(num_to_select, len(image_files))
    
    # Randomly select that many images
    selected_images = random.sample(image_files, num_to_select)
    
    return selected_images

# STEP 3B: Copy selected images to the subset folder
def copy_images_to_subset(food_101_path, subset_path, selected_categories):
    """
    For each selected category, picks 1-2 random images and copies them to the subset folder.
    
    Args:
        food_101_path: Full path to Food-101 dataset
        subset_path: Full path to where you want the subset stored
        selected_categories: List of category names to process
    """
    total_images_copied = 0
    
    # Loop through each selected category
    for category in selected_categories:
        # Build the source path (where images are in Food-101)
        source_category_path = os.path.join(food_101_path, "images", category)
        
        # Build the destination path (where we're copying to)
        dest_category_path = os.path.join(subset_path, category)
        
        # Select 1-2 random images from this category
        selected_images = select_images_from_category(
            source_category_path, 
            MIN_IMAGES_PER_CATEGORY, 
            MAX_IMAGES_PER_CATEGORY
        )
        
        # Copy each selected image
        for image in selected_images:
            source_image = os.path.join(source_category_path, image)
            dest_image = os.path.join(dest_category_path, image)
            
            try:
                shutil.copy(source_image, dest_image)
                total_images_copied += 1
            except Exception as e:
                print(f"✗ Failed to copy {image} from {category}: {e}")
        
        print(f"✓ Copied {len(selected_images)} images from {category}")
    
    print(f"\n✓ DONE! Total images copied: {total_images_copied}")

# Execute all steps
print("=" * 50)
print("Starting Food-101 Subset Extraction")
print("=" * 50)

selected_categories = select_random_categories()
create_subset_structure(selected_categories)
copy_images_to_subset(FOOD_101_PATH, SUBSET_OUTPUT_PATH, selected_categories)

print("=" * 50)
print("Extraction Complete!")
print("=" * 50)