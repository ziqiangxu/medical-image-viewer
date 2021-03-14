import PyInstaller.__main__


PyInstaller.__main__.run([
    'medical_image_viewer/main.py',
    # '--onefile',
    '--windowed',
    # '-i path/to/icon.ico',
    '-n medical-image-viewer-1.0.0-beta.1'
])
