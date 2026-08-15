import streamlit as st
import numpy as np
from PIL import Image
from ultralytics import YOLO
import easyocr
from rapidfuzz import fuzz

from database import (
    create_tables,
    register_user,
    login_user,
    save_user_allergies,
    get_user_allergies,
    add_family_member,
    get_family_members,
    delete_family_member
)


# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title='mosabb | مسبب',
    page_icon='🛡️',
    layout='wide',
    initial_sidebar_state='collapsed'
)

create_tables()


# =========================================================
# SESSION
# =========================================================

if 'user' not in st.session_state:
    st.session_state.user = None

if 'language' not in st.session_state:
    st.session_state.language = 'AR'


# =========================================================
# TRANSLATIONS
# =========================================================

translations = {

    'AR': {
        'direction': 'rtl',

        'hero_badge': 'سلامتك تبدأ قبل أول لقمة',
        'hero_title_1': 'اعرف',
        'hero_title_2': 'مسبب',
        'hero_title_3': 'الحساسية قبل ما يوصلك.',
        'hero_desc': 'صوّر مكونات المنتج، وmosabb يحللها بالذكاء الاصطناعي ويقارنها بحساسيتك وحساسيات عائلتك.',

        'login': 'تسجيل الدخول',
        'register': 'إنشاء حساب',
        'email': 'البريد الإلكتروني',
        'password': 'كلمة المرور',
        'name': 'الاسم',
        'enter': 'دخول',
        'create_account': 'إنشاء الحساب',
        'logout': 'تسجيل الخروج',

        'welcome': 'أهلاً',
        'scan_tab': 'فحص منتج',
        'profile_tab': 'ملفي وعائلتي',

        'scan_title': 'افحص منتجك',
        'scan_desc': 'صوّر قائمة المكونات أو ارفع صورة واضحة لها.',
        'checking_for': 'سيتم فحص المنتج لـ',
        'camera': 'التقط صورة للمكونات',
        'upload': 'أو ارفع صورة',
        'analyze': 'تحليل المنتج',
        'original_image': 'الصورة الأصلية',
        'detected_area': 'منطقة المكونات المكتشفة',
        'ocr_text': 'النص المقروء',
        'result': 'نتيجة الفحص',

        'processing': 'mosabb يحلل المكونات...',
        'no_label': 'ما قدرنا نحدد قائمة المكونات. جرّب صورة أوضح وأقرب.',
        'no_text': 'حددنا مكان المكونات لكن ما قدرنا نقرأ النص.',

        'danger': 'قد يكون هذا المنتج غير مناسب لـ',
        'safe': 'لم نجد مسبب الحساسية المسجل لـ',
        'all_safe': 'لم نجد أي مسبب حساسية مسجل في المنتج.',
        'allergy_type': 'نوع الحساسية',
        'found': 'تم اكتشاف',

        'profile_title': 'ملفي الصحي',
        'profile_desc': 'حدد مسببات الحساسية الخاصة بك مرة واحدة، وmosabb يتذكرها في كل فحص.',
        'my_allergies': 'حساسيتي',
        'save_allergies': 'حفظ حساسيتي',
        'saved': 'تم حفظ حساسيتك',

        'family_title': 'عائلتي',
        'family_desc': 'أضف أطفالك أو أفراد العائلة ليتم فحص المنتج للجميع في نفس الوقت.',
        'no_family': 'ما أضفت أحد للعائلة للحين — عادي، تقدر تستخدم mosabb لنفسك.',
        'relation': 'صلة القرابة',
        'allergies': 'الحساسيات',
        'delete': 'حذف',

        'add_member': 'إضافة فرد للعائلة',
        'member_name': 'اسم الشخص',
        'member_allergies': 'حساسياته',
        'add': 'إضافة فرد',

        'son': 'ابن',
        'daughter': 'ابنة',
        'mother': 'أم',
        'father': 'أب',
        'brother': 'أخ',
        'sister': 'أخت',
        'other': 'أخرى',

        'need_allergy': 'سجل حساسيتك أول من ملفي وعائلتي.',
        'fill_data': 'عب البيانات كلها.',
        'wrong_login': 'البريد الإلكتروني أو كلمة المرور غير صحيحة.',
        'email_used': 'البريد الإلكتروني مستخدم من قبل.',
        'account_created': 'تم إنشاء الحساب. سجل دخولك الآن.',
        'enter_member_name': 'اكتب اسم الشخص.',
        'choose_allergy': 'اختر حساسية واحدة على الأقل.',
        'member_added': 'تمت إضافة',

        'disclaimer': 'mosabb أداة مساعدة وليست بديلاً عن قراءة تحذيرات العبوة أو التوجيه الطبي.'
    },


    'EN': {
        'direction': 'ltr',

        'hero_badge': 'Safety starts before the first bite',
        'hero_title_1': 'Know the',
        'hero_title_2': 'cause',
        'hero_title_3': 'before it reaches you.',
        'hero_desc': 'Scan product ingredients and let mosabb analyze them with AI against your allergies and your family profiles.',

        'login': 'Log in',
        'register': 'Create account',
        'email': 'Email',
        'password': 'Password',
        'name': 'Name',
        'enter': 'Log in',
        'create_account': 'Create account',
        'logout': 'Log out',

        'welcome': 'Welcome',
        'scan_tab': 'Scan Product',
        'profile_tab': 'My Profile & Family',

        'scan_title': 'Scan your product',
        'scan_desc': 'Take a photo of the ingredients label or upload a clear image.',
        'checking_for': 'Product will be checked for',
        'camera': 'Take a photo of the ingredients',
        'upload': 'Or upload an image',
        'analyze': 'Analyze Product',
        'original_image': 'Original image',
        'detected_area': 'Detected ingredients area',
        'ocr_text': 'Extracted text',
        'result': 'Scan result',

        'processing': 'mosabb is analyzing the ingredients...',
        'no_label': 'We could not detect the ingredients label. Try a closer and clearer image.',
        'no_text': 'We detected the label but could not read the text.',

        'danger': 'This product may not be suitable for',
        'safe': 'No registered allergen detected for',
        'all_safe': 'No registered allergens were detected.',
        'allergy_type': 'Allergy',
        'found': 'Detected',

        'profile_title': 'My Health Profile',
        'profile_desc': 'Set your allergens once and mosabb remembers them for every scan.',
        'my_allergies': 'My allergies',
        'save_allergies': 'Save my allergies',
        'saved': 'Your allergies have been saved',

        'family_title': 'My Family',
        'family_desc': 'Add children or family members and scan products for everyone at the same time.',
        'no_family': 'No family members added yet — you can still use mosabb for yourself.',
        'relation': 'Relation',
        'allergies': 'Allergies',
        'delete': 'Delete',

        'add_member': 'Add family member',
        'member_name': 'Name',
        'member_allergies': 'Their allergies',
        'add': 'Add member',

        'son': 'Son',
        'daughter': 'Daughter',
        'mother': 'Mother',
        'father': 'Father',
        'brother': 'Brother',
        'sister': 'Sister',
        'other': 'Other',

        'need_allergy': 'Add your allergy first from My Profile & Family.',
        'fill_data': 'Please fill in all fields.',
        'wrong_login': 'Incorrect email or password.',
        'email_used': 'This email is already registered.',
        'account_created': 'Account created. You can now log in.',
        'enter_member_name': 'Enter the person’s name.',
        'choose_allergy': 'Select at least one allergy.',
        'member_added': 'Added',

        'disclaimer': 'mosabb is an assistive tool and does not replace package warnings or medical guidance.'
    }
}


