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
# CONFIG
# =========================================================

st.set_page_config(
    page_title='mosabb | مسبب',
    page_icon='🟢',
    layout='wide',
    initial_sidebar_state='collapsed'
)

create_tables()


if 'user' not in st.session_state:
    st.session_state.user = None

if 'language' not in st.session_state:
    st.session_state.language = 'AR'


# =========================================================
# TRANSLATIONS
# =========================================================

translations = {
    'AR': {
        'dir': 'rtl',

        'badge': 'سلامتك تبدأ قبل أول لقمة',
        'hero_1': 'اعرف',
        'hero_2': 'مسبب',
        'hero_3': 'الحساسية قبل ما يوصلك.',
        'hero_desc':
            'صوّر مكونات المنتج، وmosabb يحللها بالذكاء الاصطناعي '
            'ويقارنها بحساسيتك وحساسيات عائلتك.',

        'login': 'تسجيل الدخول',
        'register': 'إنشاء حساب',
        'name': 'الاسم',
        'email': 'البريد الإلكتروني',
        'password': 'كلمة المرور',
        'enter': 'دخول',
        'create': 'إنشاء الحساب',
        'logout': 'تسجيل الخروج',

        'scan_tab': 'فحص منتج',
        'profile_tab': 'ملفي وعائلتي',

        'welcome': 'أهلاً',
        'scan_title': 'افحص منتجك',
        'scan_desc': 'صوّر قائمة المكونات أو ارفع صورة واضحة لها.',
        'check_for': 'mosabb سيفحص المنتج لـ',
        'camera': 'صوّر مكونات المنتج',
        'upload': 'أو ارفع صورة',
        'analyze': 'تحليل المنتج',
        'original': 'الصورة الأصلية',
        'detected': 'منطقة المكونات المكتشفة',
        'text': 'النص المقروء',
        'result': 'نتيجة الفحص',

        'processing': 'mosabb يحلل المنتج...',
        'no_label':
            'ما قدرنا نحدد قائمة المكونات. جرّب صورة أوضح وأقرب.',
        'no_text':
            'حددنا قائمة المكونات لكن ما قدرنا نقرأ النص.',

        'danger': 'هذا المنتج قد يسبب حساسية لـ',
        'safe': 'لم نجد مسبب الحساسية المسجل لـ',
        'allergy_type': 'نوع الحساسية',
        'found': 'تم العثور على',

        'profile_title': 'ملفي الصحي',
        'profile_desc':
            'سجل حساسيتك مرة واحدة، وmosabb يتذكرها في كل فحص.',
        'my_allergies': 'حساسيتي',
        'save': 'حفظ حساسيتي',
        'saved': 'تم حفظ حساسيتك',

        'family_title': 'عائلتي',
        'family_desc':
            'أضف أفراد العائلة ليتم فحص المنتج للجميع في نفس الوقت.',
        'no_family':
            'ما أضفت أحد للعائلة. تقدر تستخدم mosabb لنفسك عادي.',

        'add_member': 'إضافة فرد للعائلة',
        'member_name': 'اسم الشخص',
        'relation': 'صلة القرابة',
        'member_allergies': 'حساسياته',
        'add': 'إضافة فرد',
        'delete': 'حذف',

        'son': 'ابن',
        'daughter': 'ابنة',
        'mother': 'أم',
        'father': 'أب',
        'brother': 'أخ',
        'sister': 'أخت',
        'other': 'أخرى',

        'need_allergy':
            'سجل حساسيتك أول من صفحة ملفي وعائلتي.',
        'fill': 'عب البيانات كلها.',
        'wrong': 'البريد الإلكتروني أو كلمة المرور غير صحيحة.',
        'used': 'البريد الإلكتروني مستخدم من قبل.',
        'created': 'تم إنشاء الحساب. سجل دخولك الآن.',
        'choose': 'اختر حساسية واحدة على الأقل.',
        'enter_name': 'اكتب اسم الشخص.',

        'disclaimer':
            'mosabb أداة مساعدة. تأكد دائماً من تحذيرات الحساسية على العبوة.'
    },

    'EN': {
        'dir': 'ltr',

        'badge': 'Safety starts before the first bite',
        'hero_1': 'Know the',
        'hero_2': 'cause',
        'hero_3': 'before it reaches you.',
        'hero_desc':
            'Scan the ingredient label and let mosabb analyze it '
            'against your allergy profile and your family.',

        'login': 'Log in',
        'register': 'Create account',
        'name': 'Name',
        'email': 'Email',
        'password': 'Password',
        'enter': 'Log in',
        'create': 'Create account',
        'logout': 'Log out',

        'scan_tab': 'Scan Product',
        'profile_tab': 'My Profile & Family',

        'welcome': 'Welcome',
        'scan_title': 'Scan your product',
        'scan_desc':
            'Take a clear photo of the ingredients or upload one.',
        'check_for': 'mosabb will check this product for',
        'camera': 'Take a photo',
        'upload': 'Or upload an image',
        'analyze': 'Analyze Product',
        'original': 'Original image',
        'detected': 'Detected ingredient label',
        'text': 'Extracted text',
        'result': 'Scan result',

        'processing': 'mosabb is analyzing the product...',
        'no_label':
            'We could not detect the ingredient label. Try a clearer image.',
        'no_text':
            'The label was detected but the text could not be read.',

        'danger': 'This product may trigger an allergy for',
        'safe': 'No registered allergen detected for',
        'allergy_type': 'Allergy',
        'found': 'Detected',

        'profile_title': 'My Health Profile',
        'profile_desc':
            'Save your allergies once and mosabb remembers them.',
        'my_allergies': 'My allergies',
        'save': 'Save my allergies',
        'saved': 'Your allergies have been saved',

        'family_title': 'My Family',
        'family_desc':
            'Add family members and check one product for everyone.',
        'no_family':
            'No family members added. You can still use mosabb for yourself.',

        'add_member': 'Add family member',
        'member_name': 'Name',
        'relation': 'Relation',
        'member_allergies': 'Allergies',
        'add': 'Add member',
        'delete': 'Delete',

        'son': 'Son',
        'daughter': 'Daughter',
        'mother': 'Mother',
        'father': 'Father',
        'brother': 'Brother',
        'sister': 'Sister',
        'other': 'Other',

        'need_allergy':
            'Add your allergy first from My Profile & Family.',
        'fill': 'Please fill in all fields.',
        'wrong': 'Incorrect email or password.',
        'used': 'This email is already registered.',
        'created': 'Account created. You can now log in.',
        'choose': 'Select at least one allergy.',
        'enter_name': 'Enter the person name.',

        'disclaimer':
            'mosabb is an assistive tool. Always check the package allergy warning.'
    }
}


