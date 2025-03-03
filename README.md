# Vidar Downloader

**Vidar Downloader** is a minimalistic yet powerful GUI video downloader built with [yt-dlp](https://github.com/yt-dlp/yt-dlp), [CustomTkinter](https://github.com/TomSchimansky/CustomTkinter), and optional [aria2c](https://github.com/aria2/aria2) integration. If you think waiting for videos to download is as fun as watching paint dry, let Vidar do the heavy lifting for you! This project is SEO friendly, optimized with clear headings and keywords for video downloading, GUI, yt-dlp, aria2c, and Apache 2.0 licensing.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Usage](#usage)
- [Batch Downloading](#batch-downloading)
- [Customization](#customization)
- [Credits](#credits)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **Modern GUI:** Sleek and minimal interface built with CustomTkinter.
- **Flexible Quality Options:** Choose your desired video quality (best, 1080p, 720p, etc.) and output format (mp4, mkv, mov, avi).
- **Batch Downloads:** Load multiple URLs (with optional passwords) from a text file. (Yes, you can finally stop copying and pasting!)
- **Password Support:** Enter passwords for protected videos either manually or via a file.
- **Download Acceleration (Optional):** Use aria2c for blazing-fast downloads.
- **Cookies Support:** Load cookies to bypass pesky restrictions.

## Prerequisites

- **Python 3.7+** (Because life is too short for Python 2)
- **yt-dlp**  
  Download the executable from [yt-dlp Releases](https://github.com/yt-dlp/yt-dlp/releases/download/2025.02.19/yt-dlp.exe)
- **CustomTkinter**  
  [GitHub Repository](https://github.com/TomSchimansky/CustomTkinter)
- **aria2c (Optional)**  
  Download the zip from [aria2c Releases](https://github.com/aria2/aria2/releases/download/release-1.37.0/aria2-1.37.0-win-64bit-build1.zip), extract `aria2c.exe`, and place it in the same folder.

## Installation

- **Clone or Download the Repository:**  
  ```bash
  git clone https://github.com/advaniji/vidar.git
  cd vidar

    Download Dependencies:
        yt-dlp: Download yt-dlp.exe and save it in the repository folder.
        aria2c (Optional): Download the zip file, extract aria2c.exe, and place it alongside vidar.py and yt-dlp.exe.
    Install Python Dependencies:

    pip install customtkinter

## Usage

    Run the Application:
    Execute the main script using Python 3:

    python vidar.py

    Download a Single Video:
        Enter the video URL in the GUI.
        Optionally provide a video password (if required).
        Click Download and enjoy the magic (no more waiting forever)!

## Batch Downloading

    Use the Load URLs from File button to select a text file containing multiple URLs.
    Each line can be a URL alone or a URL paired with a password (using delimiters like |, ,, or ;).
    Once loaded, verify the list and click Download to process all entries. Now that's efficiency!

## Customization

    Quality & Format:
    Select from various video quality options and output formats via the GUI.
    Aria2c Integration:
    Enable aria2c in the settings and provide any additional download arguments if needed.
    Cookies Support:
    Load a cookies file from the settings to bypass any stubborn restrictions.

## Credits

    yt-dlp: The backbone of our video downloading power.
    aria2: The download accelerator that puts the "fast" in your downloads.
    CustomTkinter: For making the GUI look so sleek.
    Special thanks to all contributors – you rock!

## Contributing

    Contributions are always welcome. Feel free to submit issues, feature requests, or pull requests. Remember, great ideas and witty comments alike help keep the project fun and useful.

## License

    This project is licensed under the Apache License 2.0. See the LICENSE file for details. Yes, we went with Apache 2.0—because even our licenses are cool.

## Contact

    For questions, suggestions, or just to say hi, please open an issue on GitHub or contact the maintainer.

Happy downloading, and may your videos load in the blink of an eye!
