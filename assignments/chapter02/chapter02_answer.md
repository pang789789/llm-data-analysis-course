# Chapter 02 확장 실습 답안

## 제출 전 개인정보 주의

- GitHub 계정 또는 별칭: `pang789789`
- 과제 작성일: `2026-09-04`
- 사용한 AI 도구: ChatGPT

---

# 1. PostgreSQL에서 현재 위치 확인

## 1-1. 실행한 SQL

```sql
SELECT version();
SELECT current_database();
SELECT current_user;
SELECT current_schema();
SHOW search_path;
```

## 1-2. 실행 결과 기록

```text
PostgreSQL 버전: PostgreSQL 18.4 on x86_64-windows
현재 데이터베이스: postgres
현재 사용자: postgres
현재 스키마: public
search_path: "$user", public
```

## 1-3. 구조를 내 말로 설명

```text
PostgreSQL은 데이터베이스를 관리하는 DBMS이다.

현재 접속한 데이터베이스는 postgres이다.

스키마는 데이터베이스 안에서 테이블 등의 객체를 묶어서 관리하는 논리적인 공간이다.

DBeaver 또는 psql 같은 도구는 PostgreSQL에 접속하여 SQL을 실행하고 데이터베이스를 관리하기 위한 클라이언트 도구이다.
```

## 1-4. 계층 구조 완성

```text
사용자
→ PostgreSQL 서버
→ PostgreSQL DBMS
→ 데이터베이스
→ 스키마
→ 테이블
→ 행 / 열
```

## 1-5. 증거 화면

PostgreSQL 환경을 확인하고 SQL 실행 결과를 확인했다.

---

# 2. 데이터베이스 안의 스키마와 테이블 관찰

## 2-1. 스키마 조회 결과

실행한 SQL:

```sql
SELECT schema_name
FROM information_schema.schemata
ORDER BY schema_name;
```

관찰한 스키마:

```text
1. information_schema
2. pg_catalog
3. public
```

### `public`은 무엇인가요?

```text
public은 PostgreSQL 데이터베이스에서 기본적으로 사용할 수 있는 스키마이다.
별도의 스키마를 지정하지 않고 테이블을 만들면 일반적으로 public 스키마에 생성된다.
```

### 데이터베이스와 스키마는 같은 것인가요?

```text
같지 않다.

데이터베이스는 데이터를 저장하고 관리하는 큰 단위이고,
스키마는 하나의 데이터베이스 안에서 테이블 등의 객체를 논리적으로 구분하는 단위이다.
```

## 2-2. 현재 보이는 테이블 조회

```sql
SELECT table_schema, table_name
FROM information_schema.tables
WHERE table_type = 'BASE TABLE'
  AND table_schema NOT IN ('pg_catalog', 'information_schema')
ORDER BY table_schema, table_name;
```

```text
조회된 사용자 테이블: Chapter 01에서 생성한 ch01_orders, ch01_questions, ch01_students 등을 확인할 수 있었다.

아직 테이블이 거의 없어도 괜찮은 이유:
데이터베이스는 처음부터 많은 테이블을 가지고 있어야 하는 것이 아니며,
필요한 업무 데이터를 기준으로 테이블을 설계하고 추가하면 되기 때문이다.
```

## 2-3. 관찰 정리

```text
PostgreSQL 서버 안에는 여러 데이터베이스가 있을 수 있다.
한 데이터베이스 안에는 여러 스키마가 있을 수 있다.
스키마 안에는 테이블과 같은 데이터베이스 객체가 존재한다.
```

---

# 3. TEMP TABLE로 테이블·행·열·키 직접 확인

## 3-1. 임시 테이블 생성 완료 확인

- [x] `ch02_students` 생성
- [x] `ch02_courses` 생성
- [x] `ch02_enrollments` 생성

| 테이블 | 한 행의 의미 |
| --- | --- |
| `ch02_students` | 한 명의 학생 정보 |
| `ch02_courses` | 하나의 강의 정보 |
| `ch02_enrollments` | 한 학생의 한 강의 수강신청 정보 |