t = translations[
    st.session_state.language
]


# =========================================================
# CSS
# =========================================================

st.markdown(
    f'''
    <style>

    /* Background */

    .stApp {{
        background:
            radial-gradient(
                circle at 15% 20%,
                rgba(28, 255, 157, 0.08),
                transparent 30%
            ),
            radial-gradient(
                circle at 85% 20%,
                rgba(70, 120, 255, 0.08),
                transparent 28%
            ),
            #070B0F;

        color: #F7F9FA;
    }}


    .block-container {{
        max-width: 1200px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }}


    /* RTL / LTR */

    .stApp {{
        direction: {t['direction']};
    }}


    /* Hide Streamlit chrome */

    #MainMenu {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    header {{
        background: transparent !important;
    }}


    /* Logo */

    .mosabb-logo {{
        font-size: 28px;
        font-weight: 900;
        letter-spacing: -1px;
        margin-bottom: 10px;
    }}

    .mosabb-dot {{
        color: #30F29B;
    }}


    /* Hero */

    .hero {{
        padding: 55px 10px 45px 10px;
        position: relative;
    }}

    .hero-badge {{
        display: inline-block;
        padding: 8px 15px;
        border-radius: 999px;
        border: 1px solid rgba(48, 242, 155, .25);
        background: rgba(48, 242, 155, .07);
        color: #70F7BC;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 23px;
    }}

    .hero h1 {{
        font-size: clamp(48px, 8vw, 92px);
        line-height: 0.95;
        letter-spacing: -4px;
        margin: 0;
        max-width: 900px;
        font-weight: 900;
    }}

    .gradient-text {{
        background: linear-gradient(
            90deg,
            #30F29B,
            #65D8FF
        );

        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .hero p {{
        color: #9BA7B2;
        font-size: 20px;
        max-width: 750px;
        line-height: 1.8;
        margin-top: 30px;
    }}


    /* Cards */

    .glass-card {{
        background: rgba(18, 25, 32, 0.72);
        border: 1px solid rgba(255,255,255,0.07);
        box-shadow:
            0 20px 70px rgba(0,0,0,0.25),
            inset 0 1px 0 rgba(255,255,255,0.03);

        backdrop-filter: blur(20px);

        border-radius: 24px;

        padding: 25px;

        margin-bottom: 18px;
    }}


    .mini-card {{
        background:
            linear-gradient(
                140deg,
                rgba(255,255,255,0.055),
                rgba(255,255,255,0.015)
            );

        border: 1px solid rgba(255,255,255,0.07);

        padding: 18px 20px;

        border-radius: 18px;

        margin-bottom: 12px;
    }}


    /* Section titles */

    .section-kicker {{
        color: #30F29B;
        text-transform: uppercase;
        font-size: 12px;
        font-weight: 800;
        letter-spacing: 1.5px;
        margin-bottom: 5px;
    }}

    .section-title {{
        font-size: 36px;
        font-weight: 850;
        margin-bottom: 4px;
    }}

    .section-desc {{
        color: #87939D;
        margin-bottom: 25px;
        font-size: 15px;
    }}


    /* Pills */

    .allergy-pill {{
        display: inline-block;

        padding: 7px 12px;

        border-radius: 999px;

        background: rgba(255, 85, 85, .09);

        color: #FF9292;

        border: 1px solid rgba(255, 85, 85, .15);

        margin: 4px;

        font-size: 13px;

        font-weight: 700;
    }}


    .safe-pill {{
        display: inline-block;

        padding: 7px 12px;

        border-radius: 999px;

        background: rgba(48, 242, 155, .09);

        color: #70F7BC;

        border: 1px solid rgba(48, 242, 155, .15);

        margin: 4px;

        font-size: 13px;

        font-weight: 700;
    }}


    /* Buttons */

    .stButton > button {{
        border-radius: 14px !important;

        min-height: 48px;

        font-weight: 750;

        border: 1px solid rgba(255,255,255,.09);

        background:
            linear-gradient(
                135deg,
                #132027,
                #11171D
            );

        transition: all .25s ease;
    }}


    .stButton > button:hover {{
        transform: translateY(-2px);

        border-color: #30F29B !important;

        color: #30F29B !important;

        box-shadow:
            0 10px 30px rgba(48,242,155,.08);
    }}


    /* Inputs */

    .stTextInput input {{
        background: #0E151B !important;

        border: 1px solid rgba(255,255,255,.08) !important;

        border-radius: 14px !important;

        min-height: 48px;
    }}


    [data-baseweb="select"] > div {{
        background: #0E151B !important;

        border-radius: 14px !important;

        border-color: rgba(255,255,255,.08) !important;
    }}


    /* Upload */

    [data-testid="stFileUploaderDropzone"] {{
        background:
            linear-gradient(
                145deg,
                rgba(48,242,155,.035),
                rgba(255,255,255,.015)
            );

        border: 1px dashed rgba(48,242,155,.25);

        border-radius: 20px;
    }}


    /* Tabs */

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: transparent;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 12px;
        padding: 10px 18px;
        background: rgba(255,255,255,.03);
    }}

    .stTabs [aria-selected="true"] {{
        background: rgba(48,242,155,.10) !important;
        color: #30F29B !important;
    }}


    /* Alerts */

    [data-testid="stAlert"] {{
        border-radius: 18px;
        border: 1px solid rgba(255,255,255,.06);
    }}


    /* Divider */

    hr {{
        border-color: rgba(255,255,255,.06);
    }}


    /* Language switch */

    .language-label {{
        color: #77838D;
        font-size: 12px;
        margin-bottom: 3px;
    }}


    /* Scan glow */

    .scanner-card {{
        position: relative;

        padding: 30px;

        border-radius: 25px;

        background:
            linear-gradient(
                150deg,
                rgba(48,242,155,.055),
                rgba(13,19,25,.75)
            );

        border: 1px solid rgba(48,242,155,.12);

        box-shadow:
            0 30px 90px rgba(0,0,0,.30);
    }}


    /* Mobile */

    @media only screen and (max-width: 700px) {{

        .hero {{
            padding-top: 30px;
        }}

        .hero h1 {{
            letter-spacing: -2px;
        }}

        .hero p {{
            font-size: 17px;
        }}

        .section-title {{
            font-size: 28px;
        }}
    }}

    </style>
    ''',
    unsafe_allow_html=True
)


