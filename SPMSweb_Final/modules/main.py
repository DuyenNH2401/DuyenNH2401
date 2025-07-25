import os
import questionary
import pwinput
from colorama import Fore, Style, init

from user_manager import UserManager
from slot_manager import SlotManager
from transaction_manager import TransactionManager
from blacklist_manager import BlacklistManager
from audit_log import AuditLog
from utils import print_table, create_invoice_pdf, show_payment_qr, find_parking_on_google_maps

init(autoreset=True)
INVOICE_DIR = "invoices"
os.makedirs(INVOICE_DIR, exist_ok=True)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    input("\nPress Enter to continue...")

def print_title():
    title = f"""
{Fore.CYAN}{Style.BRIGHT}
╔══════════════════════════════════╗
║      SMART PARKING SYSTEM        ║
╚══════════════════════════════════╝
{Style.RESET_ALL}
"""
    print(title)

def input_password(prompt='Password: '):
    return pwinput.pwinput(prompt=prompt, mask='*')

def main_menu(role):
    if role == 'attendant':
        return questionary.select(
            "Attendant Menu:",
            choices=[
                "View available slots",
                "Check-in vehicle",
                "Check-out vehicle",
                "Exit"
            ]
        ).ask()
    elif role == 'owner':
        return questionary.select(
            "Owner Menu:",
            choices=[
                "View available slots",
                "View and pay parking fees",
                "Find parking on Google Maps",
                "Exit"
            ]
        ).ask()
    elif role == 'admin':
        return questionary.select(
            "Admin Menu:",
            choices=[
                "Add parking slot",
                "Remove parking slot",
                "View available slots",
                "Revenue report",
                "Adjust dynamic pricing",
                "Create attendant/admin user",
                "View audit log",
                "Exit"
            ]
        ).ask()
    else:
        return None

def login_menu():
    return questionary.select(
        "Sign In / Sign Up:",
        choices=[
            "Sign in",
            "Sign up",
            "Exit"
        ]
    ).ask()

