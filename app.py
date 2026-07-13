import streamlit as st
import yfinance as yf
import pandas as pd

# --- إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="حاسبة زكاة الأسهم الأمريكية", layout="wide", initial_sidebar_state="expanded")

# --- محاكاة قاعدة البيانات للإحصاءات ---
if 'admin_stats' not in st.session_state:
    st.session_state.admin_stats = {
        'total_searches': 1420,
        'active_subscribers': 89,
        'one_time_purchases': 245,
        'annual_revenue': 4450, 
        'one_time_revenue': 2450, 
        'top_tickers': {'NVDA': 412, 'AAPL': 310, 'AMD': 285, 'TSLA': 213}
    }

# --- واجهة القائمة الجانبية (Sidebar) ---
st.sidebar.title("🧭 التنقل")
page = st.sidebar.radio("انتقل إلى:", ["🧮 حاسبة الزكاة للمستثمرين", "🔒 لوحة تحكم المدير (Admin)"])

# ----------------------------------------------------
# الصفحة الأولى: حاسبة الزكاة للمستخدمين
# ----------------------------------------------------
if page == "🧮 حاسبة الزكاة للمستثمرين":
    st.title("🟢 التطبيق التجاري لحساب زكاة الأسهم الأمريكية")
    st.write("احسب زكاة أسهمك آلياً وفقاً لطريقة مصادر التمويل المعتمدة زكاوياً ومحاسبياً.")
    
    st.info("💡 **نسخة تجريبية:** هذا التطبيق يتيح لك فحص الشركات. يمكنك الترقية إلى **الاشتراك السنوي ($49/سنة)** للحصول على تقارير PDF حية وتنبيهات دورية لمحفظتك.")

    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("أدخل رمز الشركة الأمريكية (Ticker):", value="AAPL").upper().strip()
        shares = st.number_input("عدد الأسهم التي تملكها:", min_value=1, value=1000, step=10)
        
    with col2:
        investment_type = st.selectbox(
            "نية الاستثمار الحالية:",
            ["استثمار طويل الأجل (أرباح ونمو)", "مضاربة (بيع وشراء قصير المدى)"]
        )
        calendar_type = st.selectbox("نوع التقويم المحاسبي لزكاتك:", ["ميلادي (نسبة 2.577%)", "هجري (نسبة 2.5%)"])

    if st.button("📊 احسب الزكاة المستحقة الآن"):
        if ticker:
            with st.spinner('جاري سحب الميزانية العمومية الحية...'):
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    company_name = info.get('longName', ticker)
                    current_price = info.get('currentPrice', info.get('regularMarketPrice', 0.0))
                    shares_outstanding = info.get('sharesOutstanding', 1)
                    
                    # جلب الميزانية العمومية
                    balance_sheet = stock.balance_sheet
                    
                    # تسجيل الإحصاءات
                    st.session_state.admin_stats['total_searches'] += 1
                    st.session_state.admin_stats['top_tickers'][ticker] = st.session_state.admin_stats['top_tickers'].get(ticker, 0) + 1
                    
                    st.success(f"تم جلب بيانات شركة: **{company_name}** بنجاح.")
                    
                    if investment_type == "مضاربة (بيع وشراء قصير المدى)":
                        total_value = shares * current_price
                        zakat_rate = 0.02577 if "ميلادي" in calendar_type else 0.025
                        zakat_due = total_value * zakat_rate
                        
                        st.metric(label="القيمة السوقية لمحفظتك", value=f"${total_value:,.2f}")
                        st.subheader(f"⚠️ زكاة المضاربة المستحقة: `${zakat_due:,.2f}`")
                        st.caption("ملاحظة: المضارب يزكي كامل القيمة السوقية للأسهم يوم وجوب الزكاة لأنها تعامل كعروض تجارة.")
                        
                    else:
                        # دالة للبحث المرن عن البنود بمسمياتها القديمة والجديدة في ياهو فاينانشال
                        def get_financial_item(keys_list, df):
                            for key in keys_list:
                                if key in df.index:
                                    return df.loc[key].iloc[0]
                            return 0.0

                        # استخراج البنود بالأسماء المحتملة في التحديث الجديد
                        equity = get_financial_item(['Stockholders Equity', 'Total Stockholders Equity'], balance_sheet)
                        long_term_debt = get_financial_item(['Long Term Debt', 'Total Long Term Debt', 'Long Term Debt And Capital Lease Obligation'], balance_sheet)
                        net_ppe = get_financial_item(['Net PPE', 'Properties', 'Property Plant Equipment'], balance_sheet)
                        goodwill_intangibles = get_financial_item(['Goodwill And Other Intangible Assets', 'Goodwill', 'Intangible Assets'], balance_sheet)
                        
                        # حساب الوعاء الزكوي للشركة ككل
                        zakat_pool = (equity + long_term_debt) - (net_ppe + goodwill_intangibles)
                        
                        # نصيب السهم الواحد من الوعاء
                        zakat_per_share = zakat_pool / shares_outstanding if shares_outstanding else 0
                        
                        # نصيب محفظة المستخدم
                        user_pool = zakat_per_share * shares
                        
                        # حساب قيمة الزكاة
                        zakat_rate = 0.02577 if "ميلادي" in calendar_type else 0.025
                        zakat_due = user_pool * zakat_rate
                        
                        # عرض النتائج
                        st.markdown("### 📋 تفاصيل الوعاء الزكوي للشركة (بالملايين)")
                        c1, c2, c3 = st.columns(3)
                        c1.metric("حقوق الملكية + الديون", f"${(equity+long_term_debt)/1e6:,.1f}M")
                        c2.metric("الأصول الثابتة المخصومة", f"${(net_ppe+goodwill_intangibles)/1e6:,.1f}M")
                        c3.metric("الوعاء الزكوي الإجمالي للشركة", f"${zakat_pool/1e6:,.1f}M")
                        
                        st.markdown("---")
                        res1, res2 = st.columns(2)
                        res1.metric("نصيب السهم الواحد من الوعاء", f"${zakat_per_share:.4f}")
                        res2.metric("وعاء محفظتك الزكوي الشخصي", f"${user_pool:,.2f}")
                        
                        st.subheader(f"💵 الزكاة المستحقة على أسهمك الاستثمارية: `${max(0.0, zakat_due):,.2f}`")
                        st.caption("تم حساب هذه الزكاة بناءً على الجزء الزكوي النامي داخل ميزانية الشركة (الأصول المتداولة الزكوية) وليس السعر السوقي.")

                except Exception as e:
                    st.error(f"عذراً، تعذر حساب البيانات لهذا الرمز. تأكد من إدخال الرمز بشكل صحيح (مثل AAPL أو AMD). نوع الخطأ: {e}")

