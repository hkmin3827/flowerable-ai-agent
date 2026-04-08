REGIONS = [
    "서울", "경기", "강원", "광주", "인천", "대구", "부산",
    "대전", "울산", "세종", "충북", "충남", "전북", "전남",
    "경북", "경남", "제주",
    "서울특별시", "경기도", "강원특별자치도", "광주광역시",
    "인천광역시", "대구광역시", "부산광역시", "대전광역시",
    "울산광역시", "세종특별자치시", "충청북도", "충청남도",
    "전라북도", "전라남도", "경상북도", "경상남도", "제주특별자치도",
]

ALL_FLOWERS = [
    "튤립", "프리지아", "라넌큘러스", "수선화", "히아신스", "조팝나무",
    "아카시아", "무스카리", "아네모네", "아이리스", "작약", "라일락",
    "스위트피", "칼라", "은방울꽃", "해바라기", "장미", "백합", "델피늄",
    "리시안셔스", "안개꽃", "글라디올러스", "안스리움", "거베라", "천일홍",
    "글로리오사", "수국", "알스트로메리아", "칼랑코에", "지니아", "아마릴리스",
    "베고니아", "국화", "소국", "코스모스", "다알리아", "핑크뮬리", "팜파스",
    "용담", "에린지움", "아스트란시아", "메리골드", "아스터", "셀로시아",
    "포인세티아", "목화", "스토크", "시클라멘", "심비디움", "카네이션",
    "낙산홍", "스노우드롭", "헬레보루스", "왁스플라워",
]

REGION_MAP = {
    "서울": "SEOUL", "경기": "GYEONGGI", "강원": "GANGWON",
    "광주": "GWANGJU", "인천": "INCHEON", "대구": "DAEGU",
    "부산": "BUSAN", "대전": "DAEJEON", "울산": "ULSAN",
    "세종": "SEJONG", "충북": "CHUNGBUK", "충청북도": "CHUNGBUK",
    "충남": "CHUNGNAM", "충청남도": "CHUNGNAM",
    "전북": "JEONBUK", "전라북도": "JEONBUK",
    "전남": "JEONNAM", "전라남도": "JEONNAM",
    "경북": "GYEONGBUK", "경상북도": "GYEONGBUK",
    "경남": "GYEONGNAM", "경상남도": "GYEONGNAM",
    "제주": "JEJU",
    "서울특별시": "SEOUL", "경기도": "GYEONGGI",
    "강원특별자치도": "GANGWON", "광주광역시": "GWANGJU",
    "인천광역시": "INCHEON", "대구광역시": "DAEGU",
    "부산광역시": "BUSAN", "대전광역시": "DAEJEON",
    "울산광역시": "ULSAN", "세종특별자치시": "SEJONG",
    "제주특별자치도": "JEJU",
}

# 인접 광역/도 (Region 레벨 fallback용 - district 없을 때 최후 수단)
NEARBY_REGIONS = {
    "SEOUL": ["GYEONGGI", "INCHEON"],
    "GYEONGGI": ["SEOUL", "INCHEON", "GANGWON", "CHUNGNAM", "CHUNGBUK"],
    "INCHEON": ["SEOUL", "GYEONGGI"],
    "GANGWON": ["GYEONGGI", "CHUNGBUK", "GYEONGBUK"],
    "DAEJEON": ["CHUNGNAM", "CHUNGBUK", "GYEONGBUK", "GYEONGNAM"],
    "CHUNGBUK": ["GYEONGGI", "GANGWON", "DAEJEON", "CHUNGNAM"],
    "CHUNGNAM": ["GYEONGGI", "DAEJEON", "CHUNGBUK", "JEONBUK"],
    "GWANGJU": ["JEONNAM", "JEONBUK"],
    "JEONBUK": ["CHUNGNAM", "GWANGJU", "JEONNAM", "GYEONGNAM"],
    "JEONNAM": ["GWANGJU", "JEONBUK", "GYEONGNAM"],
    "DAEGU": ["GYEONGBUK", "GYEONGNAM"],
    "GYEONGBUK": ["DAEGU", "GANGWON", "CHUNGBUK", "GYEONGNAM"],
    "GYEONGNAM": ["DAEGU", "BUSAN", "ULSAN", "JEONNAM"],
    "BUSAN": ["GYEONGNAM", "ULSAN"],
    "ULSAN": ["BUSAN", "GYEONGNAM", "GYEONGBUK"],
    "SEJONG": ["DAEJEON", "CHUNGNAM", "CHUNGBUK"],
    "JEJU": [],
}


