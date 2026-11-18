This is a Python Photo Album

It can browse to a directory and display the image files in a pane as thumbnails.

When you select a particular image it expands the thumbnail into a image in the adjacent pane.

valid_exts = (".png", ".jpg", ".jpeg", ".gif", ".bmp", ".webp")

#steps to create EXE for one-click use of app
place PythonPhotoAlbum.py in a folder (example:C:\Users\Admin\Desktop\work\Python\PythonApps\)
along with txt_studio.ico.
#Goto command prompt

pip install pyinstaller

pyinstaller --noconsole --onefile --icon C:\Users\Admin\Desktop\work\Python\PythonApps\txt_studio.ico C:\Users\Admin\Desktop\work\Python\PythonApps\PythonPhotoAlbum.py

It will create EXE in folder C:\Users\Admin\dist by default. Copy EXE to desired location.
