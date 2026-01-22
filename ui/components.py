import flet as ft
from flet import Icons, Colors
from ui.theme import ThemeColors, DesignSystem

def StyledTextField(label, hint, icon, on_change=None, suffix=None, on_submit=None, value=None, visible=True):
    return ft.TextField(
        label=label,
        hint_text=hint,
        value=value,
        visible=visible,
        border_radius=DesignSystem.BORDER_RADIUS,
        border_width= DesignSystem.BORDER_WIDTH,
        border_color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE30),
        focused_border_color=ThemeColors.PRIMARY,
        focused_border_width=2,
        prefix_icon=icon,
        suffix=suffix,
        text_size=14,
        content_padding=20,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        on_change=on_change,
        on_submit=on_submit,
        animate_size=300,
        error_style=ft.TextStyle(size=10),
        cursor_color=ThemeColors.PRIMARY,
        selection_color=ft.Colors.with_opacity(0.3, ThemeColors.PRIMARY),
    )

def PrimaryButton(text, icon, on_click, disabled=False):
    return ft.Container(
        content=ft.ElevatedButton(
            content=ft.Row(
                [ft.Icon(icon, size=20, color=Colors.WHITE), ft.Text(text, weight="bold", size=15, color=Colors.WHITE)],
                alignment=ft.MainAxisAlignment.CENTER,
                spacing=10
            ),
            style=ft.ButtonStyle(
                color=Colors.WHITE,
                bgcolor={"": Colors.TRANSPARENT},
                shadow_color=Colors.TRANSPARENT,
                shape=ft.RoundedRectangleBorder(radius=DesignSystem.BORDER_RADIUS),
            ),
            height=55,
            on_click=on_click,
            disabled=disabled
        ),
        gradient=DesignSystem.GRADIENT_PRIMARY if not disabled else None,
        bgcolor=Colors.GREY_800 if disabled else None,
        border_radius=DesignSystem.BORDER_RADIUS,
        shadow=DesignSystem.SHADOW_GLOW if not disabled else None,
        opacity=1.0 if not disabled else 0.5,
        animate_opacity=300,
        animate_scale=ft.Animation(300, ft.AnimationCurve.DECELERATE),
    )

def StatBadge(icon, label, value_ref):
    return ft.Container(
        content=ft.Row([
            ft.Icon(icon, size=18, color=ThemeColors.PRIMARY_LIGHT),
            ft.Column([
                ft.Text(label, size=9, color=ThemeColors.TEXT_DIM, weight="bold", text_align=ft.TextAlign.LEFT),
                value_ref,
            ], spacing=0, alignment=ft.MainAxisAlignment.CENTER)
        ], spacing=10),
        padding=ft.padding.symmetric(horizontal=15, vertical=10),
        border_radius=15,
        bgcolor=ft.Colors.with_opacity(0.05, ft.Colors.WHITE),
        border=ft.border.all(1, ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
        expand=True
    )

def QueueItem(idx, task, status, on_remove, on_move_up, on_move_down, total_items):
    url = task.url
    quality = task.options.get('quality', 'best')
    custom_name = task.options.get('filename')
    
    status_colors = {
        "waiting": Colors.GREY_500,
        "downloading": ThemeColors.PRIMARY,
        "done": Colors.GREEN_ACCENT,
        "finished": Colors.GREEN_ACCENT,
        "error": Colors.RED_400,
        "cancelled": Colors.ORANGE_400
    }
    
    status_icons = {
        "waiting": Icons.HOURGLASS_EMPTY_ROUNDED, 
        "downloading": Icons.SYNC_ROUNDED, 
        "done": Icons.CHECK_CIRCLE_ROUNDED,
        "finished": Icons.CHECK_CIRCLE_ROUNDED,
        "error": Icons.ERROR_OUTLINE_ROUNDED,
        "cancelled": Icons.CANCEL_OUTLINED
    }

    current_icon = status_icons.get(status, Icons.CIRCLE)
    current_color = status_colors.get(status, Colors.GREY)
    
    display_title = task.title if task.title else (custom_name if custom_name else url)
    is_active = status == "downloading"

    return ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Icon(current_icon, color=current_color, size=20),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.1, current_color)
                ),
                ft.Column([
                    ft.Text(display_title, size=13, weight="bold", max_lines=1, overflow="ellipsis", width=180),
                    ft.Text(f"{quality} | {url[:30]}...", size=10, color=ThemeColors.TEXT_DIM)
                ], spacing=2)
            ], spacing=12),
            
            ft.Row([
                ft.IconButton(Icons.ARROW_UPWARD_ROUNDED, icon_size=16, tooltip="Up", 
                    on_click=lambda _: on_move_up(idx), visible=(not is_active and idx > 0 and status == "waiting")),
                
                ft.IconButton(Icons.ARROW_DOWNWARD_ROUNDED, icon_size=16, tooltip="Down", 
                    on_click=lambda _: on_move_down(idx), visible=(not is_active and idx < total_items - 1 and status == "waiting")),
                
                ft.IconButton(
                    Icons.DELETE_OUTLINE_ROUNDED, 
                    icon_color=Colors.RED_400, 
                    icon_size=20,
                    tooltip="Remove",
                    on_click=lambda _: on_remove(idx),
                    visible=(not is_active)
                )
            ], spacing=0)
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=12,
        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
        border_radius=15,
        border=ft.border.all(1, ft.Colors.with_opacity(0.1, current_color) if is_active else ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
        animate=ft.Animation(300, ft.AnimationCurve.DECELERATE)
    )

