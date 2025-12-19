import flet as ft
from flet import Icons, Colors

def StyledTextField(label, hint, icon, on_change=None):
    """Поле ввода с эффектом глубины"""
    return ft.TextField(
        label=label,
        hint_text=hint,
        border_radius=15,
        border_width=1,
        border_color=Colors.BLUE_GREY_800,
        focused_border_color=Colors.BLUE_ACCENT,
        focused_border_width=2,
        prefix_icon=icon,
        text_size=14,
        content_padding=20,
        bgcolor=Colors.with_opacity(0.05, Colors.BLACK),
        on_change=on_change,
        animate_size=300
    )

def PrimaryButton(text, icon, on_click):
    """Кнопка с градиентным фоном"""
    return ft.Container(
        content=ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(icon, size=20), ft.Text(text, weight="bold", size=15)],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            style=ft.ButtonStyle(
                color=Colors.WHITE,
                bgcolor={"": Colors.TRANSPARENT},
                shadow_color=Colors.TRANSPARENT,
                shape=ft.RoundedRectangleBorder(radius=12),
            ),
            height=55,
            on_click=on_click,
        ),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[Colors.BLUE_700, Colors.BLUE_900],
        ),
        border_radius=12,
        shadow=ft.BoxShadow(blur_radius=15, color=Colors.with_opacity(0.3, Colors.BLUE_900)),
    )

def StatBadge(icon, label, value_ref):
    """Карточка статистики с легким блюром"""
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=18, color=Colors.BLUE_ACCENT),
            ft.Column([
                # УДАЛЕНО: letter_spacing=1
                ft.Text(label, size=9, color=Colors.BLUE_GREY_400, weight="bold"),
                value_ref,
            ], spacing=0)
        ], spacing=10),
        padding=12,
        border_radius=15,
        bgcolor=Colors.with_opacity(0.05, Colors.WHITE),
        border=ft.border.all(1, Colors.with_opacity(0.1, Colors.WHITE)),
        expand=True
    )

def HistoryCard(title, author, image_url, path, on_open_folder):
    """Современная карточка истории с эффектом наведения"""
    return ft.Container(
        padding=12,
        border_radius=15,
        bgcolor=Colors.with_opacity(0.03, Colors.WHITE),
        border=ft.border.all(1, Colors.BLUE_GREY_900),
        content=ft.Row([
            ft.Container(
                content=ft.Image(src=image_url, width=100, height=60, fit="cover", border_radius=8),
                shadow=ft.BoxShadow(blur_radius=10, color=Colors.BLACK),
            ),
            ft.Column([
                ft.Text(title, size=13, weight="bold", max_lines=1, overflow="ellipsis"),
                ft.Text(author, size=11, color=Colors.BLUE_GREY_400),
            ], expand=True, spacing=4),
            ft.IconButton(
                icon=Icons.FOLDER_OPEN_ROUNDED,
                icon_color=Colors.BLUE_GREY_400,
                hover_color=Colors.with_opacity(0.1, Colors.BLUE_ACCENT),
                on_click=lambda _: on_open_folder(path)
            )
        ]),
        animate=ft.Animation(300, ft.AnimationCurve.DECELERATE)
    )