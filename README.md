# yt-downloader

A simple GUI-based application to download YouTube videos using yt-dlp. The application allows you to select the video quality, format, and download location, while displaying the download progress.

<img width="760" height="458" alt="Screenshot from 2026-03-10 14-17-11" src="https://github.com/user-attachments/assets/1351c953-ccb3-4a42-8ffc-389f2d0165d3" />


## Features

- Download videos from YouTube in specified quality (360p, 480p, 720p, 1080p).
- Choose output format (MKV, MP4, WEBM).
- Select the download location (default: ~/Downloads/videos).
- Real-time download progress display.
- Built using Python and Tkinter for a user-friendly interface.

## Requirements

- Python 3.x or above
- yt-dlp (YouTube-DL fork)
- Tkinter (usually comes pre-installed with Python)

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/thesophile/yt-downloader.git
   cd yt-downloader
   ```

2. Create and activate a virtual environment:
   ```
   python3 -m venv myenv
   source myenv/bin/activate
   ```

3. Install yt-dlp:
   ``` 
   pip install yt-dlp
   ```

5. Install tkinter if you dont have it:
   ```
   sudo apt install python3-tk tk-dev
   ```

## Usage

1. Run the application:
   ```
   python3 download.py
   ```

2. Enter the YouTube URL of the video you want to download.

3. Select the desired video quality from the dropdown menu.

4. Choose the output format from the available options.

5. Specify the download location by clicking the "Browse" button (default is ~/Downloads/videos).

6. Click the "Download" button to start the download. Progress will be displayed in real-time.

## Example Command

The application uses the following command internally to download videos:
```
myenv/bin/python -m yt_dlp -f bestvideo[height=720]+bestaudio --merge-output-format mkv -o ~/Downloads/videos/%(title)s.%(ext)s <YouTube_URL>
```

## Contributing

Contributions are welcome! If you have suggestions or improvements, feel free to open an issue or submit a pull request.

## License

This project is licensed under the MIT License. See the LICENSE file for details.

## Acknowledgments

- yt-dlp for the video downloading functionality.
- Tkinter for the GUI.
