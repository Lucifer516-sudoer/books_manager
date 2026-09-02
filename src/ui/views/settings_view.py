import flet as ft

from ui.config import settings

"""
IN the settings  view, I want the user to be able to set the location of the Books to be in ...
"""


@ft.control
class SetingsView(ft.Column):
    def init(self):
        #
        # Tuning
        #
        self.alignment = ft.MainAxisAlignment.START
        self.horizontal_alignment = ft.CrossAxisAlignment.STRETCH
        self.expand = True

        #
        # Components
        #
        self.books_location = ft.TextField(
            value=str(settings.books_folder),
            hint_text="~/home/noah/Books/",
        )
        self.books_view = ft.Row(
            controls=[ft.Text("Books Location: "), self.books_location],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self.controls = [
            ft.Container(
                content=self.books_view,
                padding=15,
            )
        ]
