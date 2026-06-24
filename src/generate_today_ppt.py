from today_service import get_today_sorted_data
from ppt_generator import create_powerpoint


def main():
    (
        (
            day_events,
            night_events,
            _,
            _,
        ),
        _,
    ) = get_today_sorted_data()

    create_powerpoint(
        day_events,
        night_events
    )

    print("PPT生成完了")


if __name__ == "__main__":
    main()
