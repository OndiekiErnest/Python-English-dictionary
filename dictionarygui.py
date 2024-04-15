"""dictionary user interface"""

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QMenu,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QCompleter,
    QFileDialog,
)
from dictionary import Dictionary
from PyQt6.QtCore import Qt, QStringListModel, pyqtSignal, QSize
from PyQt6.QtGui import QIcon
from PyQt6.QtGui import QActionGroup, QAction
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, "data", "icons")


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


class MatchModes(QMenu):
    """custom QMenu: contains match mode actions and signals"""

    case_changed = pyqtSignal(Qt.CaseSensitivity)
    mode_changed = pyqtSignal(Qt.MatchFlag)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # action groups
        action_group = QActionGroup(self)
        action_group.setExclusive(True)
        case_group = QActionGroup(self)
        case_group.setExclusive(True)

        # match actions
        # starts with
        match_startswith = QAction("Startswith", self)
        match_startswith.setCheckable(True)
        match_startswith.triggered.connect(
            lambda: self.mode_changed.emit(Qt.MatchFlag.MatchStartsWith)
        )
        match_startswith.setChecked(True)
        # contains
        match_contains = QAction("Contains", self)
        match_contains.setCheckable(True)
        match_contains.triggered.connect(
            lambda: self.mode_changed.emit(Qt.MatchFlag.MatchContains)
        )
        # ends with
        match_endswith = QAction("Endswith", self)
        match_endswith.setCheckable(True)
        match_endswith.triggered.connect(
            lambda: self.mode_changed.emit(Qt.MatchFlag.MatchEndsWith)
        )
        # case sensitive
        match_case_sensitive = QAction("Case sensitive", self)
        match_case_sensitive.setCheckable(True)
        match_case_sensitive.triggered.connect(
            lambda: self.case_changed.emit(Qt.CaseSensitivity.CaseSensitive)
        )
        # case insensitive
        match_case_insensitive = QAction("Case insensitive", self)
        match_case_insensitive.setCheckable(True)
        match_case_insensitive.triggered.connect(
            lambda: self.case_changed.emit(Qt.CaseSensitivity.CaseInsensitive)
        )
        match_case_insensitive.setChecked(True)

        # add actions to action group
        self.addAction(action_group.addAction(match_startswith))
        self.addAction(action_group.addAction(match_contains))
        self.addAction(action_group.addAction(match_endswith))
        self.addSeparator()
        self.addAction(case_group.addAction(match_case_sensitive))
        self.addAction(case_group.addAction(match_case_insensitive))


