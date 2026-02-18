#include <opencv2/opencv.hpp>
#include <opencv2/dnn.hpp>
#include <iostream>
#include <vector>
#include <string>

// PEST CLASS NAMES
const std::vector<std::string> CLASS_NAMES = {
    "aphids",
    "armyworm",
    "beetle",
    "bollworm",
    "grasshopper",
    "mites",
    "mosquito",
    "sawfly",
    "stem_borer"
};

const int INPUT_WIDTH = 160;
const int INPUT_HEIGHT = 160;
const float CONFIDENCE_THRESHOLD = 0.5f;

int main(int argc, char** argv) {
    std::string modelPath = "best_pest_model_cpu.onnx";

    // LOAD MODEL
    std::cout << "Loading model: " << modelPath << "..." << std::endl;
    cv::dnn::Net net = cv::dnn::readNetFromONNX(modelPath);

    if (net.empty()) {
        std::cerr << "Error: Could not load model!" << std::endl;
        return -1;
    }

    // Set backend and target to CPU
    net.setPreferableBackend(cv::dnn::DNN_BACKEND_OPENCV);
    net.setPreferableTarget(cv::dnn::DNN_TARGET_CPU);

    // OPEN CAMERA
    cv::VideoCapture cap(0);
    if (!cap.isOpened()) {
        std::cerr << "Error: Could not open camera" << std::endl;
        return -1;
    }

    std::cout << "Starting live feed. Press 'q' to exit." << std::endl;

    cv::Mat frame;
    while (true) {
        cap >> frame;
        if (frame.empty()) {
            std::cerr << "Error: Blank frame grabbed" << std::endl;
            break;
        }

        // PREPROCESS IMAGE
        cv::Mat resized;
        cv::resize(frame, resized, cv::Size(INPUT_WIDTH, INPUT_HEIGHT));
        
        // Convert to RGB
        cv::Mat rgb;
        cv::cvtColor(resized, rgb, cv::COLOR_BGR2RGB); // OpenCV uses BGR, model needs RGB
        
        // Convert to Float and Normalize [0, 1]
        rgb.convertTo(rgb, CV_32F, 1.0 / 255.0);
        
        // Manual Normalization (Mean & Std)
        // Mean = [0.485, 0.456, 0.406]
        // Std = [0.229, 0.224, 0.225]
        cv::Vec3f mean(0.485f, 0.456f, 0.406f);
        cv::Vec3f std(0.229f, 0.224f, 0.225f);

        // Iterate and normalize
        // Note: Faster methods exist (split/subtract/divide/merge), but this is clear
        for (int y = 0; y < rgb.rows; y++) {
            for (int x = 0; x < rgb.cols; x++) {
                cv::Vec3f& pixel = rgb.at<cv::Vec3f>(y, x);
                pixel[0] = (pixel[0] - mean[0]) / std[0]; // R
                pixel[1] = (pixel[1] - mean[1]) / std[1]; // G
                pixel[2] = (pixel[2] - mean[2]) / std[2]; // B
            }
        }
        
        // Create 4D blob (1, C, H, W)
        // blobFromImage handles HWC -> NCHW conversion
        cv::Mat blob = cv::dnn::blobFromImage(rgb); 

        // INFERENCE
        net.setInput(blob);
        cv::Mat output = net.forward();

        // POST-PROCESSING
        double minVal, maxVal;
        cv::Point minLoc, maxLoc;
        cv::minMaxLoc(output, &minVal, &maxVal, &minLoc, &maxLoc);

        int classId = maxLoc.x;
        std::string className = CLASS_NAMES[classId];

        // Display result on the original frame
        std::string label = className + ": " + std::to_string(maxVal);
        cv::putText(frame, label, cv::Point(10, 30), cv::FONT_HERSHEY_SIMPLEX, 0.8, cv::Scalar(0, 255, 0), 2);
        
        cv::imshow("Pest Detection Live", frame);

        if (cv::waitKey(1) == 'q') {
            break;
        }
    }

    cap.release();
    cv::destroyAllWindows();

    return 0;
}