DISTRICT_LOOKUP = {
    # ── 서울 (대부분 고유) ──────────────────────────────────────────────
    "종로구": ["SEOUL_JONGNO"],
    "용산구": ["SEOUL_YONGSAN"],
    "성동구": ["SEOUL_SEONGDONG"],
    "광진구": ["SEOUL_GWANGJIN"],
    "동대문구": ["SEOUL_DONGDAEMUN"],
    "중랑구": ["SEOUL_JUNGNANG"],
    "성북구": ["SEOUL_SEONGBUK"],
    "강북구": ["SEOUL_GANGBUK"],
    "도봉구": ["SEOUL_DOBONG"],
    "노원구": ["SEOUL_NOWON"],
    "은평구": ["SEOUL_EUNPYEONG"],
    "서대문구": ["SEOUL_SEODAEMUN"],
    "마포구": ["SEOUL_MAPO"],
    "양천구": ["SEOUL_YANGCHEON"],
    "구로구": ["SEOUL_GURO"],
    "금천구": ["SEOUL_GEUMCHEON"],
    "영등포구": ["SEOUL_YEONGDEUNGPO"],
    "동작구": ["SEOUL_DONGJAK"],
    "관악구": ["SEOUL_GWANAK"],
    "서초구": ["SEOUL_SEOCHO"],
    "강남구": ["SEOUL_GANGNAM"],
    "송파구": ["SEOUL_SONGPA"],
    "강동구": ["SEOUL_GANGDONG"],
    # 중복: 중구(6개), 동구(6개), 서구(5개), 남구(4개), 북구(4개), 강서구(2개)
    "중구":   ["SEOUL_JUNGGU", "INCHEON_JUNGGU", "DAEGU_JUNGGU",
               "DAEJEON_JUNGGU", "BUSAN_JUNGGU", "ULSAN_JUNGGU"],
    "동구":   ["INCHEON_DONGGU", "DAEGU_DONGGU", "BUSAN_DONGGU",
               "GWANGJU_DONGGU", "DAEJEON_DONGGU", "ULSAN_DONGGU"],
    "서구":   ["INCHEON_SEOGU", "DAEGU_SEOGU", "BUSAN_SEOGU",
               "GWANGJU_SEOGU", "DAEJEON_SEOGU"],
    "남구":   ["DAEGU_NAMGU", "BUSAN_NAMGU", "GWANGJU_NAMGU", "ULSAN_NAMGU"],
    "북구":   ["DAEGU_BUKGU", "BUSAN_BUKGU", "GWANGJU_BUKGU", "ULSAN_BUKGU"],
    "강서구": ["SEOUL_GANGSEO", "BUSAN_GANGSEOGU"],

    # ── 인천 고유 ───────────────────────────────────────────────────────
    "미추홀구": ["INCHEON_MICHUHOL"],
    "연수구":   ["INCHEON_YEONSUGU"],
    "남동구":   ["INCHEON_NAMDONGGU"],
    "부평구":   ["INCHEON_BUPYEONGGU"],
    "계양구":   ["INCHEON_GYEYANGGU"],
    "강화군":   ["INCHEON_GANGHWA"],
    "옹진군":   ["INCHEON_ONGJIN"],

    # ── 대구 고유 ───────────────────────────────────────────────────────
    "수성구": ["DAEGU_SUSEONGGU"],
    "달서구": ["DAEGU_DALSEOGU"],
    "달성군": ["DAEGU_DALSEONG"],
    "군위군": ["DAEGU_GUNWI"],

    # ── 부산 고유 ───────────────────────────────────────────────────────
    "영도구":   ["BUSAN_YEONGDOGU"],
    "부산진구": ["BUSAN_BUSANJINGU"],
    "동래구":   ["BUSAN_DONGNAEGU"],
    "해운대구": ["BUSAN_HAEUNDAEGU"],
    "사하구":   ["BUSAN_SAHAGU"],
    "금정구":   ["BUSAN_GEUMJEONGGU"],
    "연제구":   ["BUSAN_YEONJEGU"],
    "수영구":   ["BUSAN_SUYEONGGU"],
    "사상구":   ["BUSAN_SASANGGU"],
    "기장군":   ["BUSAN_GIJANG"],

    # ── 광주 고유 ───────────────────────────────────────────────────────
    "광산구": ["GWANGJU_GWANGSAN"],

    # ── 대전 고유 ───────────────────────────────────────────────────────
    "유성구": ["DAEJEON_YUSEONG"],
    "대덕구": ["DAEJEON_DAEDEOK"],

    # ── 울산 고유 ───────────────────────────────────────────────────────
    "울주군": ["ULSAN_ULJU"],

    # ── 경기 ────────────────────────────────────────────────────────────
    "수원시": ["GYEONGGI_SUWON"],    "성남시": ["GYEONGGI_SEONGNAM"],
    "의정부시": ["GYEONGGI_UIJEONGBU"], "안양시": ["GYEONGGI_ANYANG"],
    "부천시": ["GYEONGGI_BUCHEON"],  "광명시": ["GYEONGGI_GWANGMYEONG"],
    "평택시": ["GYEONGGI_PYEONGTAEK"], "동두천시": ["GYEONGGI_DONGDUCHEON"],
    "안산시": ["GYEONGGI_ANSAN"],    "고양시": ["GYEONGGI_GOYANG"],
    "과천시": ["GYEONGGI_GWACHEON"], "구리시": ["GYEONGGI_GURI"],
    "남양주시": ["GYEONGGI_NAMYANGJU"], "오산시": ["GYEONGGI_OSAN"],
    "시흥시": ["GYEONGGI_SIHEUNG"],  "군포시": ["GYEONGGI_GUNPO"],
    "의왕시": ["GYEONGGI_UIWANG"],   "하남시": ["GYEONGGI_HANAM"],
    "용인시": ["GYEONGGI_YONGIN"],   "파주시": ["GYEONGGI_PAJU"],
    "이천시": ["GYEONGGI_ICHON"],    "안성시": ["GYEONGGI_ANSEONG"],
    "김포시": ["GYEONGGI_GIMPO"],    "화성시": ["GYEONGGI_HWASEONG"],
    "광주시": ["GYEONGGI_GWANGJU"],  "양주시": ["GYEONGGI_YANGJU"],
    "포천시": ["GYEONGGI_POCHEON"],  "여주시": ["GYEONGGI_YEOJU"],
    "연천군": ["GYEONGGI_YEONCHEON"], "가평군": ["GYEONGGI_GAPYEONG"],
    "양평군": ["GYEONGGI_YANGPYEONG"],

    # ── 강원 ────────────────────────────────────────────────────────────
    "춘천시": ["GANGWON_CHUNCHEON"], "원주시": ["GANGWON_WONJU"],
    "강릉시": ["GANGWON_GANGNEUNG"], "동해시": ["GANGWON_DONGHAE"],
    "태백시": ["GANGWON_TAEBAEK"],   "속초시": ["GANGWON_SOKCHO"],
    "삼척시": ["GANGWON_SAMCHEOK"],  "홍천군": ["GANGWON_HONGCHEON"],
    "횡성군": ["GANGWON_HOENGSEONG"], "영월군": ["GANGWON_YEONGWOL"],
    "평창군": ["GANGWON_PYEONGCHANG"], "정선군": ["GANGWON_JEONGSEON"],
    "철원군": ["GANGWON_CHORWON"],   "화천군": ["GANGWON_HWACHEON"],
    "양구군": ["GANGWON_YANGGU"],    "인제군": ["GANGWON_INJE"],
    "양양군": ["GANGWON_YANGYANG"],
    "고성군": ["GANGWON_GOSEONG", "GYEONGNAM_GOSEONG"],  # 중복

    # ── 충북 ────────────────────────────────────────────────────────────
    "청주시": ["CHUNGBUK_CHEONGJU"], "충주시": ["CHUNGBUK_CHUNGJU"],
    "제천시": ["CHUNGBUK_JECHEON"],  "보은군": ["CHUNGBUK_BOEUN"],
    "옥천군": ["CHUNGBUK_OKCHEON"],  "영동군": ["CHUNGBUK_YEONGDONG"],
    "증평군": ["CHUNGBUK_JEUNGPYEONG"], "진천군": ["CHUNGBUK_JINCHEON"],
    "괴산군": ["CHUNGBUK_GOESAN"],   "음성군": ["CHUNGBUK_EUMSEONG"],
    "단양군": ["CHUNGBUK_DANYANG"],

    # ── 충남 ────────────────────────────────────────────────────────────
    "천안시": ["CHUNGNAM_CHEONAN"],  "공주시": ["CHUNGNAM_GONGJU"],
    "보령시": ["CHUNGNAM_BORYEONG"], "아산시": ["CHUNGNAM_ASAN"],
    "서산시": ["CHUNGNAM_SEOSAN"],   "논산시": ["CHUNGNAM_NONSAN"],
    "계룡시": ["CHUNGNAM_GYERYONG"], "당진시": ["CHUNGNAM_DANGJIN"],
    "금산군": ["CHUNGNAM_GEUMSAN"],  "부여군": ["CHUNGNAM_BUYEO"],
    "서천군": ["CHUNGNAM_SEOCHEON"], "청양군": ["CHUNGNAM_CHEONGYANG"],
    "홍성군": ["CHUNGNAM_HONGSEONG"], "예산군": ["CHUNGNAM_YESAN"],
    "태안군": ["CHUNGNAM_TAEAN"],

    # ── 전북 ────────────────────────────────────────────────────────────
    "전주시": ["JEONBUK_JEONJU"],    "군산시": ["JEONBUK_GUNSAN"],
    "익산시": ["JEONBUK_IKSAN"],     "정읍시": ["JEONBUK_JEOBUP"],
    "남원시": ["JEONBUK_NAMWON"],    "김제시": ["JEONBUK_GIMJE"],
    "완주군": ["JEONBUK_WANJU"],     "진안군": ["JEONBUK_JINAN"],
    "무주군": ["JEONBUK_MUJU"],      "장수군": ["JEONBUK_JANGSU"],
    "임실군": ["JEONBUK_IMSIL"],     "순창군": ["JEONBUK_SUNCHANG"],
    "고창군": ["JEONBUK_GOCHANG"],   "부안군": ["JEONBUK_BUAN"],

    # ── 전남 ────────────────────────────────────────────────────────────
    "목포시": ["JEONNAM_MOKPO"],     "여수시": ["JEONNAM_YEOSU"],
    "순천시": ["JEONNAM_SUNCHEON"],  "나주시": ["JEONNAM_NAJU"],
    "광양시": ["JEONNAM_GWANGYANG"], "담양군": ["JEONNAM_DAMYANG"],
    "곡성군": ["JEONNAM_GOKSEONG"],  "구례군": ["JEONNAM_GURYE"],
    "고흥군": ["JEONNAM_GOHEUNG"],   "보성군": ["JEONNAM_BOSEONG"],
    "화순군": ["JEONNAM_HWASUN"],    "장흥군": ["JEONNAM_JANGHEUNG"],
    "강진군": ["JEONNAM_GANGJIN"],   "해남군": ["JEONNAM_HAENAM"],
    "영암군": ["JEONNAM_YEONGAM"],   "무안군": ["JEONNAM_MUAN"],
    "함평군": ["JEONNAM_HAMPYEONG"], "영광군": ["JEONNAM_YEONGGWANG"],
    "장성군": ["JEONNAM_JANGSEONG"], "완도군": ["JEONNAM_WANDO"],
    "진도군": ["JEONNAM_JINDO"],     "신안군": ["JEONNAM_SINAN"],

    # ── 경북 ────────────────────────────────────────────────────────────
    "포항시": ["GYEONGBUK_POHANG"],  "경주시": ["GYEONGBUK_GYEONGJU"],
    "김천시": ["GYEONGBUK_GIMCHEON"], "안동시": ["GYEONGBUK_ANDONG"],
    "구미시": ["GYEONGBUK_GUMI"],    "영주시": ["GYEONGBUK_YEONGJU"],
    "상주시": ["GYEONGBUK_SANGJU"],  "문경시": ["GYEONGBUK_MUNGYEONG"],
    "경산시": ["GYEONGBUK_GYEONGSAN"], "의성군": ["GYEONGBUK_UISONG"],
    "청송군": ["GYEONGBUK_CHEONGSONG"], "영양군": ["GYEONGBUK_YEONGYANG"],
    "영덕군": ["GYEONGBUK_YEONGDEOK"], "청도군": ["GYEONGBUK_CHONGDO"],
    "고령군": ["GYEONGBUK_GORYEONG"], "성주군": ["GYEONGBUK_SEONGJU"],
    "칠곡군": ["GYEONGBUK_CHILGOK"], "예천군": ["GYEONGBUK_YECHON"],
    "봉화군": ["GYEONGBUK_BONGHWA"], "울진군": ["GYEONGBUK_ULJIN"],
    "울릉군": ["GYEONGBUK_ULLUNG"],

    # ── 경남 ────────────────────────────────────────────────────────────
    "창원시": ["GYEONGNAM_CHANGWON"], "진주시": ["GYEONGNAM_JINJU"],
    "통영시": ["GYEONGNAM_TONGYEONG"], "사천시": ["GYEONGNAM_SACHEON"],
    "김해시": ["GYEONGNAM_GIMHAE"],  "밀양시": ["GYEONGNAM_MIRYANG"],
    "거제시": ["GYEONGNAM_GEOJE"],   "양산시": ["GYEONGNAM_YANGSAN"],
    "의령군": ["GYEONGNAM_UIRYEONG"], "함안군": ["GYEONGNAM_HAMAN"],
    "창녕군": ["GYEONGNAM_CHANGNYEONG"], "남해군": ["GYEONGNAM_NAMHAE"],
    "하동군": ["GYEONGNAM_HADONG"],  "산청군": ["GYEONGNAM_SANCHEONG"],
    "함양군": ["GYEONGNAM_HAMYANG"], "거창군": ["GYEONGNAM_GEOCHANG"],
    "합천군": ["GYEONGNAM_HAPCHEON"],

    # ── 세종 / 제주 ─────────────────────────────────────────────────────
    "세종특별자치시": ["SEJONG_ALL"],
    "세종시": ["SEJONG_ALL"],
    "제주시": ["JEJU_JEJU"],
    "서귀포시": ["JEJU_SEOGWIPO"],
}

