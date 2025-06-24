from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


from src.db import get_all_users, get_sessions_results_by_user

users = get_all_users()
username = st.session_state.get('username')
user_logged_in = users[users['first_name'].str.lower()+users['last_name'].str.lower() == username]

st.title(f"Aqui estão detalhes sobre os seus resultados, {user_logged_in['first_name'][0]}.")

sessions_results = get_sessions_results_by_user(user_logged_in['id'][0])

col1, col2, col3, col4 = st.columns(4)
card1 = go.Figure()
card1.add_trace(go.Indicator(
    mode = 'number',
    value = sessions_results['id'].nunique(),
    title = {'text': 'Total de provas feitas'}))
card1.update_layout(height=250)
card2 = go.Figure()
card2.add_trace(go.Indicator(
    mode = 'number',
    value = sessions_results.shape[0],
    title = {'text': 'Total de questões feitas'}))
card2.update_layout(height=250)
card3 = go.Figure()
card3.add_trace(go.Indicator(
    mode = 'number',
    value = sessions_results.user_answers.sum(),
    title = {'text': 'Total de acertos'}))
card3.update_layout(height=250)
value_card4 = datetime.today() - datetime.strptime(sessions_results.sort_values(by='created_at', ascending=False).iloc[0, 3], '%d/%m/%Y')
card4 = go.Figure()
card4.add_trace(go.Indicator(
    mode = 'number',
    value = value_card4.days,
    title = {'text': 'Dias desde a última prova'}))
card4.update_layout(height=250)

with col1:
    st.plotly_chart(card1)
with col2:
    st.plotly_chart(card2)
with col3:
    st.plotly_chart(card3)
with col4:
    st.plotly_chart(card4)

sessions_results['month_year'] = sessions_results['created_at'].apply(lambda x: f"{x.split('/')[1]}-{x.split('/')[2]}")
exams_unique = sessions_results.drop_duplicates(subset=['id'])

count_exams_unique_by_month_year = exams_unique.groupby('month_year')['id'].count().reset_index()
chart1 = px.line(count_exams_unique_by_month_year, x='month_year', y='id',
                 title='Quantidade de provas feitas por mês e ano', color_discrete_sequence=["#FF4B4B"], text='id')
chart1.update_traces(
    hovertemplate = 
        "<b>%{x}</b><br>" +
        "Quantidade de provas: %{y}<br>" +
        "<extra></extra>",
    textfont_color = '#d6d7dd',
    textposition = 'top center'
)
chart1.update_layout(
    xaxis = dict(
        type='category',
        categoryorder='array',
        categoryarray=sorted(count_exams_unique_by_month_year['month_year'].unique())
    )
)
chart1.update_yaxes(title_text='')
chart1.update_xaxes(title_text='')
st.plotly_chart(chart1)


count_utilization_by_month_year = sessions_results.groupby('month_year').agg({'user_answers': 'sum',
                                                                              'total_questions': 'count'}).reset_index()
count_utilization_by_month_year['utilization'] = count_utilization_by_month_year.apply(lambda x: f"{int(round(x['user_answers']/x['total_questions'], 2)*100)}%", axis=1)
chart3 = px.line(count_utilization_by_month_year, x='month_year', y='utilization',
                 title='Aproveitamento por mês e ano', color_discrete_sequence=["#FF4B4B"], text='utilization',
                 custom_data=['user_answers', 'total_questions'])
chart3.update_traces(
    hovertemplate = 
        "<b>%{x}</b><br>" +
        "Aproveitamento: %{y}%<br>" +
        "<br>" +
        "Total de acertos: %{customdata[0]}<br>" +
        "Total de questões: %{customdata[1]}" +
        "<extra></extra>",
    textfont_color = '#d6d7dd',
    textposition = 'top center'
)
chart3.update_layout(
    xaxis = dict(
        type='category',
        categoryorder='array',
        categoryarray=sorted(count_utilization_by_month_year['month_year'].unique())
    )
)
chart3.update_yaxes(title_text='')
chart3.update_xaxes(title_text='')
st.plotly_chart(chart3)

col1, col2 = st.columns(2)

with col1:
    count_best_subjects = sessions_results.groupby('subject')['user_answers'].sum().reset_index()
    count_best_subjects = count_best_subjects.sort_values(by='user_answers', ascending=False).head()
    count_best_subjects = count_best_subjects.query("user_answers > 0")
    chart2 = px.bar(count_best_subjects, x='user_answers', y='subject', orientation='h',
                    height=400, title='As 5 disciplinas com mais acertos',
                    color_discrete_sequence=['#FF4B4B'], text='user_answers')
    chart2.update_traces(
        hovertemplate = 
            "<b>%{y}</b><br>" + 
            "Quantidade de questões acertadas: %{x}<br>" +
            "<extra></extra>",
        textfont_color='#d6d7dd'
    )
    chart2.update_layout(
        yaxis=dict(autorange='reversed')
    )
    chart2.update_yaxes(title_text='')
    chart2.update_xaxes(title_text='')
    st.plotly_chart(chart2)

