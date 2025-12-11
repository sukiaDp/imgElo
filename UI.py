import sys
import os
from PySide6.QtWidgets import QApplication, QLabel, QHBoxLayout, QVBoxLayout, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt, Signal, QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QSoundEffect

from backend import RatingDB, Image


class ClickableLabel(QLabel):
    clicked = Signal()

    def __init__(self):
        super().__init__()
        self.setCursor(Qt.PointingHandCursor)
        self.setAlignment(Qt.AlignCenter)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


class CompareWindow(QWidget):
    def __init__(self, db: RatingDB, display_height=800):
        super().__init__()
        self.db = db
        self.display_height = display_height
        self.current_left: Image = None
        self.current_right: Image = None

        self._init_ui()
        self._load_next_pair()

    def _init_ui(self):
        self.setWindowTitle("ImgElo - 图片对比")

        main_layout = QVBoxLayout()

        # 图片区域
        image_layout = QHBoxLayout()

        self.left_label = ClickableLabel()
        self.left_label.clicked.connect(lambda: self._on_choice('left'))
        image_layout.addWidget(self.left_label)

        self.right_label = ClickableLabel()
        self.right_label.clicked.connect(lambda: self._on_choice('right'))
        image_layout.addWidget(self.right_label)

        main_layout.addLayout(image_layout)

        # 状态栏
        self.status_label = QLabel()
        self.status_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(self.status_label)

        self.setLayout(main_layout)

        current_dir = os.path.dirname(os.path.abspath(__file__))
        success_path = os.path.join(current_dir, "sound", "sfx_success.wav")
        fail_path = os.path.join(current_dir, "sound", "sfx_fail.wav")

        self.sfx_success = QSoundEffect()
        self.sfx_success.setSource(QUrl.fromLocalFile(success_path))
        self.sfx_success.setVolume(1.0)

        self.sfx_fail = QSoundEffect()
        self.sfx_fail.setSource(QUrl.fromLocalFile(fail_path))
        self.sfx_fail.setVolume(1.0)

    def _load_next_pair(self):
        try:
            self.current_left, self.current_right = self.db.sample_pair()
        except ValueError as e:
            self.status_label.setText(f"错误: {e}")
            return

        self._display_image(self.left_label, self.current_left.path)
        self._display_image(self.right_label, self.current_right.path)
        self._update_status()

    def _display_image(self, label: QLabel, path: str):
        pixmap = QPixmap(path)
        if pixmap.isNull():
            label.setText(f"加载失败:\n{path}")
            return

        # 按高度缩放，保持比例
        scaled = pixmap.scaledToHeight(self.display_height, Qt.SmoothTransformation)
        label.setPixmap(scaled)

    def _on_choice(self, side: str):
        if side == 'left':
            winner, loser = self.current_left, self.current_right
        else:
            winner, loser = self.current_right, self.current_left

        if winner.rating.mean > loser.rating.mean:
            print("success")
            self.sfx_success.play()
        else:
            self.sfx_fail.play()


        self.db.update(winner, loser)
        self._load_next_pair()

    def _update_status(self):
        left = self.current_left
        right = self.current_right
        total = self.db.count()

        self.status_label.setText(
            f"左: μ={left.rating.mean:.1f} σ={left.rating.std:.1f} (n={left.match_count}) | "
            f"右: μ={right.rating.mean:.1f} σ={right.rating.std:.1f} (n={right.match_count}) | "
            f"总计: {total} 张"
        )

    def keyPressEvent(self, event):
        # 键盘快捷键
        if event.key() == Qt.Key_Left:
            self._on_choice('left')
        elif event.key() == Qt.Key_Right:
            self._on_choice('right')
        elif event.key() == Qt.Key_Escape:
            self.close()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('--db', default='images.db', help='数据库路径')
    parser.add_argument('--folder', help='首次运行时扫描的文件夹')
    parser.add_argument('--height', type=int, default=800, help='显示高度')
    args = parser.parse_args()

    db = RatingDB(args.db)

    if args.folder:
        stats = db.init_from_folder(args.folder)
        print(f"扫描完成: 新增 {stats['new']}, 更新 {stats['updated']}")

    if db.count() < 2:
        print("图片数量不足，请用 --folder 指定文件夹")
        sys.exit(1)

    app = QApplication(sys.argv)
    window = CompareWindow(db, display_height=args.height)
    window.show()
    app.exec()

    db.close()