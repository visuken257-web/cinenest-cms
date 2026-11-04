import os
import sys

# Thêm thư mục gốc của project vào sys.path để import được app và models
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app

# Vercel Serverless Function entrypoint
# Biến 'app' được export để Vercel WSGI handler nhận diện
