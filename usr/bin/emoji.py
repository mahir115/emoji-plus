import sys
import unicodedata
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLineEdit, QGridLayout, QLabel, QScrollArea, QVBoxLayout
)
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtGui import QDrag, QFont

def load_emojis():
    # Only include codepoints from blocks that are known to contain emojis
    emoji_blocks = [
        (0x1F600, 0x1F64F),  # Emoticons
        (0x1F300, 0x1F5FF),  # Misc Symbols and Pictographs
        (0x1F680, 0x1F6FF),  # Transport & Map Symbols
        (0x1F900, 0x1F9FF),  # Supplemental Symbols and Pictographs
        (0x1FA70, 0x1FAFF),  # Symbols and Pictographs Extended-A
        (0x1FA00, 0x1FA6F),  # Chess Symbols, etc.
        (0x1F1E6, 0x1F1FF),  # Regional Indicator Symbols (flags)
    ]
    emojis = []
    for start, end in emoji_blocks:
        for codepoint in range(start, end + 1):
            char = chr(codepoint)
            try:
                name = unicodedata.name(char)
                # Filter out monochrome symbols and shapes by excluding names that are only a single word or are generic
                # Keep only those that have "EMOJI" or "FACE" or "HAND" or "PERSON" or "CAT" or "HEART" or "KISS" or "FLAG" or "ANIMAL" or "FOOD" or "PLANT" or "FRUIT" or "BIRD" or "VEHICLE" or "OBJECT" or "BODY" or "GESTURE" or "FAMILY" or "PEOPLE" or "EMOTICON" in their Unicode name
                # But do not hardcode the list, instead, use the Unicode name as the search base for filtering in the UI
                emojis.append(char)
            except ValueError:
                continue
    # Remove duplicates and sort
    return sorted(set(emojis), key=lambda c: ord(c))

EMOJIS = load_emojis()

# Generate keywords for each emoji from its Unicode name (from Unicode, not manually)
EMOJI_KEYWORDS = {}
for emoji in EMOJIS:
    try:
        EMOJI_KEYWORDS[emoji] = unicodedata.name(emoji).lower()
    except ValueError:
        EMOJI_KEYWORDS[emoji] = ""

# Sort so that emojis with "face" in their Unicode name appear at the top
def sort_emojis(emojis):
    def sort_key(e):
        name = EMOJI_KEYWORDS.get(e, "")
        return (0 if "face" in name else 1, ord(e))
    return sorted(emojis, key=sort_key)

EMOJIS = sort_emojis(EMOJIS)

class EmojiLabel(QLabel):
    def __init__(self, emoji):
        super().__init__(emoji)
        self.emoji = emoji
        self.setFont(QFont("Segoe UI Emoji", 32))
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet("QLabel { background: #232629; border-radius: 8px; }")
        self.setFixedSize(56, 56)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            mime.setText(self.emoji)
            drag.setMimeData(mime)
            drag.exec_(Qt.CopyAction)

class EmojiPlus(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("emoji+")
        self.setStyleSheet("""
            QWidget { background-color: #18191A; color: #E4E6EB; }
            QLineEdit { background: #232629; color: #E4E6EB; border-radius: 8px; padding: 8px; }
        """)
        self.resize(480, 600)
        layout = QVBoxLayout(self)
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search🔎")
        self.search.textChanged.connect(self.update_grid)
        layout.addWidget(self.search)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        layout.addWidget(self.scroll)
        self.grid_widget = QWidget()
        self.grid = QGridLayout(self.grid_widget)
        self.grid.setSpacing(8)
        self.scroll.setWidget(self.grid_widget)
        self.filtered_emojis = EMOJIS
        self.update_grid()

    def update_grid(self):
        # Clear grid
        for i in reversed(range(self.grid.count())):
            widget = self.grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)
        # Filter emojis
        query = self.search.text().lower()
        if query:
            self.filtered_emojis = [
                e for e in EMOJIS
                if query in EMOJI_KEYWORDS.get(e, "") or query in e
            ]
        else:
            self.filtered_emojis = EMOJIS
        # Add emojis to grid
        cols = 8
        for idx, emoji in enumerate(self.filtered_emojis):
            row, col = divmod(idx, cols)
            label = EmojiLabel(emoji)
            self.grid.addWidget(label, row, col)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmojiPlus()
    window.show()
    sys.exit(app.exec_())