# =========================================================
# ALLERGENS
# =========================================================

ALLERGIES = [
    'Milk / Dairy',
    'Peanuts',
    'Sesame',
    'Eggs',
    'Tree Nuts'
]


ALLERGEN_KEYWORDS = {

    'Milk / Dairy': [
        'milk',
        'milk powder',
        'dairy',
        'whey',
        'whey protein',
        'casein',
        'caseinate',
        'lactose',
        'cream',
        'butter',
        'cheese',
        'yogurt',
        'حليب',
        'مسحوق الحليب',
        'مشتقات الحليب',
        'مصل الحليب',
        'بروتين الحليب',
        'كازين',
        'لاكتوز',
        'زبدة',
        'جبن',
        'قشطة',
        'لبن'
    ],

    'Peanuts': [
        'peanut',
        'peanuts',
        'groundnut',
        'peanut butter',
        'فول سوداني',
        'الفول السوداني',
        'زبدة الفول السوداني'
    ],

    'Sesame': [
        'sesame',
        'sesame seed',
        'tahini',
        'سمسم',
        'طحينة'
    ],

    'Eggs': [
        'egg',
        'eggs',
        'egg white',
        'egg yolk',
        'albumin',
        'ovalbumin',
        'بيض',
        'البيض',
        'بياض البيض',
        'صفار البيض'
    ],

    'Tree Nuts': [
        'almond',
        'walnut',
        'cashew',
        'pistachio',
        'hazelnut',
        'pecan',
        'macadamia',
        'لوز',
        'جوز',
        'كاجو',
        'فستق',
        'بندق'
    ]
}


