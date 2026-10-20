import html
import json
import math
import os
from datetime import datetime

from reportlab.graphics.shapes import Drawing, Line, Polygon, Rect, String
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    Flowable,
    KeepTogether,
    PageBreak,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATASET = os.path.join(BASE_DIR, "restaurants.json")
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "pdf")
OUTPUT_PDF = os.path.join(OUTPUT_DIR, "Data_Modelling_Assignment_2a.pdf")

NAVY = colors.HexColor("#16324F")
BLUE = colors.HexColor("#2563A6")
TEAL = colors.HexColor("#0F766E")
PALE_BLUE = colors.HexColor("#EAF2FA")
PALE_TEAL = colors.HexColor("#E8F5F2")
LIGHT_GRAY = colors.HexColor("#F3F5F7")
MID_GRAY = colors.HexColor("#D5DCE3")
DARK_GRAY = colors.HexColor("#34404C")
WHITE = colors.white


def load_restaurants():
    documents = []
    with open(DATASET, "r", encoding="utf-8") as stream:
        for line in stream:
            line = line.strip()
            if line:
                documents.append(json.loads(line))
    return documents


def grade_scores(document):
    return [grade.get("score") for grade in document.get("grades", []) if isinstance(grade.get("score"), (int, float))]


def average(values):
    return sum(values) / len(values) if values else None


def fmt_number(value):
    if value is None:
        return "-"
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    if isinstance(value, float):
        return f"{value:.2f}"
    return str(value)


restaurants = load_restaurants()

q1_rows = [
    [
        item.get("restaurant_id", ""),
        item.get("name", ""),
        item.get("borough", ""),
        item.get("address", {}).get("zipcode", ""),
    ]
    for item in restaurants[:5]
]

bronx = [item for item in restaurants if item.get("borough") == "Bronx"]
q2_rows = [
    [item.get("restaurant_id", ""), item.get("name", ""), item.get("cuisine", ""), item.get("address", {}).get("zipcode", "")]
    for item in bronx[:5]
]

q3 = [item for item in restaurants if any(80 < score < 100 for score in grade_scores(item))]
q3_rows = [
    [
        item.get("restaurant_id", ""),
        item.get("name", ""),
        item.get("borough", ""),
        ", ".join(str(score) for score in grade_scores(item) if 80 < score < 100),
    ]
    for item in q3
]

q4 = [item for item in restaurants if "Reg" in item.get("name", "")]
q4_rows = [
    [item.get("restaurant_id", ""), item.get("name", ""), item.get("borough", ""), item.get("cuisine", "")]
    for item in q4[:10]
]

q5 = sorted(
    restaurants,
    key=lambda item: (
        item.get("cuisine", ""),
        "".join(chr(255 - ord(ch)) for ch in item.get("borough", "")),
    ),
)

# Use a stable, explicit two-pass sort to match { cuisine: 1, borough: -1 }.
q5 = sorted(restaurants, key=lambda item: item.get("borough", ""), reverse=True)
q5 = sorted(q5, key=lambda item: item.get("cuisine", ""))
q5_rows = [
    [item.get("cuisine", ""), item.get("borough", ""), item.get("name", ""), item.get("restaurant_id", "")]
    for item in q5[:15]
]

q6 = [item for item in restaurants if any(score < 5 for score in grade_scores(item))]
q6_rows = [
    [
        item.get("restaurant_id", ""),
        item.get("name", ""),
        item.get("borough", ""),
        ", ".join(str(score) for score in grade_scores(item) if score < 5),
    ]
    for item in q6[:10]
]

q7 = [
    item
    for item in restaurants
    if item.get("borough") == "Manhattan" and 2 in grade_scores(item) and 6 in grade_scores(item)
]
q7_rows = [
    [item.get("restaurant_id", ""), item.get("name", ""), item.get("borough", ""), "2, 6"]
    for item in q7[:10]
]

q8 = []
for item in restaurants:
    scores = grade_scores(item)
    q8.append(
        {
            "restaurant_id": item.get("restaurant_id", ""),
            "name": item.get("name", ""),
            "highest_score": max(scores) if scores else None,
        }
    )
q8.sort(key=lambda item: (-(item["highest_score"] if item["highest_score"] is not None else -math.inf), item["name"]))
q8_rows = [[item["restaurant_id"], item["name"], fmt_number(item["highest_score"])] for item in q8[:10]]

