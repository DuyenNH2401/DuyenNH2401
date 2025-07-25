import getpass
from fpdf import FPDF
from tabulate import tabulate
import matplotlib.pyplot as plt
from datetime import datetime
import pwinput
import qrcode
import os
import webbrowser
import bcrypt

def input_password(prompt='Password: '):
    return pwinput.pwinput(prompt=prompt, mask='*')

def print_table(data, headers):
    print(tabulate(data, headers=headers, tablefmt="fancy_grid"))

def create_invoice_pdf(transaction, username, save_dir="invoices"):

    os.makedirs(save_dir, exist_ok=True)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"invoice_{username}_{transaction.vehicle_plate}_{now}.pdf"
    filepath = os.path.join(save_dir, filename)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=14)
    pdf.cell(0, 10, "SMART PARKING - INVOICE", ln=1, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Owner: {username}", ln=1)
    pdf.cell(0, 10, f"Vehicle plate: {transaction.vehicle_plate}", ln=1)
    pdf.cell(0, 10, f"Slot: {transaction.slot_id}", ln=1)
    pdf.cell(0, 10, f"Check-in: {transaction.in_time}", ln=1)
    pdf.cell(0, 10, f"Check-out: {transaction.out_time}", ln=1)
    pdf.cell(0, 10, f"Total fee: {transaction.fee} VND", ln=1)
    pdf.output(filepath)
    return filepath

def draw_chart(data, title="Chart", xlabel="X", ylabel="Y"):
    plt.figure()
    plt.plot(data)
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.show()

def show_payment_qr(amount, plate, bank_id="VietinBank", acc_num="109876665119", acc_name="NGUYEN HUU DUYEN"):
    info = f"Parking_{plate}"
    qr_url = (
        f"https://img.vietqr.io/image/{bank_id}-{acc_num}-compact2.png"
        f"?amount={int(amount)}"
        f"&addInfo={info}"
        f"&accountName={acc_name.replace(' ', '%20')}"
    )
    img = qrcode.make(qr_url)
    img.show()

def find_parking_on_google_maps(address=None):
    if address:
        url = f"https://www.google.com/maps/search/bãi+đổ+xe+ở+{address.replace(' ', '+')}"
    else:
        url = "https://www.google.com/maps/search/bãi+đỗ+xe+gần+đây"
    webbrowser.open(url)

def hash_password(raw_password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(raw_password.encode(), salt)
    return hashed.decode()

def verify_password(raw_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(raw_password.encode(), hashed_password.encode())
    except Exception:
        return False