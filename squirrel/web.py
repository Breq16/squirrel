import uuid
import io

from PIL import Image, ImageFont, ImageDraw
import qrcode

from flask import Flask, request, send_file

from trackedqr import TrackedQRType

app = Flask(__name__)


def serve_pil_image(pil_img, dpi=72):
    img_io = io.BytesIO()
    pil_img.save(img_io, "PNG", dpi=(dpi, dpi))
    img_io.seek(0)
    return send_file(img_io, mimetype="image/png")


@app.route("/")
def index():
    return "hewwo!"


@app.route("/marker")
def marker():
    size_code = int(request.args.get("size"), 16)
    reference = bool(int(request.args.get("reference")))
    type_code = size_code \
        + (TrackedQRType.REFERENCE if reference else TrackedQRType.TARGET)
    name = request.args.get("name").encode()[:16]

    qr = qrcode.QRCode(
        version=2,
        error_correction=qrcode.constants.ERROR_CORRECT_Q,
        box_size=1,
        border=0,
    )

    qr.add_data(bytes([type_code]))
    qr.add_data(name)
    qr.make()
    qr_img = qr.make_image(fill_color="black", back_color="white")

    size = TrackedQRType.SIZES_CM[size_code]

    scaled_px = int(size / 2.54 * 72)  # size is in cm, 72 dpi final image
    qr_img = qr_img.resize((scaled_px, scaled_px), Image.NEAREST)

    full_img = Image.new("L", (qr_img.size[0], qr_img.size[0]+50), 0xFF)
    full_img.paste(qr_img, (0, 0, qr_img.size[0], qr_img.size[0]))

    font = ImageFont.truetype("UbuntuMono-B.ttf", 12)
    draw = ImageDraw.Draw(full_img)
    draw.text((10, qr_img.size[0]+30), name.decode(errors="ignore"), 0, font=font)

    return serve_pil_image(full_img)

app.run()
