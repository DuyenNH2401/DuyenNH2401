from flask import Flask, render_template, request, redirect, url_for, session
from modules.user_manager import UserManager
from modules.slot_manager import SlotManager
from modules.transaction_manager import TransactionManager
from modules.blacklist_manager import BlacklistManager
from modules.audit_log import AuditLog
from modules.utils import find_parking_on_google_maps
import urllib.parse
import io
import base64
import qrcode

app = Flask(__name__)
app.secret_key = 'your-secret-key'

user_mgr = UserManager()
slot_mgr = SlotManager()
tx_mgr = TransactionManager(default_rate=2.0)
bl_mgr = BlacklistManager()
audit = AuditLog()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = 'owner'
        if user_mgr.username_exists(username):
            return render_template('signup.html', error="Username already exists!")
        user_mgr.add_user(username, password, role)
        audit.log(username, "register", f"Role: {role}")
        return redirect(url_for('login'))
    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = user_mgr.find_user(username, password)
        if user:
            session['username'] = user.username
            session['role'] = user.role
            return redirect(url_for('dashboard', role=user.role))
        return render_template('login.html', error="Login failed. Please try again.")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard/<role>')
def dashboard(role):
    if 'username' not in session or session.get('role') != role:
        return redirect(url_for('login'))
    if role == 'admin':
        return render_template('admin_dashboard.html')
    elif role == 'attendant':
        return render_template('attendant_dashboard.html')
    elif role == 'owner':
        return render_template('owner_dashboard.html')
    return "Unauthorized", 403

# --- Admin routes ---
@app.route('/admin/add_slot', methods=['GET', 'POST'])
def add_slot():
    if request.method == 'POST':
        n = int(request.form['number_of_slots'])
        slot_mgr.add_slot(n)
        return redirect(url_for('dashboard', role='admin'))
    return render_template('add_slot.html')

@app.route('/admin/remove_slot', methods=['GET', 'POST'])
def remove_slot():
    if request.method == 'POST':
        slot_id = int(request.form['slot_id'])
        slot_mgr.remove_slot(slot_id)
        return redirect(url_for('dashboard', role='admin'))
    return render_template('remove_slot.html')

@app.route('/admin/view_revenue')
def view_revenue():
    transactions = tx_mgr.transactions
    total = tx_mgr.get_revenue()
    return render_template('view_revenue.html', revenue=transactions, total_revenue=total)

@app.route('/admin/create_user', methods=['GET', 'POST'])
def create_user():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role = request.form['role']
        if role not in ['admin', 'attendant']:
            return render_template('create_user.html', error="Invalid role.")
        user_mgr.add_user(username, password, role)
        return redirect(url_for('dashboard', role='admin'))
    return render_template('create_user.html')

@app.route('/admin/view_users')
def view_users():
    return render_template('view_users.html', users=user_mgr.users)

@app.route('/admin/delete_user/<username>')
def delete_user(username):
    if username == session.get('username'):
        return "Cannot delete yourself."
    if user_mgr.find_user_by_username(username):
        user_mgr.delete_user(username)
    return redirect(url_for('view_users'))

@app.route('/admin/set_dynamic_pricing', methods=['GET', 'POST'])
def set_dynamic_pricing():
    if request.method == 'POST':
        start = int(request.form['start'])
        end = int(request.form['end'])
        rate = float(request.form['rate'])
        tx_mgr.set_dynamic_rate(start, end, rate)
        return redirect(url_for('dashboard', role='admin'))
    return render_template('set_dynamic_pricing.html')

@app.route('/admin/view_audit_log')
def view_audit_log():
    logs = audit.load_logs()
    return render_template('view_audit_log.html', audit_log=logs)

# --- Attendant routes ---
@app.route('/attendant/checkin', methods=['GET', 'POST'])
def checkin():
    if request.method == 'POST':
        plate = request.form['vehicle_plate']
        owner = request.form['owner_username']
        if bl_mgr.is_blacklisted(plate):
            return render_template('checkin.html', error="Vehicle is blacklisted!")
        slots = slot_mgr.get_available_slots()
        if not slots:
            return render_template('checkin.html', error="No available slots.")
        slot = slots[0]
        tx_mgr.check_in(plate, owner, slot.slot_id)
        slot_mgr.update_slot(slot.slot_id, False)
        audit.log(session['username'], "checkin", f"{plate}@{slot.slot_id}")
        return redirect(url_for('dashboard', role='attendant'))
    return render_template('checkin.html')

@app.route('/attendant/checkout', methods=['GET', 'POST'])
def checkout():
    if request.method == 'POST':
        plate = request.form['vehicle_plate']
        fee, slot_id = tx_mgr.check_out(plate)
        if fee is None:
            return render_template('checkout.html', error="Not found or already checked out.")
        slot_mgr.update_slot(slot_id, True)
        audit.log(session['username'], "checkout", f"{plate}@{slot_id}, fee={fee}")
        return redirect(url_for('dashboard', role='attendant'))
    return render_template('checkout.html')

@app.route('/view_available_slots')
def view_available_slots():
    slots = slot_mgr.get_available_slots()
    return render_template('view_available_slots.html', slots=slots)

# --- Owner routes ---
@app.route('/owner/view_and_pay', methods=['GET', 'POST'])
def owner_pay():
    unpaid = tx_mgr.get_unpaid_transactions(session['username'])
    if request.method == 'POST':
        idx = int(request.form['index'])
        t = unpaid[idx]
        t.paid = True
        tx_mgr.save_transactions()
        return redirect(url_for('dashboard', role='owner'))
    return render_template('owner_pay.html', unpaid=unpaid)

@app.route('/owner/find_parking', methods=['GET', 'POST'])
def find_parking():
    if request.method == 'POST':
        address = request.form.get('address', '')
        find_parking_on_google_maps(address)
        return render_template('find_parking.html', done=True, address=address)
    return render_template('find_parking.html', done=False)


@app.route('/owner/pay_fee', methods=['GET', 'POST'])
def pay_fee():
    unpaid = tx_mgr.get_unpaid_transactions(session['username'])
    qr_data_uri = None
    cash_message = None
    error = None

    if request.method == 'POST':
        raw_idx = request.form.get('index', '')
        method  = request.form.get('method', '')

        try:
            idx = int(raw_idx)
            if idx < 0 or idx >= len(unpaid):
                raise IndexError
        except Exception:
            error = "Invalid transaction selection."
        else:
            t = unpaid[idx]
            t.paid = True
            tx_mgr.save_transactions()

            if method == 'cash':
                cash_message = f"Please pay {t.fee:.0f} VND in cash to the attendant."
            else:
                bank_account = "109876665119"
                account_name = "Nguyen Huu Duyen"
                bank_name    = "VietinBank"
                amount       = int(t.fee)
                payload = f"bank_account={bank_account}&account_name{account_name}&bank_name={bank_name}&amount={amount}"

                qr = qrcode.QRCode(
                    version=1,
                    error_correction=qrcode.constants.ERROR_CORRECT_L,
                    box_size=10,
                    border=4,
                )
                qr.add_data(payload)
                qr.make(fit=True)
                img = qr.make_image(fill_color="black", back_color="white")

                buf = io.BytesIO()
                img.save(buf, format="PNG")
                buf.seek(0)
                b64 = base64.b64encode(buf.read()).decode('ascii')
                qr_data_uri = f"data:image/png;base64,{b64}"

    return render_template(
        'pay_fee.html',
        unpaid=unpaid,
        qr_data_uri=qr_data_uri,
        cash_message=cash_message,
        error=error
    )


if __name__ == '__main__':
    app.run(debug=True)