# ----------------------------------------------------
# الصفحة الثانية: لوحة تحكم المدير
# ----------------------------------------------------
elif page == "🔒 لوحة تحكم المدير (Admin)":
    st.title("⚙️ لوحة تحكم مدير المنصة (Admin Dashboard)")
    password = st.text_input("أدخل كلمة مرور المدير للوصول للإحصاءات والأرباح:", type="password")
    
    if password == "AdminZakat2026":
        st.success("تم تسجيل الدخول بصلاحيات المدير.")
        st.markdown("### 💰 الأداء المالي والتجاري للمنصة")
        m1, m2, m3, m4 = st.columns(4)
        
        stats = st.session_state.admin_stats
        total_rev = stats['annual_revenue'] + stats['one_time_revenue']
        
        m1.metric("إجمالي الإيرادات الكلية", f"${total_rev:,.2f}")
        m2.metric("إيرادات الاشتراكات السنوية", f"${stats['annual_revenue']:,.2f}", "باقة $49/سنة")
        m3.metric("إيرادات الدفع لمرة واحدة", f"${stats['one_time_revenue']:,.2f}", "باقة $10/تقرير")
        m4.metric("المشتركون النشطون حالياً", f"{stats['active_subscribers']} مستخدم")
        
        st.markdown("---")
        st.markdown("### 📊 إحصاءات المنصة والاستخدام")
        col_graph, col_table = st.columns([2, 1])
        
        with col_graph:
            st.write("**أكثر الشركات بحثاً من قبل المستثمرين:**")
            chart_data = pd.DataFrame(list(stats['top_tickers'].items()), columns=['Ticker', 'Searches'])
            st.bar_chart(chart_data.set_index('Ticker'))
            
        with col_table:
            st.write("**مؤشرات التشغيل الكلية:**")
            st.write(f"🔹 **إجمالي عمليات فحص الزكاة:** {stats['total_searches']} عملية")
            st.write(f"🔹 **معدل تحويل المستخدمين:** 23.5%")
            st.write(f"🔹 **استهلاك الـ API المالي المتبقي:** 84.2%")
    elif password != "":
        st.error("كلمة المرور غير صحيحة.")