q9 = [
    item
    for item in restaurants
    if "A" in [grade.get("grade") for grade in item.get("grades", [])]
    and "B" in [grade.get("grade") for grade in item.get("grades", [])]
]
q9_rows = [
    [
        item.get("name", ""),
        f"{item.get('address', {}).get('building', '')} {item.get('address', {}).get('street', '')}",
        item.get("address", {}).get("zipcode", ""),
    ]
    for item in q9[:10]
]

turkish = []
for item in restaurants:
    if item.get("cuisine") == "Turkish":
        scores = grade_scores(item)
        turkish.append((average(scores), item))
turkish.sort(key=lambda pair: (-(pair[0] if pair[0] is not None else -math.inf), pair[1].get("name", "")))
q10_average, q10_item = turkish[0]
q10_rows = [[q10_item.get("restaurant_id", ""), q10_item.get("name", ""), q10_item.get("borough", ""), fmt_number(q10_average)]]


styles = getSampleStyleSheet()
styles.add(
    ParagraphStyle(
        name="CoverTitle",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=26,
        leading=31,
        textColor=WHITE,
        alignment=TA_LEFT,
        spaceAfter=12,
    )
)
styles.add(
    ParagraphStyle(
        name="CoverSub",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=17,
        textColor=colors.HexColor("#DDEBFA"),
    )
)
styles.add(
    ParagraphStyle(
        name="H1Custom",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=NAVY,
        spaceBefore=4,
        spaceAfter=9,
    )
)
styles.add(
    ParagraphStyle(
        name="H2Custom",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=12.5,
        leading=16,
        textColor=BLUE,
        spaceBefore=8,
        spaceAfter=5,
    )
)
styles.add(
    ParagraphStyle(
        name="BodyCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.4,
        leading=13.5,
        textColor=DARK_GRAY,
        spaceAfter=6,
    )
)
styles.add(
    ParagraphStyle(
        name="SmallCustom",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=7.8,
        leading=10.5,
        textColor=DARK_GRAY,
    )
)
styles.add(
    ParagraphStyle(
        name="TableHeader",
        parent=styles["SmallCustom"],
        fontName="Helvetica-Bold",
        textColor=WHITE,
    )
)
styles.add(
    ParagraphStyle(
        name="LabelWhite",
        parent=styles["BodyCustom"],
        fontName="Helvetica-Bold",
        textColor=WHITE,
    )
)
styles.add(
    ParagraphStyle(
        name="Callout",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9,
        leading=13,
        textColor=NAVY,
        backColor=PALE_BLUE,
        borderColor=colors.HexColor("#B8D2EC"),
        borderWidth=0.7,
        borderPadding=7,
        spaceBefore=4,
        spaceAfter=8,
    )
)
styles.add(
    ParagraphStyle(
        name="CodeCustom",
        fontName="Courier",
        fontSize=7.2,
        leading=9.3,
        textColor=colors.HexColor("#18212B"),
        backColor=colors.HexColor("#F4F6F8"),
        borderColor=MID_GRAY,
        borderWidth=0.6,
        borderPadding=7,
        leftIndent=0,
        rightIndent=0,
        spaceBefore=3,
        spaceAfter=7,
    )
)


def para(text, style="BodyCustom"):
    return Paragraph(text, styles[style])


def code_block(text):
    return Preformatted(text.strip(), styles["CodeCustom"])


def result_table(headers, rows, widths=None, font_size=7.2):
    processed = []
    processed.append([Paragraph(html.escape(str(cell)), styles["TableHeader"]) for cell in headers])
    for row in rows:
        processed.append([Paragraph(html.escape(str(cell)), styles["SmallCustom"]) for cell in row])
    table = Table(processed, colWidths=widths, repeatRows=1, hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), NAVY),
                ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), font_size),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.35, MID_GRAY),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_GRAY]),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return table


def question_header(number, title):
    data = [[Paragraph(f"Q{number}", styles["LabelWhite"]), Paragraph(f"<b>{html.escape(title)}</b>", styles["BodyCustom"])]]
    table = Table(data, colWidths=[0.55 * inch, 6.35 * inch], hAlign="LEFT")
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, 0), TEAL),
                ("TEXTCOLOR", (0, 0), (0, 0), WHITE),
                ("BACKGROUND", (1, 0), (1, 0), PALE_TEAL),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor("#9CCDC6")),
            ]
        )
    )
    return table