## 3-2. 열의 의미 확인

### `ch02_students`

| 열 | 값의 의미 | 내부 식별자 / 업무 식별자 / 일반 속성 |
| --- | --- | --- |
| `id` | 학생을 데이터베이스 내부에서 식별하는 번호 | 내부 식별자 |
| `student_number` | 학생의 학번 | 업무 식별자 |
| `name` | 학생 이름 | 일반 속성 |
| `major` | 학생 전공 | 일반 속성 |

### `ch02_enrollments`

| 열 | 값의 의미 | PK / FK / 일반 속성 |
| --- | --- | --- |
| `id` | 수강신청 한 건을 식별하는 번호 | PK |
| `student_id` | 수강신청한 학생의 ID | FK |
| `course_id` | 신청한 강의의 ID | FK |
| `status` | 수강신청 상태 | 일반 속성 |

## 3-3. 입력된 행 수

```text
students 행 수: 3
courses 행 수: 2
enrollments 행 수: 4
```

## 3-4. 내부 식별자와 업무 식별자

```text
students.id가 필요한 이유:
데이터베이스에서 학생 한 명을 안정적으로 식별하고 다른 테이블에서 참조하기 위해 필요하다.

student_number가 필요한 이유:
실제 학교 업무에서 학생을 구분하기 위해 사용하는 의미 있는 식별자이기 때문이다.

둘을 항상 같은 값으로 사용하지 않아도 되는 이유:
내부 ID는 데이터베이스의 관계와 참조를 위한 값이고 학번은 업무상 의미를 가진 값이기 때문이다.
업무 식별자가 변경되거나 형식이 바뀌더라도 내부 ID는 그대로 유지할 수 있다.
```

## 3-5. 숫자처럼 보이는 학번을 문자열로 저장한 이유

```text
학번은 계산할 숫자가 아니라 학생을 식별하기 위한 코드이기 때문이다.
앞자리 0이 포함될 수도 있고 학교의 규칙에 따라 문자나 다른 형식이 포함될 수도 있으므로
숫자형보다는 문자열로 저장하는 것이 적절하다고 생각한다.
```

---

# 4. 테이블과 조회 결과는 다르다

## 4-1. 원본 테이블 행 수

```text
ch02_students 전체 행 수: 3
```

## 4-2. 일부 열만 조회

```sql
SELECT name, major
FROM ch02_students
ORDER BY id;
```

```text
원본 테이블의 열 수와 조회 결과의 열 수가 다른 이유:
SELECT에서 필요한 열만 선택했기 때문이다.
원본 테이블의 구조가 변경된 것이 아니라 조회 결과만 달라진 것이다.
```

## 4-3. 조건을 적용한 조회

```sql
SELECT id, student_number, name, major
FROM ch02_students
WHERE major = '컴퓨터공학'
ORDER BY id;
```

```text
원본 테이블 행 수: 3
조회 결과 행 수: 2
원본 테이블의 데이터가 삭제된 것인가?: 아니다.
그렇게 판단한 이유:
WHERE 조건에 맞는 행만 조회했을 뿐 실제 테이블의 데이터를 삭제하는 DELETE 명령을 실행한 것이 아니기 때문이다.
```

## 4-4. 정렬 결과 비교

```sql
SELECT id, name
FROM ch02_students
ORDER BY name ASC;

SELECT id, name
FROM ch02_students
ORDER BY name DESC;
```

```text
ASC 결과의 첫 학생: 김민수
DESC 결과의 첫 학생: 이지훈

이 실험을 통해 ORDER BY에 대해 알게 된 점:
ORDER BY는 조회 결과의 표시 순서를 변경하는 것이며 원본 데이터의 저장 순서를 변경하는 것은 아니다.
ASC는 오름차순, DESC는 내림차순 정렬을 의미한다.
```

## 4-5. 증거 화면

