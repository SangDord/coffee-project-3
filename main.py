import sqlite3
import sys

from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from UI.mainWindow import Ui_MainWindow
from UI.editWindow import Ui_addEditCoffee


class Coffee(QMainWindow, Ui_MainWindow):

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.connection = sqlite3.connect('data/coffee.sqlite')
        self.editBtn.clicked.connect(self.edit)
        self.updateBtn.clicked.connect(self.update_table)
        self.update_table()

    def update_table(self):
        self.statusBar().clearMessage()
        query = "SELECT * FROM coffee_beans"
        result = self.connection.cursor().execute(query).fetchall()
        for i, data in enumerate(result):
            self.tableWidget.setRowCount(i + 1)
            for j, elem in enumerate(data):
                self.tableWidget.setItem(i, j, QTableWidgetItem(str(elem)))

    def edit(self):
        sel_items = self.tableWidget.selectedItems()
        edit_window = AddEditCoffee(sel_items, self)
        edit_window.show()

    def update_result(self, status, items):
        try:
            if status == 0:  # Добавление
                query = """INSERT INTO coffee_beans(name_of_sorts, degree_of_roasing, type_of_coffee, 
                description_of_the_taste, price, packing_volume) VALUES(?)"""
                value = ', '.join(f'"{el}"' if isinstance(el, str) else f'{el}' for el in items)
                query = query.replace('?', value)
                self.connection.cursor().execute(query)
            else:            # Редактирование
                query = """UPDATE coffee_beans SET name_of_sorts = "{}", degree_of_roasing = "{}",
                type_of_coffee = "{}", description_of_the_taste = "{}", price = {}, packing_volume = {}
                WHERE id = {}""".format(items[1], items[2], items[3], items[4], items[5], items[6], items[0])
                self.connection.cursor().execute(query)
            self.connection.commit()
            self.update_table()
            self.statusBar().showMessage('Успешно добавлено/отредактировано')
        except Exception as exp:
            self.statusBar().showMessage(f'Ошибка: {exp}')


class AddEditCoffee(QMainWindow, Ui_addEditCoffee):

    def __init__(self, sel_items, parent=None):
        super().__init__(parent)
        self.setupUi(self)
        if sel_items:
            self.fill_data(sel_items)
            self.statusEdit.setText('Редактирование')
            self.sel_items = sel_items
        else:
            self.statusEdit.setText('Добавление')
        self.saveBtn.clicked.connect(self.save_result)

    def fill_data(self, sel_items):
        items = [el.text() for el in sel_items]
        self.sortEdit.setText(items[1])
        if self.degreeBox.currentText() != items[2]:
            self.degreeBox.setCurrentIndex(self.degreeBox.currentIndex() + 1 if items[2] == 'Средняя' else 2)
        if self.conBox.currentText() != items[3]:
            self.conBox.setCurrentIndex((self.conBox.currentIndex() + 1) % 2)
        self.descPlainEdit.setPlainText(items[4])
        self.priceBox.setValue(int(items[5]))
        self.volBox.setValue(int(items[6]))

    def save_result(self):
        try:
            sort = self.sortEdit.text()
            degree = self.degreeBox.currentText()
            cond = self.conBox.currentText()
            desc = self.descPlainEdit.toPlainText()
            price = self.priceBox.value()
            volume = self.volBox.value()
            if not sort or not desc:
                raise ValueError
            items = [sort, degree, cond, desc, price, volume]
            if self.statusEdit.text() == 'Добавление':
                self.parent().update_result(0, items)
            else:
                self.parent().update_result(1, [int(self.sel_items[0].text())] + items)
            self.close()
        except ValueError:
            self.statusBar().showMessage("Заполните пустые поля!!!")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Coffee()
    ex.show()
    sys.exit(app.exec_())
