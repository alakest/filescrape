import os
import sys
import webbrowser
import numpy as np

def read_file_list(file_list_path):
  """Reads a text file that lists files."""
  with open(file_list_path, 'r') as f:
    file_list = f.readlines()
  return file_list

def get_image_dimensions(file_path):
  """Gets the dimensions of an image."""
  with open(file_path, 'rb') as f:
    image = f.read()
    image = np.array(image)
  if image.ndim >= 2:
    width, height = image.shape[:2]
  else:
    return None

def write_html_page(file_list, html_file_path):
  """Writes an HTML file that displays each of the files as an image with an href link to the file, and also shows the file path text and the dimensions of the image."""
  with open(html_file_path, 'w', encoding='utf-8') as f:
    f.write('<html>\n<head>\n<title>Image List</title>\n</head>\n<body>\n')
    for file in file_list:
      file_path = file.strip()
      width, height = get_image_dimensions(file_path)
      f.write('<a href="{}"><img src="{}" alt="{}">\n'.format(file_path, file_path, file_path))
      if width is not None and height is not None:
        f.write('<p>{} ({}x{})</p>\n'.format(file_path, width, height))
      else:
        f.write('<p>{} (no dimensions)</p>\n'.format(file_path))
    f.write('</body>\n</html>')

def open_html_page(html_file_path):
  webbrowser.open(html_file_path)

if __name__ == '__main__':
  file_list_path = r"C:\Users\boyada\Desktop\py_mulch_01\jpeg_file_paths.txt"
  html_file_path = r"C:\Users\boyada\Desktop\py_mulch_01\jpeg_file_list.html"
  file_list = read_file_list(file_list_path)
  write_html_page(file_list, html_file_path)
  open_html_page(html_file_path)