조회 결과를 확인하고 원본 테이블과 SELECT 결과의 차이를 확인했다.

---

# 5. PK와 FK를 실제로 관찰

## 5-1. 정상 데이터의 관계 읽기

```sql
SELECT
    e.id AS enrollment_id,
    s.name AS student_name,
    c.title AS course_title,
    e.status
FROM ch02_enrollments AS e
JOIN ch02_students AS s
    ON s.id = e.student_id
JOIN ch02_courses AS c
    ON c.id = e.course_id
ORDER BY e.id;
```

```text
한 행이 의미하는 것:
한 명의 학생이 특정 강의에 신청한 하나의 수강신청 정보를 의미한다.

같은 student_id가 여러 enrollment 행에서 반복될 수 있는 이유:
한 학생이 여러 강의를 수강할 수 있기 때문이다.

같은 course_id가 여러 enrollment 행에서 반복될 수 있는 이유:
하나의 강의를 여러 학생이 수강할 수 있기 때문이다.
```

## 5-2. 기본키 중복 오류 관찰

```text
실행 성공 / 실패: 실패
오류 메시지에서 확인한 핵심 단어: duplicate key / unique constraint
왜 실패했다고 생각하는가:
PK는 각 행을 유일하게 식별해야 하므로 이미 존재하는 PK 값을 다시 입력할 수 없기 때문이다.
```

## 5-3. 존재하지 않는 학생을 참조하는 FK 오류 관찰

```text
실행 성공 / 실패: 실패
오류 메시지에서 확인한 핵심 단어: foreign key constraint / key is not present
왜 실패했다고 생각하는가:
참조하려는 student_id가 부모 테이블인 ch02_students에 존재하지 않기 때문이다.
```

## 5-4. PK와 FK의 차이 정리

```text
PK는 각 테이블의 행을 유일하게 식별하기 위한 키이다.

FK는 다른 테이블의 데이터를 참조하고 테이블 사이의 관계를 표현하기 위한 키이다.

FK 값이 여러 행에서 반복될 수 있는 이유는
한 학생이 여러 수강신청을 할 수 있고 한 강의도 여러 학생이 수강할 수 있기 때문이다.
```

## 5-5. 증거 화면

PK 중복과 존재하지 않는 FK를 입력했을 때 오류가 발생하는 것을 확인했다.

---

# 6. 관계와 카디널리티를 자연어로 설명

```text
학생 한 명은 여러 수강신청을 가질 수 있는가?: 그렇다.

강의 한 개는 여러 수강신청을 가질 수 있는가?: 그렇다.

수강신청 한 건은 학생 몇 명을 참조하는가?: 한 명.

수강신청 한 건은 강의 몇 개를 참조하는가?: 한 개.
```

```text
students 1 ── N enrollments N ── 1 courses
```

### 학생과 강의가 N:M 관계라고 볼 수 있는 이유

```text
한 학생이 여러 강의를 수강할 수 있고,
한 강의도 여러 학생이 수강할 수 있기 때문이다.

학생과 강의 사이의 N:M 관계를 직접 연결하기보다는
enrollments라는 연결 테이블을 사용하여 관계를 표현한다.
```

---

# 7. AI가 만든 테이블 구조 직접 검토

## 7-1. AI에게 묻기 전에 내가 먼저 찾은 문제

```sql
CREATE TABLE student_courses (
    student_name VARCHAR(50),
    student_email VARCHAR(100),
    course_title VARCHAR(100),
    instructor_name VARCHAR(50)
);
```

```text
문제 1. 학생 정보가 여러 수강신청 행에 반복될 수 있다.
문제 2. 강의 정보가 여러 행에 반복될 수 있다.
문제 3. 학생과 강의를 식별할 고유한 ID가 없다.
문제 4. 학생 정보와 강의 정보가 하나의 테이블에 섞여 있어 수정 시 데이터 불일치가 발생할 수 있다.
```

## 7-2. AI 검토 요청 프롬프트

