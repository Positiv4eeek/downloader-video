import flet as ft
from flet import Icons, Colors

def StyledTextField(label, hint, icon):
    """Стилизованное текстовое поле для ввода URL"""
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
    """Основная кнопка действия с иконкой и закругленными углами"""
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
        height=55,
        on_click=on_click
    )

def StatBadge(icon, label, value_ref):
    """Новый компонент: карточка статистики для отображения скорости, времени и размера файла"""
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=14, color=Colors.BLUE_ACCENT),
            ft.Column([
                ft.Text(label, size=10, color=Colors.BLUE_GREY_400, weight="bold"),
                value_ref, # Ссылка на текстовый объект для динамического обновления
            ], spacing=0)
        ], spacing=8),
        padding=10,
        border_radius=10,
        bgcolor=Colors.with_opacity(0.1, Colors.BLUE_GREY_900),
        expand=True
    )