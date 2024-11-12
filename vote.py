import sys
import json
import random
import os
import csv
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QInputDialog
from PyQt6.QtGui import QPainter, QColor, QBrush, QPixmap
from PyQt6.QtCore import Qt, QRect
from datetime import datetime
import qt_material

class VotingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("설문 투표")
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # qt_material의 다크 퍼플 테마 적용
        qt_material.apply_stylesheet(self, theme='dark_purple.xml')

        # 주제 선택 버튼
        self.topic_btn = QPushButton('주제 선택')
        self.topic_btn.clicked.connect(self.select_topic)
        self.layout.addWidget(self.topic_btn)

        # 선택지 추가 버튼
        self.add_choice_btn = QPushButton('선택지 추가')
        self.add_choice_btn.clicked.connect(self.add_choice)
        self.layout.addWidget(self.add_choice_btn)

        # 투표 시작 버튼
        self.start_vote_btn = QPushButton('투표 시작')
        self.start_vote_btn.clicked.connect(self.start_voting)
        self.layout.addWidget(self.start_vote_btn)

        # 기록 불러오기 버튼
        self.load_record_btn = QPushButton('기록 불러오기')
        self.load_record_btn.clicked.connect(self.load_record)
        self.layout.addWidget(self.load_record_btn)

        self.labelbox = QVBoxLayout()
        self.layout.addLayout(self.labelbox)

        self.choices = [] # 선택지 리스트 초기화
        self.vote_counts = {} # 투표 결과 초기화
        self.stickers = {} # 스티커 초기화

    def select_topic(self):
        self.topic_input, ok = QInputDialog.getText(self, '투표 주제 입력', '주제를 입력하세요:')
        if ok and self.topic_input:
            self.topic_label = QLabel(self.topic_input)
            topic_font = self.topic_label.font()
            topic_font.setPointSize(30)
            topic_font.setBold(True)
            self.topic_label.setFont(topic_font)
            self.layout.addWidget(self.topic_label)

    def add_choice(self):
        text, ok = QInputDialog.getText(self, '선택지 추가', '선택지 이름을 입력하세요:')
        if ok and text:
            self.choices.append(text)
            self.vote_counts[text] = 0
            self.stickers[text] = []
            choice_label = QLabel(f'선택지: {text}')
            self.labelbox.addWidget(choice_label)

    def start_voting(self):
        if self.choices:
            self.hide()
            self.vote_screen = VotingScreen(self.choices, self.vote_counts, self.stickers, self)
            self.vote_screen.show()

    def load_record(self):
        file_name, _ = QInputDialog.getText(self, '기록 불러오기', '파일 이름을 입력하세요:')
        if file_name:
            try:
                with open(file_name, 'r', encoding='utf-8') as f:
                    reader = csv.reader(f)
                    self.topic_input = next(reader)[0]
                    self.choices = []
                    self.vote_counts = {}
                    self.stickers = {}
                    for row in reader:
                        choice, count, stickers = row
                        self.choices.append(choice)
                        self.vote_counts[choice] = int(count)
                        self.stickers[choice] = json.loads(stickers)
                    self.start_voting()
                    self.vote_screen.file_name = file_name  # 파일 이름 저장
            except FileNotFoundError:
                print("파일을 찾을 수 없습니다.")

    def reset_app(self):
        # 주제와 선택지를 초기화하고 처음부터 다시 시작
        self.topic_input = '' # 주제 초기화
        self.choices = [] # 선택지 리스트 초기화
        self.vote_counts = {} # 투표 결과 초기화
        self.stickers = {} # 스티커 초기화

        # 레이아웃에서 기존 위젯들을 모두 제거
        for i in reversed(range(self.labelbox.count())):
            self.labelbox.itemAt(i).widget().setParent(None) # 레이블 박스에 있는 모든 위젯 제거

        self.show()  # 초기 화면을 다시 보여줌

