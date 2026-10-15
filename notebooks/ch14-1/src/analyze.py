import json
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import pandas as pd


matplotlib.use("Agg")

BASE_DIR = Path(__file__).resolve().parents[1]
PROCESSED_DIR = BASE_DIR / "data" / "processed"
RAW_DIR = BASE_DIR / "data" / "raw"
REPORTS_DIR = BASE_DIR / "reports"
REPORTS_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


def set_korean_font() -> None:
    plt.rcParams["font.family"] = "Malgun Gothic"
    plt.rcParams["axes.unicode_minus"] = False


def latest_raw_file(kind: str) -> Path:
    files = sorted(RAW_DIR.glob(f"tourism_{kind}_*.json"))
    if not files:
        raise RuntimeError(f"tourism_{kind} Raw JSON이 없습니다.")
    return files[-1]


def read_tourism_mock(kind: str) -> tuple[pd.DataFrame, bool]:
    path = latest_raw_file(kind)
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("response", {}).get("body", {}).get("items", [])
    if not isinstance(items, list) or not items:
        raise RuntimeError(f"{path.name}에 분석할 items가 없습니다.")

    value_column = {
        "stay": "stayIntensity",
        "consumption": "consumptionIntensity",
    }[kind]
    required = {"areaName", "baseYm", value_column}
    missing = required - set(items[0])
    if missing:
        raise RuntimeError(
            f"{path.name} 필드가 예상과 다릅니다. 누락: {sorted(missing)}"
        )

    frame = pd.DataFrame(items)[["areaName", "baseYm", value_column]].copy()
    frame[value_column] = pd.to_numeric(frame[value_column], errors="coerce")
    if frame[value_column].isna().any():
        raise RuntimeError(f"{value_column} 숫자 변환 실패 값이 있습니다.")
    frame["data_source"] = "MOCK" if data.get("mock") else "TOURISM_API"
    return frame, bool(data.get("mock"))


def analyze_naver() -> pd.DataFrame:
    path = PROCESSED_DIR / "naver_trend.csv"
    if not path.exists():
        raise RuntimeError("NAVER CSV가 없습니다. collect_naver.py를 먼저 실행하세요.")

    naver = pd.read_csv(path)
    required = {"period", "keyword", "ratio"}
    missing = required - set(naver.columns)
    if missing:
        raise RuntimeError(f"NAVER CSV 필드 누락: {sorted(missing)}")

    naver["period"] = pd.to_datetime(naver["period"], errors="coerce")
    naver["ratio"] = pd.to_numeric(naver["ratio"], errors="coerce")
    if naver.empty or naver[["period", "keyword", "ratio"]].isna().any().any():
        raise RuntimeError("NAVER 분석 입력이 비었거나 결측값이 있습니다.")

    naver = naver.sort_values(["keyword", "period"])
    naver["previous_ratio"] = naver.groupby("keyword")["ratio"].shift(1)
    naver["change"] = naver["ratio"] - naver["previous_ratio"]
    latest = (
        naver.groupby("keyword", as_index=False)
        .tail(1)
        .sort_values("ratio", ascending=False)
        .copy()
    )

    set_korean_font()
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for keyword, group in naver.groupby("keyword"):
        group = group.sort_values("period")
        ax.plot(group["period"], group["ratio"], marker="o", label=keyword)
    ax.set_title("NAVER 검색 관심도 추이 (상대지수)")
    ax.set_xlabel("기간")
    ax.set_ylabel("상대 관심도")
    ax.legend()
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(REPORTS_DIR / "naver_trend.png", dpi=150)
    plt.close(fig)

    return latest


def analyze_tourism() -> tuple[pd.DataFrame, pd.DataFrame]:
    stay, _ = read_tourism_mock("stay")
    consumption, _ = read_tourism_mock("consumption")
    stay = stay.sort_values("stayIntensity", ascending=False)
    consumption = consumption.sort_values("consumptionIntensity", ascending=False)

    stay.to_csv(
        PROCESSED_DIR / "tourism_stay.csv", index=False, encoding="utf-8-sig"
    )
    consumption.to_csv(
        PROCESSED_DIR / "tourism_consumption.csv",
        index=False,
        encoding="utf-8-sig",
    )

    set_korean_font()
    top = consumption.head(10).sort_values("consumptionIntensity")
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.barh(top["areaName"], top["consumptionIntensity"], color="#4C78A8")
    ax.set_title("지역별 관광 소비 강도 (MOCK)")
    ax.set_xlabel("소비 강도")
    ax.set_ylabel("지역")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(REPORTS_DIR / "tourism_consumption_top10.png", dpi=150)
    plt.close(fig)

    return stay, consumption


def build_summary(
    naver_latest: pd.DataFrame,
    stay: pd.DataFrame,
    consumption: pd.DataFrame,
) -> pd.DataFrame:
    professor_summary = naver_latest[["keyword", "period", "ratio"]].copy()
    professor_summary = professor_summary.rename(columns={"ratio": "latest_ratio"})
    professor_summary["period"] = professor_summary["period"].dt.strftime("%Y-%m-%d")
    professor_summary.to_csv(
        PROCESSED_DIR / "analysis_summary.csv",
        index=False,
        encoding="utf-8-sig",
    )

    rows = []
    for row in naver_latest.itertuples(index=False):
        rows.append(
            {
                "section": "naver_latest",
                "name": row.keyword,
                "period": row.period.strftime("%Y-%m-%d"),
                "value": float(row.ratio),
                "change": None if pd.isna(row.change) else float(row.change),
                "metric": "relative_search_interest",
                "data_source": getattr(row, "data_source", "NAVER_API"),
            }
        )

    for row in stay.itertuples(index=False):
        rows.append(
            {
                "section": "tourism_stay",
                "name": row.areaName,
                "period": str(row.baseYm),
                "value": float(row.stayIntensity),
                "change": None,
                "metric": "stay_intensity",
                "data_source": row.data_source,
            }
        )

    for row in consumption.itertuples(index=False):
        rows.append(
            {
                "section": "tourism_consumption",
                "name": row.areaName,
                "period": str(row.baseYm),
                "value": float(row.consumptionIntensity),
                "change": None,
                "metric": "consumption_intensity",
                "data_source": row.data_source,
            }
        )

    summary = pd.DataFrame(rows)
    summary.to_csv(
        REPORTS_DIR / "analysis_summary.csv", index=False, encoding="utf-8-sig"
    )
    return summary


def main() -> None:
    naver_latest = analyze_naver()
    stay, consumption = analyze_tourism()
    summary = build_summary(naver_latest, stay, consumption)

    print("[PASS] STEP 13 analysis")
    print("NAVER latest rows:", len(naver_latest))
    print("Tourism stay rows:", len(stay))
    print("Tourism consumption rows:", len(consumption))
    print("Summary rows:", len(summary))
    print("Top NAVER keyword:", naver_latest.iloc[0]["keyword"])
    print("Top stay area:", stay.iloc[0]["areaName"])
    print("Top consumption area:", consumption.iloc[0]["areaName"])
    print("saved:", REPORTS_DIR / "naver_trend.png")
    print("saved:", REPORTS_DIR / "tourism_consumption_top10.png")
    print("saved:", REPORTS_DIR / "analysis_summary.csv")
    print("saved:", PROCESSED_DIR / "analysis_summary.csv")


if __name__ == "__main__":
    main()