class CoverPanel(Flowable):
    def __init__(self, width=7.2 * inch, height=3.0 * inch):
        super().__init__()
        self.width = width
        self.height = height

    def draw(self):
        canvas = self.canv
        canvas.setFillColor(NAVY)
        canvas.roundRect(0, 0, self.width, self.height, 14, fill=1, stroke=0)
        canvas.setFillColor(BLUE)
        canvas.circle(self.width - 0.45 * inch, self.height - 0.45 * inch, 0.8 * inch, fill=1, stroke=0)
        canvas.setFillColor(TEAL)
        canvas.circle(self.width - 1.1 * inch, 0.35 * inch, 0.55 * inch, fill=1, stroke=0)
        canvas.setFillColor(WHITE)
        canvas.setFont("Helvetica-Bold", 10)
        canvas.drawString(0.42 * inch, self.height - 0.55 * inch, "26PDPA0 - DATA MODELLING AND VISUALIZATION")
        canvas.setFont("Helvetica-Bold", 27)
        canvas.drawString(0.42 * inch, self.height - 1.22 * inch, "Assignment 2a")
        canvas.setFont("Helvetica", 15)
        canvas.drawString(0.42 * inch, self.height - 1.63 * inch, "MongoDB Exercises and NoSQL Data Models")
        canvas.setFont("Helvetica", 9.5)
        canvas.setFillColor(colors.HexColor("#DDEBFA"))
        canvas.drawString(0.42 * inch, 0.52 * inch, "Document model | Wide-column model | Graph model")


def graph_diagram():
    drawing = Drawing(500, 245)

    def node(x, y, w, label, fill):
        drawing.add(Rect(x, y, w, 38, 7, fillColor=fill, strokeColor=NAVY, strokeWidth=1.1))
        drawing.add(String(x + w / 2, y + 14, label, textAnchor="middle", fontName="Helvetica-Bold", fontSize=9, fillColor=NAVY))

    def arrow(x1, y1, x2, y2, label, label_x, label_y, dashed=False):
        line = Line(x1, y1, x2, y2, strokeColor=BLUE, strokeWidth=1.25)
        if dashed:
            line.strokeDashArray = [4, 3]
        drawing.add(line)
        angle = math.atan2(y2 - y1, x2 - x1)
        size = 6
        p1 = (x2, y2)
        p2 = (x2 - size * math.cos(angle - 0.5), y2 - size * math.sin(angle - 0.5))
        p3 = (x2 - size * math.cos(angle + 0.5), y2 - size * math.sin(angle + 0.5))
        drawing.add(Polygon([p1[0], p1[1], p2[0], p2[1], p3[0], p3[1]], fillColor=BLUE, strokeColor=BLUE))
        drawing.add(String(label_x, label_y, label, fontName="Helvetica", fontSize=7.2, fillColor=DARK_GRAY, textAnchor="middle"))

    node(10, 108, 100, "Customer", PALE_TEAL)
    node(195, 108, 100, "Order", PALE_BLUE)
    node(390, 180, 100, "Restaurant", colors.HexColor("#FFF2D8"))
    node(390, 38, 100, "FoodItem", colors.HexColor("#FFF2D8"))
    node(195, 10, 120, "DeliveryPartner", PALE_TEAL)

    arrow(110, 127, 195, 127, "PLACED", 152, 136)
    arrow(295, 137, 390, 195, "FROM_RESTAURANT", 347, 174)
    arrow(440, 180, 440, 76, "OFFERS", 462, 128)
    arrow(295, 116, 390, 68, "CONTAINS", 344, 81)
    arrow(255, 48, 245, 108, "DELIVERED", 217, 77)
    arrow(95, 146, 390, 205, "RATED_RESTAURANT", 239, 190, dashed=True)
    arrow(95, 110, 390, 56, "RATED_ITEM", 243, 62, dashed=True)

    drawing.add(String(10, 228, "Core property graph", fontName="Helvetica-Bold", fontSize=11, fillColor=NAVY))
    drawing.add(String(10, 214, "Solid: transaction flow   Dashed: customer feedback", fontName="Helvetica", fontSize=7.5, fillColor=DARK_GRAY))
    return drawing


