from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QListView, QTableView, QLineEdit, QCalendarWidget, QLabel, QDialog
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import sys
import json

from todo import Todo
from todo_model import TodoModel
from calendar_dialog import CalendarDialog
from todo_editor import TodoEditor

tick = QtGui.QColor("green")
cross = QtGui.QColor("red")

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todo")

        self.todo_list = QListView()
        self.todo_table = QTableView()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText("Enter a new todo item here")
        self.calendar_display = QCalendarWidget()
        self.calendar_display.setGridVisible(True)
        self.calendar_display.setSelectionMode(QCalendarWidget.NoSelection)
        self.selected_date = None
        self.select_date_button = QPushButton("Select Due Date")
        self.add_button = QPushButton("Add Todo")
        self.complete_button = QPushButton("Completed")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        
        main_layout = QVBoxLayout()
        # main_layout.addWidget(self.todo_list)
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
        self.todo_list.setModel(self.model)
        self.todo_list.setSelectionMode(QListView.SingleSelection)
        self.todo_table.setModel(self.model)
        self.todo_table.setSelectionMode(QTableView.SingleSelection)

        self.select_date_button.clicked.connect(self.select_due_date)
        self.add_button.clicked.connect(self.add_todo)
        self.complete_button.clicked.connect(self.complete_todo)
        self.edit_button.clicked.connect(self.edit_todo)
        self.delete_button.clicked.connect(self.delete_todo)

    def mark_date(self, date, status=True):
        format = QtGui.QTextCharFormat()
        if status:
            format.setBackground(QtGui.QColor("lightgreen"))
        else:
            format.setBackground(QtGui.QColor("lightcoral"))
        # format.setBackground(QtGui.QColor("yellow"))
        format.setForeground(QtGui.QColor("black"))
        format.setFontWeight(QtGui.QFont.Bold)
        self.calendar_display.setDateTextFormat(date, format)
        # print(f"Marked date {date.toString(QtCore.Qt.ISODate)} as {status}")

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
            self.todo_input.clear()
            self.save_todos()
            self.selected_date = None
            self.select_date_button.setText("Select Due Date")

    def edit_todo(self):
        # indexes = self.todo_list.selectedIndexes()
        indexes = self.todo_table.selectedIndexes()
        for index in indexes:
            todo = self.model.todos[index.row()]
            editor = TodoEditor(todo, self)
            if editor.exec_() == QDialog.Accepted:
                new_text = editor.get_todo_text()
                if new_text:
                    todo.text = new_text
                    self.model.dataChanged.emit(index, index)
                new_due_date = editor.get_due_date()
                if new_due_date:
                    todo.due_date = new_due_date
                    self.model.dataChanged.emit(index, index)

    def complete_todo(self):
        # indexes = self.todo_list.selectedIndexes()
        indexes = self.todo_table.selectedIndexes()
        for index in indexes:
            todo = self.model.todos[index.row()]
            todo.toggle()
            self.model.dataChanged.emit(index, index)
        # self.todo_list.clearSelection()
        self.todo_table.clearSelection()
        self.save_todos()

    def delete_todo(self):
        # indexes = self.todo_list.selectedIndexes()
        indexes = self.todo_table.selectedIndexes()
        for index in sorted(indexes, reverse=True):
            del self.model.todos[index.row()]
        self.model.layoutChanged.emit()
        # self.todo_list.clearSelection()
        self.todo_table.clearSelection()
        self.save_todos()

    def load_todos(self):
        # Load todos from a json file
        try:
            with open('./todos.json', 'r') as f:
                todos_data = json.load(f)
                self.model.todos = [Todo(todo['text'], todo['completed'], todo['due_date']) for todo in todos_data]
                for todo in self.model.todos:
                    if todo.due_date:
                        self.mark_date(todo.due_date, todo.completed)
        except Exception as e:
            print("Error when loading todos!")
            print(e)
            self.model.todos = [Todo("Sample Todo 1"), Todo("Sample Todo 2")]

    def save_todos(self):
        # Save todos to a json file
        todos_data = [{'text': todo.text, 'completed': todo.completed, 'due_date': todo.due_date.toString(QtCore.Qt.ISODate) if todo.due_date else None} for todo in self.model.todos]
        with open('todos.json', 'w') as f:
            json.dump(todos_data, f)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()