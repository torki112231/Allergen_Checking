import streamlit as st
import numpy as np
import textwrap

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
# HELPERS
# =========================================================

def html(content):
    st.markdown(
        textwrap.dedent(content),
        unsafe_allow_html=True
    )


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
        'lang_ar': 'العربية',
        'lang_en': 'English',

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
        'lang_ar': 'العربية',
        'lang_en': 'English',

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


t = translations[st.session_state.language]


# =========================================================
# CSS
# =========================================================

html(
    f'''
    <style>

    .stApp {{
        background:
            radial-gradient(circle at 10% 15%, rgba(38, 243, 154, 0.10), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(60, 120, 255, 0.09), transparent 25%),
            linear-gradient(160deg, #07100D 0%, #080D13 45%, #090C12 100%);
        color: #F7F9FA;
        min-height: 100vh;
        direction: {t['direction']};
    }}

    .block-container {{
        max-width: 1180px;
        padding-top: 1.2rem;
        padding-bottom: 5rem;
    }}

    #MainMenu {{
        visibility: hidden;
    }}

    footer {{
        visibility: hidden;
    }}

    header {{
        background: transparent !important;
    }}

    .top-shell {{
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 2px 18px 2px;
    }}

    .logo {{
        font-size: 31px;
        font-weight: 950;
        letter-spacing: -1.5px;
        color: #F8FAFB;
    }}

    .logo-dot {{
        color: #2CF19C;
    }}

    .hero {{
        padding: 62px 0 45px 0;
    }}

    .hero-badge {{
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 9px 15px;
        border-radius: 999px;
        border: 1px solid rgba(44, 241, 156, 0.20);
        background: rgba(44, 241, 156, 0.07);
        color: #74F7BE;
        font-size: 14px;
        font-weight: 800;
        margin-bottom: 24px;
    }}

    .hero-title {{
        margin: 0;
        max-width: 930px;
        font-size: clamp(48px, 7vw, 88px);
        line-height: 0.98;
        letter-spacing: -4px;
        font-weight: 950;
    }}

    .gradient-text {{
        background: linear-gradient(90deg, #2CF19C, #6AD4FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .hero-desc {{
        color: #9CA7B1;
        max-width: 760px;
        font-size: 19px;
        line-height: 1.85;
        margin-top: 25px;
    }}

    .panel {{
        background: rgba(15, 21, 27, 0.78);
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 24px;
        padding: 28px;
        box-shadow:
            0 28px 80px rgba(0, 0, 0, 0.28),
            inset 0 1px 0 rgba(255, 255, 255, 0.025);
        backdrop-filter: blur(20px);
    }}

    .panel-soft {{
        background: linear-gradient(
            145deg,
            rgba(44, 241, 156, 0.045),
            rgba(255, 255, 255, 0.02)
        );
        border: 1px solid rgba(255, 255, 255, 0.07);
        border-radius: 22px;
        padding: 24px;
    }}

    .section-kicker {{
        color: #35F1A0;
        font-size: 12px;
        font-weight: 900;
        letter-spacing: 1.5px;
        margin-bottom: 7px;
    }}

    .section-title {{
        font-size: 35px;
        font-weight: 900;
        letter-spacing: -1px;
        margin-bottom: 7px;
    }}

    .section-desc {{
        color: #87939D;
        font-size: 15px;
        line-height: 1.75;
        margin-bottom: 24px;
    }}

    .profile-card {{
        border: 1px solid rgba(255,255,255,0.07);
        background: rgba(255,255,255,0.025);
        border-radius: 18px;
        padding: 16px 18px;
        margin-bottom: 10px;
    }}

    .profile-name {{
        font-size: 17px;
        font-weight: 850;
    }}

    .profile-allergy {{
        margin-top: 6px;
        color: #FF9494;
        font-size: 14px;
    }}

    .allergy-pill {{
        display: inline-block;
        padding: 7px 12px;
        margin: 4px;
        border-radius: 999px;
        background: rgba(255, 91, 91, 0.09);
        border: 1px solid rgba(255, 91, 91, 0.15);
        color: #FF9A9A;
        font-size: 13px;
        font-weight: 800;
    }}

    .stButton > button {{
        min-height: 48px;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,0.09);
        background: linear-gradient(135deg, #142027, #11181E);
        color: #F7F9FA;
        font-weight: 800;
        transition: all 0.20s ease;
    }}

    .stButton > button:hover {{
        transform: translateY(-1px);
        border-color: #2CF19C !important;
        color: #2CF19C !important;
        box-shadow: 0 12px 35px rgba(44, 241, 156, 0.08);
    }}

    .stTextInput input {{
        background: #0E151B !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important;
        min-height: 48px;
    }}

    [data-baseweb="select"] > div {{
        background: #0E151B !important;
        border-radius: 14px !important;
        border-color: rgba(255,255,255,0.08) !important;
    }}

    [data-testid="stFileUploaderDropzone"] {{
        background:
            linear-gradient(
                145deg,
                rgba(44, 241, 156, 0.035),
                rgba(255,255,255,0.015)
            );
        border: 1px dashed rgba(44,241,156,0.28);
        border-radius: 20px;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
        background: transparent;
    }}

    .stTabs [data-baseweb="tab"] {{
        border-radius: 12px;
        padding: 10px 18px;
        background: rgba(255,255,255,0.03);
        font-weight: 750;
    }}

    .stTabs [aria-selected="true"] {{
        background: rgba(44,241,156,0.10) !important;
        color: #2CF19C !important;
    }}

    [data-testid="stAlert"] {{
        border-radius: 16px;
        border: 1px solid rgba(255,255,255,0.06);
    }}

    hr {{
        border-color: rgba(255,255,255,0.06);
    }}

    @media only screen and (max-width: 760px) {{
        .hero {{
            padding-top: 34px;
        }}

        .hero-title {{
            letter-spacing: -2px;
        }}

        .hero-desc {{
            font-size: 16px;
        }}

        .section-title {{
            font-size: 28px;
        }}

        .panel {{
            padding: 20px;
        }}
    }}

    </style>
    '''
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


def extract_ingredient_region(image, model):

    image_array = np.array(image)

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


def run_ocr(image, reader):

    results = reader.readtext(
        np.array(image),
        detail=0,
        paragraph=True
    )

    return ' '.join(results)


def find_allergen_matches(text, allergy):

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

            found.append(keyword)
            continue


        if len(keyword_lower) <= 4:
            continue


        for word in cleaned_words:

            score = fuzz.ratio(
                word,
                keyword_lower
            )

            if score >= 88:

                found.append(keyword)
                break


    return list(set(found))


def check_people(text, people):

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
    [7, 3],
    vertical_alignment='center'
)


