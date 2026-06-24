import os

from pptx import Presentation
from pptx.dml.color import RGBColor

# ----------------------------------
# 確定値
# ----------------------------------

NIGHT_X = 430746
DAY_X = 6339932

BOX_WIDTH = 5485921

BOX_HEIGHT_SINGLE = 1859264
BOX_HEIGHT_MULTI = 1216325

Y_POSITIONS = {
    1: [2734305],
    2: [2126142, 3985406],
    3: [1718949, 3122764, 4526579],
}


def create_powerpoint(day_text_list, night_text_list):

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

    #
    # 仕様上 1～3場
    #
    if len(night_text_list) > 3:
        raise Exception(
            f"ナイターが3場を超えています: {len(night_text_list)}場"
        )

    if len(day_text_list) > 3:
        raise Exception(
            f"デイが3場を超えています: {len(day_text_list)}場"
        )

    #
    # ナイター
    #
    night_count = len(night_text_list)

    if night_count > 0:

        box_height = (
            BOX_HEIGHT_SINGLE
            if night_count == 1
            else BOX_HEIGHT_MULTI
        )

        for idx, text in enumerate(night_text_list):

            textbox = slide.shapes.add_textbox(
                NIGHT_X,
                Y_POSITIONS[night_count][idx],
                BOX_WIDTH,
                box_height
            )

            textbox.text = text

            # 見本に合わせる
            p = textbox.text_frame.paragraphs[0]
            p.font.name = "Rockwell"
            p.font.bold = True
            p.font.size = prs.slides[0].shapes[0].text_frame.paragraphs[0].font.size

            try:
                p.font.color.rgb = RGBColor(
                    255,
                    255,
                    255
                )
            except Exception:
                pass

    #
    # デイ
    #
    day_count = len(day_text_list)

    if day_count > 0:

        box_height = (
            BOX_HEIGHT_SINGLE
            if day_count == 1
            else BOX_HEIGHT_MULTI
        )

        for idx, text in enumerate(day_text_list):

            textbox = slide.shapes.add_textbox(
                DAY_X,
                Y_POSITIONS[day_count][idx],
                BOX_WIDTH,
                box_height
            )

            textbox.text = text

            p = textbox.text_frame.paragraphs[0]

            p.font.name = "Rockwell"
            p.font.bold = True
            p.font.size = prs.slides[0].shapes[0].text_frame.paragraphs[0].font.size

            try:
                p.font.color.rgb = RGBColor(
                    0,
                    0,
                    0
                )
            except Exception:
                pass

    #
    # 保存
    #
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
        f"[SUCCESS] パワポ保存完了: {output_path}"
    )

    return output_path


def parse_event_text(text):
    if not text:
        return "", "", ""

    text = text.replace("ナイター", "").strip()

    parts = text.split()

    name = parts[0] if len(parts) > 0 else ""
    grade = parts[1] if len(parts) > 1 else ""
    status = parts[2] if len(parts) > 2 else ""

    return name, grade, status
```
