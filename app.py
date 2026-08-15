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
        'hero_2': 'المسبب',
        'hero_3': 'قبل لا يوصلك.',

        'hero_desc':
            'صوّر مكونات المنتج، وmosabb يحللها بالذكاء الاصطناعي '
            'ويقارنها بحساسيتك وحساسيات عائلتك.',

        'step1_title': 'صوّر',
        'step1_desc': 'صوّر قائمة مكونات المنتج',

        'step2_title': 'نحلل',
        'step2_desc': 'mosabb يقرأ ويحلل المكونات',

        'step3_title': 'اعرف',
        'step3_desc': 'نعطيك النتيجة لك ولعائلتك',

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
        'today': 'وش حاب تفحص اليوم؟',

        'scan_title': 'افحص منتجك',
        'scan_desc':
            'صوّر قائمة المكونات أو ارفع صورة واضحة لها، والباقي علينا.',

        'check_for': 'سيتم فحص المنتج للأشخاص التاليين',

        'camera': 'صوّر مكونات المنتج',
        'upload': 'أو ارفع صورة',

        'analyze': 'حلّل المنتج',

        'original': 'الصورة الأصلية',
        'detected': 'منطقة المكونات المكتشفة',
        'text': 'النص اللي قرأه mosabb',

        'processing': 'لحظة... mosabb يحلل المكونات 🔍',

        'no_label':
            'ما قدرنا نحدد قائمة المكونات. جرّب تصورها بشكل أوضح وأقرب.',

        'no_text':
            'حددنا مكان المكونات، لكن ما قدرنا نقرأ النص بشكل واضح.',

        'result': 'نتيجة الفحص',

        'safe_title': 'أمورك طيبة',
        'safe_text':
            'ما اكتشفنا أي مكوّن مرتبط بحساسيتك المسجلة.',

        'danger_title': 'انتبه',
        'danger_text':
            'هذا المنتج يحتوي على مكونات مرتبطة بحساسيتك.',

        'family_safe_title': 'أموره طيبة',
        'family_safe_text':
            'ما اكتشفنا أي مكوّن مرتبط بحساسيته المسجلة.',

        'family_danger_title': 'هذا المنتج مو مناسب لـ',
        'family_danger_text':
            'لقينا مكونات مرتبطة بحساسيته.',

        'allergy_type': 'الحساسية',
        'found': 'المكونات المكتشفة',

        'profile_title': 'ملفي الصحي',

        'profile_desc':
            'سجل حساسيتك مرة واحدة، وmosabb يتذكرها في كل فحص.',

        'my_allergies': 'حساسيتي',
        'save': 'حفظ حساسيتي',
        'saved': 'تم حفظ حساسيتك',

        'family_title': 'عائلتي',

        'family_desc':
            'أضف الأطفال أو أفراد العائلة، وmosabb يفحص المنتج للجميع بنفس اللحظة.',

        'no_family':
            'ما أضفت أحد للعائلة للحين. تقدر تستخدم mosabb لنفسك عادي.',

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
            'سجل حساسيتك أول من صفحة ملفي وعائلتي عشان نعرف وش نبحث عنه.',

        'fill': 'عب البيانات كلها.',
        'wrong': 'البريد الإلكتروني أو كلمة المرور غير صحيحة.',
        'used': 'البريد الإلكتروني مستخدم من قبل.',
        'created': 'تم إنشاء الحساب. تقدر تسجل دخولك الآن.',
        'choose': 'اختر حساسية واحدة على الأقل.',
        'enter_name': 'اكتب اسم الشخص.',

        'disclaimer':
            'النتيجة تعتمد على جودة الصورة ودقة قراءة المكونات. '
            'تأكد دائماً من تحذيرات الحساسية المكتوبة على العبوة.'
    },


    'EN': {
        'dir': 'ltr',

        'badge': 'Safety starts before the first bite',

        'hero_1': 'Know the',
        'hero_2': 'cause',
        'hero_3': 'before it reaches you.',

        'hero_desc':
            'Scan the ingredient label and let mosabb analyze it with AI '
            'against your allergy profile and your family.',

        'step1_title': 'Scan',
        'step1_desc': 'Capture the ingredient label',

        'step2_title': 'Analyze',
        'step2_desc': 'mosabb reads and checks the ingredients',

        'step3_title': 'Know',
        'step3_desc': 'Get a personalized result',

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
        'today': 'What are we checking today?',

        'scan_title': 'Scan your product',
        'scan_desc':
            'Take a clear photo of the ingredient label or upload one. We’ll handle the rest.',

        'check_for': 'This product will be checked for',

        'camera': 'Take a photo',
        'upload': 'Or upload an image',

        'analyze': 'Analyze Product',

        'original': 'Original image',
        'detected': 'Detected ingredients area',
        'text': 'What mosabb read',

        'processing': 'One moment... mosabb is checking the ingredients 🔍',

        'no_label':
            'We could not detect the ingredient label. Try a closer and clearer image.',

        'no_text':
            'We found the label, but could not read the text clearly.',

        'result': 'Scan Result',

        'safe_title': 'Looking good',
        'safe_text':
            'We did not detect any ingredient linked to your registered allergies.',

        'danger_title': 'Heads up',
        'danger_text':
            'This product contains ingredients linked to your registered allergies.',

        'family_safe_title': 'Looking good',
        'family_safe_text':
            'We did not detect anything linked to their registered allergies.',

        'family_danger_title': 'This product may not be suitable for',
        'family_danger_text':
            'We found ingredients linked to their registered allergies.',

        'allergy_type': 'Allergy',
        'found': 'Detected ingredients',

        'profile_title': 'My Health Profile',

        'profile_desc':
            'Save your allergies once and mosabb remembers them for every scan.',

        'my_allergies': 'My allergies',
        'save': 'Save my allergies',
        'saved': 'Your allergies have been saved',

        'family_title': 'My Family',

        'family_desc':
            'Add children or family members and check one product for everyone at once.',

        'no_family':
            'No family members added yet. You can still use mosabb for yourself.',

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
            'Add your allergies first so mosabb knows what to look for.',

        'fill': 'Please fill in all fields.',
        'wrong': 'Incorrect email or password.',
        'used': 'This email is already registered.',
        'created': 'Account created. You can now log in.',
        'choose': 'Select at least one allergy.',
        'enter_name': 'Enter the person’s name.',

        'disclaimer':
            'Results depend on image quality and ingredient reading accuracy. '
            'Always check the allergy warnings printed on the product.'
    }
}


