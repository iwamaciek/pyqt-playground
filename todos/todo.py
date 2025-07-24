from PyQt5 import QtCore

class Todo:
    def __init__(self, text, completed=False, due_date=None):
        print(f"Creating Todo: {text}, Completed: {completed}, Due Date: {due_date}")
        self.text = text
        self.completed = completed
        if isinstance(due_date, str):
            self.due_date = QtCore.QDate.fromString(due_date, QtCore.Qt.ISODate)
        else:
            self.due_date = due_date

    def toggle(self):
        self.completed = not self.completed

    def set_due_date(self, date):
        self.due_date = date