t = translations[st.session_state.language]


# =========================================================
# CSS — st.html ONLY
# =========================================================

st.html(
    f"""
    <style>

    :root {{
        --green: #31F2A0;
        --green-soft: rgba(49, 242, 160, 0.10);
        --bg: #070C10;
        --card: rgba(15, 22, 27, 0.82);
        --border: rgba(255,255,255,0.07);
        --muted: #8A98A3;
        --danger: #FF7777;
    }}

    .stApp {{
        direction: {t['dir']};
        background:
            radial-gradient(
                circle at 12% 10%,
                rgba(49,242,160,.10),
                transparent 28%
            ),
            radial-gradient(
                circle at 90% 5%,
                rgba(57,110,255,.08),
                transparent 25%
            ),
            linear-gradient(
                150deg,
                #07100D 0%,
                #080D12 48%,
                #080B11 100%
            );
        color: white;
    }}

    .block-container {{
        max-width: 1150px;
        padding-top: 1.3rem;
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

    .mosabb-logo {{
        font-size: 31px;
        font-weight: 950;
        letter-spacing: -1.4px;
        color: white;
    }}

    .mosabb-dot {{
        color: var(--green);
    }}

    .hero {{
        padding-top: 55px;
        padding-bottom: 45px;
    }}

    .hero-badge {{
        display: inline-block;
        padding: 9px 15px;
        border: 1px solid rgba(49,242,160,.22);
        border-radius: 999px;
        background: rgba(49,242,160,.07);
        color: #74F7BE;
        font-weight: 800;
        font-size: 14px;
        margin-bottom: 22px;
    }}

    .hero-title {{
        font-size: clamp(48px, 7vw, 84px);
        font-weight: 950;
        letter-spacing: -4px;
        line-height: 0.98;
        max-width: 900px;
        margin: 0;
    }}

    .gradient {{
        background: linear-gradient(
            90deg,
            #31F2A0,
            #6AD5FF
        );
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }}

    .hero-desc {{
        margin-top: 25px;
        max-width: 720px;
        color: var(--muted);
        font-size: 18px;
        line-height: 1.8;
    }}

    .glass {{
        padding: 27px;
        border-radius: 24px;
        background: var(--card);
        border: 1px solid var(--border);
        box-shadow: 0 30px 90px rgba(0,0,0,.28);
        backdrop-filter: blur(18px);
    }}

    .soft-card {{
        padding: 19px;
        border-radius: 18px;
        background: rgba(255,255,255,.025);
        border: 1px solid var(--border);
        margin-bottom: 10px;
    }}

    .kicker {{
        font-size: 12px;
        font-weight: 900;
        letter-spacing: 1.4px;
        color: var(--green);
        margin-bottom: 8px;
    }}

    .section-title {{
        font-size: 34px;
        font-weight: 950;
        letter-spacing: -1px;
        margin-bottom: 7px;
    }}

    .section-desc {{
        color: var(--muted);
        line-height: 1.7;
        margin-bottom: 23px;
    }}

    .person-name {{
        font-size: 18px;
        font-weight: 900;
    }}

    .person-allergy {{
        color: #FF9696;
        margin-top: 5px;
        font-size: 14px;
    }}

    .pill {{
        display: inline-block;
        border-radius: 999px;
        padding: 7px 12px;
        margin: 4px;
        color: #FF9797;
        background: rgba(255,90,90,.08);
        border: 1px solid rgba(255,90,90,.14);
        font-size: 13px;
        font-weight: 800;
    }}

    .result-danger {{
        padding: 22px;
        border-radius: 20px;
        border: 1px solid rgba(255,90,90,.22);
        background:
            linear-gradient(
                135deg,
                rgba(255,75,75,.11),
                rgba(255,75,75,.035)
            );
        margin: 12px 0;
    }}

    .result-safe {{
        padding: 22px;
        border-radius: 20px;
        border: 1px solid rgba(49,242,160,.20);
        background:
            linear-gradient(
                135deg,
                rgba(49,242,160,.10),
                rgba(49,242,160,.03)
            );
        margin: 12px 0;
    }}

    .stButton > button {{
        min-height: 48px;
        border-radius: 14px !important;
        border: 1px solid rgba(255,255,255,.09);
        background: #121B21;
        font-weight: 800;
        transition: .2s ease;
    }}

    .stButton > button:hover {{
        color: var(--green) !important;
        border-color: var(--green) !important;
        transform: translateY(-1px);
    }}

    .stTextInput input {{
        background: #0E151B !important;
        min-height: 48px;
        border-radius: 13px !important;
        border: 1px solid rgba(255,255,255,.08) !important;
    }}

    [data-baseweb="select"] > div {{
        background: #0E151B !important;
        border-radius: 13px !important;
        border-color: rgba(255,255,255,.08) !important;
    }}

    [data-testid="stFileUploaderDropzone"] {{
        border: 1px dashed rgba(49,242,160,.25);
        background: rgba(49,242,160,.025);
        border-radius: 20px;
    }}

    .stTabs [data-baseweb="tab-list"] {{
        gap: 8px;
    }}

    .stTabs [data-baseweb="tab"] {{
        padding: 10px 17px;
        border-radius: 11px;
        font-weight: 800;
    }}

    .stTabs [aria-selected="true"] {{
        color: var(--green) !important;
        background: rgba(49,242,160,.08) !important;
    }}

    [data-testid="stAlert"] {{
        border-radius: 16px;
    }}

    @media (max-width: 700px) {{

        .hero {{
            padding-top: 30px;
        }}

        .hero-title {{
            letter-spacing: -2px;
        }}

        .hero-desc {{
            font-size: 16px;
        }}

        .section-title {{
            font-size: 27px;
        }}
    }}

    </style>
    """
)


