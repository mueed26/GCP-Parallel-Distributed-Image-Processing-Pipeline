import os
import cv2
import numpy as np
from multiprocessing import Pool, cpu_count
from pathlib import Path
import time

class ImageProcessor:
    """
    Multiprocessing image processor that applies 5 different filters to images in parallel.
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
        """Convert RGB image to grayscale using luminance formula."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return gray
    
    # ============ FILTER 2: GAUSSIAN BLUR ============
    def gaussian_blur(self, image):
        """Apply Gaussian blur to smooth the image."""
        blurred = cv2.GaussianBlur(image, (5, 5), 1.0)
        return blurred
    
    # ============ FILTER 3: EDGE DETECTION (SOBEL) ============
    def edge_detection(self, image):
        """Detect edges using Sobel operator."""
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
        
        edges = np.sqrt(sobelx**2 + sobely**2)
        edges = np.uint8(np.clip(edges, 0, 255))
        
        return edges
    
    # ============ FILTER 4: IMAGE SHARPENING ============
    def sharpen(self, image):
        """Enhance edges and details using a sharpening kernel."""
        kernel = np.array([[-1, -1, -1],
                          [-1,  9, -1],
                          [-1, -1, -1]]) / 1.0
        
        sharpened = cv2.filter2D(image, -1, kernel)
        return sharpened
    
    # ============ FILTER 5: BRIGHTNESS ADJUSTMENT ============
    def brightness_adjustment(self, image, factor=1.3):
        """Increase image brightness by multiplying pixel values."""
        brightened = np.uint8(np.clip(image * factor, 0, 255))
        return brightened
    
    # ============ MAIN PROCESSING FUNCTION ============
    def process_image(self, image_path):
        """
        Apply all 5 filters to a single image and save results.
        This function will be called by worker processes.
        
        Args:
            image_path: Path to input image
            
        Returns:
            Tuple of (success, image_filename)
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return (False, os.path.basename(image_path))
            
            # Get image filename
            filename = os.path.basename(image_path)
            
            # Apply each filter and save
            # Filter 1: Grayscale
            gray_img = self.grayscale(image)
            cv2.imwrite(os.path.join(self.filter_dirs['grayscale'], filename), gray_img)
            
            # Filter 2: Blur
            blur_img = self.gaussian_blur(image)
            cv2.imwrite(os.path.join(self.filter_dirs['blur'], filename), blur_img)
            
            # Filter 3: Edge Detection
            edges_img = self.edge_detection(image)
            cv2.imwrite(os.path.join(self.filter_dirs['edges'], filename), edges_img)
            
            # Filter 4: Sharpening
            sharp_img = self.sharpen(image)
            cv2.imwrite(os.path.join(self.filter_dirs['sharpen'], filename), sharp_img)
            
            # Filter 5: Brightness
            bright_img = self.brightness_adjustment(image, factor=1.3)
            cv2.imwrite(os.path.join(self.filter_dirs['brightness'], filename), bright_img)
            
            return (True, filename)
        
        except Exception as e:
            return (False, f"{os.path.basename(image_path)}: {str(e)}")
    
    def collect_image_paths(self):
        """
        Collect all image paths from input directory.
        Returns a list of full paths to all images.
        """
        image_paths = []
        
        # Walk through all subdirectories
        for category_name in os.listdir(self.input_dir):
            category_path = os.path.join(self.input_dir, category_name)
            
            # Skip if not a directory
            if not os.path.isdir(category_path):
                continue
            
            # Collect each image in the category
            for image_file in os.listdir(category_path):
                if image_file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(category_path, image_file)
                    image_paths.append(image_path)
        
        return image_paths
    
    def process_all_images_parallel(self, num_processes=None):
        """
        Process all images in parallel using multiprocessing.
        
        Args:
            num_processes: Number of processes to use.
                          If None, uses CPU count.
                          
        Returns:
            Tuple of (total_images_processed, total_time_seconds, num_processes_used)
        """
        # Determine number of processes
        if num_processes is None:
            num_processes = cpu_count()
        
        # Collect all image paths
        image_paths = self.collect_image_paths()
        total_images = len(image_paths)
        
        start_time = time.time()
        
        # Create process pool and map process_image function to all images
        # chunksize: distribute images to processes in batches for better load balancing
        with Pool(processes=num_processes) as pool:
            results = pool.map(self.process_image, image_paths, chunksize=5)
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Count successful processes
        successful = sum(1 for success, _ in results if success)
        
        return successful, total_time, num_processes


# ============ MAIN EXECUTION ============
if __name__ == "__main__":
    INPUT_DIR = "images"
    OUTPUT_DIR_BASE = "results/multiprocessing"
    
    print("=" * 70)
    print("Multiprocessing Image Processing Pipeline")
    print("=" * 70)
    print(f"Input directory: {INPUT_DIR}")
    print()
    
    # Create processor
    processor = ImageProcessor(INPUT_DIR, OUTPUT_DIR_BASE)
    
    # Test with different process counts 
    process_counts = [2, 4, 8]
    
    print(f"System CPU count: {cpu_count()}")
    print()
    print("Testing different process counts...\n")
    
    results = {}
    
    for num_procs in process_counts:
        output_dir = os.path.join(OUTPUT_DIR_BASE, f"processes_{num_procs}")
        processor.output_dir = output_dir
        processor.filter_dirs = {
            'grayscale': os.path.join(output_dir, 'grayscale'),
            'blur': os.path.join(output_dir, 'blur'),
            'edges': os.path.join(output_dir, 'edges'),
            'sharpen': os.path.join(output_dir, 'sharpen'),
            'brightness': os.path.join(output_dir, 'brightness')
        }
        for dir_path in processor.filter_dirs.values():
            os.makedirs(dir_path, exist_ok=True)
        
        print(f"Running with {num_procs} processes...")
        total_images, total_time, used_procs = processor.process_all_images_parallel(num_procs)
        results[num_procs] = (total_images, total_time)
        
        print(f"  ✓ Processed {total_images} images in {total_time:.2f} seconds")
        print(f"  ✓ Average time per image: {total_time/total_images:.4f} seconds")
        print()
    
    # Print summary and calculate speedup
    print("=" * 70)
    print("SUMMARY - Multiprocessing Results")
    print("=" * 70)
    
    # Sequential baseline (you can hardcode this or compare with previous run)
    sequential_time = 7.97  # From your previous sequential run
    
    print(f"Sequential Baseline: {sequential_time:.2f} seconds\n")
    print(f"{'Processes':<15} {'Time (s)':<15} {'Speedup':<15} {'Efficiency':<15}")
    print("-" * 60)
    
    for num_procs in process_counts:
        images, parallel_time = results[num_procs]
        speedup = sequential_time / parallel_time
        efficiency = (speedup / num_procs) * 100
        
        print(f"{num_procs:<15} {parallel_time:<15.2f} {speedup:<15.2f}x {efficiency:<15.1f}%")
    
    print("=" * 70)
    print("\nOutput structure:")
    print("  results/multiprocessing/")
    print("    ├── processes_2/")
    print("    │   ├── grayscale/")
    print("    │   ├── blur/")
    print("    │   ├── edges/")
    print("    │   ├── sharpen/")
    print("    │   └── brightness/")
    print("    ├── processes_4/")
    print("    │   └── (same structure)")
    print("    └── processes_8/")
    print("        └── (same structure)")