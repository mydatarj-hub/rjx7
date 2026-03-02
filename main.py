import flet as ft
import json
import os
import asyncio
import re

DATA_FILE = "data.json"

# الحسابات لتسجيل الدخول
BARBER_ACCOUNTS = {
    "oussama": "1234567",
    "khireeddine": "1234567891011",
    "zaki": "1234",
    "mounir": "123456",
    "maztoule": "12345678",
}

# أسماء الحلاقين للعرض فقط (كبيرة)
BARBER_DISPLAY_NAMES = ["KHIREEDDINE", "OUSSAMA", "ZAKI", "MAZTOULE", "MOUNIR"]

# تحويل اسم العرض إلى اسم الحساب الأصلي
DISPLAY_TO_ACCOUNT = {name.upper(): name for name in BARBER_ACCOUNTS.keys()}

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
        json.dump(data, f, ensure_ascii=False, indent=2)

async def main(page: ft.Page):
    page.title = "Barber Shop"
    page.scroll = "auto"
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"
    page.window.width = 390
    page.window.height = 700
    page.scroll = "auto"
    page.padding = 20
    page.window.resizable = False

    dialog = ft.AlertDialog(modal=True)
    page.dialog = dialog

    async def show_message(title, message, color):
        dialog.title = ft.Text(title, color=color, weight="bold")
        dialog.content = ft.Text(message)
        dialog.actions = [ft.TextButton("OK", on_click=lambda e: close_dialog())]
        dialog.open = True
        page.update()

    def close_dialog():
        dialog.open = False
        page.update()

    # ---------- Home ----------
    async def show_home():
        page.controls.clear()
        welcome_text = ft.Text(
            "Welcome To Your New Look ✂️",
            size=20,
            weight="bold",
            opacity=0,
            animate_opacity=1000
        )
        page.add(
            ft.Column(
                [
                    welcome_text,
                    ft.Divider(),
                    ft.Text("Choose Your Role", size=20),
                    ft.ElevatedButton("💈 I am a Barber", on_click=show_barber_login),
                    ft.ElevatedButton("🧑 I am a Client", on_click=show_client_page),
                    ft.Divider(),
                    ft.Text("Developed by KHIRE_EDDINE_RJ7", size=12)
                ],
                horizontal_alignment="center"
            )
        )
        page.update()
        await asyncio.sleep(0.5)
        welcome_text.opacity = 1
        page.update()

    # ---------- Client ----------
    def show_client_page(e=None):
        name = ft.TextField(label="Name", width=300)
        phone = ft.TextField(label="Phone", width=300, value="+213")
        barber = ft.Dropdown(
            label="Choose Barber",
            width=300,
            options=[ft.dropdown.Option(b) for b in BARBER_DISPLAY_NAMES]
        )
        time = ft.Dropdown(
            label="Choose Time",
            width=300,
            options=[ft.dropdown.Option(t) for t in TIME_SLOTS]
        )
        date_text = ft.Text("No date selected")

        def on_date_change(e):
            date_text.value = e.control.value.strftime("%Y-%m-%d")
            page.update()

        date_picker = ft.DatePicker(on_change=on_date_change)
        page.overlay.append(date_picker)

        def open_date(e):
            date_picker.open = True
            page.update()

        async def book(e):
            if not name.value or not phone.value:
                await show_message("⚠ Error", "Fill all fields", "orange")
                return
            if not re.fullmatch(r"\+?\d+", phone.value):
                await show_message("⚠ Error", "Phone must be numbers with +", "orange")
                return
            if not barber.value or not time.value:
                await show_message("⚠ Error", "Select barber and time", "orange")
                return
            if date_text.value == "No date selected":
                await show_message("⚠ Error", "Select date", "orange")
                return

            # تحويل اسم العرض إلى اسم الحساب الأصلي
            barber_account_name = DISPLAY_TO_ACCOUNT[barber.value.upper()]

            data = load_data()
            # التحقق من تكرار الموعد
            for a in data:
                if a["barber"] == barber_account_name and a["date"] == date_text.value and a["time"] == time.value:
                    await show_message("❌ Not Available", "Time already booked", "red")
                    return

            # إضافة الموعد
            data.append({
                "name": name.value,
                "phone": phone.value,
                "barber": barber_account_name,
                "date": date_text.value,
                "time": time.value,
            })
            save_data(data)
            await show_message("✅ Success", "Appointment booked", "green")

            # إعادة ضبط الحقول
            name.value = ""
            phone.value = "+213"
            barber.value = None
            time.value = None
            date_text.value = "No date selected"
            page.update()

        page.controls.clear()
        page.add(
            ft.Column(
                [
                    ft.Text("Client Booking", size=24, weight="bold"),
                    name,
                    phone,
                    barber,
                    ft.ElevatedButton("Select Date", on_click=open_date),
                    date_text,
                    time,
                    ft.ElevatedButton("Book Appointment", on_click=book),
                    ft.TextButton("⬅ Back", on_click=lambda e: asyncio.create_task(show_home()))
                ],
                horizontal_alignment="center"
            )
        )
        page.update()

    # ---------- Barber Login ----------
    def show_barber_login(e=None):
        username = ft.TextField(label="Username", width=300)
        password = ft.TextField(label="Password", password=True, width=300)

        async def login(e):
            if username.value in BARBER_ACCOUNTS and BARBER_ACCOUNTS[username.value] == password.value:
                show_barber_dashboard(username.value)
            else:
                await show_message("❌ Error", "Wrong credentials", "red")

        page.controls.clear()
        page.add(
            ft.Column(
                [
                    ft.Text("Barber Login", size=24, weight="bold"),
                    username,
                    password,
                    ft.ElevatedButton("Login", on_click=login),
                    ft.TextButton("⬅ Back", on_click=lambda e: asyncio.create_task(show_home()))
                ],
                horizontal_alignment="center"
            )
        )
        page.update()

    # ---------- Barber Dashboard ----------
    def show_barber_dashboard(barber_name):
        page.controls.clear()
        appointments_column = ft.Column([], spacing=10)

        def build_appointments():
            appointments_column.controls.clear()
            count = 0
            for a in load_data():
                if a["barber"] == barber_name:
                    count += 1
                    def delete_appointment(e, appt=a):
                        d = load_data()
                        d.remove(appt)
                        save_data(d)
                        build_appointments()
                    appointments_column.controls.append(
                        ft.Card(
                            content=ft.Container(
                                padding=10,
                                content=ft.Column([
                                    ft.Text(f"{a['date']} - {a['time']}", weight="bold"),
                                    ft.Text(f"Client: {a['name']}"),
                                    ft.Text(f"Phone: {a['phone']}"),
                                    ft.Row([
                                        ft.IconButton(
                                            icon=ft.Icons.CALL,
                                            on_click=lambda e, p=a["phone"]: page.launch_url(f"tel:{p}")
                                        ),
                                        ft.IconButton(
                                            icon=ft.Icons.DELETE,
                                            icon_color="red",
                                            on_click=delete_appointment
                                        )
                                    ])
                                ])
                            )
                        )
                    )
            if count == 0:
                appointments_column.controls.append(ft.Text("No appointments yet"))
            page.update()

        async def auto_refresh():
            previous_count = len([a for a in load_data() if a["barber"] == barber_name])
            while True:
                await asyncio.sleep(5)
                current_count = len([a for a in load_data() if a["barber"] == barber_name])
                if current_count > previous_count:
                    page.snack_bar = ft.SnackBar(
                        ft.Text("🔔 New appointment received!"),
                        bgcolor="green"
                    )
                    page.snack_bar.open = True
                previous_count = current_count
                build_appointments()

        page.add(
            ft.Column([
                ft.Text(f"Welcome {barber_name}", size=24, weight="bold"),
                ft.Text("Your Appointments:", size=18),
                appointments_column,
                ft.TextButton("⬅ Logout", on_click=lambda e: asyncio.create_task(show_home()))
            ], horizontal_alignment="center")
        )

        build_appointments()
        asyncio.create_task(auto_refresh())

    await show_home()

ft.run(main)