# =========================================================
# ALLERGEN DATA
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
        'مصل الحليب',
        'مشتقات الحليب',
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
# AI
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

    results = model(
        np.array(image),
        conf=0.20,
        verbose=False
    )

    boxes = results[0].boxes

    if boxes is None or len(boxes) == 0:
        return None


    best_box = max(
        boxes,
        key=lambda box: float(box.conf[0])
    )


    box = (
        best_box
        .xyxy[0]
        .cpu()
        .numpy()
    )


    x1 = max(
        int(box[0]),
        0
    )

    y1 = max(
        int(box[1]),
        0
    )

    x2 = min(
        int(box[2]),
        image.width
    )

    y2 = min(
        int(box[3]),
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

    result = reader.readtext(
        np.array(image),
        detail=0,
        paragraph=True
    )

    return ' '.join(result)


def find_matches(
    text,
    allergy
):

    text_lower = text.lower()

    cleaned = (
        text_lower
        .replace(',', ' ')
        .replace('.', ' ')
        .replace(':', ' ')
        .replace(';', ' ')
        .replace('(', ' ')
        .replace(')', ' ')
        .split()
    )


    matches = []


    for keyword in ALLERGEN_KEYWORDS.get(
        allergy,
        []
    ):

        key = keyword.lower()


        if key in text_lower:

            matches.append(keyword)
            continue


        if len(key) <= 4:
            continue


        for word in cleaned:

            if fuzz.ratio(
                word,
                key
            ) >= 88:

                matches.append(keyword)
                break


    return list(set(matches))


def check_people(
    text,
    people
):

    result = []


    for person in people:

        matches = {}


        for allergy in person['allergies']:

            detected = find_matches(
                text,
                allergy
            )


            if detected:

                matches[allergy] = detected


        result.append({
            'name': person['name'],
            'matches': matches
        })


    return result


# =========================================================
# NAV
# =========================================================

logo_col, lang_col = st.columns(
    [7, 3],
    vertical_alignment='center'
)


with logo_col:

    st.html(
        """
        <div class="mosabb-logo">
            mosabb<span class="mosabb-dot">.</span>
        </div>
        """
    )


with lang_col:

    lang = st.segmented_control(
        'Language',
        ['العربية', 'English'],
        default=(
            'العربية'
            if st.session_state.language == 'AR'
            else 'English'
        ),
        label_visibility='collapsed'
    )


    new_lang = (
        'AR'
        if lang == 'العربية'
        else 'EN'
    )


    if new_lang != st.session_state.language:

        st.session_state.language = new_lang
        st.rerun()


# =========================================================
# HERO
# =========================================================

st.html(
    f"""
    <section class="hero">

        <div class="hero-badge">
            ✦ {t['badge']}
        </div>

        <h1 class="hero-title">

            {t['hero_1']}

            <span class="gradient">
                {t['hero_2']}
            </span>

            <br>

            {t['hero_3']}

        </h1>

        <div class="hero-desc">
            {t['hero_desc']}
        </div>

    </section>
    """
)


# =========================================================
# LOGIN
# =========================================================

if st.session_state.user is None:

    info_col, login_col = st.columns(
        [0.9, 1.1],
        gap='large'
    )


    with info_col:

        st.html(
            """
            <div class="glass">

                <div class="kicker">
                    FAMILY PROTECTION
                </div>

                <div class="section-title">
                    One scan.<br>
                    Everyone protected.
                </div>

                <div class="section-desc">
                    Your allergy profile stays with you.
                    Family members can be added whenever you need them.
                    mosabb checks everyone automatically.
                </div>

                <div class="soft-card">
                    <div class="person-name">
                        You
                    </div>

                    <div class="person-allergy">
                        Milk / Dairy
                    </div>
                </div>

                <div class="soft-card">
                    <div class="person-name">
                        Child
                    </div>

                    <div class="person-allergy">
                        Peanuts · Sesame
                    </div>
                </div>

            </div>
            """
        )


    with login_col:

        login_tab, register_tab = st.tabs([
            t['login'],
            t['register']
        ])


        with login_tab:

            st.html(
                f"""
                <div class="kicker">
                    MOSABB ACCOUNT
                </div>

                <div class="section-title">
                    {t['login']}
                </div>
                """
            )


            email = st.text_input(
                t['email'],
                key='login_email'
            )


            password = st.text_input(
                t['password'],
                type='password',
                key='login_password'
            )


            if st.button(
                t['enter'],
                use_container_width=True
            ):

                user = login_user(
                    email,
                    password
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
                        t['wrong']
                    )


        with register_tab:

            st.html(
                f"""
                <div class="kicker">
                    NEW ACCOUNT
                </div>

                <div class="section-title">
                    {t['register']}
                </div>
                """
            )


            name = st.text_input(
                t['name'],
                key='register_name'
            )


            email = st.text_input(
                t['email'],
                key='register_email'
            )


            password = st.text_input(
                t['password'],
                type='password',
                key='register_password'
            )


            if st.button(
                t['create'],
                use_container_width=True
            ):

                if not name or not email or not password:

                    st.warning(
                        t['fill']
                    )


                else:

                    success = register_user(
                        name,
                        email,
                        password
                    )


                    if success:

                        st.success(
                            t['created']
                        )

                    else:

                        st.error(
                            t['used']
                        )


# =========================================================
# DASHBOARD
# =========================================================

else:

    user = st.session_state.user


    user_col, logout_col = st.columns(
        [8, 2],
        vertical_alignment='center'
    )


    with user_col:

        st.html(
            f"""
            <div class="soft-card">
                <span style="color:#8A98A3;">
                    {t['welcome']}
                </span>

                <strong style="
                    margin-inline-start:8px;
                    font-size:19px;
                ">
                    {user['name']} 👋
                </strong>
            </div>
            """
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

        st.html(
            f"""
            <div style="height:20px;"></div>

            <div class="kicker">
                AI PRODUCT SCANNER
            </div>

            <div class="section-title">
                {t['scan_title']}
            </div>

            <div class="section-desc">
                {t['scan_desc']}
            </div>
            """
        )


        my_allergies = get_user_allergies(
            user['id']
        )


        family = get_family_members(
            user['id']
        )


        people = []


        if my_allergies:

            people.append({
                'name': user['name'],
                'allergies': my_allergies
            })


        for member in family:

            people.append({
                'name': member['name'],
                'allergies': member['allergies']
            })


        if not people:

            st.warning(
                t['need_allergy']
            )


        else:

            st.html(
                f"""
                <div style="
                    color:#8A98A3;
                    margin-bottom:12px;
                ">
                    {t['check_for']}
                </div>
                """
            )


            for person in people:

                allergy_text = ', '.join(
                    person['allergies']
                )


                st.html(
                    f"""
                    <div class="soft-card">

                        <div class="person-name">
                            {person['name']}
                        </div>

                        <div class="person-allergy">
                            {allergy_text}
                        </div>

                    </div>
                    """
                )


            cam_col, upload_col = st.columns(
                2,
                gap='large'
            )


            with cam_col:

                camera_image = st.camera_input(
                    t['camera']
                )


            with upload_col:

                uploaded_file = st.file_uploader(
                    t['upload'],
                    type=[
                        'jpg',
                        'jpeg',
                        'png'
                    ]
                )


            image_source = (
                camera_image
                if camera_image is not None
                else uploaded_file
            )


            if image_source is not None:

                image = Image.open(
                    image_source
                ).convert(
                    'RGB'
                )


                st.image(
                    image,
                    caption=t['original'],
                    use_container_width=True
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

                                st.html(
                                    f"""
                                    <div class="section-title"
                                         style="
                                            font-size:25px;
                                            margin-top:25px;
                                         ">
                                        {t['detected']}
                                    </div>
                                    """
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
                                        t['text']
                                    ):

                                        st.write(text)


                                    results = check_people(
                                        text,
                                        people
                                    )


                                    st.html(
                                        f"""
                                        <div style="height:20px;"></div>

                                        <div class="kicker">
                                            MOSABB RESULT
                                        </div>

                                        <div class="section-title">
                                            {t['result']}
                                        </div>
                                        """
                                    )


                                    for result in results:

                                        if result['matches']:

                                            detail = ''


                                            for allergy, matches in (
                                                result['matches'].items()
                                            ):

                                                detail += (
                                                    f'<div style="'
                                                    f'margin-top:10px;">'
                                                    f'<strong>'
                                                    f'{t["allergy_type"]}: '
                                                    f'{allergy}'
                                                    f'</strong><br>'
                                                    f'{t["found"]}: '
                                                    f'{", ".join(matches)}'
                                                    f'</div>'
                                                )


                                            st.html(
                                                f"""
                                                <div class="result-danger">

                                                    <div style="
                                                        font-size:21px;
                                                        font-weight:950;
                                                        color:#FF8585;
                                                    ">
                                                        ⚠️ {t['danger']}
                                                        {result['name']}
                                                    </div>

                                                    {detail}

                                                </div>
                                                """
                                            )


                                        else:

                                            st.html(
                                                f"""
                                                <div class="result-safe">

                                                    <div style="
                                                        font-size:19px;
                                                        font-weight:900;
                                                        color:#67F3B2;
                                                    ">
                                                        ✓ {t['safe']}
                                                        {result['name']}
                                                    </div>

                                                </div>
                                                """
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

        st.html(
            f"""
            <div style="height:20px;"></div>

            <div class="kicker">
                PERSONAL SAFETY PROFILE
            </div>

            <div class="section-title">
                {t['profile_title']}
            </div>

            <div class="section-desc">
                {t['profile_desc']}
            </div>
            """
        )


        current = get_user_allergies(
            user['id']
        )


        selected = st.multiselect(
            t['my_allergies'],
            ALLERGIES,
            default=current
        )


        if st.button(
            t['save'],
            use_container_width=True
        ):

            save_user_allergies(
                user['id'],
                selected
            )

            st.success(
                t['saved'] + ' ✓'
            )

            st.rerun()


        st.divider()


        st.html(
            f"""
            <div class="kicker">
                FAMILY PROTECTION
            </div>

            <div class="section-title">
                {t['family_title']}
            </div>

            <div class="section-desc">
                {t['family_desc']}
            </div>
            """
        )


        family = get_family_members(
            user['id']
        )


        if family:

            columns = st.columns(2)


            for index, member in enumerate(
                family
            ):

                with columns[index % 2]:

                    with st.container(
                        border=True
                    ):

                        st.html(
                            f"""
                            <div class="person-name">
                                {member['name']}
                            </div>

                            <div style="
                                color:#8A98A3;
                                margin:5px 0 10px;
                            ">
                                {member['relation']}
                            </div>
                            """
                        )


                        pills = ''.join(
                            f'<span class="pill">'
                            f'{allergy}'
                            f'</span>'
                            for allergy
                            in member['allergies']
                        )


                        st.html(
                            f"""
                            <div>
                                {pills}
                            </div>
                            """
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


        st.html(
            """
            <div style="height:30px;"></div>
            """
        )


        st.html(
            f"""
            <div class="glass">

                <div class="kicker">
                    NEW FAMILY MEMBER
                </div>

                <div class="section-title"
                     style="font-size:27px;">
                    ＋ {t['add_member']}
                </div>

            </div>
            """
        )


        col1, col2 = st.columns(2)


        with col1:

            member_name = st.text_input(
                t['member_name']
            )


        with col2:

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
            key='member_allergies'
        )


        if st.button(
            '＋ ' + t['add'],
            use_container_width=True
        ):

            if not member_name:

                st.warning(
                    t['enter_name']
                )


            elif not member_allergies:

                st.warning(
                    t['choose']
                )


            else:

                add_family_member(
                    user['id'],
                    member_name,
                    relation,
                    member_allergies
                )

                st.success(
                    '✓'
                )

                st.rerun()
