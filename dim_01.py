import cv2

def get_image_dimensions(filename):
  """Returns the dimensions of a JPG file.

  Args:
    filename: The path to the JPG file.

  Returns:
    A tuple of (width, height).
  """
  image = cv2.imread(filename)
  return image.shape[:2]


if __name__ == "__main__":
  filename = r"C:\Users\boyada\Desktop\mulch230726\1390093.jpg"
  width, height = get_image_dimensions(filename)
  #print("The dimensions of the image are: width {} x height {}".format(width, height))
  print("The dimensions of the image are: width {} x height {}".format(width, height))