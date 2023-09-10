import pandas as pd
import matplotlib.pyplot as plt

# Loading Data
fall_22_df = pd.read_csv("grd2022EN.csv", sep=',', names=["SECTION", "A", "B", "C", "D", "F", "A - F", "GPA", "I", "S", "U", "Q", "X", "TOTAL", "INSTRUCTOR"])
spring_23_df = pd.read_csv("grd20231EN.csv", sep=',', names=["SECTION", "A", "B", "C", "D", "F", "A - F", "GPA", "I", "S", "U", "Q", "X", "TOTAL", "INSTRUCTOR"])
all_sections_df = pd.read_csv("sections.csv", sep=',')

# Cleaning Data
fall_22_df_cleaned = fall_22_df.dropna().loc[fall_22_df['SECTION'] != 'SECTION']
spring_23_df_cleaned = spring_23_df.dropna().loc[spring_23_df['SECTION'] != 'SECTION']


combined_df = pd.concat([fall_22_df_cleaned, spring_23_df_cleaned], ignore_index=True)
combined_df['SECTION'] = combined_df['SECTION'].str[:-4]


combined_df.to_csv('combined.csv', index=False)

all_sections_df = all_sections_df.rename(columns={
    'section_number': 'SECTION',
    'a': 'A',
    'b': 'B',
    'c': 'C',
    'd': 'D',
    'f': 'F',
    'total_graded_students': 'TOTAL',
    'professor_name': 'INSTRUCTOR'
})

temp = pd.read_csv("sections.csv", sep=',')
all_sections_df['SECTION'] = temp['subject_code'].astype(str) + "-" + temp['course_number'].astype(str)

# Calculating GPA
all_sections_df['GPA'] = (
    all_sections_df['A'] * 4 +
    all_sections_df['B'] * 3 +
    all_sections_df['C'] * 2 +
    all_sections_df['D'] * 1
) / (all_sections_df['A'] + all_sections_df['B'] + all_sections_df['C'] + all_sections_df['D'] + all_sections_df['F'])

all_sections_df = all_sections_df[['SECTION', 'A','B','C','D','F','TOTAL','INSTRUCTOR','GPA']]
final_df = pd.concat([all_sections_df, combined_df], axis=0, ignore_index=True)
final_df['GPA'] = final_df['GPA'].astype(float)
final_df = final_df.drop(['X', 'Q', 'U', 'S', 'I','A - F'], axis=1)

# Functions
def top_three_by_gpa(SECTION):
    section_df = final_df[final_df['SECTION'] == SECTION]
    sorted_df = section_df.sort_values(by='GPA', ascending=False)
    unique_instructors_df = sorted_df.drop_duplicates(subset='INSTRUCTOR', keep='first')
    x = unique_instructors_df.iloc[:3]
    html_table = x.to_html(classes = 'table table-striped')
    return html_table


def plot_grades_piechart(row):
    grades = ['A', 'B', 'C', 'D', 'F']
    counts = [row['A'], row['B'], row['C'], row['D'], row['F']]
    colors = ['#800000', '#FFFFFF', '#808080', '#cc9999', '#e6b3b3']

    plt.figure(figsize=(10, 6))
    plt.pie(counts, colors=colors, startangle=90, wedgeprops=dict(width=0.3, edgecolor='black'))
    plt.title(f"Grade Distribution for {row['INSTRUCTOR']}'s Class", fontdict={'fontsize': 18, 'fontweight': 'bold'})
    plt.legend(grades, title="Grades", loc="best", fontsize=10, title_fontsize=12)
    plt.tight_layout()
    plt.show()
"""
top_instructors_df = top_three_by_gpa('CHEM-107')
first_professor = top_instructors_df.iloc[0]

plot_grades_piechart(first_professor)
first_professor.head()
print(first_professor['SECTION'])
"""
#with open('data1.html', 'w') as f:
#    f.write(top_three_by_gpa('CHEM-107'))


import sys
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout,
                             QLineEdit, QPushButton, QTextBrowser, QLabel, QScrollArea)
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# ... [Your previous data loading, cleaning, and function definitions]

class GradeAnalyzer(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_classes = []
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.label = QLabel("Enter Class (e.g., CHEM-107):", self)
        self.class_input = QLineEdit(self)
        self.submit_button = QPushButton('Submit', self)
        self.submit_button.clicked.connect(self.display_results)
        
        self.scroll_area = QScrollArea(self)
        self.scroll_content = QWidget(self.scroll_area)
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_area.setWidget(self.scroll_content)
        self.scroll_area.setWidgetResizable(True)
        
        layout.addWidget(self.label)
        layout.addWidget(self.class_input)
        layout.addWidget(self.submit_button)
        layout.addWidget(self.scroll_area)
        
        self.setLayout(layout)
        self.setGeometry(300, 300, 400, 600)
        self.setWindowTitle('Reville Rankings')
        self.show()

    def display_results(self):
        class_name = self.class_input.text()
        if class_name in self.selected_classes:
            return
        self.selected_classes.append(class_name)
        
        html_table = top_three_by_gpa(class_name)
        result_browser = QTextBrowser(self)
        result_browser.setHtml(html_table)
        
        figure = Figure(figsize=(5, 3))
        canvas = FigureCanvas(figure)
        
        top_instructors_df = final_df[final_df['SECTION'] == class_name].sort_values(by='GPA', ascending=False)
        first_professor = top_instructors_df.iloc[0]
        ax = figure.add_subplot(1, 1, 1)
        self.plot_grades_piechart(first_professor, ax)
        
        hlayout = QHBoxLayout()
        hlayout.addWidget(result_browser)
        hlayout.addWidget(canvas)
        
        self.scroll_layout.addLayout(hlayout)

    def plot_grades_piechart(self, row, ax):
        grades = ['A', 'B', 'C', 'D', 'F']
        counts = [row['A'], row['B'], row['C'], row['D'], row['F']]
        colors = ['#800000', '#FFFFFF', '#808080', '#cc9999', '#e6b3b3']
        
        ax.pie(counts, colors=colors, startangle=90, wedgeprops=dict(width=0.3, edgecolor='black'))
        ax.set_title(f"Grade Distribution for {row['INSTRUCTOR']}'s Class", fontdict={'fontsize': 12, 'fontweight': 'bold'})
        ax.legend(grades, title="Grades", loc="best", fontsize=8, title_fontsize=10)
        plt.tight_layout()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = GradeAnalyzer()
    sys.exit(app.exec_())
