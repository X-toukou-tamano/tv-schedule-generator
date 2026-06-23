import os
import re
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN

def parse_event_text(text):
    """
    文字列（例：「久留米 FⅠ  2日目」や「小田原 FⅡ  最終日」）を
    [場名, グレード, 日数] に分解・整形する
    """
    text = text.strip()
    text = text.replace("ナイター", "")
    # 連続する全角・半角スペースで分割
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
    仕様書の「20. レイアウトルール」に基づく縦位置（Inches）の計算
    """
    top_limit = 2.0   
    bottom_limit = 6.5 
    center_y = 4.25    
    
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
    src/元データ.pptxを読み込み、カチッとした座標へ流し込んで新パワポを生成する
    """
    # テンプレートファイルは常に src/元データ.pptx を見にいく
    template_path = os.path.join(os.getcwd(), "src", "元データ.pptx")
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"テンプレートファイルが見つかりません。パス: {template_path}")
        
    prs = Presentation(template_path)
    slide = prs.slides[0]
    
    # 座標・デザイン設計
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

    # ① 左枠（青枠・ナイター）の配置
    if night_text_list:
        night_y_positions = calculate_y_positions(len(night_text_list), is_night=True)
        for i, text in enumerate(night_text_list):
            name, grade, status = parse_event_text(text)
            y_pos = Inches(night_y_positions[i])
            
            tx_box_name = slide.shapes.add_textbox(NIGHT_X_NAME, y_pos, NIGHT_WIDTH, BOX_HEIGHT)
            tf_name = tx_box_name.text_frame
            tf_name.word_wrap = False
            tf_name.paragraphs[0].text = name
            tf_name.paragraphs[0].font.name = "MS Gothic"
            tf_name.paragraphs[0].font.size = Pt(32)
            tf_name.paragraphs[0].font.bold = True
            tf_name.paragraphs[0].font.color.rgb = NIGHT_COLOR
            tf_name.paragraphs[0].alignment = PP_ALIGN.LEFT
            
            tx_box_grade = slide.shapes.add_textbox(NIGHT_X_GRADE, y_pos, NIGHT_WIDTH, BOX_HEIGHT)
            tf_grade = tx_box_grade.text_frame
            tf_grade.word_wrap = False
            tf_grade.paragraphs[0].text = grade
            tf_grade.paragraphs[0].font.name = "MS Gothic"
            tf_grade.paragraphs[0].font.size = Pt(32)
            tf_grade.paragraphs[0].font.bold = True
            tf_grade.paragraphs[0].font.color.rgb = NIGHT_COLOR
            tf_grade.paragraphs[0].alignment = PP_ALIGN.CENTER
            
            tx_box_status = slide.shapes.add_textbox(NIGHT_X_STATUS, y_pos, NIGHT_WIDTH, BOX_HEIGHT)
            tf_status = tx_box_status.text_frame
            tf_status.word_wrap = False
            tf_status.paragraphs[0].text = status
            tf_status.paragraphs[0].font.name = "MS Gothic"
            tf_status.paragraphs[0].font.size = Pt(32)
            tf_status.paragraphs[0].font.bold = True
            tf_status.paragraphs[0].font.color.rgb = NIGHT_COLOR
            tf_status.paragraphs[0].alignment = PP_ALIGN.RIGHT

    # ② 右枠（白枠・デイ）の配置
    if day_text_list:
        day_y_positions = calculate_y_positions(len(day_text_list), is_night=False)
        for i, text in enumerate(day_text_list):
            name, grade, status = parse_event_text(text)
            y_pos = Inches(day_y_positions[i])
            
            tx_box_name = slide.shapes.add_textbox(DAY_X_NAME, y_pos, DAY_WIDTH, BOX_HEIGHT)
            tf_name = tx_box_name.text_frame
            tf_name.word_wrap = False
            tf_name.paragraphs[0].text = name
            tf_name.paragraphs[0].font.name = "MS Gothic"
            tf_name.paragraphs[0].font.size = Pt(32)
            tf_name.paragraphs[0].font.bold = True
            tf_name.paragraphs[0].font.color.rgb = DAY_COLOR
            tf_name.paragraphs[0].alignment = PP_ALIGN.LEFT
            
            tx_box_grade = slide.shapes.add_textbox(DAY_X_GRADE, y_pos, DAY_WIDTH, BOX_HEIGHT)
            tf_grade = tx_box_grade.text_frame
            tf_grade.word_wrap = False
            tf_grade.paragraphs[0].text = grade
            tf_grade.paragraphs[0].font.name = "MS Gothic"
            tf_grade.paragraphs[0].font.size = Pt(32)
            tf_grade.paragraphs[0].font.bold = True
            tf_grade.paragraphs[0].font.color.rgb = DAY_COLOR
            tf_grade.paragraphs[0].alignment = PP_ALIGN.CENTER
            
            tx_box_status = slide.shapes.add_textbox(DAY_X_STATUS, y_pos, DAY_WIDTH, BOX_HEIGHT)
            tf_status = tx_box_status.text_frame
            tf_status.word_wrap = False
            tf_status.paragraphs[0].text = status
            tf_status.paragraphs[0].font.name = "MS Gothic"
            tf_status.paragraphs[0].font.size = Pt(32)
            tf_status.paragraphs[0].font.bold = True
            tf_status.paragraphs[0].font.color.rgb = DAY_COLOR
            tf_status.paragraphs[0].alignment = PP_ALIGN.RIGHT

    # 保存先フォルダはプロジェクト直下の「uploads」に完全固定
    upload_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    output_path = os.path.join(upload_dir, "場内放映予定.pptx")
    prs.save(output_path)
    print(f"[SUCCESS] パワポファイルを生成して保存しました: {output_path}")
        
    return output_path
