from datetime import date
from database import get_summary
from today_service import get_schedule_data
from ppt_generator import create_powerpoint
from zip_utils import create_zip


def generate_range_ppt(
    start_date,
    end_date,
):
    """
    指定期間のPPTを生成してZIPを返す
    """

    schedule_data_by_date = get_schedule_data(
        start_date,
        end_date,
    )

    if not schedule_data_by_date:
        return None

    ppt_paths = []

    for (
        event_date,
        (
            day_events,
            night_events,
            _,
            _,
        ),
    ) in schedule_data_by_date.items():

        output_path = create_powerpoint(
            day_events,
            night_events,
            event_date,
        )

        ppt_paths.append(output_path)

    return create_zip(ppt_paths)


def generate_all_ppt():
    """
    公開済み全期間のPPTを生成してZIPを返す
    """

    summary = get_summary()

    if summary[2] == 0:
        return None, None

    # 文字列型からdate型に変換
    start_date = date.fromisoformat(summary[0])
    end_date = date.fromisoformat(summary[1])

    schedule_data_by_date = get_schedule_data(
        start_date,
        end_date,
    )

    if not schedule_data_by_date:
        return None, None

    ppt_paths = []

    last_date = None

    for (
        event_date,
        (
            day_events,
            night_events,
            _,
            _,
        ),
    ) in schedule_data_by_date.items():

        output_path = create_powerpoint(
            day_events,
            night_events,
            event_date,
        )

        ppt_paths.append(output_path)

        last_date = event_date

    zip_path = create_zip(
        ppt_paths
    )

    return zip_path, last_date
