from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QCalendarWidget, QVBoxLayout, QHBoxLayout, QLabel
from PyQt5 import QtCore

class TodoEditor(QDialog):
    def __init__(self, todo, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Todo")
        self.todo = todo
        self.todo_input = QLineEdit(self)
        self.todo_input.setText(todo.text)
        self.save_button = QPushButton("Save", self)
        self.save_button.clicked.connect(self.accept)
        self.cancel_button = QPushButton("Cancel", self)
        self.cancel_button.clicked.connect(self.reject)

        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.setSelectionMode(QCalendarWidget.SingleSelection)
        self.date_confirm_button = QPushButton("Set Due Date", self)
        self.date_remove_button = QPushButton("Remove Due Date")
        self.due_date = todo.due_date
        if self.due_date:
            self.calendar.setSelectedDate(self.due_date)
        self.date_confirm_button.clicked.connect(self.confirm_due_date)
        self.date_remove_button.clicked.connect(self.remove_due_date)

        self.date_label = QLabel("Due Date:", self)
        if self.due_date:
            self.date_label.setText(f"Due Date: {self.due_date.toString(QtCore.Qt.ISODate)}")
        else:
            self.date_label.setText("Due Date: None")

        layout = QVBoxLayout()
        layout.addWidget(self.todo_input)
        layout.addWidget(self.calendar)
        layout.addWidget(self.date_label)
        sublayout1 = QHBoxLayout()
        sublayout1.addWidget(self.date_confirm_button)
        sublayout1.addWidget(self.date_remove_button)
        layout.addLayout(sublayout1)
        sublayout2 = QHBoxLayout()
        sublayout2.addWidget(self.save_button)
        sublayout2.addWidget(self.cancel_button)
        layout.addLayout(sublayout2)
        self.setLayout(layout)

    def get_todo_text(self):
        return self.todo_input.text().strip()
    
    def get_due_date(self):
        return self.due_date
    
    def confirm_due_date(self):
        selected_date = self.calendar.selectedDate()
        if selected_date.isValid():
            self.due_date = selected_date
            self.date_label.setText(f"Due Date: {self.due_date.toString(QtCore.Qt.ISODate)}")
        else:
            self.due_date = None
            self.date_label.setText("Due Date: None")

    def remove_due_date(self):
        self.due_date = None
        self.calendar.setSelectedDate(QtCore.QDate())
        self.date_label.setText("Due Date: None")