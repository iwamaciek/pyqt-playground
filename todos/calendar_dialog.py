from PyQt5.QtWidgets import QDialog, QCalendarWidget, QPushButton, QVBoxLayout, QHBoxLayout

class CalendarDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Due Date")
        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.setSelectionMode(QCalendarWidget.SingleSelection)
        self.confirm_button = QPushButton("Confirm Due Date", self)
        self.confirm_button.clicked.connect(self.accept)
        self.reject_button = QPushButton("Choose No Due Date", self)
        self.reject_button.clicked.connect(self.reject)

        layout = QVBoxLayout()
        layout.addWidget(self.calendar)
        sublayout = QHBoxLayout()
        sublayout.addWidget(self.confirm_button)
        sublayout.addWidget(self.reject_button)
        layout.addLayout(sublayout)
        self.setLayout(layout)

    def selected_date(self):
        return self.calendar.selectedDate()