```text
다음과 같은 학생-강의 테이블 구조가 있습니다.

CREATE TABLE student_courses (
    student_name VARCHAR(50),
    student_email VARCHAR(100),
    course_title VARCHAR(100),
    instructor_name VARCHAR(50)
);

초보자의 관점에서 이 테이블 구조의 문제점을 검토해 주세요.
데이터 중복, 식별자, PK와 FK, 테이블 분리 관점에서 설명해 주세요.
그리고 어떤 구조로 개선하면 좋은지 제안해 주세요.
단, 실제 업무 규칙이 정해지지 않은 부분은 임의로 확정하지 말고
추가로 확인해야 할 사항으로 구분해 주세요.
```

## 7-3. AI 제안과 나의 판단

| AI의 지적 또는 제안 | 동의 / 수정 / 보류 | 나의 근거 |
| --- | --- | --- |
| 학생 정보를 별도 테이블로 분리 | 동의 | 학생 정보가 여러 수강신청에 반복되는 것을 줄일 수 있다. |
| 강의 정보를 별도 테이블로 분리 | 동의 | 강의 정보도 여러 학생에게 반복될 수 있기 때문이다. |
| 학생과 강의를 ID로 식별 | 동의 | 이름이나 강의명만으로는 유일한 식별이 어려울 수 있다. |
| 수강신청을 별도 테이블로 관리 | 동의 | 학생과 강의의 N:M 관계를 표현하기 적합하다. |
| 모든 업무 규칙을 AI가 결정 | 보류 | 실제 서비스의 업무 규칙은 사람이 정해야 한다. |

## 7-4. 본문과 대조한 항목

```text
AI가 설명한 내용:
학생과 강의가 여러 관계를 가질 경우 연결 테이블을 통해 관계를 관리하는 것이 좋다고 설명했다.

본문에서 확인한 내용:
students, courses, enrollments를 분리하고 enrollments가 학생과 강의를 연결하는 구조를 사용한다.

일치 / 부분 일치 / 수정 필요:
일치

내가 최종적으로 이해한 내용:
학생과 강의는 각각 독립적인 데이터이고 수강신청은 두 데이터를 연결하는 관계 데이터라는 것을 이해했다.
```

## 7-5. 증거 화면

AI에게 구조 검토를 요청하고 결과를 확인했다.

---

# 8. Chapter 01의 개인 서비스 아이디어를 DB 용어로 다시 표현

## 8-1. 서비스 기본 정보

```text
서비스 이름: 스터디 모임 관리 서비스
서비스 목적: 회원이 스터디에 참여하고 모임 일정, 출석, 질문 등을 관리할 수 있도록 하는 서비스
```

## 8-2. PostgreSQL 구조 후보

```text
데이터베이스 이름 후보: study_management
스키마 이름 후보: study
```

## 8-3. 테이블 후보와 한 행 의미

| 테이블 후보 | 한 행의 의미 | 내부 ID 후보 | 업무 식별자 후보 |
| --- | --- | --- | --- |
| members | 한 명의 회원 정보 | member_id | member_number 또는 email |
| studies | 하나의 스터디 정보 | study_id | study_code |
| participations | 한 회원의 한 스터디 참여 정보 | participation_id | member_id + study_id |
| meetings | 하나의 스터디 모임 정보 | meeting_id | meeting_code |
| attendance | 한 회원의 한 모임 출석 정보 | attendance_id | member_id + meeting_id |
| questions | 한 회원이 스터디에 작성한 질문 한 건 | question_id | 별도 업무 식별자 없음 |

## 8-4. FK 후보

