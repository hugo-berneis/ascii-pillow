# asciify

Turn any image into ASCII art using Python and Pillow.

## How it works

1. Loads the image and converts it to grayscale
2. Resizes it (adjusting for the fact that text characters are taller than wide)
3. Maps each pixel's brightness to a character, from dark (`@`) to light (` `)

## Requirements

- Python 3
- Pillow

```bash
pip install pillow
```

## Usage

```bash
python asciify.py
```

Edit the bottom of `asciify.py` to point at your image:

```python
print(image_to_ascii("photo.jpg", width=100))
```

- `width` controls how many characters wide the output is.
- If the output looks inverted in a dark terminal, reverse the character ramp with `CHARS[::-1]`.

## License

MIT# ascii-pillow
