import os

from pptx import Presentation
from pptx.util import Cm, Pt
from pptx.enum.shapes import MSO_AUTO_SHAPE_TYPE
from pptx.enum.text import MSO_VERTICAL_ANCHOR
from pptx.dml.color import RGBColor


# ==================================================
# 確定値
# ==================================================

# X座標
NIGHT_X = Cm(0.911)
DAY_X = Cm(17.421)

# サイズ
BOX_WIDTH = Cm(15.239)

BOX_HEIGHT_SINGLE = Cm(5.165)
BOX_HEIGHT_MULTI = Cm(3.379)

# Y座標
Y_POSITIONS = {
    1: [Cm(7.595)],
    2: [
        Cm(5.906),
        Cm(11.071)
    ],
    3: [
        Cm(4.828),
        Cm(8.680),
        Cm(12.532)
    ]
}

# 背景色
NIGHT_FILL = RGBColor(51, 86, 147)      # #335693
DAY_FILL = RGBColor(255, 255, 255)      # #FFFFFF

# 文字色
NIGHT_FONT = RGBColor(255, 255, 255)    # #FFFFFF
DAY_FONT = RGBColor(0, 0, 0)            # #000000


# ==================================================
# 表示文字作成
# ==================================================

def build_display_text(
    venue,
    grade,
    status
):
    """
    元PPTと同じ考え方で
    1本の文字列を作る
    """

    venue = str(venue).strip()
    grade = str(grade).strip()
    status = str(status).strip()

    return (
        f"{venue}"
        f"　     "
        f"{grade}"
        f"      　"
        f"{status}"
    )


# ==================================================
# 四角作成
# ==================================================

def add_schedule_box(
    slide,
    x,
    y,
    width,
    height,
    text,
    fill_color,
    font_color
):

    shape = slide.shapes.add_shape(
        MSO_AUTO_SHAPE_TYPE.RECTANGLE,
        x,
        y,
        width,
        height
    )

    # --------------------------
    # 塗りつぶし
    # --------------------------

    shape.fill.solid()
    shape.fill.fore_color.rgb = fill_color

    # --------------------------
    # 枠線なし
    # --------------------------

    shape.line.fill.background()

    # --------------------------
    # テキスト
    # --------------------------

    tf = shape.text_frame

    tf.clear()

    tf.vertical_anchor = (
        MSO_VERTICAL_ANCHOR.MIDDLE
    )

    p = tf.paragraphs[0]

    run = p.add_run()
    run.text = text

    font = run.font

    font.name = "Rockwell"
    font.size = Pt(28)
    font.bold = True
    font.color.rgb = font_color

    return shape


# ==================================================
# メイン
# ==================================================

def create_powerpoint(
    day_text_list,
    night_text_list
):

    template_path = os.path.join(
        os.getcwd(),
        "src",
        "元データ.pptx"
    )

    if not os.path.exists(template_path):
        raise FileNotFoundError(
            f"テンプレートが存在しません: {template_path}"
        )

    prs = Presentation(template_path)
    slide = prs.slides[0]

    # --------------------------
    # 最大3場
    # --------------------------

    if len(day_text_list) > 3:
        raise Exception(
            f"デイが3場を超えています: {len(day_text_list)}"
        )

    if len(night_text_list) > 3:
        raise Exception(
            f"ナイターが3場を超えています: {len(night_text_list)}"
        )

    # ==================================================
    # ナイター
    # ==================================================

    night_count = len(night_text_list)

    if night_count > 0:

        height = (
            BOX_HEIGHT_SINGLE
            if night_count == 1
            else BOX_HEIGHT_MULTI
        )

        for idx, item in enumerate(
            night_text_list
        ):

            if isinstance(item, dict):

                text = build_display_text(
                    item.get("venue", ""),
                    item.get("grade", ""),
                    item.get("status", "")
                )

            else:

                text = str(item)

            add_schedule_box(
                slide=slide,
                x=NIGHT_X,
                y=Y_POSITIONS[night_count][idx],
                width=BOX_WIDTH,
                height=height,
                text=text,
                fill_color=NIGHT_FILL,
                font_color=NIGHT_FONT
            )

    # ==================================================
    # デイ
    # ==================================================

    day_count = len(day_text_list)

    if day_count > 0:

        height = (
            BOX_HEIGHT_SINGLE
            if day_count == 1
            else BOX_HEIGHT_MULTI
        )

        for idx, item in enumerate(
            day_text_list
        ):

            if isinstance(item, dict):

                text = build_display_text(
                    item.get("venue", ""),
                    item.get("grade", ""),
                    item.get("status", "")
                )

            else:

                text = str(item)

            add_schedule_box(
                slide=slide,
                x=DAY_X,
                y=Y_POSITIONS[day_count][idx],
                width=BOX_WIDTH,
                height=height,
                text=text,
                fill_color=DAY_FILL,
                font_color=DAY_FONT
            )

    # ==================================================
    # 保存
    # ==================================================

    upload_dir = os.path.join(
        os.getcwd(),
        "uploads"
    )

    os.makedirs(
        upload_dir,
        exist_ok=True
    )

    output_path = os.path.join(
        upload_dir,
        "場内放映予定.pptx"
    )

    prs.save(output_path)

    print(
        f"[SUCCESS] {output_path}"
    )

    return output_path
