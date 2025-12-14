import os

val = os.getenv('STREAM_VISION_DISABLED', 'true')
print(f'Value: {val!r}')
print(f'Lowercase: {val.lower()!r}')
print(f'In tuple: {val.lower() in ("1", "true", "yes")}')
print(f'Should skip vision: {val.lower() in ("1", "true", "yes")}')