# =========================================================
# MODEL
# =========================================================

@st.cache_resource
def load_model():

    return YOLO(
        'models/ingredient_label_model.pt'
    )


@st.cache_resource
def load_ocr():

    return easyocr.Reader(
        ['ar', 'en'],
        gpu=False
    )


def extract_ingredient_region(
    image,
    model
):

    image_array = np.array(
        image
    )

    results = model(
        image_array,
        conf=0.20,
        verbose=False
    )

    boxes = results[0].boxes

    if boxes is None or len(boxes) == 0:
        return None

    best_box = None
    best_confidence = 0

    for box in boxes:

        confidence = float(
            box.conf[0]
        )

        if confidence > best_confidence:

            best_confidence = confidence
            best_box = box


    coordinates = (
        best_box
        .xyxy[0]
        .cpu()
        .numpy()
    )


    x1 = max(
        int(coordinates[0]),
        0
    )

    y1 = max(
        int(coordinates[1]),
        0
    )

    x2 = min(
        int(coordinates[2]),
        image.width
    )

    y2 = min(
        int(coordinates[3]),
        image.height
    )


    return image.crop(
        (
            x1,
            y1,
            x2,
            y2
        )
    )


def run_ocr(
    image,
    reader
):

    results = reader.readtext(
        np.array(image),
        detail=0,
        paragraph=True
    )

    return ' '.join(
        results
    )


