## [ BAMSAMBOT ]

디스코드 커뮤니티 뱀샘크루를 위한 자체 개발 디스코드 봇  
타 서버 사용 불가

### Git Flow
#### 1. Branch
- main
- develop
- feature
- refactor

#### 2. Commit Convention
- [Feat] : 기능 추가
- [Fix] : 기능 수정
- [Refactor] : 리팩토링

example: [Feat] 음악 재생 기능 추가
example: [Fix] username display bug



### Code Convention
1. Class명은 PascalCase로 작성한다.
2. 함수명은 snake_case로 작성한다.
3. 일반변수명은 camelCase로 작성한다.
    - boolean type은 **is**접두사를 붙여 작성한다.
    ex) isPremium, isDeveloper
4. 상수변수, 전역변수명은  UPPER_CASE로 작성한다.
5. 이 외 작명은 camelCase를 사용한다.



### Database Managing Rules
데이터베이스에 접근하는 명령어 함수 최상단에 필요한 데이터베이스를 모두 open한다.

사용한 데이터베이스는 해당 함수 최하단에서 dump한다.

다음은 데이터베이스별 파일 변수 이름이다.

| 파일 이름 | 변수 이름 |
| --- | --- |
| userdata.json | userdata |
| itemdata.json | itemdata |
| shop.json | shopdata |
| codes.json | codedata |

(DB system change project 이후 변경 예정)