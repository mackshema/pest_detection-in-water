<div align="center">

# Smart Water Tank Pest Detection System

<img src="https://img.shields.io/badge/Platform-ESP32--CAM-blue?style=for-the-badge&logo=espressif&logoColor=white"/>
<img src="https://img.shields.io/badge/AI-Computer%20Vision-blueviolet?style=for-the-badge&logo=opencv&logoColor=white"/>
<img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Status-Active-brightgreen?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Hardware-Embedded-orange?style=for-the-badge&logo=arduino&logoColor=white"/>

---

## AI Model Architecture

The detection system is built on a lightweight convolutional neural network optimized for embedded deployment. The model is trained to classify visual contamination patterns commonly found inside water tanks.

The architecture follows a compact CNN pipeline designed for efficient edge inference.

```
Input Image (160x160 RGB)
        │
        ▼
Convolution Layer
        │
        ▼
Batch Normalization
        │
        ▼
ReLU Activation
        │
        ▼
Max Pooling
        │
        ▼
Feature Extraction Layers
        │
        ▼
Global Average Pooling
        │
        ▼
Fully Connected Layer
        │
        ▼
Softmax Classification
```

The final output layer produces probability scores for each contamination class.

---

## Target Classes

The AI model is trained to detect multiple contamination types that may occur inside water tanks.

| Class | Description |
|------|-------------|
| Aphids | Small insect contamination |
| Armyworm | Worm-like biological presence |
| Beetle | Hard-shelled insect contamination |
| Bollworm | Larval stage pest |
| Grasshopper | Larger insect contamination |
| Mites | Microscopic pest clusters |
| Mosquito | Mosquito larvae and adults |
| Sawfly | Insect contamination |
| Stem Borer | Worm-like organisms |

Additional environmental objects such as frogs and floating debris are also included during testing for anomaly detection.

---

## Dataset Preparation

Training data was collected from open datasets and manually curated to represent contamination scenarios.

Dataset structure:

```
dataset/
│
├── train/
│   ├── aphids/
│   ├── armyworm/
│   ├── beetle/
│   ├── bollworm/
│   ├── grasshopper/
│   ├── mites/
│   ├── mosquito/
│   ├── sawfly/
│   └── stem_borer/
│
└── test/
```

Dataset preprocessing includes:

- Image resizing
- Normalization
- Data augmentation
- Class balancing

---

## Computer Vision Processing

Captured frames undergo several preprocessing steps before AI inference.

```
Raw Camera Frame
      │
      ▼
Image Resize (160x160)
      │
      ▼
Color Space Conversion (BGR → RGB)
      │
      ▼
Pixel Normalization
      │
      ▼
Tensor Conversion
      │
      ▼
Neural Network Input
```

Normalization parameters:

```
Mean = [0.485, 0.456, 0.406]
Std  = [0.229, 0.224, 0.225]
```

These values ensure consistency with training conditions.

---

## Edge AI Inference

The trained model is exported into **ONNX format** to enable efficient inference on edge hardware.

Inference workflow:

```
Camera Frame
      │
      ▼
Preprocessing
      │
      ▼
ONNX Runtime Inference
      │
      ▼
Softmax Probability Calculation
      │
      ▼
Confidence Threshold Filtering
      │
      ▼
Final Detection Output
```

The system uses a configurable confidence threshold to minimize false positives.

---

## Temporal Detection Filtering

To reduce incorrect predictions caused by noise or lighting variations, the system applies temporal validation.

```
Frame N Detection
      │
      ▼
Frame N+1 Detection
      │
      ▼
Frame N+2 Detection
      │
      ▼
Majority Decision
      │
      ▼
Confirmed Detection
```

This ensures that contaminants are detected consistently across multiple frames before triggering an alert.

---

## Model Optimization for Embedded Systems

Running AI models on embedded hardware requires optimization.

Techniques used:

- Model quantization
- Reduced input resolution
- Lightweight convolution layers
- ONNX model export
- Efficient memory allocation