with top_left:

    html(
        '''
        <div class="logo">
            mosabb<span class="logo-dot">.</span>
        </div>
        '''
    )


with top_right:

    language = st.segmented_control(
        '',
        ['العربية', 'English'],
        default=(
            'العربية'
            if st.session_state.language == 'AR'
            else 'English'
        ),
        key='language_switch'
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

html(
    f'''
    <div class="hero">

        <div class="hero-badge">
            ✦ {t["hero_badge"]}
        </div>

        <h1 class="hero-title">
            {t["hero_title_1"]}
            <span class="gradient-text">
                {t["hero_title_2"]}
            </span>
            <br>
            {t["hero_title_3"]}
        </h1>

        <div class="hero-desc">
            {t["hero_desc"]}
        </div>

    </div>
    '''
)


# =========================================================
# LOGIN / REGISTER
# =========================================================

if st.session_state.user is None:

    left, right = st.columns(
        [1, 1],
        gap='large'
    )


    with left:

        html(
            '''
            <div class="panel-soft">
                <div style="
                    font-size: 13px;
                    color: #2CF19C;
                    font-weight: 900;
                    letter-spacing: 1px;
                    margin-bottom: 12px;
                ">
                    FAMILY PROTECTION
                </div>

                <div style="
                    font-size: 34px;
                    font-weight: 900;
                    letter-spacing: -1px;
                    line-height: 1.15;
                    margin-bottom: 14px;
                ">
                    One scan.<br>
                    Everyone protected.
                </div>

                <div style="
                    color: #8D99A3;
                    line-height: 1.8;
                    font-size: 15px;
                ">
                    Create your allergy profile once.
                    Add family members if you want.
                    mosabb checks the same product against everyone automatically.
                </div>

                <div style="
                    margin-top: 26px;
                    display: grid;
                    gap: 10px;
                ">
                    <div class="profile-card">
                        <div class="profile-name">You</div>
                        <div class="profile-allergy">Milk / Dairy</div>
                    </div>

                    <div class="profile-card">
                        <div class="profile-name">Child</div>
                        <div class="profile-allergy">Peanuts · Sesame</div>
                    </div>
                </div>
            </div>
            '''
        )


    with right:

        login_tab, register_tab = st.tabs([
            t['login'],
            t['register']
        ])


        with login_tab:

            html(
                f'''
                <div class="section-kicker">
                    MOSABB ACCOUNT
                </div>

                <div class="section-title">
                    {t["login"]}
                </div>
                '''
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
                use_container_width=True,
                key='login_button'
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

            html(
                f'''
                <div class="section-kicker">
                    NEW ACCOUNT
                </div>

                <div class="section-title">
                    {t["register"]}
                </div>
                '''
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
                use_container_width=True,
                key='register_button'
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


# =========================================================
# LOGGED IN
# =========================================================

else:

    user = st.session_state.user


    welcome_col, logout_col = st.columns(
        [8, 2],
        vertical_alignment='center'
    )


    with welcome_col:

        html(
            f'''
            <div class="panel-soft" style="padding:18px 20px;">
                <span style="
                    color:#82909A;
                    font-size:14px;
                ">
                    {t["welcome"]}
                </span>

                <span style="
                    font-size:19px;
                    font-weight:900;
                    margin-inline-start:8px;
                ">
                    {user["name"]}
                </span>

                <span style="
                    margin-inline-start:5px;
                ">
                    👋
                </span>
            </div>
            '''
        )


    with logout_col:

        if st.button(
            t['logout'],
            use_container_width=True,
            key='logout_button'
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

        html(
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
            '''
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

            html(
                f'''
                <div style="
                    color:#7F8C96;
                    margin-bottom:10px;
                    font-size:14px;
                ">
                    {t["checking_for"]}
                </div>
                '''
            )


            cards = ''

            for person in people_to_check:

                allergies_text = ', '.join(
                    person['allergies']
                )

                cards += f'''
                <div class="profile-card">
                    <div class="profile-name">
                        {person["name"]}
                    </div>
                    <div class="profile-allergy">
                        {allergies_text}
                    </div>
                </div>
                '''


            html(cards)


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


                if st.button(
                    '✦ ' + t['analyze'],
                    use_container_width=True,
                    key='analyze_button'
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

                                html(
                                    f'''
                                    <div class="section-title"
                                         style="font-size:25px; margin-top:25px;">
                                        {t["detected_area"]}
                                    </div>
                                    '''
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

                                        st.write(text)


                                    results = check_people(
                                        text,
                                        people_to_check
                                    )


                                    html(
                                        f'''
                                        <br>

                                        <div class="section-kicker">
                                            MOSABB RESULT
                                        </div>

                                        <div class="section-title">
                                            {t["result"]}
                                        </div>
                                        '''
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

                                                html(
                                                    f'''
                                                    <div class="panel-soft">

                                                        <div style="
                                                            color:#7D8994;
                                                            font-size:13px;
                                                        ">
                                                            {t["allergy_type"]}
                                                        </div>

                                                        <div style="
                                                            font-size:22px;
                                                            font-weight:900;
                                                            margin:6px 0 12px 0;
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
                                                    '''
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

        html(
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
            '''
        )


        current_allergies = get_user_allergies(
            user['id']
        )


        selected_allergies = st.multiselect(
            t['my_allergies'],
            ALLERGIES,
            default=current_allergies,
            key='my_allergies'
        )


        if st.button(
            t['save_allergies'],
            use_container_width=True,
            key='save_my_allergies'
        ):

            save_user_allergies(
                user['id'],
                selected_allergies
            )

            st.success(
                t['saved'] + ' ✓'
            )

            st.rerun()


        st.divider()


        html(
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
            '''
        )


        family = get_family_members(
            user['id']
        )


        if family:

            cols = st.columns(2)


            for index, member in enumerate(
                family
            ):

                with cols[index % 2]:

                    with st.container(
                        border=True
                    ):

                        html(
                            f'''
                            <div style="
                                font-size:23px;
                                font-weight:900;
                                margin-bottom:5px;
                            ">
                                {member["name"]}
                            </div>

                            <div style="
                                color:#7F8C96;
                                margin-bottom:12px;
                            ">
                                {member["relation"]}
                            </div>
                            '''
                        )


                        pills = ''

                        for allergy in member['allergies']:

                            pills += f'''
                            <span class="allergy-pill">
                                {allergy}
                            </span>
                            '''


                        html(pills)


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


        st.markdown('<br>', unsafe_allow_html=True)


        html(
            f'''
            <div class="panel">

                <div class="section-kicker">
                    NEW FAMILY MEMBER
                </div>

                <div class="section-title"
                     style="font-size:26px;">
                    ＋ {t["add_member"]}
                </div>

            </div>
            '''
        )


        add_col1, add_col2 = st.columns(
            2
        )


        with add_col1:

            member_name = st.text_input(
                t['member_name'],
                key='member_name'
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
                ],
                key='relation'
            )


        member_allergies = st.multiselect(
            t['member_allergies'],
            ALLERGIES,
            key='family_allergies'
        )


        if st.button(
            '＋ ' + t['add'],
            use_container_width=True,
            key='add_family_member_button'
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
