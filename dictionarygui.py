"""dictionary user interface"""

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QCompleter,
    QFileDialog,
)
from dictionary import Dictionary
from PyQt6.QtCore import Qt, QStringListModel
from PyQt6.QtGui import QIcon
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))


class SuggestionsModel(QStringListModel):
    """
    A class representing a model for word suggestions.
    Inherits from the built-in QStringListModel class.
    """

    def data(self, index, role):
        """
        Returns the data associated with the given index and role.

        :param index: A QModelIndex object representing the index of the item to retrieve.
        :param role: A Qt.ItemDataRole representing the role to retrieve.
        :return: The data associated with the given index and role.

        The method specific implementation overrides the default implementation of the data function provided
        by QStringListModel class, to allow for the return of a specific Qt.ItemDataRole for the role parameter.

        When the role is Qt.ItemDataRole.TextAlignmentRole, the method returns the AlignmentFlag.AlignCenter.
        This ensures that the suggestions are displayed centered align in the user interface.
        """
        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter  # center suggestions

        return super().data(index, role)


class AppWindow(QWidget):
    """dictionary app window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set window attrs
        self.setWindowIcon(QIcon(os.path.join(BASE_DIR, "data", "icon.png")))
        self.setWindowTitle("Dict")
        self.setGeometry(0, 0, 350, 700)
        # window layout
        self.mainlayout = QVBoxLayout(self)
        # top layout
        toplayout = QHBoxLayout()
        toplayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        # variables
        self.dictionary = Dictionary(os.path.join(BASE_DIR, "data", "data.json"))
        self.last_known_dir = os.path.expanduser(f"~{os.sep}Documents")
        # widgets
        # change JSON button
        self.filebtn = QPushButton("+Dictionary")
        self.filebtn.setFixedWidth(115)
        self.filebtn.setToolTip("Select new dictionary JSON file")
        self.filebtn.clicked.connect(self.change_json)
        # typing area
        self.edit = QLineEdit()
        self.edit.setMinimumHeight(50)
        self.edit.setPlaceholderText("Text to Search")
        self.edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.edit.returnPressed.connect(self.get_definition)
        # results area
        self.results = QLabel()
        self.results.setWordWrap(True)
        self.results.setMinimumHeight(100)
        self.results.linkActivated.connect(self.link_clicked)
        self.results.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        # make text selectable and links clickable
        self.results.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        # text auto-completion
        self.autocompleter = QCompleter()
        suggestion_model = SuggestionsModel(self.dictionary.words)
        self.autocompleter.setModel(suggestion_model)
        # self.autocompleter.setFilterMode(Qt.MatchFlag.MatchContains)  # slow
        self.autocompleter.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.autocompleter.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        # set completer
        self.edit.setCompleter(self.autocompleter)
        # add widgets to layout
        toplayout.addWidget(self.filebtn)
        self.mainlayout.addLayout(toplayout)
        self.mainlayout.addWidget(self.edit)
        self.mainlayout.addWidget(self.results)

    def change_json(self):
        """open a file dialog to change dict JSON"""
        filename = os.path.normpath(
            QFileDialog.getOpenFileName(
                self, "Select JSON file", self.last_known_dir, "JSON files (*.json)"
            )[0]
        )
        if filename and filename != ".":
            self.last_known_dir = os.path.dirname(filename)
            self.dictionary.change_file(filename)

    def get_definition(self):
        word = self.edit.text()
        if word:
            # get definitions
            if definitions := self.dictionary.search(word):
                if isinstance(definitions, list):
                    definitions = "\n".join((line for line in definitions))
                self.results.setText(definitions)
            # if definitions is None
            else:
                # get suggestions
                if suggestions := self.dictionary.suggest(word, n=5):
                    suggested = " ".join(
                        (f'<a href="{w}">{w}</a>' for w in suggestions)
                    )
                    self.results.setText(f"Did you mean: {suggested}")
                # if suggestions is an empty list
                else:
                    self.results.setText("<i>No matching words</i>")

    def link_clicked(self, word: str):
        """
        handle clicked links;
        since href=word; set word to edit and get definition
        """
        self.edit.setText(word)
        # self.get_definition()  # search word right away


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setStyleSheet("QWidget{font:20px; color:#2d2e2e; background: white}")
    app.setStyle("Fusion")

    window = AppWindow()
    window.show()

    sys.exit(app.exec())
