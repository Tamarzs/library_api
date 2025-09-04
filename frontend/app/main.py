import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
import plotly.express as px


def get_engine():
    return create_engine("postgresql+psycopg2://tama:12345678@db:5432/library")


def load_data(start, end):
    engine = get_engine()
    query = """
        SELECT borrow_date::date AS borrow_date
        FROM Borrows
        WHERE borrow_date::date BETWEEN %(start)s AND %(end)s
    """
    df = pd.read_sql(query, engine, params={"start": start, "end": end})
    return df


def load_user_data():
    engine = get_engine()
    query = """
        SELECT u.username,
               COUNT(*) AS borrowed_books
        FROM Borrows b
        JOIN Users u ON b.user_id = u.id
        GROUP BY u.username
        ORDER BY borrowed_books DESC;
    """
    df = pd.read_sql(query, engine)
    return df


st.title("Library Dashboard")


tab1, tab2 = st.tabs(["Borrows by Date", "Borrows by User"])


with tab1:
    st.subheader("Borrows by Date")

    start = st.date_input("Start Date")
    end = st.date_input("End Date")

    if start and end:
        df = load_data(start, end)
        if not df.empty:
            df["borrow_date"] = pd.to_datetime(df["borrow_date"])
            emprestimos_por_dia = df.groupby(df["borrow_date"].dt.date).size()


            fig, ax = plt.subplots()
            emprestimos_por_dia.plot(kind="bar", ax=ax)
            ax.set_xlabel("Date")
            ax.set_ylabel("Books Borrowed")
            st.pyplot(fig)

            st.write("Data:", emprestimos_por_dia)
        else:
            st.warning("No borrows in this period.")


with tab2:
    st.subheader("Borrows by User")

    df = load_user_data()
    if df.empty:
        st.warning("No data found in database.")
    else:
        st.dataframe(df)


        fig = px.bar(
            df,
            x="username",
            y="borrowed_books",
            text="borrowed_books",
            title="Borrows by User",
            labels={"username": "Username", "borrowed_books": "Borrowed Books"}
        )
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
