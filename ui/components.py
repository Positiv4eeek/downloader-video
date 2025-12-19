import flet as ft
from flet import Icons, Colors

def StyledTextField(label, hint, icon, on_change=None, suffix=None, on_submit=None):
    """
    Поле ввода с поддержкой суффикса (кнопки внутри) и валидации.
    """
    return ft.TextField(
        label=label,
        hint_text=hint,
        border_radius=15,
        border_width=1,
        border_color=Colors.BLUE_GREY_800,
        focused_border_color=Colors.BLUE_ACCENT,
        focused_border_width=2,
        prefix_icon=icon,
        suffix=suffix, # Добавили суффикс (для кнопки вставки)
        text_size=14,
        content_padding=20,
        bgcolor=Colors.with_opacity(0.05, Colors.BLACK),
        on_change=on_change,
        on_submit=on_submit,
        animate_size=300,
        # Настройки для валидации (изначально пустые)
        error_style=ft.TextStyle(size=10),
    )

def PrimaryButton(text, icon, on_click, disabled=False):
    """Кнопка с градиентным фоном и поддержкой состояния disabled"""
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
            disabled=disabled
        ),
        gradient=ft.LinearGradient(
            begin=ft.alignment.top_left,
            end=ft.alignment.bottom_right,
            colors=[Colors.BLUE_700, Colors.BLUE_900] if not disabled else [Colors.GREY_700, Colors.GREY_800],
        ),
        border_radius=12,
        shadow=ft.BoxShadow(blur_radius=15, color=Colors.with_opacity(0.3, Colors.BLUE_900)) if not disabled else None,
        opacity=1.0 if not disabled else 0.5,
        animate_opacity=300
    )

def StatBadge(icon, label, value_ref):
    """Карточка статистики (без изменений)"""
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=18, color=Colors.BLUE_ACCENT),
            ft.Column([
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
    """Карточка истории с защитой от пустых картинок"""
    
    # Проверяем, есть ли ссылка на картинку
    if image_url:
        # Если есть - показываем картинку
        visual_content = ft.Image(
            src=image_url, 
            width=100, 
            height=60, 
            fit="cover", 
            border_radius=8,
            error_content=ft.Container(bgcolor=Colors.GREY_900) # Если ссылка битая
        )
    else:
        # Если ссылки нет (пустая строка) - показываем заглушку с иконкой
        visual_content = ft.Container(
            width=100, 
            height=60, 
            border_radius=8, 
            bgcolor=Colors.with_opacity(0.1, Colors.WHITE),
            alignment=ft.alignment.center,
            content=ft.Icon(Icons.MOVIE_CREATION_OUTLINED, color=Colors.BLUE_GREY_400)
        )

    return ft.Container(
        padding=12,
        border_radius=15,
        bgcolor=Colors.with_opacity(0.03, Colors.WHITE),
        border=ft.border.all(1, Colors.BLUE_GREY_900),
        content=ft.Row([
            ft.Container(
                content=visual_content,
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

def SettingTile(icon, title, control):
    """Новый компонент: строка настройки"""
    return ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Icon(icon, color=Colors.BLUE_GREY_400),
                ft.Text(title, size=14, weight="w500"),
            ], spacing=15),
            control
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=15,
        bgcolor=Colors.with_opacity(0.03, Colors.WHITE),
        border_radius=12
    )