class VotingScreen(QWidget):
    def __init__(self, choices, vote_counts, stickers, parent):
        super().__init__()
        self.setWindowTitle("투표 화면")
        self.choices = choices
        self.vote_counts = vote_counts
        self.stickers = stickers
        self.sticker_size = 20
        self.voting_app = parent
        self.file_name = None  # 파일 이름 초기화
        self.init_ui()

    def init_ui(self):
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.showFullScreen()
        qt_material.apply_stylesheet(self, theme='dark_purple.xml')

    def paintEvent(self, event):
        painter = QPainter(self)
        rect_width = self.width() // len(self.choices)
        label_height = self.height() // 6  # 선택지 이름 배치 영역 높이
        sticker_area_height = self.height() - label_height  # 스티커를 붙일 공간

        default_color = QColor(255, 255, 255)  # 선택지 칸과 스티커 칸의 기본 배경색

        # 주제 텍스트를 상단에 표시
        painter.setPen(QColor(255, 255, 255))  # 흰색 텍스트
        topic_font = painter.font()
        topic_font.setBold(True)
        topic_font.setPointSize(30)  # 주제 텍스트 크기 30
        painter.setFont(topic_font)
        painter.drawText(QRect(0, 0, self.width(), label_height // 2), Qt.AlignmentFlag.AlignCenter, self.voting_app.topic_input)

        # 선택지 이름을 상단에 일렬로 배열
        for i, choice in enumerate(self.choices):
            # 선택지 이름 칸
            label_rect = QRect(i * rect_width, label_height // 2, rect_width, label_height // 2)
            painter.setBrush(QBrush(default_color))  # 기본 색상으로 선택지 이름 칸 배경 채움
            painter.setPen(QColor(0, 0, 0))  # 검은색 선
            painter.drawRect(label_rect)  # 검은색 테두리를 가진 직사각형으로 선택지 영역을 그림

            # 스티커를 붙일 공간
            sticker_rect = QRect(i * rect_width, label_height, rect_width, sticker_area_height)
            painter.setBrush(QBrush(default_color))  # 기본 배경색
            painter.setPen(QColor(0, 0, 0))  # 검은색 선
            painter.drawRect(sticker_rect)  # 검은색 테두리를 가진 직사각형으로 스티커 영역을 그림

            # 선택지 이름 글씨 설정: 검은색, 볼드체 해제, 크기 증가
            painter.setPen(QColor(0, 0, 0))  # 검은색
            font = painter.font()
            font.setBold(True)  # 볼드체
            font.setPointSize(20)  # 글씨 크기
            painter.setFont(font)

            # 선택지 이름을 그리기
            painter.drawText(label_rect, Qt.AlignmentFlag.AlignCenter, choice)

            # 선택지 이름 아래의 스티커 영역에 스티커 그리기
            for sticker_pos in self.stickers[choice]:
                painter.setBrush(QBrush(QColor(sticker_pos['color'])))
                # 스티커의 중심을 클릭한 위치로 설정
                painter.drawEllipse(int(sticker_pos['x']) - self.sticker_size // 2,
                                    int(sticker_pos['y']) - self.sticker_size // 2,
                                    self.sticker_size, self.sticker_size)

    def mousePressEvent(self, event):
        rect_width = self.width() // len(self.choices)
        label_height = self.height() // 6  # 선택지 이름 칸의 높이
        clicked_index = int(event.position().x() // rect_width)  # 선택된 선택지 인덱스

        # 스티커 영역은 선택지 이름 아래에 위치하므로, y좌표가 label_height보다 큰지 확인
        if event.position().y() > label_height and 0 <= clicked_index < len(self.choices):  # 스티커 공간에만 스티커 붙임
            choice = self.choices[clicked_index]
            self.vote_counts[choice] += 1

            # 클릭한 위치에 스티커 추가 (스티커의 중심을 클릭한 위치에 맞춤)
            random_color = QColor(random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)).name()
            self.stickers[choice].append({
                'x': int(event.position().x()),  # x 좌표는 클릭한 위치
                'y': int(event.position().y()),  # y 좌표도 클릭한 위치
                'color': random_color
            })
            self.update()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            # 주제를 키로 사용하여 투표 결과 저장
            if self.file_name:
                file_name = self.file_name
            else:
                file_name = f'{self.voting_app.topic_input}_{datetime.now().strftime("%Y%m%d")}.csv'
            
            with open(file_name, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                writer.writerow([self.voting_app.topic_input])
                for choice in self.choices:
                    writer.writerow([choice, self.vote_counts[choice], json.dumps(self.stickers[choice])])

            # 화면을 이미지로 저장
            if not os.path.exists('./result'):
                os.makedirs('./result')
            pixmap = QPixmap(self.size())
            self.render(pixmap)
            pixmap.save(f'./result/{self.voting_app.topic_input}_{datetime.now().strftime("%Y%m%d")}.png')

            self.close()
            self.voting_app.reset_app()  # 초기화면으로 돌아가 주제부터 다시 입력

def main():
    app = QApplication(sys.argv)
    
    # qt_material 테마 적용
    qt_material.apply_stylesheet(app, theme='dark_purple.xml')

    voting_app = VotingApp()
    voting_app.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