NEARBY_DISTRICTS = {
    # ── 서울 ─────────────────────────────────────────────────────────────
    "SEOUL_JONGNO":       ["SEOUL_JUNGGU", "SEOUL_YONGSAN", "SEOUL_EUNPYEONG", "SEOUL_SEODAEMUN"],
    "SEOUL_JUNGGU":       ["SEOUL_JONGNO", "SEOUL_YONGSAN", "SEOUL_SEONGDONG"],
    "SEOUL_YONGSAN":      ["SEOUL_JUNGGU", "SEOUL_JONGNO", "SEOUL_SEONGDONG", "SEOUL_MAPO", "SEOUL_DONGJAK"],
    "SEOUL_SEONGDONG":    ["SEOUL_JUNGGU", "SEOUL_GWANGJIN", "SEOUL_DONGDAEMUN", "SEOUL_YONGSAN"],
    "SEOUL_GWANGJIN":     ["SEOUL_SEONGDONG", "SEOUL_DONGDAEMUN", "SEOUL_JUNGNANG", "SEOUL_SONGPA"],
    "SEOUL_DONGDAEMUN":   ["SEOUL_JUNGNANG", "SEOUL_SEONGBUK", "SEOUL_SEONGDONG", "SEOUL_GWANGJIN"],
    "SEOUL_JUNGNANG":     ["SEOUL_DONGDAEMUN", "SEOUL_SEONGBUK", "SEOUL_NOWON", "SEOUL_GWANGJIN"],
    "SEOUL_SEONGBUK":     ["SEOUL_JONGNO", "SEOUL_DONGDAEMUN", "SEOUL_JUNGNANG", "SEOUL_NOWON", "SEOUL_GANGBUK"],
    "SEOUL_GANGBUK":      ["SEOUL_SEONGBUK", "SEOUL_DOBONG", "SEOUL_NOWON", "SEOUL_EUNPYEONG"],
    "SEOUL_DOBONG":       ["SEOUL_GANGBUK", "SEOUL_NOWON", "SEOUL_SEONGBUK"],
    "SEOUL_NOWON":        ["SEOUL_DOBONG", "SEOUL_GANGBUK", "SEOUL_SEONGBUK", "SEOUL_JUNGNANG"],
    "SEOUL_EUNPYEONG":    ["SEOUL_SEODAEMUN", "SEOUL_MAPO", "SEOUL_GANGBUK", "SEOUL_JONGNO"],
    "SEOUL_SEODAEMUN":    ["SEOUL_JONGNO", "SEOUL_EUNPYEONG", "SEOUL_MAPO"],
    "SEOUL_MAPO":         ["SEOUL_SEODAEMUN", "SEOUL_EUNPYEONG", "SEOUL_GANGSEO", "SEOUL_YEONGDEUNGPO", "SEOUL_YONGSAN"],
    "SEOUL_YANGCHEON":    ["SEOUL_GANGSEO", "SEOUL_GURO", "SEOUL_YEONGDEUNGPO"],
    "SEOUL_GANGSEO":      ["SEOUL_YANGCHEON", "SEOUL_GURO", "SEOUL_MAPO"],
    "SEOUL_GURO":         ["SEOUL_GANGSEO", "SEOUL_YANGCHEON", "SEOUL_GEUMCHEON", "SEOUL_YEONGDEUNGPO"],
    "SEOUL_GEUMCHEON":    ["SEOUL_GURO", "SEOUL_YEONGDEUNGPO", "SEOUL_DONGJAK", "SEOUL_GWANAK"],
    "SEOUL_YEONGDEUNGPO": ["SEOUL_YANGCHEON", "SEOUL_GURO", "SEOUL_GEUMCHEON", "SEOUL_DONGJAK", "SEOUL_MAPO"],
    "SEOUL_DONGJAK":      ["SEOUL_GWANAK", "SEOUL_SEOCHO", "SEOUL_GEUMCHEON", "SEOUL_YEONGDEUNGPO", "SEOUL_YONGSAN"],
    "SEOUL_GWANAK":       ["SEOUL_DONGJAK", "SEOUL_SEOCHO", "SEOUL_GEUMCHEON"],
    "SEOUL_SEOCHO":       ["SEOUL_GANGNAM", "SEOUL_DONGJAK", "SEOUL_GWANAK"],
    "SEOUL_GANGNAM":      ["SEOUL_SEOCHO", "SEOUL_SONGPA", "SEOUL_GWANGJIN"],
    "SEOUL_SONGPA":       ["SEOUL_GANGNAM", "SEOUL_GANGDONG", "SEOUL_GWANGJIN"],
    "SEOUL_GANGDONG":     ["SEOUL_SONGPA", "SEOUL_GWANGJIN"],

    # ── 부산 ─────────────────────────────────────────────────────────────
    "BUSAN_JUNGGU":       ["BUSAN_SEOGU", "BUSAN_DONGGU", "BUSAN_YEONGDOGU"],
    "BUSAN_SEOGU":        ["BUSAN_JUNGGU", "BUSAN_DONGGU", "BUSAN_BUSANJINGU", "BUSAN_SAHAGU"],
    "BUSAN_DONGGU":       ["BUSAN_JUNGGU", "BUSAN_SEOGU", "BUSAN_BUSANJINGU"],
    "BUSAN_YEONGDOGU":    ["BUSAN_JUNGGU", "BUSAN_NAMGU"],
    "BUSAN_BUSANJINGU":   ["BUSAN_DONGGU", "BUSAN_YEONJEGU", "BUSAN_SASANGGU", "BUSAN_SAHAGU"],
    "BUSAN_DONGNAEGU":    ["BUSAN_YEONJEGU", "BUSAN_GEUMJEONGGU", "BUSAN_HAEUNDAEGU"],
    "BUSAN_NAMGU":        ["BUSAN_YEONGDOGU", "BUSAN_SUYEONGGU", "BUSAN_BUSANJINGU"],
    "BUSAN_BUKGU":        ["BUSAN_GEUMJEONGGU", "BUSAN_SASANGGU", "BUSAN_GANGSEOGU"],
    "BUSAN_HAEUNDAEGU":   ["BUSAN_SUYEONGGU", "BUSAN_DONGNAEGU", "BUSAN_GIJANG"],
    "BUSAN_SAHAGU":       ["BUSAN_BUSANJINGU", "BUSAN_SEOGU", "BUSAN_GANGSEOGU"],
    "BUSAN_GEUMJEONGGU":  ["BUSAN_DONGNAEGU", "BUSAN_BUKGU", "BUSAN_GIJANG"],
    "BUSAN_GANGSEOGU":    ["BUSAN_SAHAGU", "BUSAN_BUKGU"],
    "BUSAN_YEONJEGU":     ["BUSAN_SUYEONGGU", "BUSAN_DONGNAEGU", "BUSAN_BUSANJINGU"],
    "BUSAN_SUYEONGGU":    ["BUSAN_HAEUNDAEGU", "BUSAN_YEONJEGU", "BUSAN_NAMGU"],
    "BUSAN_SASANGGU":     ["BUSAN_BUSANJINGU", "BUSAN_BUKGU", "BUSAN_GANGSEOGU"],
    "BUSAN_GIJANG":       ["BUSAN_HAEUNDAEGU", "BUSAN_GEUMJEONGGU"],

    # ── 대구 ─────────────────────────────────────────────────────────────
    "DAEGU_JUNGGU":       ["DAEGU_DONGGU", "DAEGU_SEOGU", "DAEGU_NAMGU", "DAEGU_BUKGU"],
    "DAEGU_DONGGU":       ["DAEGU_JUNGGU", "DAEGU_BUKGU", "DAEGU_SUSEONGGU"],
    "DAEGU_SEOGU":        ["DAEGU_JUNGGU", "DAEGU_DALSEOGU"],
    "DAEGU_NAMGU":        ["DAEGU_JUNGGU", "DAEGU_SUSEONGGU", "DAEGU_DALSEOGU"],
    "DAEGU_BUKGU":        ["DAEGU_JUNGGU", "DAEGU_DONGGU"],
    "DAEGU_SUSEONGGU":    ["DAEGU_JUNGGU", "DAEGU_DONGGU", "DAEGU_NAMGU"],
    "DAEGU_DALSEOGU":     ["DAEGU_SEOGU", "DAEGU_NAMGU"],
    "DAEGU_DALSEONG":     ["DAEGU_DALSEOGU", "DAEGU_SEOGU"],

    # ── 인천 ─────────────────────────────────────────────────────────────
    "INCHEON_JUNGGU":     ["INCHEON_DONGGU", "INCHEON_MICHUHOL"],
    "INCHEON_DONGGU":     ["INCHEON_JUNGGU", "INCHEON_BUPYEONGGU"],
    "INCHEON_MICHUHOL":   ["INCHEON_YEONSUGU", "INCHEON_NAMDONGGU", "INCHEON_JUNGGU"],
    "INCHEON_YEONSUGU":   ["INCHEON_MICHUHOL", "INCHEON_NAMDONGGU"],
    "INCHEON_NAMDONGGU":  ["INCHEON_BUPYEONGGU", "INCHEON_YEONSUGU", "INCHEON_MICHUHOL"],
    "INCHEON_BUPYEONGGU": ["INCHEON_NAMDONGGU", "INCHEON_GYEYANGGU", "INCHEON_SEOGU"],
    "INCHEON_GYEYANGGU":  ["INCHEON_BUPYEONGGU", "INCHEON_SEOGU"],
    "INCHEON_SEOGU":      ["INCHEON_GYEYANGGU", "INCHEON_BUPYEONGGU"],

    # ── 광주 ─────────────────────────────────────────────────────────────
    "GWANGJU_DONGGU":     ["GWANGJU_BUKGU", "GWANGJU_NAMGU"],
    "GWANGJU_SEOGU":      ["GWANGJU_NAMGU", "GWANGJU_GWANGSAN", "GWANGJU_BUKGU"],
    "GWANGJU_NAMGU":      ["GWANGJU_SEOGU", "GWANGJU_DONGGU"],
    "GWANGJU_BUKGU":      ["GWANGJU_DONGGU", "GWANGJU_SEOGU", "GWANGJU_GWANGSAN"],
    "GWANGJU_GWANGSAN":   ["GWANGJU_SEOGU", "GWANGJU_BUKGU"],

    # ── 대전 ─────────────────────────────────────────────────────────────
    "DAEJEON_JUNGGU":     ["DAEJEON_DONGGU", "DAEJEON_SEOGU", "DAEJEON_DAEDEOK"],
    "DAEJEON_DONGGU":     ["DAEJEON_JUNGGU", "DAEJEON_DAEDEOK"],
    "DAEJEON_SEOGU":      ["DAEJEON_JUNGGU", "DAEJEON_YUSEONG"],
    "DAEJEON_YUSEONG":    ["DAEJEON_SEOGU", "DAEJEON_JUNGGU"],
    "DAEJEON_DAEDEOK":    ["DAEJEON_JUNGGU", "DAEJEON_DONGGU"],

    # ── 울산 ─────────────────────────────────────────────────────────────
    "ULSAN_JUNGGU":       ["ULSAN_NAMGU", "ULSAN_DONGGU", "ULSAN_BUKGU"],
    "ULSAN_NAMGU":        ["ULSAN_JUNGGU", "ULSAN_DONGGU", "ULSAN_ULJU"],
    "ULSAN_DONGGU":       ["ULSAN_JUNGGU", "ULSAN_NAMGU", "ULSAN_BUKGU"],
    "ULSAN_BUKGU":        ["ULSAN_JUNGGU", "ULSAN_DONGGU", "ULSAN_ULJU"],
    "ULSAN_ULJU":         ["ULSAN_NAMGU", "ULSAN_BUKGU"],
}

# Region 코드 집합 (district/region 판별용)
REGION_CODES = set(REGION_MAP.values())
