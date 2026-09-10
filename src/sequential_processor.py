import os
import cv2
import numpy as np
from pathlib import Path
import time

class ImageProcessor:
    """
    Sequential image processor that applies 5 different filters to images.
    Filters: Grayscale, Gaussian Blur, Edge Detection, Sharpening, Brightness Adjustment
    """
    
    def __init__(self, input_dir, output_dir):
        """
        Initialize the processor with input and output directories.
        
        Args:
            input_dir: Path to folder containing images
            output_dir: Path to save processed images
        """
        self.input_dir = input_dir
        self.output_dir = output_dir
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Define output subdirectories for each filter
        self.filter_dirs = {
            'grayscale': os.path.join(output_dir, 'grayscale'),
            'blur': os.path.join(output_dir, 'blur'),
            'edges': os.path.join(output_dir, 'edges'),
            'sharpen': os.path.join(output_dir, 'sharpen'),
            'brightness': os.path.join(output_dir, 'brightness')
        }
        
        # Create subdirectories
        for dir_path in self.filter_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
    
    # ============ FILTER 1: GRAYSCALE CONVERSION ============
    def grayscale(self, image):
        """
        Convert RGB image to grayscale using luminance formula.
        Formula: Gray = 0.299*R + 0.587*G + 0.114*B
        
        Args:
            image: BGR image from OpenCV
            
        Returns:
            Grayscale image (single channel)
        """
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray
    
    # ============ FILTER 2: GAUSSIAN BLUR ============
    def gaussian_blur(self, image):
        """
        Apply Gaussian blur to smooth the image.
        Uses a 3x3 kernel to blur pixels.
        
        Args:
            image: Input image
            
        Returns:
            Blurred image
        """
        blurred = cv2.GaussianBlur(image, (5, 5), 1.0)
        return blurred
    
    # ============ FILTER 3: EDGE DETECTION (SOBEL) ============
    def edge_detection(self, image):
        """
        Detect edges using Sobel operator.
        Sobel computes gradients in X and Y directions.
        
        Args:
            image: Input image
            
        Returns:
            Edge-detected image (high values at edges)
        """
        # Convert to grayscale first if color image
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Sobel in X and Y directions
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        # Combine X and Y gradients
        edges = np.sqrt(sobelx**2 + sobely**2)
        
        # Normalize to 0-255 range
        edges = np.uint8(np.clip(edges, 0, 255))
        
        return edges
    
    # ============ FILTER 4: IMAGE SHARPENING ============
    def sharpen(self, image):
        """
        Enhance edges and details using a sharpening kernel.
        Uses unsharp masking technique.
        
        Args:
            image: Input image
            
        Returns:
            Sharpened image
        """
        # Create sharpening kernel
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]]) / 1.0
        
        # Apply kernel
        sharpened = cv2.filter2D(image, -1, kernel)
        
        return sharpened
    
    # ============ FILTER 5: BRIGHTNESS ADJUSTMENT ============
    def brightness_adjustment(self, image, factor=1.3):
        """
        Increase image brightness by multiplying pixel values.
        Factor > 1.0 increases brightness, < 1.0 decreases it.
        
        Args:
            image: Input image
            factor: Brightness factor (default 1.3 = 30% brighter)
            
        Returns:
            Brightened image
        """
        # Convert to float, apply brightness, clip to valid range
        brightened = np.uint8(np.clip(image * factor, 0, 255))
        return brightened
    
    # ============ MAIN PROCESSING FUNCTION ============
    def process_image(self, image_path):
        """
        Apply all 5 filters to a single image and save results.
        
        Args:
            image_path: Path to input image
            
        Returns:
            Dictionary with filter results and execution time
        """
        # Load image
        image = cv2.imread(image_path)
        if image is None:
            return None
        
        # Get image filename
        filename = os.path.basename(image_path)
        
        # Apply each filter and save
        results = {}
        
        # Filter 1: Grayscale
        gray_img = self.grayscale(image)
        cv2.imwrite(os.path.join(self.filter_dirs['grayscale'], filename), gray_img)
        results['grayscale'] = True
        
        # Filter 2: Blur
        blur_img = self.gaussian_blur(image)
        cv2.imwrite(os.path.join(self.filter_dirs['blur'], filename), blur_img)
        results['blur'] = True
        
        # Filter 3: Edge Detection
        edges_img = self.edge_detection(image)
        cv2.imwrite(os.path.join(self.filter_dirs['edges'], filename), edges_img)
        results['edges'] = True
        
        # Filter 4: Sharpening
        sharp_img = self.sharpen(image)
        cv2.imwrite(os.path.join(self.filter_dirs['sharpen'], filename), sharp_img)
        results['sharpen'] = True
        
        # Filter 5: Brightness
        bright_img = self.brightness_adjustment(image, factor=1.3)
        cv2.imwrite(os.path.join(self.filter_dirs['brightness'], filename), bright_img)
        results['brightness'] = True
        
        return results
    
    def process_all_images(self):
        """
        Process all images in input directory recursively.
        Handles nested folders (one per food category).
        
        Returns:
            Tuple of (total_images_processed, total_time_seconds)
        """
        start_time = time.time()
        total_images = 0
        
        # Walk through all subdirectories
        for category_name in os.listdir(self.input_dir):
            category_path = os.path.join(self.input_dir, category_name)
            
            # Skip if not a directory
            if not os.path.isdir(category_path):
                continue
            
            # Process each image in the category
            for image_file in os.listdir(category_path):
                if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(category_path, image_file)
                    
                    try:
                        result = self.process_image(image_path)
                        if result:
                            total_images += 1
                            if total_images % 10 == 0:
                                print(f"  Processed {total_images} images...")
                    except Exception as e:
                        print(f"  Error processing {image_file}: {e}")
        
        end_time = time.time()
        total_time = end_time - start_time
        
        return total_images, total_time


# ============ MAIN EXECUTION ============
if __name__ == "__main__":
    # Paths
    INPUT_DIR = "images"  # Your extracted subset
    OUTPUT_DIR = "results/sequential"  # Where to save results
    
    print("=" * 60)
    print("Sequential Image Processing Pipeline")
    print("=" * 60)
    print(f"Input directory: {INPUT_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print()
    
    # Create processor
    processor = ImageProcessor(INPUT_DIR, OUTPUT_DIR)
    
    # Process all images
    print("Processing images with 5 filters...")
    print()
    total_images, total_time = processor.process_all_images()
    
    print()
    print("=" * 60)
    print(f"✓ Processing Complete!")
    print(f"  Total images processed: {total_images}")
    print(f"  Total time: {total_time:.2f} seconds")
    print(f"  Average time per image: {total_time/total_images:.4f} seconds")
    print("=" * 60)
    print()
    print("Output structure:")
    print("  results/sequential/")
    print("    ├── grayscale/  (all images converted to grayscale)")
    print("    ├── blur/       (all images blurred)")
    print("    ├── edges/      (edge detection applied)")
    print("    ├── sharpen/    (sharpening applied)")
    print("    └── brightness/ (brightness increased)")