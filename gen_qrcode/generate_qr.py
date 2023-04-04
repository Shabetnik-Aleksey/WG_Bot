import qrcode


def generate_code(value):
    img = qrcode.make(value)
    img.save("code.png")

# generate_code()