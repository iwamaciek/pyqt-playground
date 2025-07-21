from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QListView, QLineEdit
import PyQt5.QtCore as QtCore
import PyQt5.QtGui as QtGui
import sys
import json

tick = QtGui.QColor("green")
cross = QtGui.QColor("red")

class Todo:
    def __init__(self, text, completed=False):
        self.text = text
        self.completed = completed

    def toggle(self):
        self.completed = not self.completed

class TodoModel(QtCore.QAbstractListModel):
    def __init__(self, *args, todos=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.todos = todos or []

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            todo = self.todos[index.row()]
            return todo.text
        elif role == QtCore.Qt.DecorationRole:
            todo = self.todos[index.row()]
            if todo.completed:
                return tick
            else:
                return cross
        
    def rowCount(self, index):
        return len(self.todos)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Todo")

        self.todo_list = QListView()
        self.todo_input = QLineEdit()
        self.todo_input.setPlaceholderText("Enter a new todo item here")
        self.add_button = QPushButton("Add Todo")
        self.complete_button = QPushButton("Completed")
        self.delete_button = QPushButton("Delete")
        
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.todo_list)
        sublayout = QHBoxLayout()
        sublayout.addWidget(self.complete_button)
        sublayout.addWidget(self.delete_button)
        main_layout.addLayout(sublayout)
        main_layout.addWidget(self.todo_input)
        main_layout.addWidget(self.add_button)

        self.w = QWidget()
        self.w.setLayout(main_layout)
        self.setCentralWidget(self.w)

        self.model = TodoModel(todos=[Todo("Sample Todo 1"), Todo("Sample Todo 2")])
        self.load_todos()
        self.todo_list.setModel(self.model)
        self.todo_list.setSelectionMode(QListView.MultiSelection)

        self.add_button.clicked.connect(self.add_todo)
        self.complete_button.clicked.connect(self.complete_todo)
        self.delete_button.clicked.connect(self.delete_todo)

    def add_todo(self):
        text = self.todo_input.text().strip()
        if text:
            new_todo = Todo(text)
            self.model.todos.append(new_todo)
            self.model.layoutChanged.emit()
            self.todo_input.clear()
            self.save_todos()

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