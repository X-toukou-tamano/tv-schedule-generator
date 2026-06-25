import os
from datetime import datetime
from zoneinfo import ZoneInfo

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

        today_str = (
            datetime.now(
                ZoneInfo("Asia/Tokyo")
            )
            .strftime("%m%d")
        )

        target_path = os.path.join(
            os.getcwd(),
            "uploads",
            f"場内放映予定{today_str}.pptx"
        )

        if not os.path.exists(
            target_path
        ):

            return abort(
                500,
                "パワポファイルが生成されていません。ダッシュボードからやり直してください。"
            )

        return send_file(
            target_path,
            mimetype="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            as_attachment=True,
            download_name=f"場内放映予定{today_str}.pptx"
        )

    except Exception as e:

        return abort(
            500,
            f"システムエラーが発生しました: {e}"
        )
