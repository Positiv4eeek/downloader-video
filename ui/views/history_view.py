import flet as ft
from flet import Icons
from ui.theme import ThemeColors, DesignSystem
from ui.components import HistoryCard
from core.utils import open_path

class HistoryView(ft.Column):
    def __init__(self, page: ft.Page, app_state):
        super().__init__(expand=True, spacing=15)
        self.page = page
        self.app_state = app_state
        self.visible = False
        
        self.history_list = ft.ListView(expand=True, spacing=12)
        self.controls = [
            ft.Container(
                content=ft.Row([
                    ft.Icon(Icons.HISTORY_ROUNDED, color=ThemeColors.PRIMARY, size=24),
                    ft.Text("Недавние", size=20, weight="bold", color=ThemeColors.TEXT_MAIN),
                ], spacing=10),
                padding=ft.padding.only(bottom=5)
            ),
            self.history_list
        ]

    def refresh(self):
        self.history_list.controls.clear()
        if not self.app_state.history:
            self.history_list.controls.append(
                ft.Container(
                    content=ft.Column([
                        ft.Icon(Icons.HISTORY_TOGGLE_OFF_ROUNDED, size=50, color=ft.Colors.with_opacity(0.1, ft.Colors.WHITE)),
                        ft.Text("История пуста", text_align="center", color=ThemeColors.TEXT_DIM, size=14),
                    ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER),
                    expand=True,
                    alignment=ft.alignment.center
                )
            )
        else:
            for item in reversed(self.app_state.history):
                self.history_list.controls.append(HistoryCard(
                    item,
                    on_open_folder=lambda p: open_path(p, False),
                    on_open_file=lambda p: open_path(p, True),
                    on_copy_link=self.copy_link,
                    on_delete=self.delete_item
                ))
        self.update()

    def delete_item(self, item):
        self.app_state.remove_history_item(item)
        self.refresh()

    def copy_link(self, url):
        self.page.set_clipboard(url)
        self.page.snack_bar = ft.SnackBar(ft.Text("Ссылка скопирована"))
        self.page.snack_bar.open = True
        self.page.update()