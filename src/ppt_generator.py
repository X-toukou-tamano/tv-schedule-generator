import os
import re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def parse_event_text(text):
    """
    リアルタイム確認の文字列（例：「久留米ナイター F1 2日目」や「小田原 F1 2日目」）を
    [場名, グレード, 日数] に完全に分解する関数。
    ナイターの文字は自動で削ぎ落とし、グレードは全角（FⅠ, GⅢ）に変換します。
    """
    # 1. 前後の余白を削除
    text = text.strip()
    
    # 2. 「ナイター」という文字が含まれていたら消去
    text = text.replace("ナイター", "")
    
    # 3. 連続するスペースを1つの半角スペースに統一して分割
    # 例: "久留米 F1 2日目" -> ["久留米", "F1", "2日目"]
    parts = [p for p in re.split(r'\s+', text) if p]
    
    # 万が一分割が想定通りにいかなかった場合のセーフティ
    if len(parts) < 3:
        # 分割に失敗した場合は、最低限パーツを埋める
        name = parts[0] if len(parts) > 0 else "不明"
        grade = parts[1] if len(parts) > 1 else "-"
        status = parts[2] if len(parts) > 2 else "-"
    else:
        name = parts[0]
        grade = parts[1]
        status = parts[2]
        
    # 4. グレード表記を例のパワポ通り「全角」に変換
    grade_map = {
        "F1": "FⅠ", "F2": "FⅡ", "G1": "GⅠ", "G2": "GⅡ", "G3": "GⅢ", "GP": "GP",
        "f1": "FⅠ", "f2": "FⅡ", "g1": "GⅠ", "g2": "GⅡ", "g3": "GⅢ", "gp": "GP"
    }
    grade = grade_map.get(grade, grade)
    
    return name, grade, status

def calculate_y_positions(count, is_night):
    """
    仕様書の「20. レイアウトルール（1件なら上下中央、2件なら上下均等…）」に基づき、
    件数に応じて1行ごとの正確な縦位置（Y座標：Inches）を計算して返す関数。
    """
    # 青枠（ナイター）と白枠（デイ）の、文字を入れても良い有効な縦領域（高さの範囲）
    # 例のパワポのレイアウト基準値
    top_limit = 2.0   # 上端の限界位置
    bottom_limit = 6.5 # 下端の限界位置
    center_y = 4.25    # ど真ん中の位置
    
    y_positions = []
    
    if count == 1:
        # 1件：上下中央
        y_positions.append(center_y - 0.3)
    elif count == 2:
        # 2件：上下均等配置（上寄りと下寄り）
        y_positions.append(3.0)
        y_positions.append(5.5)
    elif count == 3:
        # 3件：上・中・下
        y_positions.append(2.4)
        y_positions.append(center_y - 0.3)
        y_positions.append(6.1)
    else:
        # 4件以上：全体に均等に敷き詰める
        total_height = bottom_limit - top_limit
        step = total_height / (count - 1)
        for i in range(count):
            y_positions.append(top_limit + (step * i))
            
    return y_positions

