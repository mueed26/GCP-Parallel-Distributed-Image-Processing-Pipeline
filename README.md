# Parallel Image Processing System

## Overview
This project implements a parallel image processing system that applies 5 different filters to images from the Food-101 dataset using two Python parallel paradigms: multiprocessing and concurrent.futures.

## Filters Implemented
1. Grayscale Conversion
2. Gaussian Blur
3. Edge Detection (Sobel)
4. Image Sharpening
5. Brightness Adjustment

## Implementations
- **Sequential**: Baseline implementation (src/sequential_processor.py)
- **Multiprocessing**: Parallel version using multiprocessing (src/multiprocessing_processor.py)
- **Concurrent.futures**: Parallel version using concurrent.futures (src/concurrent_processor.py)

## Dataset
Food-101 dataset: 750 images from 75 different food categories

## Performance Results
See technical report for detailed speedup and efficiency analysis.

## Usage

### Sequential Version
```bash
python src/sequential_processor.py
```

### Multiprocessing Version
```bash
python src/multiprocessing_processor.py
```

### Concurrent.futures Version
```bash
python src/concurrent_processor.py
```

## Project Structure
```
cst435_assignment2/
├── src/
│   ├── extract_subset.py              # Food-101 dataset extraction
│   ├── sequential_processor.py         # Sequential implementation
│   ├── multiprocessing_processor.py    # Multiprocessing implementation
│   └── concurrent_processor.py         # Concurrent.futures implementation
├── images/                             # Extracted images (not in repo)
├── results/                            # Processed images (not in repo)
└── README.md
```