def main():
    user_mgr = UserManager()
    slot_mgr = SlotManager()
    tx_mgr = TransactionManager(
        default_rate=2.0,
        dynamic_rates={
            (7, 17): 3.0,
            (17, 22): 5.0,
            (22, 7): 2.0
        }
    )
    bl_mgr = BlacklistManager()
    audit = AuditLog()
    while True:
        clear_screen()
        print_title()
        choice = login_menu()
        if choice == "Sign up":
            clear_screen()
            print_title()
            username = input("Username: ")
            if user_mgr.username_exists(username):
                print("Username already exists!")
                pause()
                continue
            password = input_password("Password: ")
            role = "owner"
            user_mgr.add_user(username, password, role)
            print("Sign up successful! You are now an owner.")
            audit.log(username, "register", f"Role: {role}")
            pause()
        elif choice == "Sign in":
            clear_screen()
            print_title()
            username = input("Username: ")
            password = input_password("Password: ")
            user = user_mgr.find_user(username, password)
            if not user:
                print("Sign in failed. Please try again.")
                pause()
                continue
            audit.log(username, "login", f"Role: {user.role}")
            while True:
                clear_screen()
                print_title()
                action = main_menu(user.role)
                if action == "Exit":
                    audit.log(username, "logout", "")
                    break
                # ==== ATTENDANT ====
                if user.role == "attendant":
                    if action == "Check-in vehicle":
                        plate = input("Vehicle plate: ")
                        if bl_mgr.is_blacklisted(plate):
                            print("This vehicle is blacklisted! Entry denied.")
                            audit.log(username, "block_checkin", plate)
                            pause()
                            continue
                        owner = input("Owner username: ")
                        available_slots = slot_mgr.get_available_slots()
                        if not available_slots:
                            print("No slots available.")
                            pause()
                            continue
                        slot_id = available_slots[0].slot_id
                        tx_mgr.check_in(plate, owner, slot_id)
                        slot_mgr.update_slot(slot_id, False)
                        print(f"Checked in at slot {slot_id}.")
                        audit.log(username, "checkin", f"Vehicle {plate} in slot {slot_id}")
                        pause()
                    elif action == "Check-out vehicle":
                        plate = input("Vehicle plate: ")
                        fee, slot_id = tx_mgr.check_out(plate)
                        if fee is not None:
                            slot_mgr.update_slot(slot_id, True)
                            print(f"Checked out. Parking fee: {fee} VND")
                            audit.log(username, "checkout", f"Vehicle {plate} out slot {slot_id}, fee {fee}")
                            for t in tx_mgr.transactions:
                                if t.vehicle_plate == plate and t.fee == fee and not t.paid:
                                    print("Please remind the owner to pay the fee at the owner menu.")
                                    break
                        else:
                            print("Vehicle not found or already checked out.")
                        pause()
                    elif action == "View available slots":
                        av = slot_mgr.get_available_slots()
                        print(f"Available slots: {len(av)}")
                        print_table([[s.slot_id, s.is_available] for s in av], ["Slot ID", "Available"])
                        audit.log(username, "view_available_slots", f"Available slots: {len(av)}")
                        pause()
                # ==== OWNER ====
                elif user.role == "owner":
                    if action == "View available slots":
                        av = slot_mgr.get_available_slots()
                        print(f"Available slots: {len(av)}")
                        print_table([[s.slot_id, s.is_available] for s in av], ["Slot ID", "Available"])
                        audit.log(username, "view_available_slots", f"Available slots: {len(av)}")
                        pause()
                    elif action == "View and pay parking fees":
                        unpaid = tx_mgr.get_unpaid_transactions(user.username)
                        if not unpaid:
                            print("You have no unpaid parking fees.")
                            pause()
                            continue
                        data = [[i+1, t.vehicle_plate, t.in_time, t.out_time, t.fee, "Paid" if t.paid else "Unpaid"] for i, t in enumerate(unpaid)]
                        print_table(data, ["#", "Plate", "Check-in", "Check-out", "Fee", "Status"])
                        index = input(f"Enter # to pay (or Enter to skip): ")
                        if index.isdigit():
                            idx = int(index) - 1
                            if 0 <= idx < len(unpaid):
                                t = unpaid[idx]
                                method = questionary.select(
                                    "Choose payment method:",
                                    choices=["QR code", "Cash"]
                                ).ask()
                                if method == "QR code":
                                    show_payment_qr(t.fee, t.vehicle_plate)
                                    print("Scan the QR code above to complete your payment.")
                                else:
                                    print(f"Please pay {t.fee} VND in cash to the attendant.")
                                t.paid = True
                                tx_mgr.save_transactions()
                                invoice_path = create_invoice_pdf(t, username, save_dir=INVOICE_DIR)
                                print(f"Payment completed! Invoice saved at: {invoice_path}")
                                audit.log(username, "pay_fee", f"Paid for plate {t.vehicle_plate} by {method}")
                                pause()
                        else:
                            print("Skipped payment.")
                        pause()
                    elif action == "Find parking on Google Maps":
                        address = input("Enter address/city to search (or leave empty for nearby): ")
                        print("Opening Google Maps in your browser...")
                        find_parking_on_google_maps(address)
                        pause()
                # ==== ADMIN ====
                elif user.role == "admin":
                    if action == "Add parking slot":
                        n = int(input("Number of slots to add: "))
                        slot_mgr.add_slot(n)
                        print(f"Added {n} new slots.")
                        audit.log(username, "add_slot", f"Added {n} slots")
                        pause()
                    elif action == "Remove parking slot":
                        slot_id = int(input("Slot ID to remove: "))
                        slot_mgr.remove_slot(slot_id)
                        print(f"Removed slot {slot_id}")
                        audit.log(username, "remove_slot", f"Slot {slot_id}")
                        pause()
                    elif action == "View available slots":
                        av = slot_mgr.get_available_slots()
                        print(f"Available slots: {len(av)}")
                        print_table([[s.slot_id, s.is_available] for s in av], ["Slot ID", "Available"])
                        audit.log(username, "view_available_slots", f"Available slots: {len(av)}")
                        pause()
                    elif action == "Revenue report":
                        revenue = tx_mgr.get_revenue()
                        print(f"Total revenue: {revenue} VND")
                        audit.log(username, "revenue_report", f"Total: {revenue}")
                        pause()
                    elif action == "Adjust dynamic pricing":
                        print("Current pricing:")
                        for (start, end), rate in tx_mgr.dynamic_rates.items():
                            print(f"{start}:00 to {end}:00 — {rate} VND/hour")
                        start = int(input("Start hour (0-23): "))
                        end = int(input("End hour (0-23): "))
                        rate = float(input("Enter new rate: "))
                        tx_mgr.set_dynamic_rate(start, end, rate)
                        print(f"Set {start}:00 to {end}:00 as {rate} VND/hour")
                        pause()
                    elif action == "Create attendant/admin user":
                        new_user = input("Username: ")
                        if user_mgr.username_exists(new_user):
                            print("Username already exists!")
                            pause()
                            continue
                        new_pass = input_password("Password: ")
                        new_role = questionary.select("Role:", choices=["attendant", "admin"]).ask()
                        user_mgr.add_user(new_user, new_pass, new_role)
                        print(f"User {new_user} ({new_role}) created.")
                        audit.log(username, "add_user", f"Added {new_user}, role {new_role}")
                        pause()
                    elif action == "View audit log":
                        print("See file: data/audit_log.csv for details.")
                        pause()
        else:
            print("Exiting program.")
            break

if __name__ == "__main__":
    main()
