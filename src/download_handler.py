import os
from flask import abort, send_file

def handle_pptx_download(session, day_text_list, night_text_list):
    """
    uploads/場内放映予定.pptx を確実にダウンロードさせる
    """
    if not session.get("logged_in"):
        return abort(403)

    try:
        # プロジェクトルート直下の uploads フォルダ内を絶対パスで指定
        target_path = os.path.join(os.getcwd(), "uploads", "場内放映予定.pptx")
        
        if not os.path.exists(target_path):
            print(f"[ERROR] ダウンロード対象のファイルが存在しません: {target_path}")
            return abort(500, "パワポファイルが生成されていません。ダッシュボードからやり直してください。")
            
        print(f"[SUCCESS] パワポファイルをクライアントへ送信します: {target_path}")
        return send_file(
            target_path,
            mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            as_attachment=True,
            download_name="場内放映予定.pptx"
        )
        
    except Exception as e:
        print(f"[CRITICAL] ダウンロード処理で致命的なエラーが発生しました: {e}")
        return abort(500, f"システムエラーが発生しました: {e}")
