# SlowCraft: RIFE-Powered Slow Motion Video Generator 🎥✨

![SlowCraft Logo](https://img.shields.io/badge/SlowCraft-RIFE--Powered-blue?style=flat&logo=python)

[![Download Latest Release](https://img.shields.io/badge/Download%20Latest%20Release-v1.0.0-orange?style=flat&logo=github)](https://github.com/G11br/SlowCraft/releases)

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)
- [Acknowledgments](#acknowledgments)

---

## Overview

SlowCraft is a desktop application designed to enhance your video editing experience by generating stunning slow-motion effects. It leverages the power of RIFE (Real-Time Intermediate Flow Estimation) to interpolate frames and create smooth slow-motion videos. Built using Python and Tkinter, this open-source tool provides an intuitive interface for users to easily process their videos.

## Features

- **Frame Interpolation**: Utilizes RIFE technology to create additional frames for smoother slow-motion playback.
- **User-Friendly Interface**: Built with Tkinter, the application is easy to navigate, making it accessible for users of all skill levels.
- **Video Processing**: Supports various video formats and resolutions, allowing for versatile video enhancement.
- **Open Source**: The code is available for anyone to view, modify, and contribute to.
- **Cross-Platform**: Works on Windows, macOS, and Linux, ensuring a wide reach.

## Technologies Used

- **Python**: The core programming language for the application.
- **Tkinter**: Used for creating the graphical user interface.
- **FFmpeg**: A powerful multimedia framework to handle video processing.
- **RIFE**: The real-time frame interpolation engine that powers the slow-motion effect.
- **ncnn**: A high-performance neural network inference framework.
- **Vulkan**: A modern graphics API that enhances performance.

## Installation

To get started with SlowCraft, follow these steps:

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/G11br/SlowCraft.git
   cd SlowCraft
   ```

2. **Install Dependencies**:
   Ensure you have Python 3.7 or higher installed. Then, install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

3. **Download the Latest Release**:
   Visit the [Releases](https://github.com/G11br/SlowCraft/releases) section to download the latest version of SlowCraft. You will need to download the executable file and run it.

4. **Run the Application**:
   Launch the application using:
   ```bash
   python main.py
   ```

## Usage

Using SlowCraft is straightforward:

1. **Open the Application**: Launch SlowCraft to access the main interface.
2. **Import Video**: Click on the "Import" button to select the video you want to enhance.
3. **Select Slow-Motion Settings**: Choose the desired slow-motion effect and frame rate.
4. **Process Video**: Click on the "Process" button to start generating the slow-motion video.
5. **Export Video**: Once processing is complete, export the video to your desired location.

For detailed instructions and tips, refer to the documentation included in the repository.

## Contributing

Contributions are welcome! If you have suggestions for improvements or features, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push your branch to your forked repository.
5. Submit a pull request.

Please ensure your code adheres to the existing style and includes relevant tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgments

- **RIFE Team**: For developing the RIFE technology that powers our frame interpolation.
- **FFmpeg Team**: For providing a robust multimedia framework.
- **Tkinter Documentation**: For offering great resources on building GUIs with Python.
- **Community Contributors**: For your feedback and support in making SlowCraft better.

---

For the latest updates, visit the [Releases](https://github.com/G11br/SlowCraft/releases) section.