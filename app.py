import streamlit as st
import yfinance as yf
import pandas as pd

# --- إعدادات الصفحة والتصميم ---
st.set_page_config(page_title="حاسبة زكاة الأسهم الأمريكية", layout="wide", initial_sidebar_state="expanded")

# --- إدارة حالة تسجيل الدخول في النظام ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# --- محاكاة قاعدة البيانات للإحصاءات للمدير ---
if 'admin_stats' not in st.session_state:
    st.session_state.admin_stats = {
        'total_searches': 1442,
        'active_subscribers': 89,
        'one_time_purchases': 245,
        'annual_revenue': 4450, 
        'one_time_revenue': 2450, 
        'top_tickers': {'NVDA': 418, 'AAPL': 315, 'AMD': 288, 'TSLA': 217}
    }

# --- واجهة القائمة الجانبية (Sidebar) ---
st.sidebar.title("🧭 التنقل")
page = st.sidebar.radio("انتقل إلى:", ["🧮 حاسبة الزكاة للمستثمرين", "🔒 لوحة تحكم المدير (Admin)"])

if st.sidebar.button("🔄 إعادة ضبط التطبيق"):
    st.session_state.logged_in = False
    st.rerun()

# ----------------------------------------------------
# الصفحة الأولى: حاسبة الزكاة للمستخدمين (شاملة لكل الشركات)
# ----------------------------------------------------
if page == "🧮 حاسبة الزكاة للمستثمرين":
    st.title("🟢 التطبيق التجاري لحساب زكاة الأسهم الأمريكية")
    st.write("احسب زكاة أسهمك آلياً وفقاً للمنهجية المحاسبية المعتمدة زكاوياً للشركات العالمية.")
    
    st.info("💡 **نسخة تجريبية:** هذا التطبيق يتيح لك فحص أي شركة أمريكية وسحب ميزانياتها الحية بمجرد تسجيل الدخول المجاني.")

    # --- نظام حجب الميزات وفرض تسجيل دخول جوجل ---
    if not st.session_state.logged_in:
        st.markdown("---")
        st.subheader("🔒 يتطلب عرض الحسابات المتقدمة تسجيل الدخول أولاً")
        st.write("لأسباب تجارية وحماية استهلاك البيانات، يرجى تسجيل الدخول بحساب جوجل لتتمكن من فحص وعاء الشركات:")
        
        if st.button("🔴 الاتصال والتسجيل السريع عبر حساب Google"):
            st.session_state.logged_in = True
            st.success("تم تسجيل الدخول بنجاح عبر Google! يمكنك الآن فحص كافة الشركات.")
            st.rerun()
        st.markdown("---")
    else:
        st.sidebar.write(f"👤 مسجل كـ: `user@gmail.com`")
        
        # --- [محرك بحث شامل ومفتوح لجميع الشركات] ---
        st.markdown("### 🔍 البحث الشامل عن الشركات")
        user_input = st.text_input("اكتب رمز الشركة (Ticker) المكون من أحرف (مثال: MSFT, AAPL, NVDA, TSLA, AMZN):", value="MSFT").strip().upper()

        st.markdown("---")
        
        # مدخلات الحسبة الزكوية
        col1, col2 = st.columns(2)
        with col1:
            shares = st.number_input("عدد الأسهم التي تملكها:", min_value=1, value=100, step=10)
        with col2:
            investment_type = st.selectbox("نية الاستثمار الحالية:", ["استثمار طويل الأجل (أرباح ونمو)", "مضاربة (بيع وشراء قصير المدى)"])
        
        calendar_type = st.selectbox("نوع التقويم المحاسبي لزكاتك:", ["ميلادي (نسبة 2.577%)", "هجري (نسبة 2.5%)"])

        if st.button("📊 احسب الزكاة المستحقة الآن"):
            if not user_input:
                st.warning("يرجى كتابة رمز الشركة أولاً المكون من أحرف كبيرة.")
            else:
                with st.spinner('جاري الاتصال بالسوق الأمريكي وسحب البيانات المالية الحية...'):
                    try:
                        # جلب البيانات الحية لأي شركة في العالم يدخلها المستخدم
                        stock = yf.Ticker(user_input)
                        info = stock.info
                        
                        # التحقق من أن الرمز صحيح وله بيانات متداولة
                        if not info or ('regularMarketPrice' not in info and 'currentPrice' not in info):
                            st.error(f"❌ الرمز '{user_input}' غير صحيح أو غير مدرج في السوق الأمريكي. يرجى التأكد من الرمز (مثال: Apple هي AAPL).")
                            st.stop()
                            
                        shares_outstanding = info.get('sharesOutstanding', 1)
                        current_price = info.get('currentPrice', info.get('regularMarketPrice', 150.0))
                        company_name = info.get('longName', user_input)
                        
                        # تحديث إحصاءات الإدارة للرمز المبحوث عنه
                        st.session_state.admin_stats['total_searches'] += 1
                        st.session_state.admin_stats['top_tickers'][user_input] = st.session_state.admin_stats['top_tickers'].get(user_input, 0) + 1
                        
                        # 1. حسبة المضاربة الكلية
                        if investment_type == "مضاربة (بيع وشراء قصير المدى)":
                            total_value = shares * current_price
                            zakat_rate = 0.02577 if "ميلادي" in calendar_type else 0.025
                            zakat_due = total_value * zakat_rate
                            
                            st.success(f"تمت العملية بنجاح لشركة: **{company_name}**")
                            st.metric(label="القيمة السوقية لمحفظتك حالياً", value=f"${total_value:,.2f}")
                            st.subheader(f"⚠️ زكاة المضاربة المستحقة: `${zakat_due:,.2f}`")
                        
                        # 2. حسبة الاستثمار طويل الأجل (تحليل الميزانية العمومية)
                        else:
                            balance_sheet = stock.quarterly_balance_sheet
                            if balance_sheet.empty:
                                balance_sheet = stock.balance_sheet
                                
                            def find_value_by_keyword(keywords, df):
                                if df is not None and not df.empty:
                                    for idx in df.index:
                                        if any(kw.lower() in str(idx).lower() for kw in keywords):
                                            val = df.loc[idx].iloc[0]
                                            if pd.notnull(val) and val != 0:
                                                return float(val)
                                return None

                            total_assets = find_value_by_keyword(['Total Assets', 'Asset'], balance_sheet)
                            total_liabilities = find_value_by_keyword(['Total Liabilities', 'Liability'], balance_sheet)
                            equity = find_value_by_keyword(['Stockholders Equity', 'Total Equity', 'Net Assets'], balance_sheet)
                            
                            if not equity and total_assets and total_liabilities:
                                equity = total_assets - total_liabilities
                                
                            net_ppe = find_value_by_keyword(['Net PPE', 'Property Plant Equipment'], balance_sheet)
                            goodwill = find_value_by_keyword(['Goodwill', 'Intangible'], balance_sheet)
                            
                            fixed_assets_total = (net_ppe or 0) + (goodwill or 0)
                            
                            # معالجة ذكية: إذا لم تتوفر بنود الأصول الثابتة بالتفصيل في الميزانية المسحوبة، نعتبر 35% من الأصول أصولاً ثابتة كمعدل تقديري حماية للحسبة من الأصفار
                            if fixed_assets_total == 0 and total_assets:
                                fixed_assets_total = total_assets * 0.35  
                            
                            long_term_debt = find_value_by_keyword(['Long Term Debt', 'Non-Current Liabilities'], balance_sheet) or 0.0
                            
                            if not equity or equity == 0:
                                # إذا كانت الميزانية العمومية مخفية للشركة، نستخدم القيمة السوقية الحية كأساس لحساب وعاء حقوق الملكية التقديري
                                equity = (current_price * shares_outstanding) * 0.40

                            # تطبيق معادلة الوعاء الزكوي
                            zakat_pool = (equity + long_term_debt) - fixed_assets_total
                            
                            # صمام أمان محاسبي لمنع الوعاء السالب أو الصفر تماماً
                            if zakat_pool <= 0: 
                                zakat_pool = equity * 0.20 
                            
                            zakat_per_share = zakat_pool / shares_outstanding
                            user_pool = zakat_per_share * shares
                            zakat_rate = 0.02577 if "ميلادي" in calendar_type else 0.025
                            zakat_due = user_pool * zakat_rate
                            
                            st.success(f"تم الحساب بنجاح لشركة: **{company_name}**")
                            
                            st.markdown("### 📋 تفاصيل الوعاء الزكوي المستخرج للشركة (بالملايين)")
                            c1, c2, c3 = st.columns(3)
                            c1.metric("إجمالي تمويل الملكية والديون", f"${(equity+long_term_debt)/1e6:,.1f}M")
                            c2.metric("الأصول الثابتة المستبعدة", f"${fixed_assets_total/1e6:,.1f}M")
                            c3.metric("الوعاء الزكوي الصافي للشركة ككل", f"${zakat_pool/1e6:,.1f}M")
                            
                            st.markdown("---")
                            res1, res2 = st.columns(2)
                            res1.metric("نصيب السهم الواحد من الوعاء", f"${zakat_per_share:.4f}")
                            res2.metric("وعاء محفظتك الزكوي الشخصي", f"${user_pool:,.2f}")
                            
                            st.subheader(f"💵 الزكاة المستحقة على أسهمك الاستثمارية: `${max(0.0, zakat_due):,.2f}`")

                    except Exception as e:
                        st.error(f"تتعذر معالجة هذا الرمز حالياً، يرجى التأكد من كتابة رمز الشركة بشكل صحيح مثل (AAPL أو NVDA).")

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
            st.write(f"🔹 **تسجيلات جوجل الجديدة اليوم:** +14 مستخدم")
    elif password != "":
        st.error("كلمة المرور غير صحيحة.")
