
from sys import argv
from requests import get
import pandas as pd
from bs4 import BeautifulSoup

"""
Create virtual environment
>python -m venv venv
>source venv/bin/activate (linux/mac)
>venv\Scripts\activate

pip install requests
pip install beautifulsoup4
pip install html5lib
pip install pandas

"""

year = input('What season? Note: Input a season between 1999 and 2019. If not I cannot help you :) ')
week = input('What week of the {0} season? '.format(year))

year, week = int(year), int(week)

passingURL = """ 
https://www.pro-football-reference.com/play-index/pgl_finder.cgi?request=1&match=game&year_min={year}&year_max={year}&season_start=1&season_end=-1&age_min=0&age_max=99&game_type=A&league_id=&team_id=&opp_id=&game_num_min=0&game_num_max=99&week_num_min={week}&week_num_max={week}&game_day_of_week=&game_location=&game_result=&handedness=&is_active=&is_hof=&c1stat=pass_att&c1comp=gt&c1val=1&c2stat=&c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&order_by=pass_rating&from_link=1
""".format(year=year, week=week)

receivingURL = """
https://www.pro-football-reference.com/play-index/pgl_finder.cgi?request=1&match=game&year_min={year}&year_max={year}&season_start=1&season_end=-1&age_min=0&age_max=99&game_type=A&league_id=&team_id=&opp_id=&game_num_min=0&game_num_max=99&week_num_min={week}&week_num_max={week}&game_day_of_week=&game_location=&game_result=&handedness=&is_active=&is_hof=&c1stat=rec&c1comp=gt&c1val=1&c2stat=&c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&order_by=rec_yds&from_link=1
""".format(year=year, week=week)

rushingURL = """
https://www.pro-football-reference.com/play-index/pgl_finder.cgi?request=1&match=game&year_min={year}&year_max={year}&season_start=1&season_end=-1&age_min=0&age_max=99&game_type=A&league_id=&team_id=&opp_id=&game_num_min=0&game_num_max=99&week_num_min={week}&week_num_max={week}&game_day_of_week=&game_location=&game_result=&handedness=&is_active=&is_hof=&c1stat=rush_att&c1comp=gt&c1val=1&c2stat=&c2comp=gt&c2val=&c3stat=&c3comp=gt&c3val=&c4stat=&c4comp=gt&c4val=&order_by=rush_yds&from_link=1
""".format(year=year, week=week)

urls = {
    'Passing': passingURL,
    'Receiving': receivingURL,
    'Rushing': rushingURL
}

dfs = []

defColumnSettings = {
    'axis': 1,
    'inplace': True
}

for key, url in urls.items():

    response = get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    table = soup.find('table', {'id': 'results'})

    df = pd.read_html(str(table))[0]

    df.columns = df.columns.droplevel(level = 0)

    df.drop(['Result', 'Week', 'G#', 'Opp', 'Unnamed: 7_level_1', 'Age', 'Rk', 'Lg', 'Date', 'Day'], **defColumnSettings)

    df = df[df['Pos'] != 'Pos']

    df.set_index(['Player', 'Pos', 'Tm'], inplace=True)

    if key == 'Passing':
        df = df[['Yds', 'TD', 'Int', 'Att', 'Cmp']]
        df.rename({'Yds': 'PassingYds', 'Att': 'PassingAtt', 'Y/A': 'Y/PassingAtt', 'TD': 'PassingTD'}, **defColumnSettings)
    elif key =='Receiving':
        df = df[['Rec', 'Tgt', 'Yds', 'TD']]
        df.rename({'Yds': 'ReceivingYds', 'TD': 'ReceivingTD'}, **defColumnSettings)
    elif key == 'Rushing':
        df.drop('Y/A', **defColumnSettings)
        df.rename({'Att': 'RushingAtt', 'Yds': 'RushingYds', 'TD': 'RushingTD'}, **defColumnSettings)
    dfs.append(df)


df = dfs[0].join(dfs[1:], how='outer')
df.fillna(0, inplace=True)
df = df.astype('int64')

df['FantasyPoints'] = df['PassingYds']/25 + df['PassingTD']*4 - df['Int']*2 + df['Rec'] + df['ReceivingYds']/10 + df['ReceivingTD']*6 + df['RushingYds']/10 + df['RushingTD']*6

df.reset_index(inplace=True)

try:
    if argv[1] == '--save':
        df.to_csv('datasets/season{}week{}.csv'.format(year, week))
except IndexError:
    pass