def create_powerpoint(day_text_list, night_text_list):
    """
    ルート直下の「元データ(2).pptx」を読み込み、
    パーツ分解したデータをカチッとした座標へ流し込んで新パワポを生成するメイン関数。
    """
    template_path = os.path.join(os.getcwd(), "元データ(2).pptx")
    if not os.path.exists(template_path):
        raise FileNotFoundError("テンプレートファイル「元データ(2).pptx」がルート直下に見つかりません。")
        
    prs = Presentation(template_path)
    slide = prs.slides[0] # 最初のスライドを使用
    
    # -------------------------------------------------------------
    # 枠（テキストボックス）の横位置（X座標）と横幅、および文字色の設計
    # -------------------------------------------------------------
    # 左枠（青枠・ナイター）のX座標・幅の規格
    NIGHT_X_NAME  = Inches(0.8)   # 場名の左端位置
    NIGHT_X_GRADE = Inches(2.6)   # グレードの中央位置
    NIGHT_X_STATUS = Inches(4.2)  # 日数の右端位置
    NIGHT_WIDTH   = Inches(1.5)   # 各ボックスの十分な横幅
    NIGHT_COLOR   = RGBColor(255, 255, 255) # 文字色：白
    
    # 右枠（白枠・デイ）のX座標・幅の規格
    DAY_X_NAME    = Inches(6.8)   # 場名の左端位置
    DAY_X_GRADE   = Inches(8.6)   # グレードの中央位置
    DAY_X_STATUS  = Inches(10.2)  # 日数の右端位置
    DAY_WIDTH     = Inches(1.5)   # 各ボックスの十分な横幅
    DAY_COLOR     = RGBColor(0, 0, 0)       # 文字色：黒

    BOX_HEIGHT = Inches(0.6)      # 1行の枠としての高さ規格

    # -------------------------------------------------------------
    # ① 左枠（青枠・ナイター放映用）の生成と配置
    # -------------------------------------------------------------
    if night_text_list:
        night_y_positions = calculate_y_positions(len(night_text_list), is_night=True)
        for i, text in enumerate(night_text_list):
            name, grade, status = parse_event_text(text)
            y_pos = Inches(night_y_positions[i])
            
            # 【場名】左揃え
            tx_box_name = slide.shapes.add_textbox(NIGHT_X_NAME, y_pos, NIGHT_WIDTH, BOX_HEIGHT)
            tf_name = tx_box_name.text_frame
            tf_name.word_wrap = False
            p_name = tf_name.paragraphs[0]
            p_name.text = name
            p_name.font.name = "MS Gothic"
            p_name.font.size = Pt(32)
            p_name.font.bold = True
            p_name.font.color.rgb = NIGHT_COLOR
            p_name.alignment = PP_ALIGN.LEFT
            
            # 【グレード】中央揃え
            tx_box_grade = slide.shapes.add_textbox(NIGHT_X_GRADE, y_pos, NIGHT_WIDTH, BOX_HEIGHT)
            tf_grade = tx_box_grade.text_frame
            tf_grade.word_wrap = False
            p_grade = tf_grade.paragraphs[0]
            p_grade.text = grade
            p_grade.font.name = "MS Gothic"
            p_grade.font.size = Pt(32)
            p_grade.font.bold = True
            p_grade.font.color.rgb = NIGHT_COLOR
            p_grade.alignment = PP_ALIGN.CENTER
            
            # 【開催日数】右揃え
            tx_box_status = slide.shapes.add_textbox(NIGHT_X_STATUS, y_pos, NIGHT_WIDTH, BOX_HEIGHT)
            tf_status = tx_box_status.text_frame
            tf_status.word_wrap = False
            p_status = tf_status.paragraphs[0]
            p_status.text = status
            p_status.font.name = "MS Gothic"
            p_status.font.size = Pt(32)
            p_status.font.bold = True
            p_status.font.color.rgb = NIGHT_COLOR
            p_status.alignment = PP_ALIGN.RIGHT

    # -------------------------------------------------------------
    # ② 右枠（白枠・デイ放映用）の生成と配置
    # -------------------------------------------------------------
    if day_text_list:
        day_y_positions = calculate_y_positions(len(day_text_list), is_night=False)
        for i, text in enumerate(day_text_list):
            name, grade, status = parse_event_text(text)
            y_pos = Inches(day_y_positions[i])
            
            # 【場名】左揃え
            tx_box_name = slide.shapes.add_textbox(DAY_X_NAME, y_pos, DAY_WIDTH, BOX_HEIGHT)
            tf_name = tx_box_name.text_frame
            tf_name.word_wrap = False
            p_name = tf_name.paragraphs[0]
            p_name.text = name
            p_name.font.name = "MS Gothic"
            p_name.font.size = Pt(32)
            p_name.font.bold = True
            p_name.font.color.rgb = DAY_COLOR
            p_name.alignment = PP_ALIGN.LEFT
            
            # 【グレード】中央揃え
            tx_box_grade = slide.shapes.add_textbox(DAY_X_GRADE, y_pos, DAY_WIDTH, BOX_HEIGHT)
            tf_grade = tx_box_grade.text_frame
            tf_grade.word_wrap = False
            p_grade = tf_grade.paragraphs[0]
            p_grade.text = grade
            p_grade.font.name = "MS Gothic"
            p_grade.font.size = Pt(32)
            p_grade.font.bold = True
            p_grade.font.color.rgb = DAY_COLOR
            p_grade.alignment = PP_ALIGN.CENTER
            
            # 【開催日数】右揃え
            tx_box_status = slide.shapes.add_textbox(DAY_X_STATUS, y_pos, DAY_WIDTH, BOX_HEIGHT)
            tf_status = tx_box_status.text_frame
            tf_status.word_wrap = False
            p_status = tf_status.paragraphs[0]
            p_status.text = status
            p_status.font.name = "MS Gothic"
            p_status.font.size = Pt(32)
            p_status.font.bold = True
            p_status.font.color.rgb = DAY_COLOR
            p_status.alignment = PP_ALIGN.RIGHT

    # 3. 完成したスライドを指定フォルダへ一時保存
    os.makedirs("uploads", exist_ok=True)
    output_path = os.path.join("uploads", "場内放映予定.pptx")
    prs.save(output_path)
    
    return output_path