def find_allergen_matches(
    text,
    allergy
):

    text_lower = text.lower()

    found = []

    keywords = ALLERGEN_KEYWORDS.get(
        allergy,
        []
    )


    cleaned_words = (
        text_lower
        .replace(',', ' ')
        .replace('.', ' ')
        .replace(':', ' ')
        .replace(';', ' ')
        .replace('(', ' ')
        .replace(')', ' ')
        .split()
    )


    for keyword in keywords:

        keyword_lower = keyword.lower()

        if keyword_lower in text_lower:

            found.append(
                keyword
            )

            continue


        if len(keyword_lower) <= 4:
            continue


        for word in cleaned_words:

            if fuzz.ratio(
                word,
                keyword_lower
            ) >= 88:

                found.append(
                    keyword
                )

                break


    return list(
        set(found)
    )


def check_people(
    text,
    people
):

    output = []

    for person in people:

        matches = {}

        for allergy in person['allergies']:

            found = find_allergen_matches(
                text,
                allergy
            )

            if found:

                matches[allergy] = found


        output.append({
            'name': person['name'],
            'relation': person['relation'],
            'matches': matches
        })


    return output


# =========================================================
# TOP BAR
# =========================================================

top_left, top_right = st.columns(
    [8, 2]
)


with top_left:

    st.markdown(
        '''
        <div class="mosabb-logo">
            mosabb<span class="mosabb-dot">.</span>
        </div>
        ''',
        unsafe_allow_html=True
    )


with top_right:

    language = st.segmented_control(
        '',
        ['العربية', 'English'],
        default=(
            'العربية'
            if st.session_state.language == 'AR'
            else 'English'
        )
    )


    selected_language = (
        'AR'
        if language == 'العربية'
        else 'EN'
    )


    if selected_language != st.session_state.language:

        st.session_state.language = selected_language
        st.rerun()


# =========================================================
# HERO
# =========================================================

st.markdown(
    f'''
    <div class="hero">

        <div class="hero-badge">
            ✦ {t["hero_badge"]}
        </div>

        <h1>
            {t["hero_title_1"]}
            <span class="gradient-text">
                {t["hero_title_2"]}
            </span>
            <br>
            {t["hero_title_3"]}
        </h1>

        <p>
            {t["hero_desc"]}
        </p>

    </div>
    ''',
    unsafe_allow_html=True
)


# =========================================================
# LOGIN
# =========================================================

