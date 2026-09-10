import os
import cv2
import numpy as np
import time
from concurrent.futures import ThreadPoolExecutor
from multiprocessing import cpu_count

# ============ FILTER FUNCTIONS ============

def grayscale(image):
    return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

def gaussian_blur(image):
    return cv2.GaussianBlur(image, (5, 5), 1.0)

def edge_detection(image):
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image

    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)
    edges = np.sqrt(sobelx**2 + sobely**2)
    return np.uint8(np.clip(edges, 0, 255))

def sharpen(image):
    kernel = np.array([[-1, -1, -1],
                       [-1,  9, -1],
                       [-1, -1, -1]])
    return cv2.filter2D(image, -1, kernel)

def brightness_adjustment(image, factor=1.3):
    return np.uint8(np.clip(image * factor, 0, 255))


# ============ IMAGE PROCESSING TASK ============

def process_image_task(args):
    image_path, output_dirs = args

    image = cv2.imread(image_path)
    if image is None:
        return False

    filename = os.path.basename(image_path)

    cv2.imwrite(os.path.join(output_dirs['grayscale'], filename), grayscale(image))
    cv2.imwrite(os.path.join(output_dirs['blur'], filename), gaussian_blur(image))
    cv2.imwrite(os.path.join(output_dirs['edges'], filename), edge_detection(image))
    cv2.imwrite(os.path.join(output_dirs['sharpen'], filename), sharpen(image))
    cv2.imwrite(os.path.join(output_dirs['brightness'], filename), brightness_adjustment(image))

    return True


# ============ HELPER FUNCTIONS ============

def collect_image_paths(input_dir):
    paths = []
    for category in os.listdir(input_dir):
        category_path = os.path.join(input_dir, category)
        if not os.path.isdir(category_path):
            continue
        for img in os.listdir(category_path):
            if img.lower().endswith(('.jpg', '.jpeg', '.png')):
                paths.append(os.path.join(category_path, img))
    return paths


def create_output_dirs(base_dir):
    dirs = {
        'grayscale': os.path.join(base_dir, 'grayscale'),
        'blur': os.path.join(base_dir, 'blur'),
        'edges': os.path.join(base_dir, 'edges'),
        'sharpen': os.path.join(base_dir, 'sharpen'),
        'brightness': os.path.join(base_dir, 'brightness')
    }
    for d in dirs.values():
        os.makedirs(d, exist_ok=True)
    return dirs


# ============ MAIN EXECUTION ============

if __name__ == "__main__":

    INPUT_DIR = "images"
    OUTPUT_BASE = "results/thread_pool"
    THREAD_COUNTS = [2, 4, 8]

    print("=" * 70)
    print("Thread Pool Image Processing Pipeline")
    print("=" * 70)
    print(f"CPU count: {cpu_count()}")
    print()

    image_paths = collect_image_paths(INPUT_DIR)
    print(f"Total images found: {len(image_paths)}\n")

    results = {}

    for threads in THREAD_COUNTS:
        print(f"Running with {threads} threads...")

        output_dir = os.path.join(OUTPUT_BASE, f"threads_{threads}")
        output_dirs = create_output_dirs(output_dir)

        start = time.time()

        with ThreadPoolExecutor(max_workers=threads) as executor:
            tasks = [(path, output_dirs) for path in image_paths]
            completed = list(executor.map(process_image_task, tasks))

        end = time.time()

        success_count = sum(completed)
        total_time = end - start
        results[threads] = total_time

        print(f"  ✓ Processed {success_count} images")
        print(f"  ✓ Time: {total_time:.2f} seconds\n")

    # ============ PERFORMANCE SUMMARY ============
    print("=" * 70)
    print("SUMMARY – Thread Pool Results")
    print("=" * 70)

    sequential_time = 8.14  # your measured sequential time

    print(f"Sequential Baseline: {sequential_time:.2f} seconds\n")
    print(f"{'Threads':<15}{'Time (s)':<15}{'Speedup':<15}{'Efficiency':<15}")
    print("-" * 60)

    for threads, parallel_time in results.items():
        speedup = sequential_time / parallel_time
        efficiency = (speedup / threads) * 100
        print(f"{threads:<15}{parallel_time:<15.2f}{speedup:<15.2f}x{efficiency:<15.1f}%")

    print("=" * 70)