t = translations[st.session_state.language]


# =========================================================
# CSS
# =========================================================

css = """
<style>

:root {
    --green: #31F2A0;
    --aqua: #63D7FF;
    --bg: #060B0F;
    --card: rgba(15,22,28,.82);
    --border: rgba(255,255,255,.075);
    --muted: #8C99A4;
    --red: #FF6969;
}

.stApp {
    direction: __DIR__;
    background:
        radial-gradient(circle at 8% 5%, rgba(49,242,160,.12), transparent 27%),
        radial-gradient(circle at 94% 6%, rgba(65,115,255,.10), transparent 23%),
        linear-gradient(150deg, #06100C 0%, #070C11 48%, #080A10 100%);
    color: #F7FAFB;
}

.block-container {
    max-width: 1160px;
    padding-top: 1.35rem;
    padding-bottom: 5rem;
}

#MainMenu {
    visibility: hidden;
}

footer {
    visibility: hidden;
}

header {
    background: transparent !important;
}

/* logo */

.logo {
    font-size: 31px;
    font-weight: 950;
    letter-spacing: -1.5px;
}

.logo-dot {
    color: var(--green);
}

/* hero */

.hero {
    padding: 65px 0 48px 0;
}

.hero-badge {
    display: inline-block;
    padding: 9px 16px;
    border-radius: 999px;
    background: rgba(49,242,160,.07);
    border: 1px solid rgba(49,242,160,.23);
    color: #72F8BC;
    font-size: 14px;
    font-weight: 800;
    margin-bottom: 25px;
}

.hero-title {
    font-size: clamp(53px, 7vw, 90px);
    line-height: .98;
    letter-spacing: -4.5px;
    font-weight: 950;
    max-width: 920px;
    margin: 0;
}

.gradient {
    background: linear-gradient(90deg, var(--green), var(--aqua));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-desc {
    margin-top: 28px;
    max-width: 730px;
    color: #99A6AF;
    line-height: 1.8;
    font-size: 18px;
}

/* section */

.kicker {
    color: var(--green);
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 1.5px;
    margin-bottom: 8px;
}

.section-title {
    font-size: 35px;
    font-weight: 950;
    letter-spacing: -1px;
    margin-bottom: 7px;
}

.section-desc {
    color: var(--muted);
    line-height: 1.7;
    margin-bottom: 24px;
}

/* cards */

.glass {
    padding: 28px;
    border-radius: 25px;
    background:
        linear-gradient(
            145deg,
            rgba(18,28,33,.92),
            rgba(10,16,21,.82)
        );
    border: 1px solid var(--border);
    box-shadow: 0 30px 100px rgba(0,0,0,.28);
    backdrop-filter: blur(18px);
}

.soft-card {
    padding: 18px 20px;
    border-radius: 17px;
    background: rgba(255,255,255,.025);
    border: 1px solid var(--border);
    margin-bottom: 10px;
}

.person-name {
    font-size: 18px;
    font-weight: 900;
}

.person-allergy {
    color: #FF9696;
    margin-top: 5px;
    font-size: 14px;
}

/* how it works */

.step-card {
    padding: 22px;
    border-radius: 19px;
    background: rgba(255,255,255,.025);
    border: 1px solid var(--border);
    min-height: 145px;
}

.step-number {
    color: var(--green);
    font-size: 12px;
    font-weight: 900;
    letter-spacing: 1px;
    margin-bottom: 16px;
}

.step-title {
    font-size: 22px;
    font-weight: 900;
    margin-bottom: 6px;
}

.step-desc {
    color: var(--muted);
    line-height: 1.6;
    font-size: 14px;
}

/* pills */

.pill {
    display: inline-block;
    padding: 7px 12px;
    margin: 4px;
    border-radius: 999px;
    background: rgba(255,90,90,.08);
    border: 1px solid rgba(255,90,90,.15);
    color: #FF9696;
    font-size: 13px;
    font-weight: 800;
}

/* result cards */

.safe-result {
    position: relative;
    overflow: hidden;
    padding: 30px;
    border-radius: 25px;
    margin: 18px 0;
    background:
        radial-gradient(circle at 92% 15%, rgba(49,242,160,.23), transparent 30%),
        linear-gradient(135deg, rgba(49,242,160,.11), rgba(49,242,160,.025));
    border: 1px solid rgba(49,242,160,.25);
}

.danger-result {
    position: relative;
    overflow: hidden;
    padding: 30px;
    border-radius: 25px;
    margin: 18px 0;
    background:
        radial-gradient(circle at 92% 15%, rgba(255,95,95,.22), transparent 30%),
        linear-gradient(135deg, rgba(255,80,80,.13), rgba(255,80,80,.025));
    border: 1px solid rgba(255,90,90,.28);
}

.result-status-safe {
    color: #62F3AF;
    font-size: 12px;
    font-weight: 950;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}

.result-status-danger {
    color: #FF8585;
    font-size: 12px;
    font-weight: 950;
    letter-spacing: 1.5px;
    margin-bottom: 12px;
}

.result-title {
    font-size: 31px;
    font-weight: 950;
    letter-spacing: -.7px;
    margin-bottom: 8px;
}

.result-text {
    color: #A2ADB5;
    font-size: 16px;
    line-height: 1.7;
}

.result-detail {
    margin-top: 20px;
    padding: 16px 18px;
    border-radius: 15px;
    background: rgba(0,0,0,.18);
    border: 1px solid rgba(255,255,255,.06);
}

/* buttons */

.stButton > button {
    min-height: 49px;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,.09);
    background: #111B21;
    font-weight: 850;
    transition: all .2s ease;
}

.stButton > button:hover {
    transform: translateY(-1px);
    border-color: var(--green) !important;
    color: var(--green) !important;
    box-shadow: 0 12px 30px rgba(49,242,160,.08);
}

/* inputs */

.stTextInput input {
    background: #0D151A !important;
    min-height: 49px;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,.08) !important;
}

[data-baseweb="select"] > div {
    background: #0D151A !important;
    border-radius: 14px !important;
    border-color: rgba(255,255,255,.08) !important;
}

/* uploader */

[data-testid="stFileUploaderDropzone"] {
    min-height: 180px;
    border-radius: 21px;
    background: rgba(49,242,160,.022);
    border: 1px dashed rgba(49,242,160,.27);
}

/* tabs */

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    padding: 10px 17px;
    border-radius: 11px;
    font-weight: 800;
}

.stTabs [aria-selected="true"] {
    color: var(--green) !important;
    background: rgba(49,242,160,.08) !important;
}

[data-testid="stAlert"] {
    border-radius: 16px;
}

@media (max-width: 700px) {

    .hero {
        padding-top: 35px;
    }

    .hero-title {
        letter-spacing: -2.5px;
    }

    .hero-desc {
        font-size: 16px;
    }

    .section-title {
        font-size: 28px;
    }

    .glass {
        padding: 21px;
    }

    .result-title {
        font-size: 25px;
    }
}

</style>
"""