def on_page(canvas, doc):
    canvas.saveState()
    page_number = canvas.getPageNumber()
    if page_number > 1:
        canvas.setStrokeColor(MID_GRAY)
        canvas.setLineWidth(0.5)
        canvas.line(doc.leftMargin, letter[1] - 0.45 * inch, letter[0] - doc.rightMargin, letter[1] - 0.45 * inch)
        canvas.setFont("Helvetica-Bold", 8)
        canvas.setFillColor(NAVY)
        canvas.drawString(doc.leftMargin, letter[1] - 0.34 * inch, "DATA MODELLING AND VISUALIZATION - ASSIGNMENT 2a")
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(colors.HexColor("#65717D"))
    canvas.drawRightString(letter[0] - doc.rightMargin, 0.35 * inch, f"Page {page_number}")
    canvas.drawString(doc.leftMargin, 0.35 * inch, "MongoDB primer dataset | 25,359 documents")
    canvas.restoreState()


story = []

# Cover page
story.append(Spacer(1, 0.7 * inch))
story.append(CoverPanel())
story.append(Spacer(1, 0.42 * inch))
student_table = Table(
    [
        [para("<b>Student name</b>", "SmallCustom"), para("________________________________________", "SmallCustom")],
        [para("<b>Register number</b>", "SmallCustom"), para("________________________________________", "SmallCustom")],
        [para("<b>Submission date</b>", "SmallCustom"), para("________________________________________", "SmallCustom")],
    ],
    colWidths=[1.45 * inch, 4.9 * inch],
    hAlign="LEFT",
)
student_table.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (0, -1), LIGHT_GRAY),
            ("BOX", (0, 0), (-1, -1), 0.6, MID_GRAY),
            ("INNERGRID", (0, 0), (-1, -1), 0.4, MID_GRAY),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 8),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]
    )
)
story.append(student_table)
story.append(Spacer(1, 0.35 * inch))
story.append(
    para(
        "<b>Scope.</b> This submission answers all four questions. Question 1 uses the imported "
        "MongoDB restaurant collection; Questions 2-4 present document, wide-column, and graph models "
        "designed around their stated access patterns.",
        "Callout",
    )
)
story.append(Spacer(1, 0.15 * inch))
story.append(para("Prepared using MongoDB 9.0.4 and Mongosh 2.13.0.", "SmallCustom"))
story.append(PageBreak())

# Q1 overview
story.append(para("Question 1 - MongoDB Restaurant Queries", "H1Custom"))
story.append(
    para(
        "The collection contains <b>25,359</b> restaurant documents. Large result sets are represented by "
        "their exact match count and a compact sample so the output remains readable. Queries can be run "
        "unchanged in <b>mongosh</b> against <b>assignment2.restaurants</b>.",
        "BodyCustom",
    )
)
story.append(
    result_table(
        ["Database", "Collection", "Documents", "Core fields"],
        [["assignment2", "restaurants", "25,359", "address, borough, cuisine, grades, name, restaurant_id"]],
        [1.2 * inch, 1.2 * inch, 0.85 * inch, 3.7 * inch],
    )
)
story.append(Spacer(1, 0.16 * inch))

story.append(question_header(1, "Project restaurant ID, name, borough, and zip code; exclude _id"))
story.append(code_block('''db.restaurants.find(
  {},
  { _id: 0, restaurant_id: 1, name: 1,
    borough: 1, "address.zipcode": 1 }
)'''))
story.append(para("Output: 25,359 documents. First five are shown below.", "SmallCustom"))
story.append(result_table(["Restaurant ID", "Name", "Borough", "Zip code"], q1_rows, [1.05 * inch, 3.05 * inch, 1.35 * inch, 1.0 * inch]))
story.append(Spacer(1, 0.16 * inch))

story.append(question_header(2, "Display the first five restaurants in the Bronx"))
story.append(code_block('''db.restaurants.find({ borough: "Bronx" }).limit(5)'''))
story.append(para("Output: exactly five complete restaurant documents; identifying fields are shown.", "SmallCustom"))
story.append(result_table(["Restaurant ID", "Name", "Cuisine", "Zip code"], q2_rows, [1.05 * inch, 3.0 * inch, 1.45 * inch, 1.0 * inch]))
story.append(PageBreak())

story.append(question_header(3, "Find restaurants with a score greater than 80 and less than 100"))
story.append(code_block('''db.restaurants.find({
  grades: { $elemMatch: { score: { $gt: 80, $lt: 100 } } }
})'''))
story.append(para(f"Output: <b>{len(q3)}</b> restaurants. All matches are listed.", "SmallCustom"))
story.append(result_table(["Restaurant ID", "Name", "Borough", "Matching score(s)"], q3_rows, [1.0 * inch, 3.3 * inch, 1.25 * inch, 1.15 * inch]))
story.append(Spacer(1, 0.18 * inch))

