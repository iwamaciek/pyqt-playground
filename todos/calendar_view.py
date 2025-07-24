from PyQt5.QtWidgets import QCalendarWidget
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QDate

class CalendarModel:
    def __init__(self, data=None):
        # This model will hold the calendar data
        # It contains a dictionary mapping dates to events
        # An event is a boolean indicating if the todo is completed (True) or not (False)
        self.data = data if data is not None else {}

    def set_data(self, data):
        self.data = data

    def add_event(self, date, event):
        if date not in self.data.keys():
            self.data[date] = []
        self.data[date].append(event)

    def get_events(self, date):
        return self.data.get(date, [])
    
    def remove_event(self, date, event):
        if date in self.data.keys():
            if event in self.data[date]:
                self.data[date].remove(event)

class CalendarView(QCalendarWidget):
    def __init__(self, model=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.model = model
        self.setGridVisible(True)
        self.setSelectionMode(QCalendarWidget.NoSelection)

    def setModel(self, model):
        self.model = model
        self.refresh()

    def refresh(self):
        for date, events in self.model.data.items():
            if all(events): # All events are completed
                self.markDate(date, "lightgreen")
            elif all([not event for event in events]): # All events are not completed
                self.markDate(date, "lightcoral")
            else: # Mixed events
                self.markDate(date, "yellow")

    def markDate(self, date, color):
        format = QtGui.QTextCharFormat()
        format.setBackground(QtGui.QColor(color))
        format.setForeground(QtGui.QColor("black"))
        format.setFontWeight(QtGui.QFont.Bold)
        self.setDateTextFormat(QDate.fromString(date, Qt.ISODate), format)