css = css.replace(
    '__DIR__',
    t['dir']
)

st.html(css)


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
        'sesame seeds',
        'tahini',
        'سمسم',
        'بذور السمسم',
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
        'almonds',
        'walnut',
        'walnuts',
        'cashew',
        'cashews',
        'pistachio',
        'pistachios',
        'hazelnut',
        'hazelnuts',
        'pecan',
        'macadamia',
        'لوز',
        'اللوز',
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

    results = reader.readtext(
        np.array(image),
        detail=0,
        paragraph=True
    )

    return ' '.join(results)


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

    results = []


    for person in people:

        matches = {}


        for allergy in person['allergies']:

            detected = find_matches(
                text,
                allergy
            )


            if detected:

                matches[allergy] = detected


        results.append({
            'name': person['name'],
            'is_owner': person.get(
                'is_owner',
                False
            ),
            'matches': matches
        })


    return results


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
        <div class="logo">
            mosabb<span class="logo-dot">.</span>
        </div>
        """
    )


with lang_col:

    language = st.segmented_control(
        'Language',
        [
            'العربية',
            'English'
        ],
        default=(
            'العربية'
            if st.session_state.language == 'AR'
            else 'English'
        ),
        label_visibility='collapsed'
    )


    new_language = (
        'AR'
        if language == 'العربية'
        else 'EN'
    )


    if new_language != st.session_state.language:

        st.session_state.language = new_language

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
        [
            0.95,
            1.05
        ],
        gap='large'
    )


    with info_col:

        st.html(
            f"""
            <div class="glass">

                <div class="kicker">
                    HOW IT WORKS
                </div>

                <div class="section-title">
                    Simple. Personal. Fast.
                </div>

                <div class="section-desc">
                    mosabb turns a product label into a personalized
                    allergy check in three simple steps.
                </div>

            </div>
            """
        )


        step_cols = st.columns(3)


        with step_cols[0]:

            st.html(
                f"""
                <div class="step-card">

                    <div class="step-number">
                        01
                    </div>

                    <div class="step-title">
                        {t['step1_title']}
                    </div>

                    <div class="step-desc">
                        {t['step1_desc']}
                    </div>

                </div>
                """
            )


        with step_cols[1]:

            st.html(
                f"""
                <div class="step-card">

                    <div class="step-number">
                        02
                    </div>

                    <div class="step-title">
                        {t['step2_title']}
                    </div>

                    <div class="step-desc">
                        {t['step2_desc']}
                    </div>

                </div>
                """
            )


        with step_cols[2]:

            st.html(
                f"""
                <div class="step-card">

                    <div class="step-number">
                        03
                    </div>

                    <div class="step-title">
                        {t['step3_title']}
                    </div>

                    <div class="step-desc">
                        {t['step3_desc']}
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
                use_container_width=True,
                key='login'
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
                use_container_width=True,
                key='register'
            ):

                if (
                    not name
                    or not email
                    or not password
                ):

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
# LOGGED IN
# =========================================================

