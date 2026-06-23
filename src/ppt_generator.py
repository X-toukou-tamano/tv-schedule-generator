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
    text = text.strip()
    text = text.replace("ナイター", "")
    parts = [p for p in re.split(r'\s+', text) if p]
    
    if len(parts) < 3:
        name = parts[0] if len(parts) > 0 else "不明"
        grade = parts[1] if len(parts) > 1 else "-"
        status = parts[2] if len(parts) > 2 else "-"
    else:
        name = parts[0]
        grade = parts[1]
        status = parts[2]
        
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
    top_limit = 2.0   # 上端の限界位置
    bottom_limit = 6.5 # 下端の限界位置
    center_y = 4.25    # ど真ん中の位置
    
    y_positions = []
    
    if count == 1:
        y_positions.append(center_y - 0.3)
    elif count == 2:
        y_positions.append(3.0)
        y_positions.append(5.5)
    elif count == 3:
        y_positions.append(2.4)
        y_positions.append(center_y - 0.3)
        y_positions.append(6.1)
    else:
        total_height = bottom_limit - top_limit
        step = total_height / (count - 1)
        for i in range(count):
            y_positions.append(top_limit + (step * i))
            
    return y_positions

def create_powerpoint(day_text_list, night_text_list):
    """
    srcフォルダ内の「元データ.pptx」を読み込み、
    パーツ分解したデータをカチッとした座標へ流し込んで新パワポを生成するメイン関数。
    """
    template_path = os.path.join(os.getcwd(), "src", "元データ.pptx")
    if not os.path.exists(template_path):
        raise FileNotFoundError("テンプレートファイル「src/元データ.pptx」が見つかりません。")
        
    prs = Presentation(template_path)
    slide = prs.slides[0]
    
    # -------------------------------------------------------------
    # 枠（テキストボックス）の横位置（X座標）と横幅、および文字色の設計
    # -------------------------------------------------------------
    NIGHT_X_NAME  = Inches(0.8)   
    NIGHT_X_GRADE = Inches(2.6)   
    NIGHT_X_STATUS = Inches(4.2)  
    NIGHT_WIDTH   = Inches(1.5)   
    NIGHT_COLOR   = RGBColor(255, 255, 255) 
    
    DAY_X_NAME    = Inches(6.8)   
    DAY_X_GRADE   = Inches(8.6)   
    DAY_X_STATUS  = Inches(10.2)  
    DAY_WIDTH     = Inches(1.5)   
    DAY_COLOR     = RGBColor(0, 0, 0)       

    BOX_HEIGHT = Inches(0.6)      

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

    os.makedirs("uploads", exist_ok=True)
    output_path = os.path.join("uploads", "場内放映予定.pptx")
    prs.save(output_path)

    try:
        import comtypes.client
        abs_pptx = os.path.abspath(output_path)
        static_dir = os.path.join(os.getcwd(), "static")
        os.makedirs(static_dir, exist_ok=True)
        abs_png = os.path.abspath(os.path.join(static_dir, "preview.png"))
        
        powerpoint = comtypes.client.CreateObject("Powerpoint.Application")
        powerpoint.Visible = 1
        deck = powerpoint.Presentations.Open(abs_pptx, WithWindow=False)
        deck.Slides[1].Export(abs_png, "PNG")
        deck.Close()
        powerpoint.Quit()
        print("[SUCCESS] パワポ実物の画像を static/preview.png にエクスポートしました")
    except Exception as e:
        print(f"[WARNING] 実際のパワポ画像化に失敗したため、HTML簡易再現プレビューを使用します: {e}")
        
    return output_path
