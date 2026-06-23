import os
from copy import deepcopy

from pptx import Presentation

# ----------------------------------
# 確定値
# ----------------------------------

NIGHT_X = 430746
DAY_X = 6339932

Y_POSITIONS = {
    1: [2734305],
    2: [2126142, 3985406],
    3: [1718949, 3122764, 4526579],
}


def clone_shape(slide, shape):
    new_el = deepcopy(shape.element)
    slide.shapes._spTree.insert_element_before(new_el, "p:extLst")
    return slide.shapes[-1]


def remove_shape(shape):
    sp = shape.element
    sp.getparent().remove(sp)


def create_powerpoint(day_text_list, night_text_list):
    template_path = os.path.join(os.getcwd(), "src", "元データ.pptx")

    if not os.path.exists(template_path):
        raise FileNotFoundError(f"テンプレートが存在しません: {template_path}")

    prs = Presentation(template_path)
    slide = prs.slides[0]

    night_template = None
    day_template = None

    #
    # 元データ内の見本を探す
    #
    for shape in slide.shapes:
        if not getattr(shape, "has_text_frame", False):
            continue

        text = shape.text.strip()

        if "ナイター" in text:
            night_template = shape
        elif text.startswith("武雄") or text.startswith("伊東"):
            day_template = shape

    if night_template is None:
        raise Exception("ナイターテンプレートが見つかりません")

    if day_template is None:
        raise Exception("デイテンプレートが見つかりません")

    #
    # 元見本を消す
    #
    remove_shape(night_template)
    remove_shape(day_template)

    #
    # ナイター生成
    #
    night_count = len(night_text_list)
    if night_count > 0:
        for idx, text in enumerate(night_text_list):
            shape = clone_shape(slide, night_template)
            shape.left = NIGHT_X
            shape.top = Y_POSITIONS[night_count][idx]
            shape.text = text

    #
    # デイ生成
    #
    day_count = len(day_text_list)
    if day_count > 0:
        for idx, text in enumerate(day_text_list):
            shape = clone_shape(slide, day_template)
            shape.left = DAY_X
            shape.top = Y_POSITIONS[day_count][idx]
            shape.text = text

    #
    # 保存
    #
    upload_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)

    output_path = os.path.join(upload_dir, "場内放映予定.pptx")
    prs.save(output_path)

    print(f"[SUCCESS] パワポ保存完了: {output_path}")
    return output_path


def parse_event_text(text):
    """イベントテキスト（例：「武雄 F1 最終日」や「ナイター松阪 G3 初日」など）を

    [競輪場名, グレード, 状態] の3つに分解する関数
    """
    if not text:
        return "", "", ""

    # 「ナイター」という文字が含まれている場合は除外して処理
    clean_text = text.replace("ナイター", "").strip()

    # スペース（全角・半角）で分割
    parts = [p for p in clean_text.replace(" ", " ").split(" ") if p]

    # 分割した結果に応じて値を割り振り
    name = parts[0] if len(parts) > 0 else ""
    grade = parts[1] if len(parts) > 1 else ""
    status = parts[2] if len(parts) > 2 else ""

    return name, grade, status
