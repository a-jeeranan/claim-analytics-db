import streamlit as st
import pandas as pd
import plotly.express as px
import warnings
import os

warnings.filterwarnings('ignore')


st.set_page_config(
    page_title='7 Dangerous Days Claims Report',
    layout='wide',
    initial_sidebar_state='expanded'
)

df = pd.read_excel('clean_data_all.xlsx')

st.title("7 Dangerous Days Claims Report 🚗")
st.markdown("<style>div.block-container{padding-top:2rem;}</style>", unsafe_allow_html=True)

# sidebar
st.sidebar.header("Filter Data:")

event = st.sidebar.multiselect("Select Event",['All'] + list(df['เทศกาล'].unique()), default=['All'])
if 'All' in event:
    event = df['เทศกาล'].unique().tolist()
    
year = st.sidebar.multiselect("Select Year",['All'] + list(df['ปี'].unique()), default=['All'])
if 'All' in year:
    year = df['ปี'].unique().tolist()

df_selected = df.query("เทศกาล == @event and ปี == @year")


# filter data details
def df_selected_details():
    if not df_selected.empty:
        st.markdown(f"เทศกาล: {', '.join(map(str, event))}")
        if len(year) > 1:
            min_year = df_selected['ปี'].min()
            max_year = df_selected['ปี'].max()
            st.markdown(f"ปี: {min_year} - {max_year}")
        else:
            st.markdown(f"ปี: {', '.join(map(str, year))}")
    else:
        st.warning("Select at least one data")
        st.stop()
        
# upload file
def upload_file():
    with st.expander("Upload Data"):
        fl = st.file_uploader(":file_folder: Upload a file", type=['xlsx'])

        if fl is not None:
            filename = fl.name
            st.write(filename)
            df = pd.read_excel(filename, engine='openpyxl')
        else:
            df = pd.read_excel('clean_data_all.xlsx', engine='openpyxl')
upload_file()

# raw data
with st.expander("Raw Data"):
    df_selected_details()
    st.dataframe(df_selected)
 # export
    csv = df_selected.to_csv(index=False,).encode('utf-8-sig')
    st.download_button("Download", data=csv, file_name="claim_report.csv", mime="text/csv")
   
# main
#Total
with st.container():
    c1,c2,c3,c4 = st.columns(4)
    st.markdown("""
        <style>
        .metric-box {
            padding: 10px;
            border-radius: 10px;
            text-align: center;
            margin-bottom: 10px;
            font-weight: bold;
        }
        .white-box {
            border-left: 12px solid #C9B59C;
            background-color: #F4F4F4;
        }
        .blue-box {
            border-left: 12px solid #8FABD4;
            background-color: #F4F4F4;
        }
        .green-box {
            border-left: 12px solid #A3D78A;
            background-color: #F4F4F4;
        }
        .yellow-box {
            border-left: 12px solid #F5C857;
            background-color: #F4F4F4;
        }
        .metric-title {
            font-size: 16px;
            margin-bottom: 5px;
            font-weight: 600;
        }
        .metric-value {
            font-size: 22px;
        }
        </style>
    """, unsafe_allow_html=True)


    with c1:
        acd_dt = df_selected[['จำนวนผู้เสียชีวิต','จำนวนผู้บาดเจ็บ','จำนวนผู้ทุพพลภาพ']].sum().reset_index()
        acd_dt.columns = ['ประเภท','จำนวน']
        total_pp = acd_dt['จำนวน'].sum()
        st.markdown(f"""
            <div class="metric-box white-box">
                <div class="metric-title">Total Amount</div>
                <div class="metric-value">{total_pp:,} คน</div>
            </div>
        """, unsafe_allow_html=True)

    
    with c2:    
        claim_acd_amt = df_selected[['จำนวนเงินที่เคลม_เสียชีวิต','จำนวนเงินที่เคลม_บาดเจ็บ','จำนวนเงินที่เคลม_ทุพพลภาพ']].sum().reset_index()
        claim_acd_amt.columns = ['ประเภท','จำนวน (ล้านบาท)']
        total_claim = claim_acd_amt['จำนวน (ล้านบาท)'].sum()
        st.markdown(f"""
            <div class="metric-box blue-box">
                <div class="metric-title">Total Claims Amount</div>
                <div class="metric-value">{total_claim:,.2f} MB</div>
            </div>
        """, unsafe_allow_html=True)

    with c3:    
        claim_status_paid = df_selected[['เคลม_ผู้ประสบอุบัติเหตุ_จ่ายแล้ว','เคลม_ทรัพย์สิน_จ่ายแล้ว']].sum().reset_index()
        claim_status_paid.columns = ['สถานะ','จำนวน (ล้านบาท)']
        total_claim_paid = claim_status_paid['จำนวน (ล้านบาท)'].sum()
        st.markdown(f"""
            <div class="metric-box green-box">
                <div class="metric-title">Total Paid Claims Amount</div>
                <div class="metric-value">{total_claim_paid:,.2f} MB</div>
            </div>
        """, unsafe_allow_html=True)
    with c4:
        claim_status_pending = df_selected[['เคลม_ผู้ประสบอุบัติเหตุ_อยู่ระหว่างดำเนินการ','เคลม_ทรัพย์สิน_อยู่ระหว่างดำเนินการ']].sum().reset_index()
        claim_status_pending.columns = ['สถานะ','จำนวน (ล้านบาท)']
        total_claim_pending = claim_status_pending['จำนวน (ล้านบาท)'].sum()
        st.markdown(f"""
            <div class="metric-box yellow-box">
                <div class="metric-title">Total Pending Claims Amount</div>
                <div class="metric-value">{total_claim_pending:,.2f} MB</div>
            </div>
        """, unsafe_allow_html=True)