class LargerIconBtn(QPushButton):
    """a QPushButton with a larger icon size"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setIconSize(QSize(20, 20))


class AppWindow(QWidget):
    """dictionary app window"""

    DEFAULT_FILE = os.path.join(BASE_DIR, "data", "default.json")
    WEBSTER_FILE = os.path.join(BASE_DIR, "data", "webster.json")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # set window attrs
        self.setWindowIcon(QIcon(os.path.join(ICONS_DIR, "icon.png")))
        self.setWindowTitle("Dict")
        self.setGeometry(0, 0, 350, 700)
        # window layout
        self.mainlayout = QVBoxLayout(self)
        # top layout
        toplayout = QHBoxLayout()
        toplayout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        toplayout.setContentsMargins(0, 0, 0, 0)
        toplayout.setSpacing(1)
        # search area layout
        search_layout = QHBoxLayout()
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(1)
        # variables
        self.added_files = {
            "Default Dictionary (English)": self.DEFAULT_FILE,
            "Webster Dictionary (English)": self.WEBSTER_FILE,
        }
        self.dictionary = Dictionary(self.DEFAULT_FILE)
        self.last_known_dir = os.path.expanduser(f"~{os.sep}Documents")
        self.search_modes_menu = MatchModes(self)
        # widgets
        # change JSON button
        self.filebtn = LargerIconBtn()
        self.filebtn.setMinimumHeight(35)
        self.filebtn.setIcon(QIcon(os.path.join(ICONS_DIR, "add.png")))
        self.filebtn.setToolTip("Add new dictionary JSON file")
        self.filebtn.clicked.connect(self.choose_json)
        # file chooser dropdown menu
        self.files_dropdown = QComboBox()
        self.files_dropdown.addItems(self.added_files.keys())
        self.files_dropdown.currentTextChanged.connect(self.change_json)
        # typing area
        self.edit = QLineEdit()
        self.edit.setMinimumHeight(50)
        self.edit.setPlaceholderText("Text to Search")
        self.edit.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.edit.returnPressed.connect(self.get_definition)
        # action
        search_action = QAction(self.edit)
        search_action.setIcon(QIcon(os.path.join(ICONS_DIR, "search.png")))
        search_action.setToolTip("Search")
        search_action.triggered.connect(self.get_definition)
        self.edit.addAction(search_action, QLineEdit.ActionPosition.TrailingPosition)
        # suggestion settings button
        self.suggestions_settings = LargerIconBtn()
        self.suggestions_settings.setIcon(QIcon(os.path.join(ICONS_DIR, "adjust.png")))
        self.suggestions_settings.setMinimumHeight(50)
        self.suggestions_settings.setToolTip("Adjust Suggestions")
        self.suggestions_settings.clicked.connect(self.suggestions_settings_clicked)
        # results area
        self.results = QLabel()
        self.results.setWordWrap(True)
        self.results.setMinimumHeight(100)
        self.results.linkActivated.connect(self.link_clicked)
        self.results.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
        )
        # make text selectable and links clickable
        self.results.setTextInteractionFlags(
            Qt.TextInteractionFlag.TextSelectableByMouse
            | Qt.TextInteractionFlag.LinksAccessibleByMouse
        )
        # text auto-completion
        self.autocompleter = QCompleter()
        self.autocompleter.setMaxVisibleItems(10)
        self.suggestion_model = SuggestionsModel(self.dictionary.words)
        self.autocompleter.setModel(self.suggestion_model)
        self.autocompleter.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.autocompleter.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        self.autocompleter.setFilterMode(Qt.MatchFlag.MatchStartsWith)
        self.autocompleter.popup().clicked.connect(self.get_definition)
        # bind signals
        self.search_modes_menu.case_changed.connect(self.change_casesensitivity)
        self.search_modes_menu.mode_changed.connect(self.change_filtermode)
        # set completer
        self.edit.setCompleter(self.autocompleter)
        # add widgets to layout
        toplayout.addWidget(self.filebtn)
        toplayout.addWidget(self.files_dropdown)
        search_layout.addWidget(self.suggestions_settings)
        search_layout.addWidget(self.edit)
        self.mainlayout.addLayout(toplayout)
        self.mainlayout.addLayout(search_layout)
        self.mainlayout.addWidget(self.results)

    def change_json(self, key: str):
        """switch a dict JSON file from the added files"""
        filename = self.added_files[key]
        self.dictionary.change_file(filename)
        # update the suggestions model data
        self.suggestion_model.setStringList(self.dictionary.words)

    def choose_json(self):
        """open file dialog to choose a dict JSON file"""
        filename = os.path.normpath(
            QFileDialog.getOpenFileName(
                self, "Select JSON file", self.last_known_dir, "JSON files (*.json)"
            )[0]
        )
        if filename and filename != ".":
            self.last_known_dir = os.path.dirname(filename)
            name, _ = os.path.splitext(os.path.basename(filename))
            # update record
            self.added_files[name] = filename
            self.files_dropdown.addItem(name)
            # make the chosen file the current text;
            # this will trigger change_json call
            self.files_dropdown.setCurrentText(name)

    def get_definition(self):
        word = self.edit.text()
        if word:
            # get definitions
            if definitions := self.dictionary.search(word):
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

    def read_for_user(self):
        """use tts to say the current word and its definition to the user"""
        # TODO
        to_say = f"{self.dictionary.current_word}: {self.dictionary.current_definition}"
        print(to_say)

    def change_filtermode(self, mode):
        """change completer filter mode"""
        self.autocompleter.setFilterMode(mode)

    def change_casesensitivity(self, case):
        """change completer case sensitivity"""
        self.autocompleter.setCaseSensitivity(case)

    def suggestions_settings_clicked(self):
        """create and open pop-up menu with different filter modes"""
        self.search_modes_menu.exec(self.mapToGlobal(self.suggestions_settings.pos()))

    def link_clicked(self, word: str):
        """
        handle clicked links;
        since href=word; set word to edit and get definition
        """
        self.edit.setText(word)
        self.get_definition()  # search word right away


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setStyleSheet("QWidget{font:20px; color:#2d2e2e; background: white}")
    app.setStyle("Fusion")

    window = AppWindow()
    window.show()

    sys.exit(app.exec())
