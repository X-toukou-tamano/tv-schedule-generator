import os
from flask import send_file, redirect
from ppt_generator import create_powerpoint

def handle_pptx_download(session, day_text_list, night_text_list):
    """
    パワーポイントの生成を指示し、完成したファイルをユーザーにダウンロードさせる制御関数
    """
    # 1. ログインチェック（セーフティ）
    if not session.get("logged_in"):
        return redirect("/")

    try:
        # 2. パワポ生成専用エンジン（ppt_generator.py）を呼び出し
        # パーツ分解、X・Y座標計算、テキストボックス配置はすべてあちらで完結
        output_path = create_powerpoint(day_text_list, night_text_list)
        
        # 3. 出来上がった「場内放映予定.pptx」をユーザーへ安全に送出
        output_filename = "場内放映予定.pptx"
        return send_file(
            output_path,
            as_attachment=True,
            download_name=output_filename,
            mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation"
        )
        
    except Exception as e:
        print(f"[ERROR] パワーポイントの生成・転送中にエラーが発生しました: {e}")
        return f"PowerPointの生成に失敗しました: {e}", 500
