# GUI imports
from PySide2.QtGui import QFont
from PySide2.QtCore import Slot
from PySide2.QtWidgets import (
    QApplication,
    QLabel,
    QMessageBox,
    QPushButton,
    QWidget,
    QDoubleSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit
)
# Plotting imports
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT
# Utilities imports
import numpy as np
import sys
import re

# list of allowed words to be entered by the user
allowed_words = [
    'x',
    'sin',
    'cos',
    'sqrt',
    'exp',
    '/',
    '+',
    '*',
    '^',
    '-'
]

# for converting from string to mathematical expression
replacements = {
    'sin': 'np.sin',
    'cos': 'np.cos',
    'exp': 'np.exp',
    'sqrt': 'np.sqrt',
    '^': '**',
}

DEFAULT_FONT = QFont("Calibri", 15)
X_RANGE = (-1000, 1000)
DEFAULT_FUNCTION = "x"
DEFAULT_RANGE = (-10,10)

# convert from string to mathematical expression that supported by matplotlib
def string2func(string):
    ''' evaluates the string and returns a function of x '''
    # find all words and check if all are allowed:
    for word in re.findall('[a-zA-Z_]+', string):
        if word not in allowed_words:
            raise ValueError(
                f"'{word}' is forbidden to use in math expression.\nOnly functions of 'x' are allowed.\ne.g., 5*x^3 + 2/x - 1\nList of allowed words: {', '.join(allowed_words)}"
            )

    for old, new in replacements.items():
        string = string.replace(old, new)

    # to deal with constant functions e.g., y = 1
    if "x" not in string:
        string = f"{string}+0*x"

    def func(x):
        return eval(string)

    return func


"""interaction between Qt Widgets and a 2D matplotlib ploty"""


class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Function Plotter")
        
        #  create widgets
        self.view = FigureCanvas(Figure(figsize=(8, 8)))
        self.axes = self.view.figure.subplots()
        self.toolbar = NavigationToolbar2QT(self.view, self)
        # min and max values of x
        self.mn = QDoubleSpinBox()
        self.mx = QDoubleSpinBox()
        self.mn.setPrefix("min x: ")
        self.mx.setPrefix("max x: ")
        self.mn.setFont(DEFAULT_FONT) 
        self.mx.setFont(DEFAULT_FONT) 
        self.mn.setRange(*X_RANGE)
        self.mx.setRange(*X_RANGE)
        self.mn.setValue(DEFAULT_RANGE[0])
        self.mx.setValue(DEFAULT_RANGE[1])

        self.function = QLineEdit()
        self.function.setFont(DEFAULT_FONT) 
        self.function.setText(DEFAULT_FUNCTION)
        self.func_label = QLabel(text="Function: ")
        self.func_label.setFont(DEFAULT_FONT) 
        self.submit = QPushButton(text="plot")
        self.submit.setFont(DEFAULT_FONT)
        #  Create layout
        input_layout1 = QHBoxLayout()
        input_layout1.addWidget(self.func_label)
        input_layout1.addWidget(self.function)
        input_layout1.addWidget(self.submit)

        input_layout2 = QHBoxLayout()
        input_layout2.addWidget(self.mn)
        input_layout2.addWidget(self.mx)

        vlayout = QVBoxLayout()
        vlayout.addWidget(self.toolbar)
        vlayout.addWidget(self.view)
        vlayout.addLayout(input_layout1)
        vlayout.addLayout(input_layout2)
        self.setLayout(vlayout)

        self.error_dialog = QMessageBox()
        self.error_dialog.setFont(DEFAULT_FONT)
        # connect inputs with on_change method
        self.mn.valueChanged.connect(lambda _: self.on_change(1))
        self.mx.valueChanged.connect(lambda _: self.on_change(2))
        self.submit.clicked.connect(lambda _: self.on_change(3))

        self.on_change(0)

    @Slot()
    def on_change(self, idx): # idx is needed to identify what value is changed
        """ Update the plot with the current input values """
        mn = self.mn.value()
        mx = self.mx.value()

        # warning: min x can't be greater than or equal to max x
        if idx == 1 and mn >= mx:
            self.mn.setValue(mx-1)
            self.error_dialog.setWindowTitle("x limits Error!")
            self.error_dialog.setText("'min x' should be less than 'max x'.")
            self.error_dialog.show()
            return

        # warning: max x can't be less than or equal to min x
        if idx == 2 and mx <= mn:
            self.mx.setValue(mn+1)
            self.error_dialog.setWindowTitle("x limits Error!")
            self.error_dialog.setText("'max x' should be greater than 'min x'.")
            self.error_dialog.show()
            return

        x = np.linspace(mn, mx)
        try:
            y = string2func(self.function.text())(x)
        except ValueError as e:
            self.error_dialog.setWindowTitle("Function Error!")
            self.error_dialog.setText(str(e))
            self.error_dialog.show()
            return

        self.axes.clear()
        self.axes.plot(x, y)
        self.view.draw()


if __name__ == "__main__":

    app = QApplication(sys.argv)
    w = PlotWidget()
    w.show()
    sys.exit(app.exec_())
