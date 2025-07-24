from PyQt5 import QtCore, QtGui

tick = QtGui.QColor("green")
cross = QtGui.QColor("red")

class TodoModel(QtCore.QAbstractTableModel):
    def __init__(self, *args, todos=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.todos = todos or []
        self.horizontal_header_labels = ["Todo", "Due Date"]

    def data(self, index, role):
        if role == QtCore.Qt.DisplayRole:
            todo = self.todos[index.row()]
            if index.column() == 0:
                return todo.text
            elif index.column() == 1:
                if todo.due_date:
                    return todo.due_date.toString(QtCore.Qt.ISODate)
                else:
                    return "No Due Date"
        elif role == QtCore.Qt.DecorationRole:
            todo = self.todos[index.row()]
            if index.column() == 0:
                if todo.completed:
                    return tick
                else:
                    return cross
        
    def rowCount(self, index):
        return len(self.todos)
    
    def columnCount(self, index):
        return 2
    
    def headerData(self, section, orientation, role):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.horizontal_header_labels[section]
            elif orientation == QtCore.Qt.Vertical:
                return "No." + str(section + 1)
            
# class TodoModel(QtCore.QAbstractListModel):
#     def __init__(self, *args, todos=None, **kwargs):
#         super().__init__(*args, **kwargs)
#         self.todos = todos or []

#     def data(self, index, role):
#         if role == QtCore.Qt.DisplayRole:
#             todo = self.todos[index.row()]
#             return f"{todo.text} {' - Due by ' + todo.due_date.toString(QtCore.Qt.ISODate) if todo.due_date else ''}"
#         elif role == QtCore.Qt.DecorationRole:
#             todo = self.todos[index.row()]
#             if todo.completed:
#                 return tick
#             else:
#                 return cross
        
#     def rowCount(self, index):
#         return len(self.todos)