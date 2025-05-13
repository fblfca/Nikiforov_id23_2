from random import (randint, uniform)
from PyQt6.QtCore import QTimer, Qt, QPointF
from PyQt6.QtGui import QPainter, QBrush, QColor, QPainterPath
from PyQt6.QtWidgets import (QApplication,
                             QWidget,
                             QLabel,
                             QVBoxLayout,
                             QSizePolicy,
                             QMessageBox
                             )
import sys


class Cabbage(object):
    def __init__(self):
        self.value = randint(200, 500)
        self.radius = self.change_radius()
        self.x_coord = randint(150, 500)
        self.y_coord = randint(150, 500)
        self.eaten_status = False

    def change_radius(self):
        return self.value ** 0.4

    @property
    def get_x_coord(self):
        return self.x_coord

    @property
    def get_y_coord(self):
        return self.y_coord

    @property
    def get_radius(self):
        return self.radius


class Goat(object):
    def __init__(self):
        self.x_coord = randint(100, 500)
        self.y_coord = randint(100, 500)
        self.starve = 800
        self.speed = uniform(0.5, 0.8)
        self.eat_speed = self.change_eat_speed()
        self.endurance = randint(2, 4)
        self.radius = self.change_radius()
        self.eating_status = False

    def change_radius(self):
        return self.starve ** 0.35

    def change_eat_speed(self):
        if self.starve > 700:
            return 10
        return (800 - self.starve) // 10

    def animate_circles(self):
        self.radius = self.change_radius()
        self.eat_speed = self.change_eat_speed()

    @property
    def get_x_coord(self):
        return self.x_coord

    @property
    def get_y_coord(self):
        return self.y_coord

    @property
    def get_radius(self):
        return self.radius

    @property
    def get_speed(self):
        return self.speed


def get_closest(x1, x2, y1, y2):
    return ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5


def show_popup():
    msg = QMessageBox()
    msg.setWindowTitle("Warning!")
    msg.setText("These goats don't wanna live like that")

    msg.setStandardButtons(QMessageBox.StandardButton.Ok)

    # msg.button(QMessageBox.StandardButton.Ok).clicked.connect(QApplication.quit)

    msg.exec()


class Graphical_view(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Goats pen')
        self.setGeometry(50, 50, 750, 750)
        self.radius = 350
        self.center_x = self.width() // 2
        self.center_y = self.height() // 2

        layout = QVBoxLayout()
        layout.addStretch()

        self.info_label = QLabel(self)
        self.info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.info_label)
        self.info_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        self.setLayout(layout)

        self.cabbages = [Cabbage() for _ in range(7)]
        self.pen = [Goat() for _ in range(1)]

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.simulation_update)
        self.timer.start(16)

    def add_cabbage(self):
        new_cabbage = Cabbage()
        self.cabbages.append(new_cabbage)

    def paintEvent(self, event):
        painter = QPainter(self)

        painter.setBrush(QBrush(Qt.GlobalColor.green, Qt.BrushStyle.SolidPattern))
        painter.drawEllipse(self.center_x - self.radius, self.center_y - self.radius, self.radius * 2,
                            int(self.radius * 1.7))

        for cabbage in self.cabbages:
            center = QPointF(cabbage.get_x_coord, cabbage.get_y_coord)
            painter.setBrush(QBrush(QColor(0, 127, 0), Qt.BrushStyle.SolidPattern))

            if not cabbage.eaten_status:
                painter.drawEllipse(center, cabbage.get_radius, cabbage.get_radius)

            if cabbage.eaten_status:
                path = QPainterPath()
                path.moveTo(cabbage.get_x_coord, cabbage.get_y_coord)
                path.arcTo(cabbage.get_x_coord - cabbage.get_radius, cabbage.get_y_coord - cabbage.get_radius,
                           cabbage.get_radius * 2, cabbage.get_radius * 2, 0, -180)

                painter.fillPath(path, painter.brush())
                painter.drawPath(path)

        for goat in self.pen:
            center = QPointF(goat.get_x_coord, goat.get_y_coord)
            painter.setBrush(QBrush(Qt.GlobalColor.lightGray, Qt.BrushStyle.SolidPattern))

            if not goat.eating_status:
                painter.drawEllipse(center, goat.get_radius, goat.get_radius)

            if goat.eating_status:
                path = QPainterPath()
                path.moveTo(goat.get_x_coord, goat.get_y_coord)
                path.arcTo(goat.get_x_coord - goat.get_radius, goat.get_y_coord - goat.get_radius,
                           goat.get_radius * 2, goat.get_radius * 2, 0, 180)

                painter.fillPath(path, painter.brush())
                painter.drawPath(path)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            print("App closed")
            QApplication.quit()

    def simulation_update(self):
        for goat in self.pen:
            closest_cabbage = min(self.cabbages,
                                  key=lambda cabbage: get_closest(goat.get_x_coord, cabbage.get_x_coord,
                                                                  goat.get_y_coord, cabbage.get_y_coord))
            distance = get_closest(goat.get_x_coord, closest_cabbage.get_x_coord, goat.get_y_coord,
                                   closest_cabbage.get_y_coord)
            if distance != 0:

                direction_x = closest_cabbage.get_x_coord - goat.get_x_coord
                direction_y = closest_cabbage.get_y_coord - goat.get_y_coord

                direction_x /= distance
                direction_y /= distance

                if distance <= goat.get_radius / 5:
                    goat.x_coord = closest_cabbage.get_x_coord
                    goat.y_coord = closest_cabbage.get_y_coord
                    goat.eating_status = True

                else:
                    goat.eating_status = False
                    goat.x_coord += direction_x * goat.get_speed
                    goat.y_coord += direction_y * goat.get_speed

                goat.starve -= goat.endurance
                goat.animate_circles()

            else:
                if closest_cabbage.value > goat.eat_speed:
                    closest_cabbage.eaten_status = True
                    closest_cabbage.value -= goat.eat_speed
                    closest_cabbage.radius = closest_cabbage.change_radius()
                    goat.starve += goat.eat_speed
                    goat.animate_circles()

                else:
                    closest_cabbage.eaten_status = True
                    goat.starve += closest_cabbage.value
                    goat.animate_circles()
                    closest_cabbage.value = 0
                    self.cabbages.remove(closest_cabbage)
                    self.add_cabbage()

            if goat.starve <= 0:
                self.pen.remove(goat)  # решение к ошибке при выходе из анимации
                show_popup()
                print('App closed')
                sys.exit(app.exec())
                # QTimer.singleShot(3000, QApplication.instance().quit)

            info_text = f"Cabbages: {len(self.cabbages)}, Goat Starvation: {goat.starve}, Cabbage Value: {closest_cabbage.value}, " \
                        f"Goat Radius: {round(goat.radius, 2)}, Goat eat speed: {goat.eat_speed}"
            self.info_label.setText(info_text)
        self.update()


app = QApplication(sys.argv)
window = Graphical_view()
window.show()
sys.exit(app.exec())