if st.session_state.user is None:

    col1, col2 = st.columns(
        [1.15, 0.85],
        gap='large'
    )


    with col1:

        login_tab, register_tab = st.tabs([
            t['login'],
            t['register']
        ])


        with login_tab:

            st.markdown(
                f'''
                <div class="section-kicker">
                    MOSABB ACCOUNT
                </div>

                <div class="section-title">
                    {t["login"]}
                </div>
                ''',
                unsafe_allow_html=True
            )


            login_email = st.text_input(
                t['email'],
                key='login_email'
            )


            login_password = st.text_input(
                t['password'],
                type='password',
                key='login_password'
            )


            if st.button(
                t['enter'],
                use_container_width=True
            ):

                user = login_user(
                    login_email,
                    login_password
                )


                if user:

                    st.session_state.user = {
                        'id': user[0],
                        'name': user[1],
                        'email': user[2]
                    }

                    st.rerun()

                else:

                    st.error(
                        t['wrong_login']
                    )


        with register_tab:

            st.markdown(
                f'''
                <div class="section-kicker">
                    NEW ACCOUNT
                </div>

                <div class="section-title">
                    {t["register"]}
                </div>
                ''',
                unsafe_allow_html=True
            )


            register_name = st.text_input(
                t['name'],
                key='register_name'
            )


            register_email = st.text_input(
                t['email'],
                key='register_email'
            )


            register_password = st.text_input(
                t['password'],
                type='password',
                key='register_password'
            )


            if st.button(
                t['create_account'],
                use_container_width=True
            ):

                if (
                    not register_name
                    or not register_email
                    or not register_password
                ):

                    st.warning(
                        t['fill_data']
                    )

                else:

                    success = register_user(
                        register_name,
                        register_email,
                        register_password
                    )


                    if success:

                        st.success(
                            t['account_created']
                        )

                    else:

                        st.error(
                            t['email_used']
                        )


    with col2:

        st.markdown(
            '''
            <div class="glass-card">

                <div style="
                    font-size:55px;
                    margin-bottom:20px;
                ">
                    🛡️
                </div>

                <div style="
                    font-size:25px;
                    font-weight:850;
                    margin-bottom:12px;
                ">
                    One scan.
                    <br>
                    Every person protected.
                </div>

                <div style="
                    color:#82909A;
                    line-height:1.8;
                ">
                    Your allergy profile stays with you.
                    Add family members and mosabb checks
                    everyone automatically.
                </div>

            </div>
            ''',
            unsafe_allow_html=True
        )


# =========================================================
# APP
# =========================================================

