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

        ppt_paths.append(
            output_path
        )

    zip_path = create_zip(
        ppt_paths
    )

    return zip_path