else:

    user = st.session_state.user


    greeting_col, logout_col = st.columns(
        [
            8,
            2
        ],
        vertical_alignment='center'
    )


    with greeting_col:

        st.html(
            f"""
            <div class="soft-card">

                <div style="
                    color:#8C99A4;
                    font-size:13px;
                    margin-bottom:3px;
                ">
                    {t['welcome']} {user['name']} 👋
                </div>

                <div style="
                    font-size:20px;
                    font-weight:900;
                ">
                    {t['today']}
                </div>

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
            <div style="height:22px;"></div>

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
                'allergies': my_allergies,
                'is_owner': True
            })


        for member in family:

            people.append({
                'name': member['name'],
                'allergies': member['allergies'],
                'is_owner': False
            })


        if not people:

            st.warning(
                t['need_allergy']
            )


        else:

            st.html(
                f"""
                <div style="
                    color:#8C99A4;
                    font-size:14px;
                    margin-bottom:12px;
                ">
                    {t['check_for']}
                </div>
                """
            )


            person_columns = st.columns(
                min(
                    len(people),
                    3
                )
            )


            for index, person in enumerate(
                people
            ):

                with person_columns[
                    index % len(person_columns)
                ]:

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


            st.html(
                """
                <div style="height:12px;"></div>
                """
            )


            camera_col, upload_col = st.columns(
                2,
                gap='large'
            )


            with camera_col:

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
                    use_container_width=True,
                    key='analyze'
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
                                            margin-top:28px;
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

                                        st.write(
                                            text
                                        )


                                    results = check_people(
                                        text,
                                        people
                                    )


                                    st.html(
                                        f"""
                                        <div style="height:24px;"></div>

                                        <div class="kicker">
                                            MOSABB RESULT
                                        </div>

                                        <div class="section-title">
                                            {t['result']}
                                        </div>
                                        """
                                    )


                                    for result in results:

                                        # ==================
                                        # DANGER
                                        # ==================

                                        if result['matches']:

                                            details = ''


                                            for allergy, matches in (
                                                result['matches'].items()
                                            ):

                                                details += f"""
                                                <div class="result-detail">

                                                    <div style="
                                                        color:#A7B0B7;
                                                        font-size:13px;
                                                        margin-bottom:5px;
                                                    ">
                                                        {t['allergy_type']}
                                                    </div>

                                                    <div style="
                                                        font-size:18px;
                                                        font-weight:900;
                                                        margin-bottom:10px;
                                                    ">
                                                        {allergy}
                                                    </div>

                                                    <div style="
                                                        color:#FF9A9A;
                                                        font-size:14px;
                                                    ">
                                                        {t['found']}:
                                                        <strong>
                                                            {', '.join(matches)}
                                                        </strong>
                                                    </div>

                                                </div>
                                                """


                                            if result['is_owner']:

                                                title = (
                                                    f"{t['danger_title']} "
                                                    f"{result['name']} ⚠️"
                                                )

                                                description = t[
                                                    'danger_text'
                                                ]


                                            else:

                                                title = (
                                                    f"{t['family_danger_title']} "
                                                    f"{result['name']} ⚠️"
                                                )

                                                description = t[
                                                    'family_danger_text'
                                                ]


                                            st.html(
                                                f"""
                                                <div class="danger-result">

                                                    <div class="result-status-danger">
                                                        ALLERGY ALERT
                                                    </div>

                                                    <div class="result-title">
                                                        {title}
                                                    </div>

                                                    <div class="result-text">
                                                        {description}
                                                    </div>

                                                    {details}

                                                </div>
                                                """
                                            )


                                        # ==================
                                        # SAFE
                                        # ==================

                                        else:

                                            if result['is_owner']:

                                                title = (
                                                    f"{t['safe_title']} "
                                                    f"{result['name']} ✨"
                                                )

                                                description = t[
                                                    'safe_text'
                                                ]


                                            else:

                                                title = (
                                                    f"{result['name']} "
                                                    f"{t['family_safe_title']} ✨"
                                                )

                                                description = t[
                                                    'family_safe_text'
                                                ]


                                            st.html(
                                                f"""
                                                <div class="safe-result">

                                                    <div class="result-status-safe">
                                                        LOOKING GOOD
                                                    </div>

                                                    <div class="result-title">
                                                        {title}
                                                    </div>

                                                    <div class="result-text">
                                                        {description}
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
            <div style="height:22px;"></div>

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
            default=current,
            key='my_allergy_select'
        )


        if st.button(
            t['save'],
            use_container_width=True,
            key='save_allergies'
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

                with columns[
                    index % 2
                ]:

                    with st.container(
                        border=True
                    ):

                        st.html(
                            f"""
                            <div class="person-name">
                                {member['name']}
                            </div>

                            <div style="
                                color:#8C99A4;
                                margin:5px 0 11px;
                            ">
                                {member['relation']}
                            </div>
                            """
                        )


                        pills = ''.join(
                            f"""
                            <span class="pill">
                                {allergy}
                            </span>
                            """
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


        first_col, second_col = st.columns(
            2
        )


        with first_col:

            member_name = st.text_input(
                t['member_name'],
                key='member_name'
            )


        with second_col:

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
            key='member_allergies'
        )


        if st.button(
            '＋ ' + t['add'],
            use_container_width=True,
            key='add_member'
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