def HistoryCard(item_data, on_open_folder, on_open_file, on_copy_link, on_delete):
    image_url = item_data.get('thumb')
    
    if image_url:
        visual_content = ft.Image(src=image_url, width=110, height=65, fit="cover", border_radius=12, error_content=ft.Container(bgcolor=Colors.BLACK))
    else:
        visual_content = ft.Container(width=110, height=65, border_radius=12, bgcolor=ft.Colors.with_opacity(0.1, ft.Colors.WHITE), alignment=ft.alignment.center, content=ft.Icon(Icons.MOVIE_CREATION_OUTLINED, color=ThemeColors.TEXT_DIM))

    return ft.Container(
        padding=12,
        border_radius=DesignSystem.BORDER_RADIUS,
        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
        border=ft.border.all(DesignSystem.BORDER_WIDTH, ft.Colors.with_opacity(0.05, ft.Colors.WHITE)),
        content=ft.Row([
            ft.Container(content=visual_content, shadow=ft.BoxShadow(blur_radius=15, color=ft.Colors.BLACK, spread_radius=-2)),
            ft.Column([
                ft.Text(item_data.get('title', 'Без названия'), size=13, weight="bold", max_lines=1, overflow="ellipsis"),
                ft.Text(item_data.get('author', 'Неизвестно'), size=11, color=ThemeColors.TEXT_DIM),
            ], expand=True, spacing=4),
            
            ft.PopupMenuButton(
                icon=Icons.MORE_VERT_ROUNDED,
                icon_color=ThemeColors.TEXT_DIM,
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
        animate=ft.Animation(300, ft.AnimationCurve.EASE_OUT_EXPO)
    )

def SettingTile(icon, title, control):
    return ft.Container(
        content=ft.Row([
            ft.Row([
                ft.Container(
                    content=ft.Icon(icon, color=ThemeColors.PRIMARY_LIGHT, size=20),
                    padding=10,
                    border_radius=10,
                    bgcolor=ft.Colors.with_opacity(0.1, ThemeColors.PRIMARY)
                ),
                ft.Text(title, size=14, weight="w500"),
            ], spacing=15),
            control
        ], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
        padding=ft.padding.all(12),
        bgcolor=ft.Colors.with_opacity(0.03, ft.Colors.WHITE),
        border_radius=15,
        border=ft.border.all(1, ft.Colors.with_opacity(0.05, ft.Colors.WHITE))
    )