These optimizations allow real-time inference on constrained devices.

---

## Detection Confidence Logic

Each prediction produces a probability score.

```
Prediction = Softmax(Output)

If Confidence > Threshold
    Detection Confirmed
Else
    Frame Ignored
```

Typical threshold values range from **0.30 to 0.60** depending on sensitivity requirements.

---

## AI Processing Workflow

The full AI workflow combines computer vision, machine learning inference, and embedded processing.

```
Camera Frame
      │
      ▼
Image Preprocessing
      │
      ▼
AI Model Inference
      │
      ▼
Confidence Filtering
      │
      ▼
Temporal Validation
      │
      ▼
Detection Result
      │
      ▼
Display Output
```

---

## Edge Deployment Strategy

The system follows an **Edge AI architecture**, where processing occurs locally rather than in the cloud.

Advantages:

- No internet dependency
- Reduced latency
- Increased privacy
- Lower operational cost
- Real-time decision making



<br/>

> **An AI-powered embedded vision system that detects biological contamination inside water tanks — keeping your water safe, automatically.**

<br/>


---

## Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [System Objectives](#system-objectives)
- [System Architecture](#system-architecture)
- [Detection Pipeline](#detection-pipeline)
- [Hardware Architecture](#hardware-architecture)
- [Hardware Components](#hardware-components)
- [PCB Design Considerations](#pcb-design-considerations)
- [Output Results](#output-results)
- [Software Workflow](#software-workflow)
- [Future Improvements](#future-improvements)
- [Applications](#applications)
- [Project Structure](#project-structure)
- [Contributors](#contributors)

---

## Overview

The **Smart Water Tank Pest Detection System** is a low-cost, AI-powered embedded device designed to visually inspect water tanks for biological contamination — without manual intervention.

Built around the **ESP32-CAM** module, the system captures real-time images of the tank interior, runs AI inference directly on the edge, and displays detection results on a compact LCD interface.

> No cloud required &nbsp;·&nbsp; Runs on embedded hardware &nbsp;·&nbsp; Real-time detection &nbsp;·&nbsp; Scalable architecture

---

## Problem Statement

Water tanks are rarely inspected internally, which can lead to contamination caused by insects, larvae, frogs, and suspended debris. Manual inspection is unsafe and inefficient because tanks are often sealed or located in inaccessible areas.

Current monitoring systems primarily measure water quality parameters but do not visually detect biological contamination.

This project addresses this gap by introducing an **AI-based vision system** capable of detecting pests and contaminants inside water tanks.

---

## System Objectives

| # | Objective |
|---|-----------|
| 1 | Detect biological contaminants using AI vision |
| 2 | Provide real-time monitoring of water tank conditions |
| 3 | Develop a compact embedded system using ESP32-CAM |
| 4 | Design a scalable hardware architecture for future sensor integration |
| 5 | Build a low-cost device suitable for residential and institutional use |

---

## System Architecture

```
┌─────────────────────────────────────┐
│             💧 Water Tank            │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│         ESP32-CAM Module            │
│   Camera + WiFi + Microcontroller   │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│         Image Preprocessing         │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│         AI Detection Model          │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│     Detection Result Processing     │
└──────────────────┬──────────────────┘
                   │
                   ▼
┌─────────────────────────────────────┐
│          LCD Display Output         │
└─────────────────────────────────────┘
```

---

## Detection Pipeline

```
  Camera Capture
       │
       ▼
  Frame Preprocessing
       │
       ▼
  Neural Network Inference
       │
       ▼
  Confidence Evaluation
       │
       ▼
  Temporal Validation
       │
       ▼
  Final Detection Result
```

---

## Hardware Architecture

```
  5V Power Adapter
       │
       ▼
  Power Stabilization Circuit
  (100uF + 0.1uF Capacitors)
       │
       ▼
  ESP32-CAM Controller
       │
       ▼
  I2C Interface
       │
       ▼
  16x2 LCD Display
```

---

## Hardware Components

| Component | Qty | Description |
|-----------|:---:|-------------|
| ESP32-CAM (AI Thinker) | 1 | Main microcontroller with OV2640 camera module |
| 16×2 LCD with I2C | 1 | Displays system status and detection output |
| 5V 2A Power Adapter | 1 | Primary power supply for the system |
| Terminal Block 2-Pin | 1 | Power input connector |
| 100µF Electrolytic Capacitor | 1 | Power rail stabilization |
| 0.1µF Ceramic Capacitor | 1 | High-frequency noise filtering |
| Push Buttons | 2 | Boot and reset control |
| Pin Headers | 1 | PCB connectivity interface |
| Wiring & Miscellaneous | — | Signal routing hardware |
| Custom PCB | 1 | Integrated hardware platform |
| Plastic Enclosure | 1 | Weatherproof system housing |
| Screws & Standoffs | — | Mechanical mounting hardware |

---

## PCB Design Considerations

The system uses a custom-designed PCB to ensure reliability and a compact form factor.

- Stable 5V power delivery
- Proper decoupling for ESP32-CAM
- Short analog signal traces
- Separation between power and signal routing
- Solid ground plane for noise reduction
- Adequate clearance around ESP32 WiFi antenna

---

## Output Results

Sample detection outputs from the deployed system:

| | | |
|:---:|:---:|:---:|
| ![Output A](A.jpeg) | ![Output B](B.jpeg) | ![Output C](C.jpeg) |
| Detection Sample 1 | Detection Sample 2 | Detection Sample 3 |
| ![Output D](D.jpeg) | ![Output E](WhatsApp_Image_2026-03-07_at_11.42.13_PM.jpeg) | ![Frog Detection](frog_image.png) |
| Detection Sample 4 | Live System Output | Frog Detection |

---

## Software Workflow

1. Capture image frames via ESP32-CAM
2. Preprocess frames for AI inference
3. Run detection model on edge hardware
4. Evaluate prediction confidence score
5. Determine contamination status
6. Display detection result on LCD

---

## Future Improvements

The system is engineered for extensibility. Planned enhancements include:

| Sensor | Purpose |
|--------|---------|
| pH Sensor | Chemical contamination detection |
| Turbidity Sensor | Suspended particle monitoring |
| Temperature Sensor | Environmental condition tracking |
| Ultrasonic Sensor | Water level measurement |
| IoT Dashboard | Remote cloud-based monitoring |

### Future System Architecture

```
┌──────────────────────────────┐
│     AI Vision Detection      │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│    Sensor Monitoring Layer   │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│   IoT Communication Layer    │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│   Remote Monitoring Dash     │
└──────────────────────────────┘
```

---

## Applications

- Household water tank monitoring
- Institutional water safety systems (schools, hospitals, offices)
- Smart building water management
- Public water infrastructure monitoring
- Environmental monitoring systems

---

## Project Structure

```
smart-water-ai/
│
├── ai_model/
│   ├── training/
│   ├── inference/
│   └── onnx_model/
│
├── firmware/
│   └── esp32_camera_code/
│
├── hardware/
│   ├── pcb_design/
│   └── schematics/
│
├── dataset/
│   ├── pest_images/
│   └── annotations/
│
└── docs/
    └── project_report/
```

---

## License

This project is released under the **MIT License** — free to use, modify, and distribute with attribution.

---

## Contributors

| Role | Contribution |
|------|-------------|
| Embedded Systems Engineer | Hardware design & firmware development |
| AI/ML Engineer | Model training, optimization & deployment |
| Hardware Architect | PCB design & system integration |

</div>
---

<div align="center">

## Vision

*"Develop an intelligent water monitoring platform that integrates artificial intelligence,*
*embedded hardware, and environmental sensing to ensure safe and reliable water storage systems."*

<br/>

<img src="https://img.shields.io/badge/Clean_Water-AI_Powered-00BFFF?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Edge_AI-ESP32--CAM-blueviolet?style=for-the-badge"/>

</div>
