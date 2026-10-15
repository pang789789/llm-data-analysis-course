import json
import os
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
MOCK_DIR = BASE_DIR / "data" / "mock"
CONFIG_PATH = BASE_DIR / "config" / "tourism_params.json"

RAW_DIR.mkdir(parents=True, exist_ok=True)
load_dotenv(BASE_DIR / ".env")


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        raise RuntimeError(f"설정 파일이 없습니다: {CONFIG_PATH}")
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_mock(kind: str) -> dict:
    mock_files = {
        "stay": MOCK_DIR / "tourism_stay_sample.json",
        "consumption": MOCK_DIR / "tourism_consumption_sample.json",
    }
    path = mock_files[kind]
    if not path.exists():
        raise RuntimeError(f"모의 응답 파일이 없습니다: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def request_api(kind: str, url: str, service_key: str, params: dict) -> dict:
    request_params = {**params, "serviceKey": service_key}
    response = requests.get(url, params=request_params, timeout=30)
    if response.status_code != 200:
        raise RuntimeError(
            f"관광 {kind} API 실패: HTTP {response.status_code} "
            f"{response.text[:300]}"
        )
    try:
        return response.json()
    except requests.JSONDecodeError as exc:
        raise RuntimeError(
            f"관광 {kind} API가 JSON을 반환하지 않았습니다: {response.text[:300]}"
        ) from exc


def validate_response(kind: str, data: dict, use_mock: bool) -> None:
    if not isinstance(data, dict) or not data:
        raise RuntimeError(f"관광 {kind} 응답이 비어 있습니다.")
    if use_mock and data.get("mock") is not True:
        raise RuntimeError(f"관광 {kind} 모의 응답에 mock 표시가 없습니다.")


def main() -> None:
    config = load_config()
    use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
    service_key = os.getenv("TOURISM_SERVICE_KEY", "")
    urls = {
        "stay": os.getenv("TOURISM_STAY_URL", ""),
        "consumption": os.getenv("TOURISM_CONSUMPTION_URL", ""),
    }

    if not use_mock and not service_key:
        raise RuntimeError("TOURISM_SERVICE_KEY가 없습니다.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for kind in ("stay", "consumption"):
        if kind not in config or "params" not in config[kind]:
            raise RuntimeError(f"설정에 {kind}.params가 없습니다.")

        if use_mock:
            data = load_mock(kind)
        else:
            if not urls[kind]:
                raise RuntimeError(f"TOURISM_{kind.upper()}_URL이 없습니다.")
            data = request_api(kind, urls[kind], service_key, config[kind]["params"])

        validate_response(kind, data, use_mock)
        output_path = RAW_DIR / f"tourism_{kind}_{timestamp}.json"
        output_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        mode = "MOCK DATA" if use_mock else "API"
        print(f"[PASS] Tourism {kind} {mode}")
        print("params:", config[kind]["params"])
        print("saved:", output_path)


if __name__ == "__main__":
    main()
