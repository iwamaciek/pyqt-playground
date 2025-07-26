from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QListView, QTableView, QLineEdit, QCalendarWidget, QLabel, QDialog
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import sys
import os
import json

from todo import Todo
from todo_model import TodoModel
from calendar_dialog import CalendarDialog
from todo_editor import TodoEditor
from calendar_view import CalendarView, CalendarModel

tick = QtGui.QColor("green")
cross = QtGui.QColor("red")
current_directory = os.path.dirname(os.path.abspath(__file__))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todo App")

        self.todo_table = QTableView()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText("Enter a new todo item here")
        self.calendar_display = CalendarView()
        self.selected_date = None
        self.select_date_button = QPushButton("Select Due Date")
        self.add_button = QPushButton("Add Todo")
        self.complete_button = QPushButton("Completed")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.todo_table)
        sublayout = QHBoxLayout()
        sublayout.addWidget(self.complete_button)
        sublayout.addWidget(self.edit_button)
        sublayout.addSpacing(20)
        sublayout.addWidget(self.delete_button)
        main_layout.addLayout(sublayout)
        main_layout.addWidget(self.calendar_display)
        main_layout.addWidget(self.todo_input)
        main_layout.addWidget(self.select_date_button)
        main_layout.addWidget(self.add_button)

        self.w = QWidget()
        self.w.setLayout(main_layout)
        self.setCentralWidget(self.w)

        self.model = TodoModel(todos=[Todo("Sample Todo 1"), Todo("Sample Todo 2")])
        self.load_todos()
        self.todo_table.setModel(self.model)
        self.todo_table.setSelectionMode(QTableView.SingleSelection)
        self.todo_table.resizeColumnsToContents()

        self.calendar_data = self.get_calendar_data()
        self.calendar_model = CalendarModel(self.calendar_data)
        self.calendar_display.setModel(self.calendar_model)

        self.select_date_button.clicked.connect(self.select_due_date)
        self.add_button.clicked.connect(self.add_todo)
        self.complete_button.clicked.connect(self.complete_todo)
        self.edit_button.clicked.connect(self.edit_todo)
        self.delete_button.clicked.connect(self.delete_todo)

    def get_calendar_data(self):
        calendar_data = {}
        for todo in self.model.todos:
            if todo.due_date:
                date_str = todo.due_date.toString(QtCore.Qt.ISODate)
                if date_str not in calendar_data.keys():
                    calendar_data[date_str] = []
                calendar_data[date_str].append(todo.completed)
        return calendar_data

    def select_due_date(self):
        dialog = CalendarDialog(self)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            selected_date = dialog.selected_date()
            self.calendar_display.setSelectedDate(selected_date)
            self.select_date_button.setText(f"Selected Date: {selected_date.toString(QtCore.Qt.ISODate)}")
        elif result == QDialog.Rejected:
            selected_date = None
            self.calendar_display.setSelectedDate(QtCore.QDate())
            self.select_date_button.setText("Select Due Date")
        else:
            raise ValueError("Unexpected dialog result")
        self.selected_date = selected_date

    def add_todo(self):
        text = self.todo_input.text().strip()
        if text:
            new_todo = Todo(text, due_date=self.selected_date)
            self.model.todos.append(new_todo)
            self.model.layoutChanged.emit()
            self.todo_table.resizeColumnsToContents()
            self.calendar_model.add_event(self.selected_date.toString(QtCore.Qt.ISODate), new_todo.completed)
            self.calendar_display.refresh()
            self.todo_input.clear()
            self.save_todos()
            self.selected_date = None
            self.select_date_button.setText("Select Due Date")

    def edit_todo(self):
        indexes = self.todo_table.selectedIndexes()
        for index in indexes:
            todo = self.model.todos[index.row()]
            editor = TodoEditor(todo, self)
            if editor.exec_() == QDialog.Accepted:
                new_text = editor.get_todo_text()
                if new_text:
                    todo.text = new_text
                    self.model.dataChanged.emit(index, index)
                    self.todo_table.resizeColumnsToContents()
                new_due_date = editor.get_due_date()
                if new_due_date:
                    if todo.due_date:
                        self.calendar_model.remove_event(todo.due_date.toString(QtCore.Qt.ISODate), todo.completed)
                    todo.due_date = new_due_date
                    self.model.dataChanged.emit(index, index)
                    self.todo_table.resizeColumnsToContents()
                    self.calendar_model.add_event(new_due_date.toString(QtCore.Qt.ISODate), todo.completed)
                    self.calendar_display.refresh()
                self.save_todos()

    def complete_todo(self):
        indexes = self.todo_table.selectedIndexes()
        for index in indexes:
            todo = self.model.todos[index.row()]
            todo.toggle()
            self.model.dataChanged.emit(index, index)
            if todo.due_date:
                self.calendar_model.remove_event(todo.due_date.toString(QtCore.Qt.ISODate), not todo.completed)
                self.calendar_model.add_event(todo.due_date.toString(QtCore.Qt.ISODate), todo.completed)
                self.calendar_display.refresh()
        self.todo_table.clearSelection()
        self.save_todos()

    def delete_todo(self):
        indexes = self.todo_table.selectedIndexes()
        for index in sorted(indexes, reverse=True):
            todo = self.model.todos[index.row()]
            if todo.due_date:
                self.calendar_model.remove_event(todo.due_date.toString(QtCore.Qt.ISODate), todo.completed)
                self.calendar_display.refresh()
            del self.model.todos[index.row()]
        self.model.layoutChanged.emit()
        self.todo_table.resizeColumnsToContents()
        self.todo_table.clearSelection()
        self.save_todos()

    def load_todos(self):
        # Load todos from a json file
        try:
            with open(os.path.join(current_directory, 'todos.json'), 'r') as f:
                todos_data = json.load(f)
                self.model.todos = [Todo(todo['text'], todo['completed'], todo['due_date']) for todo in todos_data]
        except Exception as e:
            print("Error when loading todos!")
            print(e)
            self.model.todos = [Todo("Sample Todo 1"), Todo("Sample Todo 2")]

    def save_todos(self):
        # Save todos to a json file
        todos_data = [{'text': todo.text, 'completed': todo.completed, 'due_date': todo.due_date.toString(QtCore.Qt.ISODate) if todo.due_date else None} for todo in self.model.todos]
        with open(os.path.join(current_directory, 'todos.json'), 'w') as f:
            json.dump(todos_data, f)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()