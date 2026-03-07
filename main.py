import flet as ft
import json
import os
from datetime import datetime
import re

DATA_FILE = "data.json"

BARBERS = {
    "oussama": "1234567",
    "khireeddine": "1234567891011",
    "zaki": "1234",
    "maztoule": "12345678",
    "mounir": "123456",
    "mohamed bosta": "12345678",
}

TIME_SLOTS = [
    "09:00","09:30","10:00","10:30",
    "11:00","11:30","12:00",
    "14:00","14:30","15:00","15:30",
    "16:00","16:30","17:00","17:30"
]

def load_data():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def main(page: ft.Page):
    page.title = "Elite Barber"
    page.window.width = 400
    page.window.height = 800
    page.padding = 20
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.theme = ft.Theme(color_scheme_seed=ft.Colors.BLUE)

    def snack(msg, color=ft.Colors.GREEN):
        page.snack_bar = ft.SnackBar(ft.Text(msg), bgcolor=color)
        page.snack_bar.open = True
        page.update()

    def home():
        page.controls.clear()
        page.add(
            ft.Column(
                [
                    ft.Text("ELITE BARBER", size=28, weight="bold"),
                    ft.Text("Premium Booking Experience"),
                    ft.Divider(),
                    ft.FilledButton("💈 Barber Login", width=250, on_click=barber_login),
                    ft.OutlinedButton("🧑 Book Appointment", width=250, on_click=client_page),
                    ft.IconButton(icon=ft.Icons.DARK_MODE, on_click=toggle_theme)
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
                spacing=20
            )
        )
        page.update()

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode == ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.update()

    def client_page(e=None):
        name = ft.TextField(label="Full Name", width=320)
        phone = ft.TextField(label="Phone (+213)", value="+213", width=320)
        phone.on_change = lambda e: setattr(phone, "value", "+213") if not phone.value.startswith("+213") else None

        barber_dropdown = ft.Dropdown(
            label="Choose Barber",
            width=320,
            options=[ft.dropdown.Option(key=b, text=b.upper()) for b in BARBERS]
        )

        time = ft.Dropdown(
            label="Choose Time",
            width=320,
            options=[ft.dropdown.Option(t) for t in TIME_SLOTS]
        )

        selected_date = ft.Text("Select Date")
        picker = ft.DatePicker(on_change=lambda e: setattr(selected_date, "value", e.control.value.strftime("%Y-%m-%d")))
        page.overlay.append(picker)

        def book(e):
            if not name.value:
                snack("Enter your name", ft.Colors.RED)
                return
            if not re.fullmatch(r"\+213\d+", phone.value):
                snack("Invalid phone", ft.Colors.RED)
                return
            if not barber_dropdown.value or not time.value:
                snack("Select barber and time", ft.Colors.RED)
                return
            if selected_date.value == "Select Date":
                snack("Choose a date", ft.Colors.RED)
                return

            data = load_data()
            for a in data:
                if a["barber"] == barber_dropdown.value and a["date"] == selected_date.value and a["time"] == time.value:
                    snack("Time already booked", ft.Colors.RED)
                    return

            data.append({
                "name": name.value,
                "phone": phone.value,
                "barber": barber_dropdown.value,
                "date": selected_date.value,
                "time": time.value
            })
            save_data(data)
            snack("Appointment Confirmed 🎉")
            home()

        page.controls.clear()
        page.add(
            ft.Column(
                [
                    ft.Text("Book Appointment", size=24, weight="bold"),
                    name, phone, barber_dropdown,
                    ft.FilledButton("Select Date", on_click=lambda e: setattr(picker, "open", True)),
                    selected_date, time,
                    ft.FilledButton("Confirm Booking", on_click=book),
                    ft.TextButton("Back", on_click=home)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            )
        )
        page.update()

    def barber_login(e=None):
        user = ft.TextField(label="Username", width=320)
        pwd = ft.TextField(label="Password", password=True, width=320)

        def login(e):
            if user.value in BARBERS and BARBERS[user.value] == pwd.value:
                dashboard(user.value)
            else:
                snack("Wrong credentials", ft.Colors.RED)

        page.controls.clear()
        page.add(
            ft.Column(
                [
                    ft.Text("Barber Login", size=24, weight="bold"),
                    user, pwd,
                    ft.FilledButton("Login", on_click=login),
                    ft.TextButton("Back", on_click=home)
                ],
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                spacing=15
            )
        )
        page.update()

    def dashboard(barber_name):
        search = ft.TextField(label="Search client", width=320)
        appointments_list = ft.ListView(expand=True, spacing=5, padding=10, auto_scroll=True)

        def refresh():
            appointments_list.controls.clear()
            data = [a for a in load_data() if a["barber"] == barber_name]
            today = datetime.now().strftime("%Y-%m-%d")
            today_count = sum(1 for a in data if a["date"] == today)
            appointments_list.controls.append(ft.Text(f"Today's Appointments: {today_count}", weight="bold"))

            for a in data:
                if search.value and search.value.lower() not in a["name"].lower():
                    continue
                appointments_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column(
                                [
                                    ft.Text(f"{a['date']} - {a['time']}", weight="bold"),
                                    ft.Text(a["name"]),
                                    ft.Text(a["phone"]),
                                    ft.IconButton(icon=ft.Icons.CALL, on_click=lambda e, p=a["phone"]: page.launch_url(f"tel:{p}"))
                                ]
                            )
                        )
                    )
                )
            page.update()

        search.on_change = refresh

        page.controls.clear()
        page.add(
            ft.Column(
                [
                    search,
                    appointments_list,
                    ft.Row(
                        [ft.IconButton(icon=ft.Icons.LOGOUT, on_click=home, tooltip="Logout", icon_color=ft.Colors.RED)],
                        alignment=ft.MainAxisAlignment.END
                    )
                ],
                expand=True
            )
        )
        refresh()

    home()

ft.app(target=main)