```text
1. participations.member_id → members.member_id
   이유: 어떤 회원이 스터디에 참여했는지 연결하기 위해 필요하다.

2. participations.study_id → studies.study_id
   이유: 어떤 스터디에 참여했는지 연결하기 위해 필요하다.

3. meetings.study_id → studies.study_id
   이유: 해당 모임이 어느 스터디에 속하는지 표현하기 위해 필요하다.

4. attendance.member_id → members.member_id
   이유: 출석한 회원을 연결하기 위해 필요하다.

5. attendance.meeting_id → meetings.meeting_id
   이유: 어떤 모임의 출석인지 연결하기 위해 필요하다.

6. questions.member_id → members.member_id
   이유: 질문을 작성한 회원을 연결하기 위해 필요하다.

7. questions.study_id → studies.study_id
   이유: 질문이 어느 스터디와 관련되어 있는지 표현하기 위해 필요하다.
```

## 8-5. 자연어 관계 문장

```text
1. 한 회원은 여러 스터디에 참여할 수 있다.
2. 한 스터디에는 여러 회원이 참여할 수 있다.
3. 한 스터디에는 여러 모임이 있을 수 있다.
4. 한 모임에는 여러 회원의 출석 정보가 있을 수 있다.
5. 한 회원은 여러 질문을 작성할 수 있다.
```

## 8-6. 아직 확정하지 않을 정책

```text
Q1. 동일 회원이 같은 스터디에 중복 참여할 수 있는지 결정해야 한다.
Q2. 탈퇴한 회원의 과거 참여 및 출석 기록을 얼마나 오래 보관할지 결정해야 한다.
Q3. 출석 정보의 상태와 날짜가 NULL이 될 수 있는지 결정해야 한다.
```

---

# 9. AI를 개인 구조의 검토자로 사용

## 9-1. 사용한 프롬프트

```text
스터디 모임 관리 서비스를 데이터베이스로 설계하고 있습니다.

현재 회원, 스터디, 스터디 참여, 모임, 출석, 질문 테이블을 생각하고 있습니다.

다음 관점에서 구조를 검토해 주세요.

1. 중복 데이터가 발생할 가능성
2. 회원과 스터디의 관계
3. 회원과 모임의 출석 관계
4. 질문 데이터가 어떤 테이블과 연결되어야 하는지
5. NULL 허용 여부를 결정해야 하는 부분
6. 탈퇴 회원의 과거 이력 관리

기술적으로 개선할 수 있는 부분과
서비스 정책으로 사람이 결정해야 하는 부분을 구분해서 설명해 주세요.
```

## 9-2. AI가 질문한 내용 중 유용했던 것

```text
1. 동일 회원의 동일 스터디 중복 참여를 허용할지 확인해야 한다는 점
2. 출석 정보를 별도의 관계 데이터로 관리해야 한다는 점
3. 탈퇴 회원의 과거 데이터를 삭제할지 보존할지 업무 정책이 필요하다는 점
```

## 9-3. AI가 너무 빨리 결정한 내용 또는 내가 보류한 내용

```text
1. 탈퇴 회원 데이터를 무조건 삭제하거나 보존하는 것은 서비스 정책에 따라 달라지므로 보류했다.
2. 모든 컬럼의 NULL 허용 여부는 실제 업무 흐름을 더 확인한 뒤 결정해야 하므로 보류했다.
```

## 9-4. 검토 후 수정한 구조

| 수정 전 | 수정 후 | 수정 이유 |
| --- | --- | --- |
| 회원과 스터디 정보를 직접 한 테이블에서 관리 | `members`, `studies`, `participations`로 분리 | N:M 관계를 명확하게 표현하기 위해 |
| 출석을 모임 테이블에 직접 저장 | `attendance` 테이블로 분리 | 회원과 모임 사이의 관계를 표현하기 위해 |
| 질문에 불필요한 회원 정보를 반복 저장 | 회원 ID와 스터디 ID로 연결 | 중복 데이터를 줄이고 관계를 명확하게 하기 위해 |

---

# 10. 최종 개념 정리