#Charts   
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("จำนวนผู้ประสบอุบัติเหตุจากรถ")
        fig = px.pie(acd_dt, values="จำนวน", names="ประเภท", title='จำนวนผู้ประสบอุบัติเหตุจากรถ', hole=0.5, color='ประเภท', color_discrete_map={'จำนวนผู้เสียชีวิต':'#D1512D','จำนวนผู้บาดเจ็บ':'#53629E','จำนวนผู้ทุพพลภาพ':'#8AA624'})
        fig.update_layout(annotations=[dict(text=f"Total<br>{total_pp:,} คน<br>", x=0.5, y=0.5, font_size=16, showarrow=False)], paper_bgcolor='#F4F4F4')
        fig.update_traces(textposition='outside', texttemplate='%{percent} (%{value:,} คน)')
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("สถานะการจ่ายค่าสินไหมทดแทน")
        claim_status_life = df_selected[['เคลม_ผู้ประสบอุบัติเหตุ_จ่ายแล้ว','เคลม_ผู้ประสบอุบัติเหตุ_อยู่ระหว่างดำเนินการ']].sum().reset_index()
        claim_status_life.columns = ['สถานะ','จำนวน (ล้านบาท)']
        total_claim_life = claim_status_life['จำนวน (ล้านบาท)'].sum()
        fig3 = px.pie(claim_status_life, values='จำนวน (ล้านบาท)', names='สถานะ', title='ผู้ประสบอุบัติเหตุ', hole=0.5, color='สถานะ', color_discrete_map={'เคลม_ผู้ประสบอุบัติเหตุ_จ่ายแล้ว':'#A3D78A','เคลม_ผู้ประสบอุบัติเหตุ_อยู่ระหว่างดำเนินการ':'#F5C857'})
        fig3.update_traces(textposition='auto', texttemplate='%{percent} (%{value:.2f} MB)')
        fig3.update_layout(annotations=[dict(text=f"Total<br>{total_claim_life:,.2f} MB<br>", x=0.5, y=0.5, font_size=16, showarrow=False)],paper_bgcolor='#F4F4F4')
        st.plotly_chart(fig3, use_container_width=True)


    with col2:
        
        st.subheader("จำนวนเงินการเรียกร้องค่าสินไหมทดแทน")
        fig2 = px.bar(claim_acd_amt, x='ประเภท', y='จำนวน (ล้านบาท)', title='จำนวนเงินการเรียกร้องค่าสินไหมทดแทน', color='ประเภท', color_discrete_map={'จำนวนเงินที่เคลม_เสียชีวิต':'#D1512D','จำนวนเงินที่เคลม_บาดเจ็บ':'#53629E','จำนวนเงินที่เคลม_ทุพพลภาพ':'#8AA624'})
        fig2.update_traces(textposition='auto', texttemplate='%{y:,.2f} MB')
        fig2.update_layout(margin=dict(t=80), yaxis=dict(automargin=True), uniformtext_mode='hide',paper_bgcolor='#F4F4F4')
        st.plotly_chart(fig2, use_container_width=True)
        
        
        st.subheader("   ")
        claim_status_nl = df_selected[['เคลม_ทรัพย์สิน_จ่ายแล้ว','เคลม_ทรัพย์สิน_อยู่ระหว่างดำเนินการ']].sum().reset_index()
        claim_status_nl.columns = ['สถานะ','จำนวน (ล้านบาท)']
        total_claim_nl = claim_status_nl['จำนวน (ล้านบาท)'].sum()
        fig4 = px.pie(claim_status_nl, values='จำนวน (ล้านบาท)', names='สถานะ', title='ทรัพย์สิน', hole=0.5, color='สถานะ', color_discrete_map={'เคลม_ทรัพย์สิน_จ่ายแล้ว':'#A3D78A','เคลม_ทรัพย์สิน_อยู่ระหว่างดำเนินการ':'#F5C857'},)
        fig4.update_traces(textposition='auto', texttemplate='%{percent} (%{value:.2f} MB)')
        fig4.update_layout(annotations=[dict(text=f"Total<br>{total_claim_nl:,.2f} MB<br>", x=0.5, y=0.5, font_size=16, showarrow=False)],paper_bgcolor='#F4F4F4')
        st.plotly_chart(fig4, use_container_width=True)
        





