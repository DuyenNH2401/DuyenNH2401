Smart Parking System

1. Introduction

Smart Parking System is a web-based application designed to streamline parking lot management with three distinct user roles:

**Admin**: Manage user accounts (create/delete Admin or Attendant), parking slots, revenue reports, dynamic pricing settings, and view audit logs.
**Attendant**: Perform vehicle check-in/check-out and view available slots.
**Owner**: View available slots, view and pay parking fees (QR code or cash), and find parking locations on a map.

The application is built with **Flask** (Python) on the backend and uses **Bootstrap 5** for a responsive frontend.

---

2. Prerequisites

* Python 3.10 or higher
* pip (Python package installer)
* Recommended: virtual environment (venv or similar)

---

3. Install dependencies

   pip install -r requirements.txt

---

4. Environment Configuration

Set environment variables before running the app:

export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_SECRET_KEY="your-secret-key"


5. Running the Application

Start the Flask development server:

```bash
flask run
```

Open your browser and navigate to `http://127.0.0.1:5000`.

---

## 6. Usage

### Landing Page

* Click **Start** to go to the login page.

### Authentication

* **Sign Up**: Register as an Owner.
* **Login**: Access the dashboard based on your role.

### Dashboards

* **Admin Dashboard**:

  * Create or delete users (Admin/Attendant)
  * Add or remove parking slots
  * View revenue reports
  * Configure dynamic pricing
  * View audit logs
* **Attendant Dashboard**:

  * Check-in vehicles
  * Check-out vehicles
  * View available slots
* **Owner Dashboard**:

  * View available slots
  * View and pay parking fees (QR code or cash)
  * Find parking locations on a map

---

## 7. Project Structure

```plaintext
smart-parking-system/
├── app.py                  # Main Flask application
├── modules/                # Business logic modules
│   ├── user_manager.py
│   ├── slot_manager.py
│   ├── transaction_manager.py
│   ├── blacklist_manager.py
│   └── audit_log.py
├── utils/                  # Utility functions
│   └── utils.py            # Helpers: password hash, PDF invoice, map, etc.
├── templates/              # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── admin_dashboard.html
│   ├── attendant_dashboard.html
│   ├── owner_dashboard.html
│   ├── create_user.html
│   ├── view_users.html
│   ├── add_slot.html
│   ├── remove_slot.html
│   ├── view_revenue.html
│   ├── set_dynamic_pricing.html
│   ├── view_audit_log.html
│   ├── checkin.html
│   ├── checkout.html
│   ├── view_available_slots.html
│   ├── find_parking.html
│   └── pay_fee.html
├── static/                 # Static assets
│   ├── css/
│   │   └── style.css       # Custom styles
│   └── js/
│       └── script.js       # Frontend scripts
├── data/                   # CSV storage
│   ├── users.csv
│   ├── slots.csv
│   ├── transactions.csv
│   ├── blacklist.csv
│   ├── attendance.csv
│   └── audit_log.csv
├── invoices/               # Generated PDF invoices
│   └── *.pdf
└── requirements.txt        # Python dependencies
```

---

## 8. Notes & Future Enhancements

* Data is stored in CSV files; can migrate to a relational database (PostgreSQL/MySQL).
* QR payments are generated in-app without exposing sensitive bank details.
* Map integration uses Leaflet and OpenStreetMap by default (no API key required).
* Secured sessions using Flask's session management.

---

## 9. License & Contact

* **License**: MIT License
* **Contact**: [your-email@example.com](mailto:your-email@example.com)