else:

    user = st.session_state.user


    welcome_col, logout_col = st.columns(
        [8, 2]
    )


    with welcome_col:

        st.markdown(
            f'''
            <div class="mini-card">

                <span style="
                    color:#81909A;
                ">
                    {t["welcome"]}
                </span>

                <span style="
                    font-size:18px;
                    font-weight:800;
                ">
                    {user["name"]}
                </span>

                <span style="
                    margin-left:5px;
                ">
                    👋
                </span>

            </div>
            ''',
            unsafe_allow_html=True
        )


    with logout_col:

        if st.button(
            t['logout'],
            use_container_width=True
        ):

            st.session_state.user = None
            st.rerun()


    scan_tab, profile_tab = st.tabs([
        '◉ ' + t['scan_tab'],
        '◎ ' + t['profile_tab']
    ])


    # =====================================================
    # SCAN
    # =====================================================

    with scan_tab:

        st.markdown(
            f'''
            <br>

            <div class="section-kicker">
                AI PRODUCT SCANNER
            </div>

            <div class="section-title">
                {t["scan_title"]}
            </div>

            <div class="section-desc">
                {t["scan_desc"]}
            </div>
            ''',
            unsafe_allow_html=True
        )


        my_allergies = get_user_allergies(
            user['id']
        )

        family = get_family_members(
            user['id']
        )


        people_to_check = []


        if my_allergies:

            people_to_check.append({
                'name': user['name'],
                'relation': 'Me',
                'allergies': my_allergies
            })


        for member in family:

            people_to_check.append({
                'name': member['name'],
                'relation': member['relation'],
                'allergies': member['allergies']
            })


        if not people_to_check:

            st.warning(
                t['need_allergy']
            )


        else:

            st.markdown(
                f'''
                <div style="
                    color:#7F8C96;
                    margin-bottom:10px;
                    font-size:14px;
                ">
                    {t["checking_for"]}
                </div>
                ''',
                unsafe_allow_html=True
            )


            pills = ''


            for person in people_to_check:

                allergies_text = ', '.join(
                    person['allergies']
                )

                pills += f'''
                    <div class="mini-card">

                        <strong>
                            {person["name"]}
                        </strong>

                        <span style="
                            color:#6E7C87;
                            margin:0 7px;
                        ">
                            ·
                        </span>

                        <span style="
                            color:#FF9898;
                        ">
                            {allergies_text}
                        </span>

                    </div>
                '''


            st.markdown(
                pills,
                unsafe_allow_html=True
            )


            st.markdown(
                '<div style="height:15px"></div>',
                unsafe_allow_html=True
            )


            input_col1, input_col2 = st.columns(
                2,
                gap='large'
            )


            with input_col1:

                camera_image = st.camera_input(
                    t['camera']
                )


            with input_col2:

                uploaded_file = st.file_uploader(
                    t['upload'],
                    type=[
                        'jpg',
                        'jpeg',
                        'png'
                    ]
                )


            image_source = None


            if camera_image is not None:

                image_source = camera_image


            elif uploaded_file is not None:

                image_source = uploaded_file


            if image_source is not None:

                image = Image.open(
                    image_source
                ).convert(
                    'RGB'
                )


                st.image(
                    image,
                    caption=t['original_image'],
                    use_container_width=True
                )


                st.markdown(
                    '<div style="height:10px"></div>',
                    unsafe_allow_html=True
                )


                if st.button(
                    '✦ ' + t['analyze'],
                    use_container_width=True
                ):

                    with st.spinner(
                        t['processing']
                    ):

                        try:

                            model = load_model()

                            reader = load_ocr()


                            cropped = extract_ingredient_region(
                                image,
                                model
                            )


                            if cropped is None:

                                st.error(
                                    t['no_label']
                                )


                            else:

                                st.markdown(
                                    f'''
                                    <div class="section-title"
                                         style="font-size:25px">
                                        {t["detected_area"]}
                                    </div>
                                    ''',
                                    unsafe_allow_html=True
                                )


                                st.image(
                                    cropped,
                                    use_container_width=True
                                )


                                text = run_ocr(
                                    cropped,
                                    reader
                                )


                                if not text.strip():

                                    st.error(
                                        t['no_text']
                                    )


                                else:

                                    with st.expander(
                                        t['ocr_text']
                                    ):

                                        st.write(
                                            text
                                        )


                                    results = check_people(
                                        text,
                                        people_to_check
                                    )


                                    st.markdown(
                                        f'''
                                        <br>

                                        <div class="section-kicker">
                                            MOSABB RESULT
                                        </div>

                                        <div class="section-title">
                                            {t["result"]}
                                        </div>
                                        ''',
                                        unsafe_allow_html=True
                                    )


                                    any_warning = False


                                    for result in results:

                                        if result['matches']:

                                            any_warning = True


                                            st.error(
                                                '⚠️ '
                                                + t['danger']
                                                + ' '
                                                + result['name']
                                            )


                                            for allergy, matches in result['matches'].items():

                                                st.markdown(
                                                    f'''
                                                    <div class="glass-card">

                                                        <div style="
                                                            color:#7D8994;
                                                            font-size:13px;
                                                        ">
                                                            {t["allergy_type"]}
                                                        </div>

                                                        <div style="
                                                            font-size:22px;
                                                            font-weight:850;
                                                            margin-bottom:12px;
                                                        ">
                                                            {allergy}
                                                        </div>

                                                        <div>
                                                            {t["found"]}:
                                                            <strong>
                                                                {", ".join(matches)}
                                                            </strong>
                                                        </div>

                                                    </div>
                                                    ''',
                                                    unsafe_allow_html=True
                                                )


                                        else:

                                            st.success(
                                                '✓ '
                                                + t['safe']
                                                + ' '
                                                + result['name']
                                            )


                                    if not any_warning:

                                        st.success(
                                            '✓ '
                                            + t['all_safe']
                                        )


                                    st.info(
                                        t['disclaimer']
                                    )


                        except Exception as error:

                            st.error(
                                'Analysis error'
                            )

                            st.code(
                                str(error)
                            )


    # =====================================================
    # PROFILE
    # =====================================================

    with profile_tab:

        st.markdown(
            f'''
            <br>

            <div class="section-kicker">
                PERSONAL SAFETY PROFILE
            </div>

            <div class="section-title">
                {t["profile_title"]}
            </div>

            <div class="section-desc">
                {t["profile_desc"]}
            </div>
            ''',
            unsafe_allow_html=True
        )


        current_allergies = get_user_allergies(
            user['id']
        )


        selected_allergies = st.multiselect(
            t['my_allergies'],
            ALLERGIES,
            default=current_allergies
        )


        if st.button(
            t['save_allergies'],
            use_container_width=True
        ):

            save_user_allergies(
                user['id'],
                selected_allergies
            )

            st.success(
                t['saved'] + ' ✓'
            )

            st.rerun()


        st.markdown(
            '<br><hr><br>',
            unsafe_allow_html=True
        )


        st.markdown(
            f'''
            <div class="section-kicker">
                FAMILY PROTECTION
            </div>

            <div class="section-title">
                {t["family_title"]}
            </div>

            <div class="section-desc">
                {t["family_desc"]}
            </div>
            ''',
            unsafe_allow_html=True
        )


        family = get_family_members(
            user['id']
        )


        if family:

            cols = st.columns(
                2
            )


            for index, member in enumerate(
                family
            ):

                with cols[index % 2]:

                    with st.container(
                        border=True
                    ):

                        st.markdown(
                            f'''
                            <div style="
                                font-size:24px;
                                font-weight:850;
                                margin-bottom:5px;
                            ">
                                {member["name"]}
                            </div>

                            <div style="
                                color:#7F8C96;
                                margin-bottom:14px;
                            ">
                                {member["relation"]}
                            </div>
                            ''',
                            unsafe_allow_html=True
                        )


                        for allergy in member['allergies']:

                            st.markdown(
                                f'''
                                <span class="allergy-pill">
                                    {allergy}
                                </span>
                                ''',
                                unsafe_allow_html=True
                            )


                        if st.button(
                            t['delete']
                            + ' '
                            + member['name'],
                            key='delete_'
                            + str(member['id']),
                            use_container_width=True
                        ):

                            delete_family_member(
                                member['id']
                            )

                            st.rerun()


        else:

            st.info(
                t['no_family']
            )


        st.markdown(
            '<br><br>',
            unsafe_allow_html=True
        )


        st.markdown(
            f'''
            <div class="glass-card">

                <div class="section-title"
                     style="font-size:26px">
                    ＋ {t["add_member"]}
                </div>

            </div>
            ''',
            unsafe_allow_html=True
        )


        add_col1, add_col2 = st.columns(
            2
        )


        with add_col1:

            member_name = st.text_input(
                t['member_name']
            )


        with add_col2:

            relation = st.selectbox(
                t['relation'],
                [
                    t['son'],
                    t['daughter'],
                    t['mother'],
                    t['father'],
                    t['brother'],
                    t['sister'],
                    t['other']
                ]
            )


        member_allergies = st.multiselect(
            t['member_allergies'],
            ALLERGIES,
            key='family_allergies'
        )


        if st.button(
            '＋ ' + t['add'],
            use_container_width=True
        ):

            if not member_name:

                st.warning(
                    t['enter_member_name']
                )

            elif not member_allergies:

                st.warning(
                    t['choose_allergy']
                )

            else:

                add_family_member(
                    user['id'],
                    member_name,
                    relation,
                    member_allergies
                )


                st.success(
                    t['member_added']
                    + ' '
                    + member_name
                    + ' ✓'
                )


                st.rerun()
