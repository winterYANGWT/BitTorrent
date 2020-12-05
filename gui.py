import sys
from PyQt5.QtWidgets import *

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.torrent_path=''
        self.setWindowTitle('BitTorrent')
        self.resize(800,450)
        self.load_widget()
        self.setCentralWidget(self.top_widget)

    def load_widget(self):
        self.add_file_button=QPushButton('Add File',self)
        self.add_file_button.setFixedSize(160,90)
        self.add_file_button.clicked.connect(self.show_file_dialog)
        self.layout=QHBoxLayout()
        self.top_widget=QWidget()
        self.layout.addWidget(self.add_file_button)
        self.top_widget.setLayout(self.layout)

    def show_file_dialog(self):
        self.torrent_path,_=QFileDialog.getOpenFileName(self,
                                                        'Open File',
                                                        './',
                                                        '(*.torrent)')
        

if __name__=='__main__':
    app=QApplication(sys.argv)
    w=MainWindow()
    w.show()
    sys.exit(app.exec_())