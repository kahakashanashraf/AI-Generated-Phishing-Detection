"""Kaggle/Colab environment smoke test; no model training."""
import platform
import sys

print('Python:', sys.version.split()[0])
print('Platform:', platform.platform())

for name in ('numpy', 'pandas', 'sklearn'):
    module = __import__(name)
    print(f'{name}: {module.__version__}')

try:
    import torch
    print('PyTorch:', torch.__version__)
    print('CUDA available:', torch.cuda.is_available())
    if torch.cuda.is_available():
        print('CUDA GPU count:', torch.cuda.device_count())
        for i in range(torch.cuda.device_count()):
            print(f'GPU {i}:', torch.cuda.get_device_name(i))
except ImportError:
    print('PyTorch not installed; this check does not require it.')

print('Environment check completed. No training was run.')