story.append(question_header(4, "Find restaurants containing 'Reg' somewhere in the name"))
story.append(code_block('''db.restaurants.find(
  { name: /Reg/ },
  { _id: 0, restaurant_id: 1, name: 1,
    borough: 1, cuisine: 1 }
)'''))
story.append(para(f"Output: <b>{len(q4)}</b> matches. First ten are shown.", "SmallCustom"))
story.append(result_table(["Restaurant ID", "Name", "Borough", "Cuisine"], q4_rows, [1.0 * inch, 2.75 * inch, 1.25 * inch, 1.6 * inch]))
story.append(PageBreak())

story.append(question_header(5, "Sort cuisine ascending and borough descending within each cuisine"))
story.append(code_block('''db.restaurants.find({}).sort({ cuisine: 1, borough: -1 })'''))
story.append(para("Output: 25,359 sorted documents. First fifteen are shown.", "SmallCustom"))
story.append(result_table(["Cuisine", "Borough", "Restaurant", "Restaurant ID"], q5_rows, [1.45 * inch, 1.2 * inch, 3.0 * inch, 1.0 * inch]))
story.append(Spacer(1, 0.18 * inch))

story.append(question_header(6, "Find restaurants with at least one grade score below 5"))
story.append(code_block('''db.restaurants.find({ "grades.score": { $lt: 5 } })'''))
story.append(para(f"Output: <b>{len(q6):,}</b> matches. First ten are shown.", "SmallCustom"))
story.append(result_table(["Restaurant ID", "Name", "Borough", "Score(s) below 5"], q6_rows, [1.0 * inch, 3.1 * inch, 1.25 * inch, 1.25 * inch]))
story.append(PageBreak())

story.append(question_header(7, "Manhattan restaurants having a score of 2 and a score of 6"))
story.append(code_block('''db.restaurants.find({
  borough: "Manhattan",
  "grades.score": { $all: [2, 6] }
})'''))
story.append(
    para(
        "The <b>$all</b> operator checks the score values across the embedded grades array. "
        f"Output: <b>{len(q7)}</b> matches; first ten are shown.",
        "SmallCustom",
    )
)
story.append(result_table(["Restaurant ID", "Name", "Borough", "Required scores"], q7_rows, [1.0 * inch, 3.1 * inch, 1.3 * inch, 1.2 * inch]))
story.append(Spacer(1, 0.2 * inch))

story.append(question_header(8, "Find the highest score for each restaurant"))
story.append(code_block('''db.restaurants.aggregate([
  { $project: {
      _id: 0, restaurant_id: 1, name: 1,
      highest_score: { $max: "$grades.score" }
  }},
  { $sort: { highest_score: -1, name: 1 } }
])'''))
story.append(para("Output: one result per restaurant. The ten highest maximum scores are shown.", "SmallCustom"))
story.append(result_table(["Restaurant ID", "Restaurant", "Highest score"], q8_rows, [1.2 * inch, 4.4 * inch, 1.1 * inch]))
story.append(PageBreak())

story.append(question_header(9, "Find names and addresses of restaurants having both A and B grades"))
story.append(code_block('''db.restaurants.find(
  { "grades.grade": { $all: ["A", "B"] } },
  { _id: 0, name: 1, address: 1 }
)'''))
story.append(para(f"Output: <b>{len(q9):,}</b> matches. First ten are shown.", "SmallCustom"))
story.append(result_table(["Restaurant", "Street address", "Zip code"], q9_rows, [2.8 * inch, 3.0 * inch, 0.9 * inch]))
story.append(Spacer(1, 0.22 * inch))

story.append(question_header(10, "Find the Turkish restaurant with the highest average score"))
story.append(code_block('''db.restaurants.aggregate([
  { $match: { cuisine: "Turkish" } },
  { $project: {
      _id: 0, restaurant_id: 1, name: 1,
      borough: 1, cuisine: 1,
      average_score: { $avg: "$grades.score" }
  }},
  { $sort: { average_score: -1 } },
  { $limit: 1 }
])'''))
story.append(para(f"Output: highest average among {len(turkish)} Turkish restaurants.", "SmallCustom"))
story.append(result_table(["Restaurant ID", "Name", "Borough", "Average score"], q10_rows, [1.15 * inch, 3.3 * inch, 1.2 * inch, 1.1 * inch]))
story.append(PageBreak())

