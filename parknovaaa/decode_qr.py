import cv2
from pyzbar.pyzbar import decode
import sys

def decode_qr(image_path):
    try:
        img = cv2.imread(image_path)
        decoded_objects = decode(img)
        for obj in decoded_objects:
            print(f"Data: {obj.data.decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    decode_qr(sys.argv[1])
