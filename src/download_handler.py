import os
from datetime import date
from flask import abort, send_file


def handle_pptx_download(
    session,
    day_events,
    night_events
):
    """
    当日生成されたPowerPointをダウンロードさせる
    """

    if not session.get("logged_in"):
        return abort(403)

    try:

        today_str = date.today().strftime(
            "%m%d"
        )

        target_path = os.path.join(
            os.getcwd(),
            "uploads",
            f"場内放映予定{today_str}.pptx"
        )

        if not os.path.exists(
            target_path
        ):

            print(
                f"[ERROR] ダウンロード対象のファイルが存在しません: {target_path}"
            )

            return abort(
                500,
                "パワポファイルが生成されていません。ダッシュボードからやり直してください。"
            )

        print(
            f"[SUCCESS] パワポファイルをクライアントへ送信します: {target_path}"
        )

        return send_file(
            target_path,
            mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            as_attachment=True,
            download_name=f"場内放映予定{today_str}.pptx"
        )

    except Exception as e:

        print(
            f"[CRITICAL] ダウンロード処理で致命的なエラーが発生しました: {e}"
        )

        return abort(
            500,
            f"システムエラーが発生しました: {e}"
        )
