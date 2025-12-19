import flet as ft
from flet import Icons, Colors

def StyledTextField(label, hint, icon):
    return ft.TextField(
        label=label,
        hint_text=hint,
        border_radius=15,
        border_color=Colors.BLUE_GREY_700,
        focused_border_color=Colors.BLUE_ACCENT,
        prefix_icon=icon,
        text_size=14,
    )

def PrimaryButton(text, icon, on_click):
    return ft.ElevatedButton(
        content=ft.Row(
            [ft.Icon(icon), ft.Text(text, weight="bold")],
            alignment=ft.MainAxisAlignment.CENTER,
            spacing=10
        ),
        style=ft.ButtonStyle(
            color=Colors.WHITE,
            bgcolor=Colors.BLUE_700,
            shape=ft.RoundedRectangleBorder(radius=12),
        ),
        height=50,
        on_click=on_click
    )