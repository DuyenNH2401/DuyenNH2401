import questionary

def main_menu(role):
    if role == 'admin':
        return questionary.select(
            "Admin Menu:",
            choices=[
                "Thêm chỗ đỗ",
                "Xóa chỗ đỗ",
                "Báo cáo doanh thu",
                "Thiết lập dynamic pricing",
                "Xem lịch sử thao tác",
                "Thoát"
            ]
        ).ask()
    elif role == 'attendant':
        return questionary.select(
            "Attendant Menu:",
            choices=[
                "Check-in xe",
                "Check-out xe",
                "Chấm công vào ca",
                "Chấm công ra ca",
                "Thoát"
            ]
        ).ask()
    elif role == 'owner':
        return questionary.select(
            "Owner Menu:",
            choices=[
                "Xem slot trống",
                "Đặt chỗ trước",
                "Xem hóa đơn xe",
                "Thoát"
            ]
        ).ask()
    else:
        return None

def login_menu():
    return questionary.select(
        "Login/Register:",
        choices=[
            "Đăng nhập",
            "Đăng ký",
            "Thoát"
        ]
    ).ask()
