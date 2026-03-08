import flet as ft
import re
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime

# ---------------- FIREBASE ----------------
cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

BARBERS = {
    "khireeddine": "1234567891011",
    "oussama": "1234567",
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

# ---------------- FUNCTIONS ----------------
def load_data():
    docs = db.collection("appointments").stream()
    data = []
    for doc in docs:
        d = doc.to_dict()
        d["id"] = doc.id
        data.append(d)
    return data

def save_appointment(data_dict):
    doc_ref = db.collection("appointments").document()
    doc_ref.set(data_dict)
    return doc_ref.id

def update_status_safe(doc_id, status):
    try:
        db.collection("appointments").document(doc_id).update({"status": status})
        print(f"Updated {doc_id} -> {status}")
    except Exception as e:
        print(f"Failed to update {doc_id}: {e}")

def delete_appointment_safe(doc_id):
    try:
        db.collection("appointments").document(doc_id).delete()
        print(f"Deleted {doc_id}")
    except Exception as e:
        print(f"Failed to delete {doc_id}: {e}")

# ---------------- MAIN APP ----------------
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

    # ---------------- HOME ----------------
    def home(e=None):
        page.controls.clear()
        page.add(
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    [
                        ft.Text("ELITE BARBER", size=28, weight="bold"),
                        ft.Text("Premium Booking Experience"),
                        ft.Divider(),
                        ft.FilledButton("💈 Barber Login", width=250, on_click=barber_login),
                        ft.OutlinedButton("🧑 Book Appointment", width=250, on_click=client_page),
                        ft.OutlinedButton("📄 My Appointments", width=250, on_click=my_appointments),
                        ft.IconButton(icon=ft.Icons.DARK_MODE, on_click=toggle_theme, tooltip="Toggle Dark/Light Mode")
                    ],
                    spacing=15,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            )
        )
        page.update()

    def toggle_theme(e):
        page.theme_mode = ft.ThemeMode.DARK if page.theme_mode==ft.ThemeMode.LIGHT else ft.ThemeMode.LIGHT
        page.update()

    # ---------------- CLIENT PAGE ----------------
    def client_page(e=None):
        name = ft.TextField(label="Full Name", width=250)
        phone = ft.TextField(label="Phone", value="+213", width=250)
        phone.on_change = lambda e: setattr(phone, "value", "+213") if not phone.value.startswith("+213") else None

        barber_dropdown = ft.Dropdown(
            label="Choose Barber",
            width=250,
            options=[ft.dropdown.Option(b) for b in BARBERS]
        )

        time_dropdown = ft.Dropdown(
            label="Choose Time",
            width=250,
            options=[ft.dropdown.Option(t) for t in TIME_SLOTS]
        )

        selected_date = ft.Text("Select Date")
        date_picker = ft.DatePicker(on_change=lambda e: setattr(selected_date, "value", e.control.value.strftime("%Y-%m-%d")))
        page.overlay.append(date_picker)

        def book(e):
            if not name.value.strip() or not phone.value.strip() or not barber_dropdown.value or not time_dropdown.value or selected_date.value=="Select Date":
                snack("يرجى ملء جميع الحقول", ft.Colors.RED)
                return
            if not re.fullmatch(r"\+213\d{9}", phone.value.strip()):
                snack("الرقم غير صالح، يجب إدخال 9 أرقام بعد +213", ft.Colors.RED)
                return
            # تحقق من الحجز المكرر
            for a in load_data():
                if a["barber"]==barber_dropdown.value and a["date"]==selected_date.value and a["time"]==time_dropdown.value:
                    snack("هذا الوقت محجوز مسبقًا", ft.Colors.RED)
                    return
            save_appointment({
                "name": name.value.strip(),
                "phone": phone.value.strip(),
                "barber": barber_dropdown.value,
                "date": selected_date.value,
                "time": time_dropdown.value,
                "status": "pending"
            })
            snack("تم إرسال طلب الحجز 🎉")
            home()

        page.controls.clear()
        page.add(
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    [
                        ft.Text("Book Appointment", size=24, weight="bold"),
                        name, phone, barber_dropdown,
                        ft.FilledButton("Select Date", on_click=lambda e: setattr(date_picker, "open", True)),
                        selected_date, time_dropdown,
                        ft.FilledButton("Confirm Booking", on_click=book),
                        ft.TextButton("Back", on_click=home)
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            )
        )
        page.update()

    # ---------------- BARBER LOGIN ----------------
    def barber_login(e=None):
        user = ft.TextField(label="Username", width=250)
        pwd = ft.TextField(label="Password", password=True, width=250)

        def login(e):
            if user.value.lower() in BARBERS and BARBERS[user.value.lower()]==pwd.value:
                barber_dashboard(user.value)
            else:
                snack("Wrong credentials", ft.Colors.RED)

        page.controls.clear()
        page.add(
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    [
                        ft.Text("Barber Login", size=24, weight="bold"),
                        user, pwd,
                        ft.FilledButton("Login", on_click=login),
                        ft.TextButton("Back", on_click=home)
                    ],
                    spacing=10,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    alignment=ft.MainAxisAlignment.CENTER
                )
            )
        )
        page.update()

    # ---------------- BARBER DASHBOARD ----------------
    def barber_dashboard(barber_name):
        appointments_list = ft.ListView(expand=True, spacing=5, padding=10, auto_scroll=True)

        def refresh():
            appointments_list.controls.clear()
            data = [a for a in load_data() if a["barber"]==barber_name]
            for a in data:
                status_color = ft.Colors.ORANGE
                if a["status"]=="accepted": status_color=ft.Colors.GREEN
                if a["status"]=="rejected": status_color=ft.Colors.RED

                # دوال لكل زر مع doc_id الصحيح
                def make_status_button(doc_id, new_status):
                    return ft.IconButton(
                        ft.Icons.CHECK if new_status=="accepted" else ft.Icons.CLOSE,
                        icon_color=ft.Colors.GREEN if new_status=="accepted" else ft.Colors.RED,
                        on_click=lambda e: [update_status_safe(doc_id, new_status), refresh()]
                    )

                def make_delete_button(doc_id):
                    return ft.IconButton(
                        ft.Icons.DELETE,
                        icon_color=ft.Colors.RED,
                        on_click=lambda e: [delete_appointment_safe(doc_id), refresh()]
                    )

                appointments_list.controls.append(
                    ft.Card(
                        content=ft.Container(
                            padding=10,
                            alignment=ft.Alignment.CENTER,
                            content=ft.Column(
                                [
                                    ft.Text(f"{a['date']} {a['time']}", weight="bold"),
                                    ft.Text(a["name"]),
                                    ft.Text(a["phone"]),
                                    ft.Text(f"Status: {a['status']}", color=status_color),
                                    ft.Row(
                                        [
                                            make_status_button(a["id"], "accepted"),
                                            make_status_button(a["id"], "rejected"),
                                            make_delete_button(a["id"])
                                        ],
                                        alignment=ft.MainAxisAlignment.CENTER
                                    )
                                ],
                                alignment=ft.MainAxisAlignment.CENTER,
                                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                spacing=5
                            )
                        )
                    )
                )
            page.update()

        page.controls.clear()
        page.add(
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    [
                        appointments_list,
                        ft.IconButton(ft.Icons.LOGOUT, icon_color=ft.Colors.RED, on_click=home)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER
                )
            )
        )
        refresh()

    # ---------------- CLIENT VIEW ----------------
    def my_appointments(e=None):
        phone = ft.TextField(label="Phone (+213)", value="+213", width=150)
        phone.on_change = lambda e: setattr(phone, "value", "+213") if not phone.value.startswith("+213") else None

        list_view = ft.ListView(expand=True, spacing=5, padding=10)

        def search(e):
            list_view.controls.clear()
            data = load_data()
            found = False
            for a in data:
                if a["phone"]==phone.value.strip():
                    found = True
                    status_color = ft.Colors.ORANGE
                    if a["status"]=="accepted": status_color=ft.Colors.GREEN
                    if a["status"]=="rejected": status_color=ft.Colors.RED
                    list_view.controls.append(
                        ft.Card(
                            content=ft.Container(
                                padding=10,
                                alignment=ft.Alignment.CENTER,
                                content=ft.Column(
                                    [
                                        ft.Text(a["barber"], weight="bold"),
                                        ft.Text(f"{a['date']} {a['time']}"),
                                        ft.Text(f"Status: {a['status']}", color=status_color)
                                    ],
                                    alignment=ft.MainAxisAlignment.CENTER,
                                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                                    spacing=5
                                )
                            )
                        )
                    )
            if not found:
                snack("لا توجد مواعيد بهذا الرقم", ft.Colors.RED)
            page.update()

        page.controls.clear()
        page.add(
            ft.Container(
                expand=True,
                alignment=ft.Alignment.CENTER,
                content=ft.Column(
                    [
                        phone,
                        ft.FilledButton("Show my appointments", on_click=search),
                        list_view,
                        ft.TextButton("Back", on_click=home)
                    ],
                    alignment=ft.MainAxisAlignment.CENTER,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    spacing=10
                )
            )
        )
        page.update()

    home()

ft.run(main)
