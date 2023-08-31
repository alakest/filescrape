import os
import sys
import webbrowser

def find_jpeg_files():
  """Finds all JPEG files in all directories on the computer."""
  jpeg_files = []
  for root, directories, files in os.walk('.'):
    for file in files:
      if file.endswith('.jpeg'):
        jpeg_files.append(os.path.join(root, file))
  return jpeg_files

def write_jpeg_file_paths_to_html_page(jpeg_file_paths):
  """Writes the file paths of all JPEG files to an HTML page."""
  with open('jpeg_file_paths.html', 'w', encoding='utf-8') as f:
    f.write('<html>\n<head>\n<title>JPEG File List</title>\n</head>\n<body>\n')
    for jpeg_file_path in jpeg_file_paths:
      f.write('<p><a href="{}">{}</a></p>\n'.format(jpeg_file_path, jpeg_file_path))
    f.write('</body>\n</html>')

def open_html_page(html_file_path):
  webbrowser.open(html_file_path)

if __name__ == '__main__':
  jpeg_file_paths = find_jpeg_files()
  write_jpeg_file_paths_to_html_page(jpeg_file_paths)
  open_html_page('jpeg_file_paths.html')