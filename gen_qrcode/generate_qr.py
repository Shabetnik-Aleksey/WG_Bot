import qrcode
import settings


def generate_code(client_priv_key, current_ip, server_pub_key):
    value = "[Interface]\n" \
            f"PrivateKey = {client_priv_key}\n" \
            f"Address = {current_ip}/32\n" \
            'DNS = "8.8.8.8"\n' \
            "\n" \
            "[Peer]\n" \
            f"PublicKey = {server_pub_key}\n" \
            f"Endpoint = {settings.ENDPOINT}\n" \
            "AllowedIPs = 0.0.0.0/0,::/0"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=3,
        border=4,
    )
    with open('conf_settings.txt', 'w') as f:
        f.write(value)
    qr.add_data(value)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    img.save("code.png")