# Q2
story.append(para("Question 2 - Document Data Model", "H1Custom"))
story.append(
    para(
        "A course is the aggregate root. Modules and resources are embedded because they are normally read and "
        "updated in the context of one course. Instructor details are included as a snapshot; an instructor ID can "
        "also reference a separate instructor collection when profiles are shared across many courses.",
        "BodyCustom",
    )
)
story.append(code_block('''{
  "_id": ObjectId("..."),
  "course_code": "DS301",
  "title": "Applied Data Science with Python",
  "description": "Data preparation, modelling and evaluation.",
  "category": "Data Science",
  "level": "Intermediate",
  "instructor": {
    "instructor_id": "INS104",
    "name": "Dr. Maya Rao",
    "email": "maya.rao@example.edu",
    "expertise": ["Python", "Machine Learning"]
  },
  "prerequisites": [
    { "course_code": "PY101", "title": "Python Fundamentals" },
    { "course_code": "ST101", "title": "Basic Statistics" }
  ],
  "modules": [
    {
      "module_no": 1,
      "title": "Data Preparation",
      "sequence": 1,
      "estimated_minutes": 180,
      "resources": [
        { "resource_id": "R101", "type": "video",
          "title": "Cleaning Data", "url": "/videos/r101",
          "duration_minutes": 24 },
        { "resource_id": "R102", "type": "reading",
          "title": "Missing Values", "url": "/readings/r102",
          "estimated_minutes": 20 },
        { "resource_id": "R103", "type": "quiz",
          "title": "Preparation Quiz", "questions": 10,
          "max_score": 20, "attempts_allowed": 2 },
        { "resource_id": "R104", "type": "assignment",
          "title": "Clean a Dataset", "max_score": 50,
          "submission_type": "notebook" }
      ]
    }
  ],
  "metadata": {
    "language": "English", "duration_hours": 24,
    "tags": ["python", "analytics", "machine-learning"],
    "published": true, "version": 3
  },
  "created_at": ISODate("2026-08-01T09:00:00Z"),
  "updated_at": ISODate("2026-10-01T11:30:00Z")
}'''))
story.append(PageBreak())

story.append(para("Design Decisions and Indexes", "H2Custom"))
story.append(
    result_table(
        ["Decision", "Reason"],
        [
            ["Embed modules", "Modules belong to one course and are normally retrieved with it."],
            ["Embed resources", "Different resource types can use flexible type-specific fields."],
            ["Instructor snapshot", "Preserves the displayed instructor data; instructor_id supports a separate master record."],
            ["Prerequisite references", "Course codes avoid duplicating complete prerequisite course documents."],
            ["Version and timestamps", "Support publishing workflow, cache invalidation and auditability."],
        ],
        [1.7 * inch, 5.0 * inch],
    )
)
story.append(Spacer(1, 0.18 * inch))
story.append(code_block('''db.courses.createIndex({ course_code: 1 }, { unique: true })
db.courses.createIndex({ category: 1, level: 1 })
db.courses.createIndex({ "instructor.instructor_id": 1 })
db.courses.createIndex({ "metadata.tags": 1 })
db.courses.createIndex({ "modules.resources.type": 1 })'''))
story.append(
    para(
        "<b>Scaling note.</b> If a course grows close to MongoDB's document-size limit or resources need frequent "
        "independent updates, store resource metadata in a separate <b>resources</b> collection and keep only "
        "resource IDs and ordering information inside each module.",
        "Callout",
    )
)
story.append(PageBreak())

