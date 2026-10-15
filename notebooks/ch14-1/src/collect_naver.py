import json
import os
from datetime import date, datetime
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(BASE_DIR / ".env")


def build_mock_response() -> dict:
    periods = pd.date_range(end=date.today(), periods=13, freq="MS")
    mock_values = {
        "여행": [62, 65, 69, 74, 78, 83, 91, 88, 81, 76, 72, 70, 75],
        "축제": [28, 31, 36, 42, 55, 67, 73, 69, 58, 48, 39, 35, 41],
        "캠핑": [44, 46, 51, 59, 68, 77, 82, 79, 71, 63, 54, 49, 52],
        "맛집": [71, 73, 76, 79, 82, 86, 90, 92, 89, 85, 83, 81, 84],
    }
    return {
        "mock": True,
        "notice": "수업용 모의 데이터이며 실제 NAVER 검색 결과가 아닙니다.",
        "startDate": periods[0].date().isoformat(),
        "endDate": periods[-1].date().isoformat(),
        "timeUnit": "month",
        "results": [
            {
                "title": keyword,
                "keywords": [keyword],
                "data": [
                    {"period": period.date().isoformat(), "ratio": ratio}
                    for period, ratio in zip(periods, values, strict=True)
                ],
            }
            for keyword, values in mock_values.items()
        ],
    }


def request_naver() -> dict:
    client_id = os.getenv("NAVER_CLIENT_ID")
    client_secret = os.getenv("NAVER_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("NAVER API Key가 설정되지 않았습니다.")

    end_date = date.today()
    start_date = end_date.replace(year=end_date.year - 1)
    payload = {
        "startDate": start_date.isoformat(),
        "endDate": end_date.isoformat(),
        "timeUnit": "month",
        "keywordGroups": [
            {"groupName": "여행", "keywords": ["여행"]},
            {"groupName": "축제", "keywords": ["축제"]},
            {"groupName": "캠핑", "keywords": ["캠핑"]},
            {"groupName": "맛집", "keywords": ["맛집"]},
        ],
    }
    headers = {
        "X-NCP-APIGW-API-KEY-ID": client_id,
        "X-NCP-APIGW-API-KEY": client_secret,
        "Content-Type": "application/json",
    }
    response = requests.post(
        "https://naverapihub.apigw.ntruss.com/search-trend/v1/search",
        headers=headers,
        json=payload,
        timeout=30,
    )
    if response.status_code != 200:
        raise RuntimeError(
            f"NAVER API 실패: HTTP {response.status_code} {response.text[:300]}"
        )
    return response.json()


def main() -> None:
    use_mock = os.getenv("USE_MOCK_DATA", "false").lower() == "true"
    data = build_mock_response() if use_mock else request_naver()
    if "results" not in data:
        raise RuntimeError("NAVER 응답에 results가 없습니다.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_path = RAW_DIR / f"naver_trend_{timestamp}.json"
    raw_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    rows = []
    for result in data["results"]:
        for point in result.get("data", []):
            rows.append(
                {
                    "period": point.get("period"),
                    "keyword": result.get("title"),
                    "ratio": point.get("ratio"),
                    "data_source": "MOCK" if use_mock else "NAVER_API",
                }
            )

    df = pd.DataFrame(rows)
    if df.empty:
        raise RuntimeError("NAVER 결과가 비어 있습니다.")
    df["period"] = pd.to_datetime(df["period"], errors="coerce")
    df["ratio"] = pd.to_numeric(df["ratio"], errors="coerce")
    if df["period"].isna().any() or df["ratio"].isna().any():
        raise RuntimeError("날짜 또는 ratio 변환 실패 값이 있습니다.")

    output_path = PROCESSED_DIR / "naver_trend.csv"
    df.to_csv(output_path, index=False, encoding="utf-8-sig")
    mode = "MOCK DATA" if use_mock else "API"
    print(f"[PASS] NAVER Trend {mode}")
    print("rows:", len(df))
    print("period:", df["period"].min().date(), "~", df["period"].max().date())
    print("keywords:", sorted(df["keyword"].unique().tolist()))
    print("saved:", output_path)


if __name__ == "__main__":
    main()

