from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QListView, QLineEdit, QCalendarWidget, QLabel, QDialog
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import sys
import json

tick = QtGui.QColor("green")
cross = QtGui.QColor("red")

class Todo:
    def __init__(self, text, completed=False, due_date=None):
        self.text = text
        self.completed = completed
        self.due_date = due_date

    def toggle(self):
        self.completed = not self.completed

    def set_due_date(self, date):
        self.due_date = date

class TodoModel(QtCore.QAbstractListModel):
    def __init__(self, *args, todos=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.todos = todos or []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            todo = self.todos[index.row()]
            return f"{todo.text} {' - Due by ' + todo.due_date.strftime('%Y-%m-%d') if todo.due_date else ''}"
        elif role == QtCore.Qt.DecorationRole:
            todo = self.todos[index.row()]
            if todo.completed:
                return tick
            else:
                return cross
        
    def rowCount(self, index):
        return len(self.todos)
    
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

        layout = QVBoxLayout()
        layout.addWidget(self.todo_input)
        sublayout = QHBoxLayout()
        sublayout.addWidget(self.save_button)
        sublayout.addWidget(self.cancel_button)
        layout.addLayout(sublayout)
        self.setLayout(layout)

    def get_todo_text(self):
        return self.todo_input.text().strip()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todo")

        self.todo_list = QListView()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText("Enter a new todo item here")
        self.calendar_display = QCalendarWidget()
        self.calendar_display.setGridVisible(True)
        self.calendar_display.setSelectionMode(QCalendarWidget.NoSelection)
        self.selected_date = None
        self.select_date_button = QPushButton("Select Due Date")
        self.add_button = QPushButton("Add Todo (With Due Date)")
        self.complete_button = QPushButton("Completed")
        self.edit_button = QPushButton("Edit")
        self.delete_button = QPushButton("Delete")
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.todo_list)
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
        self.todo_list.setSelectionMode(QListView.MultiSelection)

        self.select_date_button.clicked.connect(self.select_due_date)
        self.add_button.clicked.connect(self.add_todo)
        self.complete_button.clicked.connect(self.complete_todo)
        self.edit_button.clicked.connect(self.edit_todo)
        self.delete_button.clicked.connect(self.delete_todo)

    def mark_date(self, date):
        format = QtGui.QTextCharFormat()
        format.setBackground(QtGui.QColor("yellow"))
        format.setForeground(QtGui.QColor("black"))
        format.setFontWeight(QtGui.QFont.Bold)
        self.calendar_display.setDateTextFormat(date, format)

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
            new_todo = Todo(text)
            self.model.todos.append(new_todo)
            self.model.layoutChanged.emit()
            self.todo_input.clear()
            self.save_todos()

    def edit_todo(self):
        indexes = self.todo_list.selectedIndexes()
        for index in indexes:
            todo = self.model.todos[index.row()]
            editor = TodoEditor(todo, self)
            if editor.exec_() == QDialog.Accepted:
                new_text = editor.get_todo_text()
                if new_text:
                    todo.text = new_text
                    self.model.dataChanged.emit(index, index)
                else:
                    pass  # Ignore empty edits
            else:
                pass  # Ignore cancelled edits

    def complete_todo(self):
        indexes = self.todo_list.selectedIndexes()
        for index in indexes:
            todo = self.model.todos[index.row()]
            todo.toggle()
            self.model.dataChanged.emit(index, index)
        self.todo_list.clearSelection()
        self.save_todos()

    def delete_todo(self):
        indexes = self.todo_list.selectedIndexes()
        for index in sorted(indexes, reverse=True):
            del self.model.todos[index.row()]
        self.model.layoutChanged.emit()
        self.todo_list.clearSelection()
        self.save_todos()

    def load_todos(self):
        # Load todos from a json file
        try:
            with open('todos.json', 'r') as f:
                todos_data = json.load(f)
                self.model.todos = [Todo(todo['text'], todo['completed']) for todo in todos_data]
                for todo in self.model.todos:
                    if todo.due_date:
                        self.mark_date(todo.due_date)
        except:
            self.model.todos = [Todo("Sample Todo 1"), Todo("Sample Todo 2")]

    def save_todos(self):
        # Save todos to a json file
        todos_data = [{'text': todo.text, 'completed': todo.completed} for todo in self.model.todos]
        with open('todos.json', 'w') as f:
            json.dump(todos_data, f)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()