# Q3
story.append(para("Question 3 - Wide-Column Data Model", "H1Custom"))
story.append(
    para(
        "The main access pattern is: retrieve one passenger's newest transactions without scanning other "
        "passengers. A month bucket keeps partitions bounded, while transaction_timestamp in descending order "
        "places the newest transaction first.",
        "BodyCustom",
    )
)
story.append(para("Primary table: passenger history by month", "H2Custom"))
story.append(code_block('''CREATE TABLE passenger_transactions_by_month (
  passenger_id        text,
  history_month       text,       // Example: "2026-10"
  transaction_ts      timestamp,
  booking_reference   text,
  train_number        text,
  journey_date        date,
  transaction_type    text,       // BOOKING, CANCELLATION, MODIFY
  transaction_status  text,       // SUCCESS, FAILED, PENDING
  from_station        text,
  to_station          text,
  travel_class        text,
  amount              decimal,
  PRIMARY KEY (
    (passenger_id, history_month),
    transaction_ts,
    booking_reference
  )
) WITH CLUSTERING ORDER BY (
  transaction_ts DESC,
  booking_reference ASC
);'''))
story.append(
    result_table(
        ["Key component", "Columns", "Purpose"],
        [
            ["Partition key", "passenger_id, history_month", "Routes one passenger-month to one partition and prevents unbounded growth."],
            ["Clustering keys", "transaction_ts DESC, booking_reference", "Returns newest records first and uniquely orders same-time events."],
            ["Regular columns", "train, journey, type, status, route, class, amount", "Makes each transaction row self-contained for fast reads."],
        ],
        [1.25 * inch, 2.2 * inch, 3.25 * inch],
    )
)
story.append(Spacer(1, 0.18 * inch))
story.append(para("Query for recent passenger transactions", "H2Custom"))
story.append(code_block('''SELECT *
FROM passenger_transactions_by_month
WHERE passenger_id = 'P10027'
  AND history_month = '2026-10'
LIMIT 20;'''))
story.append(para("For history spanning several months, the application queries the required month buckets in parallel and merges the already time-ordered results.", "Callout"))
story.append(PageBreak())

story.append(para("Secondary table: audit trail by booking reference", "H2Custom"))
story.append(
    para(
        "Wide-column systems commonly duplicate data for a second access pattern. This table retrieves every "
        "booking, modification and cancellation for a booking reference without filtering the passenger table.",
        "BodyCustom",
    )
)
story.append(code_block('''CREATE TABLE booking_transactions_by_reference (
  booking_reference   text,
  transaction_ts      timestamp,
  passenger_id        text,
  train_number        text,
  journey_date        date,
  transaction_type    text,
  transaction_status  text,
  PRIMARY KEY (booking_reference, transaction_ts)
) WITH CLUSTERING ORDER BY (transaction_ts DESC);'''))
story.append(code_block('''SELECT *
FROM booking_transactions_by_reference
WHERE booking_reference = 'BR893541';'''))
story.append(
    result_table(
        ["Passenger ID", "Month", "Timestamp", "Booking ref", "Train", "Type", "Status"],
        [
            ["P10027", "2026-10", "2026-10-19 09:42", "BR893541", "12628", "MODIFY", "SUCCESS"],
            ["P10027", "2026-10", "2026-10-18 20:11", "BR893541", "12628", "BOOKING", "SUCCESS"],
        ],
        [0.8 * inch, 0.65 * inch, 1.1 * inch, 0.9 * inch, 0.65 * inch, 0.75 * inch, 0.85 * inch],
        6.7,
    )
)
story.append(Spacer(1, 0.2 * inch))
story.append(
    para(
        "<b>Write strategy.</b> Each transaction is written to both tables. This controlled denormalization is "
        "intentional: it trades a small amount of storage for predictable, scan-free reads.",
        "Callout",
    )
)
story.append(PageBreak())

# Q4
story.append(para("Question 4 - Graph Data Model", "H1Custom"))
story.append(
    para(
        "Orders are represented as nodes because they carry status, time and amount and connect several actors. "
        "Ratings are relationships because they express a customer's opinion about a restaurant or food item. "
        "This structure supports order history, fulfilment tracking and recommendations through short graph traversals.",
        "BodyCustom",
    )
)
story.append(graph_diagram())
story.append(Spacer(1, 0.1 * inch))
story.append(para("Node Types and Properties", "H2Custom"))
story.append(
    result_table(
        ["Node label", "Key properties", "Purpose"],
        [
            ["Customer", "customer_id, name, city", "Person placing orders and creating ratings."],
            ["Restaurant", "restaurant_id, name, cuisine, location, avg_rating", "Merchant from which an order is placed."],
            ["FoodItem", "item_id, name, category, price, available", "Menu item offered by a restaurant."],
            ["Order", "order_id, ordered_at, total_amount, status", "Transaction connecting customer, restaurant, items and delivery."],
            ["DeliveryPartner", "partner_id, name, vehicle_type, rating", "Partner assigned to fulfil an order."],
        ],
        [1.2 * inch, 2.85 * inch, 2.65 * inch],
    )
)
story.append(PageBreak())

