# Chapter 01. AI와 함께하는 데이터 분석의 시작

## 제출 정보

- GitHub 계정: `pang789789`
- 사용한 AI 도구: ChatGPT
- 데이터: 수업용 가상 쇼핑몰 CSV 4개

## STEP 1. 질문 구체화

### 원래 업무 질문

요즘 매출이 줄어든 것 같은데 왜 그런가?

### 모호한 이유

기간, 주문 상태, 금액 계산 방식, 비교 기준이 정해져 있지 않아 현재 데이터만으로 바로 답할 수 없다.

### 구체화한 분석 질문

최근 12개월 동안 `completed` 주문의 월별 판매 금액은 어떻게 변하며, 판매 금액이 큰 상품 카테고리는 무엇인가?

### 나의 판단

`order_items.quantity × order_items.unit_price`를 주문 상세 금액으로 정의하고, `orders.order_status == "completed"`인 주문만 분석 범위에 포함하기로 했다. 이 계산값은 할인·반품·배송비를 반영한 순매출이나 이익이라고 단정할 수 없다.

## STEP 2. 질문과 데이터 구조 연결

필요한 파일과 컬럼은 다음과 같다.

| 목적 | 파일 | 컬럼 |
| --- | --- | --- |
| 완료 주문 선택 및 월 기준 | `orders.csv` | `order_id`, `order_date`, `order_status` |
| 주문 상세 금액 계산 | `order_items.csv` | `order_id`, `product_id`, `quantity`, `unit_price` |
| 카테고리 연결 | `products.csv` | `product_id`, `category` |

파일 관계는 `orders.order_id → order_items.order_id`, `products.product_id → order_items.product_id`이다. 실제 CSV를 확인한 결과 네 파일 모두 존재했으며, `orders`의 고객 ID와 `order_items`의 주문·상품 ID에서 부모 테이블에 없는 값은 0건이었다.

## STEP 3. LLM에게 질문 후보 요청

### 사용한 Prompt

```text
온라인 쇼핑몰 데이터 분석을 준비하고 있습니다.
데이터는 customers, products, orders, order_items의 4개 CSV로 구성됩니다.
목적은 completed 주문 기준 판매 금액과 구매 패턴을 이해하는 것입니다.
현재 데이터로 확인 가능한 분석 질문 5개와 각 질문에 필요한 파일·컬럼 후보를 제안해 주세요.
원인을 단정하지 말아 주세요.
```

### 답변에서 검토한 후보

1. 월별 completed 주문 판매 금액 추이
2. 카테고리별 completed 주문 판매 금액 비교
3. 상품별 판매 금액 순위
4. 고객별 구매 금액 분포
5. 결제수단별 주문 상태 분포

## STEP 4. LLM 제안 검증

| 제안 | 검증 | 최종 판단 |
| --- | --- | --- |
| 카테고리별 completed 주문 금액 비교 | `products.category`, `orders.order_status`, `order_items.quantity`, `unit_price`가 실제 존재한다. | 사용 |
| 고객 직업별 구매 금액 비교 | `customers.csv`에 직업 컬럼이 없다. | 보류 |
| 월별 판매 금액 감소 원인 규명 | 월별 금액은 계산할 수 있지만 프로모션·재고·광고 정보가 없다. | 수정 후 사용 |

### 해석

LLM이 제안한 질문도 실제 컬럼과 계산 범위를 확인해야 한다. 특히 월별 판매 금액 변화는 관찰할 수 있지만, 변화의 원인을 현재 네 CSV만으로 확정할 수는 없다.

## STEP 5. Prompt Log

| 항목 | 기록 |
| --- | --- |
| 사용 목적 | 분석 질문 후보 만들기 |
| 입력 정보 | 파일명과 컬럼 역할만 제공 |
| 실제 반영 | 카테고리·월별 completed 주문 금액 질문 채택 |
| 사람이 검증한 항목 | 컬럼 존재 여부, 주문 상태 범위, 계산 기준, 키 관계 |
| 보류한 항목 | 직업별 분석, 판매 변화 원인 단정 |

## 보안 확인

- API Key, Token, 비밀번호, `.env` 실제 값은 이 문서와 GitHub에 포함하지 않았다.
- 수업용 가상 쇼핑몰 데이터만 사용했다.

## 최종 정리

이번 장에서는 LLM이 만든 질문을 바로 정답으로 사용하지 않고, 실제 데이터 구조와 컬럼을 대조한 뒤 분석 범위를 정했다. 분석 결과를 해석할 때도 판매 금액과 이익, 관찰과 원인 설명을 구분해야 한다.

> Evidence 이미지는 실제 VS Code·LLM 화면을 캡처한 뒤 `chapter01/images/`에 추가한다. 실제로 촬영하지 않은 화면을 Evidence로 만들지는 않았다.
