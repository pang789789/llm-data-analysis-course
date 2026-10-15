# Step 12 — 관광 응답 구조 확인 기록

현재 확인한 파일은 **수업용 MOCK 응답**입니다. 실제 API를 연결하면 Swagger 응답을 기준으로 아래 필드명을 다시 확인해야 합니다.

| 구분 | 현재 MOCK 필드 |
|---|---|
| 지역 필드 | `areaName` |
| 기준월 필드 | `baseYm` |
| 체류 강도 필드 | `stayIntensity` |
| 소비 강도 필드 | `consumptionIntensity` |

확인한 구조:

```text
response
└─ body
   └─ items[]
      ├─ areaName
      ├─ baseYm
      └─ stayIntensity 또는 consumptionIntensity
```

실제 Swagger 응답을 받으면 이 문서의 `MOCK` 필드를 실제 필드명으로 교체합니다.

