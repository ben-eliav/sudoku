from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget,
    QLineEdit, QLabel, QGridLayout, QPushButton, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QKeyEvent



class ClickableLabel(QLabel):
    clicked = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setAlignment(Qt.AlignCenter)
        self.setFixedSize(40, 40)
        self.setStyleSheet("border: 1px solid black; font-size: 18px;")
        self.setFont(QFont("Arial", 16))
        self.setAttribute(Qt.WA_StyledBackground, True)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


class SudokuWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sudoku Grid")
        self.setGeometry(100, 100, 400, 600)
        self.setWindowFlags(Qt.FramelessWindowHint)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        self.central_widget.setLayout(self.layout)

        self.title_bar = QWidget(self)
        self.title_bar.setFixedSize(360, 50)

        self.close_button = QPushButton('X', self)
        self.close_button.setStyleSheet(
            "border: 1px solid black; border-radius: 5px; background-color: red; color: white;"
        )
        self.close_button.setCursor(Qt.PointingHandCursor)
        self.close_button.setFixedSize(30, 30)

        self.close_button.setStyleSheet("""
            QPushButton {
                border: 1px solid black;
                border-radius: 5px;
                background-color: red;
                color: white;
            }
            QPushButton:hover {
                background-color: #cc0000;
            }
            QPushButton:pressed {
                background-color: #990000;
            }
        """)

        self.close_button.pressed.connect(lambda : self.close_clicked(self.close_button.pos()))
        self.close_button.clicked.connect(self.close)

        title_layout = QHBoxLayout(self.title_bar)
        title_layout.setContentsMargins(5, 5, 5, 5)
        title_layout.setSpacing(0)
        title_layout.addStretch(1)
        title_layout.addWidget(self.close_button)
        self.layout.addWidget(self.title_bar)

        # Sudoku grid layout
        self.grid_widget = QWidget()
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_widget.setLayout(self.grid_layout)
        self.layout.addWidget(self.grid_widget)

        self.cells = []
        self.selected_cell = None

        self.create_sudoku_grid()
        self.grid_widget.setFixedSize(360, 360)
        self.grid_widget.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def create_sudoku_grid(self):
        """Create a 9x9 grid of clickable labels."""
        for row in range(9):
            row_cells = []
            for col in range(9):
                label = ClickableLabel()
                label.clicked.connect(lambda r=row, c=col: self.cell_clicked(r, c))
                self.grid_layout.addWidget(label, row, col)
                row_cells.append(label)
                top = 2 if row % 3 == 0 else 1
                left = 2 if col % 3 == 0 else 1
                right = 2 if col == 8 else 0
                bottom = 2 if row == 8 else 0
                label.original_style = f"""
                    QLabel {{
                        border-top: {top}px solid black;
                        border-left: {left}px solid black;
                        border-right: {right}px solid black;
                        border-bottom: {bottom}px solid black;
                    }}
                """
                label.setStyleSheet(label.original_style)
            self.cells.append(row_cells)

    def cell_clicked(self, row, col):
        """Handle cell selection and highlight it."""
        if self.selected_cell:
            self.selected_cell.setStyleSheet(self.selected_cell.original_style)
        self.selected_cell = self.cells[row][col]
        self.selected_cell.setStyleSheet(self.selected_cell.original_style.replace("QLabel {", "QLabel {\nbackground=color: #000000;"))
        print(f"Cell clicked: ({row}, {col}), style: {self.selected_cell.styleSheet()}")

    def keyPressEvent(self, event: QKeyEvent):
        """Handle number input for selected cell."""
        if not self.selected_cell:
            return
        key = event.text()
        if key in "123456789":
            self.selected_cell.setText(key)
        if event.key() == Qt.Key_Backspace:  # Backspace
            self.selected_cell.setText("")

    def close_clicked(self, pos):
        self.drag_start_pos = pos

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_start_pos = event.globalPos()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton and self.title_bar.geometry().contains(event.pos()):
            delta = event.globalPos() - self.drag_start_pos
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.drag_start_pos = event.globalPos()


if __name__ == "__main__":
    app = QApplication([])
    window = SudokuWindow()
    window.show()
    app.exec()
