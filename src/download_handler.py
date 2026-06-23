import os
from flask import abort, send_file
from ppt_generator import create_powerpoint

def handle_pptx_download(session, day_text_list, night_text_list):
    """
    app.py から呼び出され、PowerPointの生成処理（ppt_generator）を仲介して
    ユーザーのブラウザへ安全にファイルを返却・ダウンロードさせる制御関数。
    """
    # 1. 未ログイン状態のアクセスは拒否
    if not session.get("logged_in"):
        return abort(403)

    try:
        # 2. ppt_generator.py を呼び出してパワポを実生成
        output_path = create_powerpoint(day_text_list, night_text_list)
        
        # 3. 生成されたファイルが存在するかチェック
        if not os.path.exists(output_path):
            return abort(500, "PowerPointファイルの生成に失敗しました。")
            
        # 4. ブラウザへファイルを送信してダウンロードさせる
        return send_file(
            output_path,
            mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            as_attachment=True,
            download_name="場内放映予定.pptx"
        )
        
    except Exception as e:
        print(f"[ERROR] ダウンロードハンドラー内で予期せぬエラー: {e}")
        return abort(500, f"システムエラーが発生しました: {e}")