```text
PostgreSQL은 데이터베이스를 관리하는 DBMS이다.

DBeaver 또는 psql은 PostgreSQL에 접속해서 SQL을 실행하고 데이터를 확인하는 도구이다.

데이터베이스와 스키마의 차이는 데이터베이스가 더 큰 저장 및 관리 단위이고 스키마는 데이터베이스 안에서 객체를 논리적으로 구분하는 단위라는 것이다.

테이블 한 행은 특정 객체나 사건을 하나 표현하는 데이터이다.

조회 결과가 원본 테이블과 다른 이유는 SELECT, WHERE, ORDER BY 등의 조건에 따라 필요한 행과 열만 선택하여 보여줄 수 있기 때문이다.

내부 식별자와 업무 식별자의 차이는 내부 식별자는 데이터베이스에서 관계와 참조를 안정적으로 관리하기 위한 값이고, 업무 식별자는 실제 업무에서 의미를 가지고 객체를 구분하는 값이라는 점이다.

PK는 테이블의 각 행을 유일하게 식별하기 위한 키이다.

FK는 다른 테이블의 데이터를 참조하고 테이블 사이의 관계를 표현하기 위한 키이다.
```

---

# 11. 이번 Chapter에서 새롭게 알게 된 점

```text
1. 데이터베이스와 스키마는 같은 개념이 아니며 하나의 데이터베이스 안에도 여러 스키마가 존재할 수 있다는 것을 알게 되었다.

2. SELECT와 WHERE를 사용한 조회는 원본 테이블을 변경하는 것이 아니라 조회 결과만 바꾸는 것이라는 점을 확인했다.

3. PK는 데이터를 유일하게 식별하고 FK는 테이블 사이의 관계를 연결한다는 차이를 실제 오류를 통해 이해했다.

4. 학생과 강의처럼 서로 여러 개씩 연결되는 관계는 중간에 수강신청 같은 연결 테이블을 사용하여 표현할 수 있다는 것을 알게 되었다.
```

## 아직 헷갈리는 내용

```text
1. 실제 서비스에서 내부 ID와 업무 식별자를 어떤 기준으로 선택해야 하는지 더 공부할 필요가 있다.

2. NULL 허용 여부와 삭제 정책을 어떤 기준으로 결정해야 하는지 아직 더 이해할 필요가 있다.
```

## AI에게 다시 질문하고 싶은 내용

```text
실제 서비스에서 PK, FK, UNIQUE 제약조건을 어떤 기준으로 설계하는지,
그리고 회원 탈퇴나 데이터 삭제가 발생했을 때 과거 데이터를 어떻게 보존하는지 더 질문해 보고 싶다.
```

---

# 12. 제출 전 자기 점검

- [x] PostgreSQL에서 현재 database / schema / search_path를 확인했다.
- [x] DBMS, database, schema, table을 구분해서 설명할 수 있다.
- [x] TEMP TABLE 3개를 생성하고 데이터를 조회했다.
- [x] 각 테이블의 한 행 의미를 작성했다.
- [x] 테이블과 조회 결과가 다르다는 것을 확인했다.
- [x] ORDER BY의 의미를 확인했다.
- [x] 내부 식별자와 업무 식별자의 차이를 설명했다.
- [x] PK 중복 입력 실패를 확인했다.
- [x] 존재하지 않는 FK 참조 실패를 확인했다.
- [x] FK 값이 반복될 수 있는 이유를 설명했다.
- [x] AI가 만든 테이블 구조를 먼저 검토했다.
- [x] AI 설명 중 하나 이상을 본문 내용과 대조했다.
- [x] 개인 서비스의 테이블 후보를 작성했다.
- [x] 개인 서비스의 FK 후보와 미확정 정책을 작성했다.
- [x] 실제 비밀번호·API Key·민감한 접속 정보를 작성하지 않았다.

---

# 13. GitHub 제출 정보

답안 파일 위치:

```text
assignments/chapter02/chapter02_answer.md
```

이미지 폴더:

```text
assignments/chapter02/images/
```

LMS 제출 URL:

```text
https://github.com/pang789789/llm-data-analysis-course/blob/main/assignments/chapter02/chapter02_answer.md
```
