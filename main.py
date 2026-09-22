import FinanceDataReader as fdr
import pandas_ta as ta
import pandas as pd
from jinja2 import Template

print("데이터를 불러오고 있습니다...")
# 1. 주가 데이터 불러오기 (ACE 미국배당다우존스)
df = fdr.DataReader('460870', '2026-01-01')

# 2. 보조지표 계산 (RSI, MACD)
df.ta.rsi(length=14, append=True)
df.ta.macd(fast=12, slow=26, signal=9, append=True)
df.dropna(inplace=True)

# 3. 매수 시그널 점수 계산
df['Buy_Score'] = 0.0
df['Signal_Log'] = ''

# 조건 A: RSI 과매도
cond_rsi = df['RSI_14'] <= 30
df.loc[cond_rsi, 'Buy_Score'] += 1.2
df.loc[cond_rsi, 'Signal_Log'] += 'RSI과매도(+1.2) '

# 조건 B: MACD 골든크로스
macd = df['MACD_12_26_9']
macds = df['MACDs_12_26_9']
cond_macd_cross = (macd > macds) & (macd.shift(1) <= macds.shift(1))
df.loc[cond_macd_cross, 'Buy_Score'] += 1.2
df.loc[cond_macd_cross, 'Signal_Log'] += 'MACD골든크로스(+1.2)'

# 신호가 발생한 날만 추리기 (최근 5건)
signal_df = df[df['Buy_Score'] > 0].copy().tail(5)

# 4. HTML 웹 문서 파일 만들기
html_template = """
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>나만의 주식 시그널 리포트</title>
    <style>
        table { border-collapse: collapse; width: 100%; max-width: 600px; margin-top: 20px; }
        th, td { border: 1px solid #ddd; padding: 10px; text-align: center; font-family: sans-serif; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h2>ACE 미국배당다우존스 - 최근 매수 시그널</h2>
    {{ table_html }}
</body>
</html>
"""

# 데이터를 표 형식으로 변환
table_html = signal_df[['Close', 'RSI_14', 'Buy_Score', 'Signal_Log']].to_html(index=True)

# index.html 파일 저장
template = Template(html_template)
with open("index.html", "w", encoding="utf-8-sig") as f:
    f.write(template.render(table_html=table_html))

print("성공! 폴더에 index.html 파일이 생성되었습니다.")