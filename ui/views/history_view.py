import flet as ft
from flet import Colors, Icons
from ui.components import HistoryCard
from core.utils import open_path

class HistoryView(ft.Column):
    def __init__(self, page: ft.Page, app_state):
        super().__init__()
        self.page = page
        self.app_state = app_state
        self.visible = False
        self.expand = True
        
        self.history_list = ft.ListView(expand=True, spacing=12)
        self.controls = [
            ft.Text("Недавние", size=18, weight="bold"),
            self.history_list
        ]

    def refresh(self):
        self.history_list.controls.clear()
        if not self.app_state.history:
            self.history_list.controls.append(ft.Text("История пуста", text_align="center", color=Colors.GREY))
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