from app.domain.enums.traffic_source import TrafficSource

_PAYLOAD_MAP: dict[str, TrafficSource] = {
    TrafficSource.INSTAGRAM: TrafficSource.INSTAGRAM,
    TrafficSource.TELEGRAM_STORY: TrafficSource.TELEGRAM_STORY,
}


def parse_traffic_source(args: str | None) -> TrafficSource:
    """Определяет источник перехода из payload команды /start."""
    if not args:
        return TrafficSource.DIRECT

    return _PAYLOAD_MAP.get(args.strip(), TrafficSource.DIRECT)
