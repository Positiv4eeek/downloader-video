import flet as ft
from flet import Icons, Colors

def StyledTextField(label, hint, icon, on_change=None, suffix=None, on_submit=None, value=None, visible=True):
    return ft.TextField(
        label=label,
        hint_text=hint,
        value=value,
        visible=visible,
        border_radius=15,
        border_width=1,
        border_color=Colors.BLUE_GREY_800,
        focused_border_color=Colors.BLUE_ACCENT,
        focused_border_width=2,
        prefix_icon=icon,
        suffix=suffix,
        text_size=14,
        content_padding=20,
        bgcolor=Colors.with_opacity(0.05, Colors.BLACK),
        on_change=on_change,
        on_submit=on_submit,
        animate_size=300,
        error_style=ft.TextStyle(size=10),
    )

def PrimaryButton(text, icon, on_click, disabled=False):
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

def QueueItem(idx, item_data, status, on_remove, on_move_up, on_move_down, total_items):
    url = item_data['url']
    quality = item_data['quality']
    custom_name = item_data.get('filename')
    
    status_colors = {
        "waiting": Colors.GREY_500,
        "downloading": Colors.BLUE_ACCENT,
        "done": Colors.GREEN,
    }
    
    status_icons = {
        "waiting": Icons.HOURGLASS_EMPTY_ROUNDED, 
        "downloading": Icons.DOWNLOADING, 
        "done": Icons.CHECK_CIRCLE_ROUNDED,
    }

    current_icon = status_icons.get(status, Icons.CIRCLE)
    current_color = status_colors.get(status, Colors.GREY)
    
    # Отображаем кастомное имя, если есть, иначе URL
    display_title = custom_name if custom_name else url
    is_active = status == "downloading"

    return ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Icon(current_icon, color=current_color),
                ft.Column([
                    ft.Text(display_title, size=12, weight="bold", max_lines=1, overflow="ellipsis", width=180),
                    ft.Text(f"{quality} | {url[:30]}...", size=10, color=Colors.GREY_500)
                ], spacing=2)
            ]),
            
            ft.Row([
                # Кнопка ВВЕРХ (скрыта для первого элемента и активной загрузки)
                ft.IconButton(Icons.ARROW_UPWARD_ROUNDED, icon_size=16, tooltip="Up", 
                    on_click=lambda _: on_move_up(idx), visible=(not is_active and idx > 0 and status == "waiting")),
                
                # Кнопка ВНИЗ (скрыта для последнего элемента и активной загрузки)
                ft.IconButton(Icons.ARROW_DOWNWARD_ROUNDED, icon_size=16, tooltip="Down", 
                    on_click=lambda _: on_move_down(idx), visible=(not is_active and idx < total_items - 1 and status == "waiting")),
                
                ft.IconButton(
                    Icons.CLOSE_ROUNDED, 
                    icon_color=Colors.RED_400, 
                    icon_size=20,
                    tooltip="Remove",
                    on_click=lambda _: on_remove(idx),
                    visible=(not is_active)
                )
            ], spacing=0)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=10,
        bgcolor=Colors.with_opacity(0.05, Colors.WHITE),
        border_radius=10,
        border=ft.border.all(1, current_color if is_active else Colors.TRANSPARENT)
    )

def HistoryCard(item_data, on_open_folder, on_open_file, on_copy_link, on_delete):
    image_url = item_data.get('thumb')
    
    if image_url:
        visual_content = ft.Image(src=image_url, width=100, height=60, fit="cover", border_radius=8, error_content=ft.Container(bgcolor=Colors.GREY_900))
    else:
        visual_content = ft.Container(width=100, height=60, border_radius=8, bgcolor=Colors.with_opacity(0.1, Colors.WHITE), alignment=ft.alignment.center, content=ft.Icon(Icons.MOVIE_CREATION_OUTLINED, color=Colors.BLUE_GREY_400))

    return ft.Container(
        padding=12,
        border_radius=15,
        bgcolor=Colors.with_opacity(0.03, Colors.WHITE),
        border=ft.border.all(1, Colors.BLUE_GREY_900),
        content=ft.Row([
            ft.Container(content=visual_content, shadow=ft.BoxShadow(blur_radius=10, color=Colors.BLACK)),
            ft.Column([
                ft.Text(item_data.get('title', 'Без названия'), size=13, weight="bold", max_lines=1, overflow="ellipsis"),
                ft.Text(item_data.get('author', 'Неизвестно'), size=11, color=Colors.BLUE_GREY_400),
            ], expand=True, spacing=4),
            
            ft.PopupMenuButton(
                icon=Icons.MORE_VERT_ROUNDED,
                icon_color=Colors.GREY_400,
                tooltip="Действия",
                items=[
                    ft.PopupMenuItem(text="Открыть файл", icon=Icons.PLAY_ARROW_ROUNDED, on_click=lambda _: on_open_file(item_data.get('file_path'))),
                    ft.PopupMenuItem(text="Открыть папку", icon=Icons.FOLDER_OPEN_ROUNDED, on_click=lambda _: on_open_folder(item_data.get('path'))),
                    ft.PopupMenuItem(text="Копировать ссылку", icon=Icons.COPY_ROUNDED, on_click=lambda _: on_copy_link(item_data.get('url'))),
                    ft.PopupMenuItem(), 
                    ft.PopupMenuItem(text="Удалить запись", icon=Icons.DELETE_OUTLINE_ROUNDED, content=ft.Text("Удалить запись", color=Colors.RED_400), on_click=lambda _: on_delete(item_data)),
                ]
            )
        ]),
        animate=ft.Animation(300, ft.AnimationCurve.DECELERATE)
    )

def SettingTile(icon, title, control):
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