story.append(para("Relationship Types and Properties", "H2Custom"))
story.append(
    result_table(
        ["Relationship", "Direction", "Relevant properties"],
        [
            ["PLACED", "Customer -> Order", "ordered_at"],
            ["FROM_RESTAURANT", "Order -> Restaurant", "restaurant snapshot or branch_id (optional)"],
            ["CONTAINS", "Order -> FoodItem", "quantity, unit_price, customization"],
            ["OFFERS", "Restaurant -> FoodItem", "current_price, available_since"],
            ["DELIVERED", "DeliveryPartner -> Order", "assigned_at, picked_up_at, delivered_at"],
            ["RATED_RESTAURANT", "Customer -> Restaurant", "rating, comment, reviewed_at"],
            ["RATED_ITEM", "Customer -> FoodItem", "rating, comment, reviewed_at"],
            ["SIMILAR_TO", "Restaurant <-> Restaurant", "similarity_score, basis, calculated_at"],
        ],
        [1.55 * inch, 1.65 * inch, 3.5 * inch],
    )
)
story.append(Spacer(1, 0.2 * inch))
story.append(para("Recommendation traversal", "H2Custom"))
story.append(code_block('''MATCH (c:Customer {customer_id: $customerId})
      -[:PLACED]->(:Order)-[:FROM_RESTAURANT]->(visited:Restaurant)
MATCH (visited)-[s:SIMILAR_TO]-(candidate:Restaurant)
WHERE NOT EXISTS {
  MATCH (c)-[:PLACED]->(:Order)
        -[:FROM_RESTAURANT]->(candidate)
}
RETURN candidate.restaurant_id AS restaurant_id,
       candidate.name AS restaurant,
       candidate.cuisine AS cuisine,
       max(s.similarity_score) AS score
ORDER BY score DESC, candidate.avg_rating DESC
LIMIT 10;'''))
story.append(
    para(
        "The traversal starts with restaurants from the customer's previous orders, follows precomputed similarity "
        "edges, removes restaurants already ordered from, and ranks the remaining candidates. Similarity can combine "
        "shared cuisine, overlapping menu categories, geographic distance and rating patterns.",
        "Callout",
    )
)
story.append(PageBreak())

# Closing page
story.append(para("Conclusion", "H1Custom"))
story.append(
    para(
        "The four solutions demonstrate query-driven NoSQL modelling. MongoDB embeds inspection grades within each "
        "restaurant, the learning platform embeds course-owned modules and polymorphic resources, the railway model "
        "uses partition and clustering keys for bounded chronological reads, and the food-delivery graph makes "
        "customer-order-restaurant relationships directly traversable.",
        "BodyCustom",
    )
)
story.append(
    result_table(
        ["Question", "Model / technique", "Primary design objective"],
        [
            ["Q1", "MongoDB queries and aggregation", "Correct filtering, projection, sorting and array analysis."],
            ["Q2", "Document model", "Flexible course structures retrieved as cohesive aggregates."],
            ["Q3", "Wide-column model", "Fast passenger history reads with bounded partitions."],
            ["Q4", "Property graph", "Efficient order-history traversal and restaurant recommendations."],
        ],
        [0.7 * inch, 2.1 * inch, 3.9 * inch],
    )
)
story.append(Spacer(1, 0.3 * inch))
story.append(
    para(
        "<b>Reproducibility.</b> Query counts and displayed examples were generated from the locally imported "
        "MongoDB primer restaurant dataset containing 25,359 newline-delimited JSON documents.",
        "Callout",
    )
)


os.makedirs(OUTPUT_DIR, exist_ok=True)
document = SimpleDocTemplate(
    OUTPUT_PDF,
    pagesize=letter,
    rightMargin=0.65 * inch,
    leftMargin=0.65 * inch,
    topMargin=0.62 * inch,
    bottomMargin=0.58 * inch,
    title="Data Modelling and Visualization - Assignment 2a",
    author="Student Submission",
    subject="MongoDB exercises and NoSQL data models",
)
document.build(story, onFirstPage=on_page, onLaterPages=on_page)

print(OUTPUT_PDF)
print(f"pages_data_source={len(restaurants)}")
print(f"q3={len(q3)} q4={len(q4)} q6={len(q6)} q7={len(q7)} q9={len(q9)} q10={q10_item.get('name')}:{fmt_number(q10_average)}")
