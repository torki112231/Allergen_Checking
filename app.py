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

if 'page' not in st.session_state:
    st.session_state.page = 'scan'


# =========================================================
# TRANSLATIONS
# =========================================================

translations = {

    'AR': {
        'dir': 'rtl',

        'hero_1': 'افحص قبل',
        'hero_2': 'ما تتحسس',

        'hero_desc':
            'صورة وحدة تكفي. مسبب يقرأ مكونات المنتج ويقارنها '
            'بحساسيتك وحساسيات أفراد عائلتك.',

        'main_card_title':
            'فحص واحد، ونتيجة مخصصة لك ولعائلتك',

        'main_card_desc':
            'مسبب يقارن مكونات المنتج بحساسية كل شخص مسجل عندك، '
            'ويعطيك تنبيه واضح قبل الاستخدام.',

        'step1': 'صوّر',
        'step2': 'نفحصلك',
        'step3': 'تتطمن',

        'login': 'تسجيل الدخول',
        'register': 'إنشاء حساب',

        'login_title': 'مرحباً بعودتك 👋',
        'login_desc':
            'سجل دخولك وكمل فحص منتجاتك.',

        'register_title': 'ابدأ مع مسبب',
        'register_desc':
            'أنشئ حسابك وسجل حساسيتك مرة وحدة.',

        'name': 'الاسم',
        'email': 'البريد الإلكتروني',
        'password': 'كلمة المرور',

        'enter': 'دخول',
        'create': 'إنشاء الحساب',
        'logout': 'تسجيل الخروج',

        'hello': 'ياهلا',
        'today': 'وش حاب تفحص اليوم؟',

        'scan_nav': '📷 افحص',
        'profile_nav': '👤 ملفي',
        'family_nav': '👨‍👩‍👧 عائلتي',

        'scan_title': 'صوّر المنتج وخله علينا',
        'scan_desc':
            'صوّر قائمة المكونات أو ارفع صورة واضحة، '
            'ومسبب يقارنها بالحساسيات المسجلة.',

        'check_for':
            'راح نفحص هذا المنتج لـ:',

        'camera': 'صوّر المكونات',
        'upload': 'أو ارفع صورة',
        'analyze': 'افحص المنتج',

        'original': 'الصورة الأصلية',
        'detected': 'قائمة المكونات اللي اكتشفناها',
        'ocr_text': 'النص اللي قرأه مسبب',

        'processing':
            'ثواني... مسبب قاعد يفحص المكونات 🔍',

        'no_label':
            'ما قدرنا نحدد قائمة المكونات. جرّب صورة أوضح وأقرب.',

        'no_text':
            'لقينا قائمة المكونات، لكن النص مو واضح كفاية للقراءة.',

        'result': 'نتيجة الفحص',

        'safe_title': 'أمورك طيبة',
        'safe_text':
            'ما لقينا في المكونات المقروءة أي شيء مرتبط بحساسيتك المسجلة.',

        'danger_title': 'انتبه',
        'danger_text':
            'لقينا في هذا المنتج مكونات مرتبطة بحساسيتك المسجلة.',

        'family_safe_title': 'أموره طيبة',
        'family_safe_text':
            'ما لقينا أي شيء مرتبط بحساسيته المسجلة.',

        'family_danger_title':
            'هذا المنتج مو مناسب لـ',

        'family_danger_text':
            'لقينا مكونات مرتبطة بحساسيته المسجلة.',

        'allergy_type': 'الحساسية',
        'found': 'المكونات اللي لقيناها',

        'profile_title': 'ملفي',
        'profile_subtitle':
            'هنا بياناتك وحساسيتك أنت، ومسبب يستخدمها تلقائياً في كل فحص.',

        'account_info': 'بيانات الحساب',

        'my_allergies':
            'وش عندك حساسية منه؟',

        'save':
            'حفظ الحساسية',

        'saved':
            'تم حفظ حساسيتك',

        'family_title':
            'عائلتي',

        'family_subtitle':
            'أضف أفراد عائلتك وحساسية كل شخص، '
            'وبعدها نفس المنتج ينفحص للجميع.',

        'no_family':
            'ما أضفت أحد للحين. تقدر تستخدم مسبب لنفسك عادي.',

        'add_member':
            'إضافة فرد للعائلة',

        'member_name':
            'اسم الشخص',

        'relation':
            'صلة القرابة',

        'member_allergies':
            'وش عنده حساسية منه؟',

        'add':
            'إضافة',

        'delete':
            'حذف',

        'son': 'ابن',
        'daughter': 'ابنة',
        'mother': 'أم',
        'father': 'أب',
        'brother': 'أخ',
        'sister': 'أخت',
        'other': 'أخرى',

        'need_allergy':
            'سجل حساسيتك أول من صفحة ملفي عشان مسبب يعرف وش يبحث عنه.',

        'fill':
            'عب البيانات كلها أول.',

        'wrong':
            'الإيميل أو كلمة المرور مو صحيحة.',

        'used':
            'هذا البريد مسجل من قبل.',

        'created':
            'تم إنشاء الحساب، تقدر تسجل دخولك الحين.',

        'choose':
            'اختر حساسية واحدة على الأقل.',

        'enter_name':
            'اكتب اسم الشخص أول.',

        'disclaimer':
            'مسبب أداة مساعدة، والنتيجة تعتمد على جودة الصورة ودقة قراءة المكونات. '
            'تأكد دائماً من تحذيرات الحساسية الموجودة على العبوة.'
    },


    'EN': {
        'dir': 'ltr',

        'hero_1': 'Check before',
        'hero_2': 'you react',

        'hero_desc':
            'One photo is enough. mosabb reads the ingredients and checks '
            'them against your allergies and your family profiles.',

        'main_card_title':
            'One scan. Personalized for you and your family.',

        'main_card_desc':
            'mosabb compares product ingredients with every saved allergy profile '
            'and gives you a clear warning before use.',

        'step1': 'Capture',
        'step2': 'We check',
        'step3': 'Feel sure',

        'login': 'Log in',
        'register': 'Create account',

        'login_title': 'Welcome back 👋',
        'login_desc':
            'Sign in and continue checking products.',

        'register_title': 'Start with mosabb',
        'register_desc':
            'Create an account and save your allergies once.',

        'name': 'Name',
        'email': 'Email',
        'password': 'Password',

        'enter': 'Log in',
        'create': 'Create account',
        'logout': 'Log out',

        'hello': 'Hey',
        'today': 'What are we checking today?',

        'scan_nav': '📷 Scan',
        'profile_nav': '👤 My Profile',
        'family_nav': '👨‍👩‍👧 My Family',

        'scan_title': 'Take a photo. We’ll handle the rest.',
        'scan_desc':
            'Capture the ingredient label or upload a clear image. '
            'mosabb compares it with your saved allergy profiles.',

        'check_for':
            'We’ll check this product for:',

        'camera': 'Take a photo',
        'upload': 'Or upload an image',
        'analyze': 'Check Product',

        'original': 'Original image',
        'detected': 'Ingredient label detected',
        'ocr_text': 'What mosabb read',

        'processing':
            'One moment... mosabb is checking the ingredients 🔍',

        'no_label':
            'We could not detect the ingredient label. Try a clearer photo.',

        'no_text':
            'We found the label, but the text was not clear enough to read.',

        'result': 'Scan Result',

        'safe_title': 'You’re in the clear',
        'safe_text':
            'We did not find anything in the ingredients we read '
            'that matches your saved allergies.',

        'danger_title': 'Heads up',
        'danger_text':
            'We found ingredients in this product that match your saved allergies.',

        'family_safe_title': 'Looks clear',
        'family_safe_text':
            'We did not find anything linked to their saved allergies.',

        'family_danger_title':
            'This product may not be suitable for',

        'family_danger_text':
            'We found ingredients linked to their saved allergies.',

        'allergy_type': 'Allergy',
        'found': 'Ingredients found',

        'profile_title': 'My Profile',
        'profile_subtitle':
            'Your personal allergy information lives here. '
            'mosabb automatically uses it in every scan.',

        'account_info':
            'Account information',

        'my_allergies':
            'What are you allergic to?',

        'save':
            'Save allergies',

        'saved':
            'Your allergies have been saved',

        'family_title':
            'My Family',

        'family_subtitle':
            'Add family members and their allergies, '
            'then check the same product for everyone.',

        'no_family':
            'No family members yet. You can still use mosabb for yourself.',

        'add_member':
            'Add family member',

        'member_name':
            'Name',

        'relation':
            'Relation',

        'member_allergies':
            'What are they allergic to?',

        'add':
            'Add',

        'delete':
            'Delete',

        'son': 'Son',
        'daughter': 'Daughter',
        'mother': 'Mother',
        'father': 'Father',
        'brother': 'Brother',
        'sister': 'Sister',
        'other': 'Other',

        'need_allergy':
            'Save your allergies in My Profile before scanning.',

        'fill':
            'Please fill in all fields.',

        'wrong':
            'Incorrect email or password.',

        'used':
            'This email is already registered.',

        'created':
            'Account created. You can log in now.',

        'choose':
            'Select at least one allergy.',

        'enter_name':
            'Enter the person’s name first.',

        'disclaimer':
            'mosabb is an assistive tool. Results depend on image quality '
            'and ingredient-reading accuracy. Always check the allergy warnings on the package.'
    }
}


t = translations[
    st.session_state.language
]


# =========================================================
# CSS
# =========================================================

css = """
<style>

:root {
    --green: #35F29E;
    --cyan: #55D8FF;
    --border: rgba(255,255,255,.075);
    --muted: #909DA7;
}

.stApp {
    direction: __DIR__;

    background:
        radial-gradient(
            circle at 5% 7%,
            rgba(53,242,158,.11),
            transparent 27%
        ),
        radial-gradient(
            circle at 95% 3%,
            rgba(67,116,255,.10),
            transparent 24%
        ),
        linear-gradient(
            145deg,
            #06100C 0%,
            #070C11 50%,
            #070A10 100%
        );

    color: #F8FAFB;
}

.block-container {
    max-width: 1180px;
    padding-top: 1.3rem;
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


/* LOGO */

.logo {
    font-size: 33px;
    font-weight: 950;
    letter-spacing: -1.7px;
}


/* HERO */

.hero {
    padding: 75px 0 55px 0;
}

.hero-title {
    font-size: clamp(58px, 7.5vw, 96px);
    line-height: .96;
    letter-spacing: -5px;
    font-weight: 950;
    max-width: 950px;
    margin: 0;
}

.gradient {
    background:
        linear-gradient(
            90deg,
            var(--green),
            var(--cyan)
        );

    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.hero-desc {
    margin-top: 28px;
    max-width: 760px;
    color: #9DA9B2;
    line-height: 1.85;
    font-size: 18px;
}


/* FEATURE CARD */

.feature-card {
    padding: 30px;
    border-radius: 26px;

    background:
        radial-gradient(
            circle at 10% 15%,
            rgba(53,242,158,.10),
            transparent 35%
        ),
        linear-gradient(
            145deg,
            rgba(17,27,32,.94),
            rgba(9,15,20,.88)
        );

    border:
        1px solid rgba(53,242,158,.14);

    margin-bottom: 16px;
}

.feature-icon {
    width: 58px;
    height: 58px;

    border-radius: 18px;

    display: flex;
    align-items: center;
    justify-content: center;

    font-size: 29px;

    background:
        rgba(53,242,158,.08);

    border:
        1px solid rgba(53,242,158,.18);

    margin-bottom: 22px;
}

.feature-title {
    font-size: 29px;
    font-weight: 950;
    line-height: 1.25;
    letter-spacing: -.7px;
    margin-bottom: 10px;
}

.feature-desc {
    color: var(--muted);
    line-height: 1.75;
}


/* HOME 3 STEPS */

.step-card {
    min-height: 145px;

    padding: 22px;

    border-radius: 22px;

    display: flex;

    flex-direction: column;

    align-items: center;

    justify-content: center;

    text-align: center;

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.035),
            rgba(255,255,255,.012)
        );

    border:
        1px solid var(--border);
}

.step-icon {
    font-size: 31px;
    margin-bottom: 11px;
}

.step-word {
    font-size: 23px;
    font-weight: 950;
}


/* PAGE HEADER */

.page-head {
    margin-top: 30px;
    margin-bottom: 27px;
}

.page-title {
    font-size: 38px;
    font-weight: 950;
    letter-spacing: -1px;
    margin-bottom: 7px;
}

.page-desc {
    color: var(--muted);
    font-size: 16px;
    line-height: 1.75;
    max-width: 760px;
}


/* USER CARD */

.user-card {
    padding: 18px 21px;

    border-radius: 19px;

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.035),
            rgba(255,255,255,.015)
        );

    border:
        1px solid var(--border);
}

.user-small {
    font-size: 13px;
    color: #8997A1;
    margin-bottom: 3px;
}

.user-big {
    font-size: 21px;
    font-weight: 900;
}


/* =====================================================
   NAVIGATION — ALL 3 EXACTLY SAME SIZE
===================================================== */

div[role="radiogroup"] {
    display: grid !important;

    grid-template-columns:
        repeat(3, minmax(0, 1fr)) !important;

    gap: 14px !important;

    width: 100% !important;

    margin-top: 18px !important;
}

div[role="radiogroup"] label {
    width: 100% !important;
    min-width: 0 !important;
    max-width: none !important;

    height: 118px !important;

    box-sizing: border-box !important;

    display: flex !important;
    align-items: center !important;
    justify-content: center !important;

    margin: 0 !important;

    padding: 16px 12px !important;

    border-radius: 23px !important;

    background:
        linear-gradient(
            145deg,
            rgba(255,255,255,.035),
            rgba(255,255,255,.012)
        ) !important;

    border:
        1px solid rgba(255,255,255,.08) !important;

    transition:
        all .2s ease !important;
}

div[role="radiogroup"] label > div {
    width: 100% !important;
    height: 100% !important;

    display: flex !important;

    align-items: center !important;
    justify-content: center !important;

    text-align: center !important;

    padding: 0 !important;
    margin: 0 !important;
}

div[role="radiogroup"] label p {
    width: 100% !important;

    margin: 0 !important;

    padding: 0 !important;

    font-size: 20px !important;

    line-height: 1.3 !important;

    font-weight: 900 !important;

    text-align: center !important;

    white-space: normal !important;
}

div[role="radiogroup"] label:hover {
    transform:
        translateY(-2px);

    border-color:
        rgba(53,242,158,.30) !important;

    background:
        rgba(53,242,158,.035) !important;
}

div[role="radiogroup"] label:has(input:checked) {
    background:
        radial-gradient(
            circle at 50% 15%,
            rgba(53,242,158,.15),
            transparent 75%
        ),
        linear-gradient(
            145deg,
            rgba(53,242,158,.11),
            rgba(53,242,158,.035)
        ) !important;

    border-color:
        rgba(53,242,158,.40) !important;

    box-shadow:
        0 15px 45px rgba(0,0,0,.19) !important;
}

div[role="radiogroup"] input {
    display: none !important;
}


/* CONTENT CARD */

.content-card {
    padding: 27px;

    border-radius: 24px;

    background:
        linear-gradient(
            145deg,
            rgba(17,25,31,.90),
            rgba(10,16,21,.82)
        );

    border:
        1px solid var(--border);

    margin-bottom: 16px;
}

.card-title {
    font-size: 23px;
    font-weight: 900;
    margin-bottom: 7px;
}

.card-desc {
    color: var(--muted);
    line-height: 1.7;
}


/* PROFILE */

.profile-name {
    font-size: 33px;
    font-weight: 950;
    letter-spacing: -.7px;
}

.profile-email {
    color: var(--muted);
    margin-top: 5px;
}


/* PERSON */

.person-card {
    padding: 23px;

    border-radius: 22px;

    background:
        rgba(255,255,255,.025);

    border:
        1px solid var(--border);

    margin-bottom: 12px;
}

.person-name {
    font-size: 22px;
    font-weight: 950;
}

.person-relation {
    color: #8996A0;
    margin-top: 3px;
    margin-bottom: 12px;
}

.person-allergy {
    color: #FF9898;
}


/* PILLS */

.pill {
    display: inline-block;

    padding: 7px 12px;

    margin: 4px;

    border-radius: 999px;

    background:
        rgba(255,90,90,.08);

    border:
        1px solid rgba(255,90,90,.15);

    color: #FF9696;

    font-size: 13px;
    font-weight: 800;
}


/* RESULTS */

.safe-result {
    padding: 31px;

    border-radius: 26px;

    margin: 18px 0;

    background:
        radial-gradient(
            circle at 92% 15%,
            rgba(53,242,158,.23),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            rgba(53,242,158,.11),
            rgba(53,242,158,.025)
        );

    border:
        1px solid rgba(53,242,158,.25);
}

.danger-result {
    padding: 31px;

    border-radius: 26px;

    margin: 18px 0;

    background:
        radial-gradient(
            circle at 92% 15%,
            rgba(255,95,95,.23),
            transparent 30%
        ),
        linear-gradient(
            135deg,
            rgba(255,80,80,.13),
            rgba(255,80,80,.025)
        );

    border:
        1px solid rgba(255,90,90,.28);
}

.result-status-safe {
    color: #64F4B1;
    font-size: 12px;
    font-weight: 950;
    letter-spacing: 1.5px;
    margin-bottom: 13px;
}

.result-status-danger {
    color: #FF8585;
    font-size: 12px;
    font-weight: 950;
    letter-spacing: 1.5px;
    margin-bottom: 13px;
}

.result-title {
    font-size: 32px;
    font-weight: 950;
    letter-spacing: -.8px;
    margin-bottom: 9px;
}

.result-text {
    color: #A4AFB7;
    font-size: 16px;
    line-height: 1.75;
}

.result-detail {
    margin-top: 20px;

    padding: 17px 19px;

    border-radius: 16px;

    background:
        rgba(0,0,0,.18);

    border:
        1px solid rgba(255,255,255,.06);
}


/* BUTTON */

.stButton > button {
    min-height: 49px;

    border-radius:
        14px !important;

    border:
        1px solid rgba(255,255,255,.09);

    background:
        #111B21;

    font-weight: 850;

    transition:
        all .2s ease;
}

.stButton > button:hover {
    transform:
        translateY(-1px);

    border-color:
        var(--green) !important;

    color:
        var(--green) !important;
}


/* INPUT */

.stTextInput input {
    background:
        #0D151A !important;

    min-height:
        49px;

    border-radius:
        14px !important;

    border:
        1px solid rgba(255,255,255,.08) !important;
}

[data-baseweb="select"] > div {
    background:
        #0D151A !important;

    border-radius:
        14px !important;

    border-color:
        rgba(255,255,255,.08) !important;
}


/* UPLOAD */

[data-testid="stFileUploaderDropzone"] {
    min-height:
        180px;

    border-radius:
        21px;

    background:
        rgba(53,242,158,.022);

    border:
        1px dashed rgba(53,242,158,.27);
}


/* LOGIN TABS */

.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
}

.stTabs [data-baseweb="tab"] {
    padding:
        10px 17px;

    border-radius:
        11px;

    font-weight:
        800;
}

.stTabs [aria-selected="true"] {
    color:
        var(--green) !important;

    background:
        rgba(53,242,158,.08) !important;
}


[data-testid="stAlert"] {
    border-radius: 16px;
}


/* MOBILE */

@media (max-width: 700px) {

    .hero {
        padding-top: 40px;
    }

    .hero-title {
        letter-spacing: -2.8px;
    }

    .hero-desc {
        font-size: 16px;
    }

    .page-title {
        font-size: 30px;
    }

    .result-title {
        font-size: 25px;
    }

    div[role="radiogroup"] {
        grid-template-columns:
            repeat(3, minmax(0, 1fr)) !important;

        gap: 7px !important;
    }

    div[role="radiogroup"] label {
        height: 92px !important;

        padding:
            10px 5px !important;
    }

    div[role="radiogroup"] label p {
        font-size:
            15px !important;
    }
}

</style>
"""


css = css.replace(
    '__DIR__',
    t['dir']
)

st.html(
    css
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
        [
            'ar',
            'en'
        ],
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


    if (
        boxes is None
        or len(boxes) == 0
    ):

        return None


    best_box = max(
        boxes,
        key=lambda box:
            float(
                box.conf[0]
            )
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


    return ' '.join(
        results
    )


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

            matches.append(
                keyword
            )

            continue


        if len(key) <= 4:

            continue


        for word in cleaned:

            if fuzz.ratio(
                word,
                key
            ) >= 88:

                matches.append(
                    keyword
                )

                break


    return list(
        set(matches)
    )


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

                matches[
                    allergy
                ] = detected


        results.append({
            'name':
                person['name'],

            'is_owner':
                person.get(
                    'is_owner',
                    False
                ),

            'matches':
                matches
        })


    return results


# =========================================================
# HEADER
# =========================================================

logo_col, lang_col = st.columns(
    [
        7,
        3
    ],
    vertical_alignment='center'
)


with logo_col:

    st.html(
        """
        <div class="logo">
            mosabb
        </div>
        """
    )


with lang_col:

    ar_col, en_col = st.columns(
        2
    )


    with ar_col:

        if st.button(
            'العربية',
            use_container_width=True,
            key='arabic_language'
        ):

            st.session_state.language = 'AR'

            st.rerun()


    with en_col:

        if st.button(
            'English',
            use_container_width=True,
            key='english_language'
        ):

            st.session_state.language = 'EN'

            st.rerun()


# =========================================================
# NOT LOGGED IN
# =========================================================

if st.session_state.user is None:

    st.html(
        f"""
        <section class="hero">

            <h1 class="hero-title">

                {t['hero_1']}

                <span class="gradient">
                    {t['hero_2']}
                </span>

            </h1>

            <div class="hero-desc">
                {t['hero_desc']}
            </div>

        </section>
        """
    )


    info_col, login_col = st.columns(
        [
            1,
            1
        ],
        gap='large'
    )


    with info_col:

        st.html(
            f"""
            <div class="feature-card">

                <div class="feature-icon">
                    🛡️
                </div>

                <div class="feature-title">
                    {t['main_card_title']}
                </div>

                <div class="feature-desc">
                    {t['main_card_desc']}
                </div>

            </div>
            """
        )


        step_cols = st.columns(
            3
        )


        with step_cols[0]:

            st.html(
                f"""
                <div class="step-card">

                    <div class="step-icon">
                        📷
                    </div>

                    <div class="step-word">
                        {t['step1']}
                    </div>

                </div>
                """
            )


        with step_cols[1]:

            st.html(
                f"""
                <div class="step-card">

                    <div class="step-icon">
                        🔍
                    </div>

                    <div class="step-word">
                        {t['step2']}
                    </div>

                </div>
                """
            )


        with step_cols[2]:

            st.html(
                f"""
                <div class="step-card">

                    <div class="step-icon">
                        🛡️
                    </div>

                    <div class="step-word">
                        {t['step3']}
                    </div>

                </div>
                """
            )


    # =====================================================
    # LOGIN
    # =====================================================

    with login_col:

        login_tab, register_tab = st.tabs([
            t['login'],
            t['register']
        ])


        with login_tab:

            st.html(
                f"""
                <div class="page-title"
                     style="
                        font-size:31px;
                        margin-top:15px;
                     ">
                    {t['login_title']}
                </div>

                <div class="page-desc">
                    {t['login_desc']}
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
                key='login_button'
            ):

                user = login_user(
                    email,
                    password
                )


                if user:

                    st.session_state.user = {
                        'id':
                            user[0],

                        'name':
                            user[1],

                        'email':
                            user[2]
                    }


                    st.session_state.page = 'scan'

                    st.rerun()


                else:

                    st.error(
                        t['wrong']
                    )


        with register_tab:

            st.html(
                f"""
                <div class="page-title"
                     style="
                        font-size:31px;
                        margin-top:15px;
                     ">
                    {t['register_title']}
                </div>

                <div class="page-desc">
                    {t['register_desc']}
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
                key='register_button'
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


    # =====================================================
    # USER HEADER
    # =====================================================

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
            <div class="user-card">

                <div class="user-small">
                    {t['hello']} {user['name']} 👋
                </div>

                <div class="user-big">
                    {t['today']}
                </div>

            </div>
            """
        )


    with logout_col:

        if st.button(
            t['logout'],
            use_container_width=True,
            key='logout_button'
        ):

            st.session_state.user = None

            st.rerun()


    # =====================================================
    # NAVIGATION
    # =====================================================

    options = [
        t['scan_nav'],
        t['profile_nav'],
        t['family_nav']
    ]


    current_map = {
        'scan':
            options[0],

        'profile':
            options[1],

        'family':
            options[2]
    }


    navigation = st.radio(
        'Navigation',
        options,
        horizontal=True,
        index=options.index(
            current_map[
                st.session_state.page
            ]
        ),
        label_visibility='collapsed'
    )


    if navigation == options[0]:

        st.session_state.page = 'scan'


    elif navigation == options[1]:

        st.session_state.page = 'profile'


    else:

        st.session_state.page = 'family'


    # =====================================================
    # SCAN PAGE
    # =====================================================

    if st.session_state.page == 'scan':

        st.html(
            f"""
            <div class="page-head">

                <div class="page-title">
                    {t['scan_title']}
                </div>

                <div class="page-desc">
                    {t['scan_desc']}
                </div>

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
                'name':
                    user['name'],

                'allergies':
                    my_allergies,

                'is_owner':
                    True
            })


        for member in family:

            people.append({
                'name':
                    member['name'],

                'allergies':
                    member['allergies'],

                'is_owner':
                    False
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
                    margin-bottom:13px;
                    font-size:14px;
                ">
                    {t['check_for']}
                </div>
                """
            )


            number_of_columns = min(
                len(people),
                3
            )


            people_cols = st.columns(
                number_of_columns
            )


            for index, person in enumerate(
                people
            ):

                with people_cols[
                    index % number_of_columns
                ]:

                    allergy_text = ', '.join(
                        person['allergies']
                    )


                    st.html(
                        f"""
                        <div class="person-card">

                            <div class="person-name">
                                {person['name']}
                            </div>

                            <div class="person-allergy">
                                {allergy_text}
                            </div>

                        </div>
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


            if camera_image is not None:

                image_source = camera_image


            else:

                image_source = uploaded_file


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

                                st.html(
                                    f"""
                                    <div class="page-title"
                                         style="
                                            font-size:26px;
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
                                        t['ocr_text']
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
                                        <div class="page-head">

                                            <div class="page-title">
                                                {t['result']}
                                            </div>

                                        </div>
                                        """
                                    )


                                    for result in results:

                                        # =================
                                        # DANGER
                                        # =================

                                        if result['matches']:

                                            details = ''


                                            for allergy, matches in (
                                                result[
                                                    'matches'
                                                ].items()
                                            ):

                                                details += f"""
                                                <div class="result-detail">

                                                    <div style="
                                                        color:#9FAAB2;
                                                        font-size:13px;
                                                        margin-bottom:5px;
                                                    ">
                                                        {t['allergy_type']}
                                                    </div>

                                                    <div style="
                                                        font-size:19px;
                                                        font-weight:900;
                                                        margin-bottom:10px;
                                                    ">
                                                        {allergy}
                                                    </div>

                                                    <div style="
                                                        color:#FF9999;
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

                                                description = (
                                                    t[
                                                        'danger_text'
                                                    ]
                                                )


                                            else:

                                                title = (
                                                    f"{t['family_danger_title']} "
                                                    f"{result['name']} ⚠️"
                                                )

                                                description = (
                                                    t[
                                                        'family_danger_text'
                                                    ]
                                                )


                                            st.html(
                                                f"""
                                                <div class="danger-result">

                                                    <div class="result-status-danger">
                                                        ⚠ ALLERGY ALERT
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


                                        # =================
                                        # SAFE
                                        # =================

                                        else:

                                            if result['is_owner']:

                                                title = (
                                                    f"{t['safe_title']} "
                                                    f"{result['name']} ✨"
                                                )

                                                description = (
                                                    t[
                                                        'safe_text'
                                                    ]
                                                )


                                            else:

                                                if (
                                                    st.session_state.language
                                                    == 'AR'
                                                ):

                                                    title = (
                                                        f"{result['name']}، "
                                                        f"{t['family_safe_title']} ✨"
                                                    )

                                                else:

                                                    title = (
                                                        f"{result['name']}: "
                                                        f"{t['family_safe_title']} ✨"
                                                    )


                                                description = (
                                                    t[
                                                        'family_safe_text'
                                                    ]
                                                )


                                            st.html(
                                                f"""
                                                <div class="safe-result">

                                                    <div class="result-status-safe">
                                                        ✓ CLEAR
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
    # PROFILE PAGE
    # =====================================================

    elif st.session_state.page == 'profile':

        st.html(
            f"""
            <div class="page-head">

                <div class="page-title">
                    {t['profile_title']}
                </div>

                <div class="page-desc">
                    {t['profile_subtitle']}
                </div>

            </div>
            """
        )


        st.html(
            f"""
            <div class="content-card">

                <div style="
                    color:#8996A0;
                    font-size:13px;
                    margin-bottom:12px;
                ">
                    {t['account_info']}
                </div>

                <div class="profile-name">
                    {user['name']}
                </div>

                <div class="profile-email">
                    {user['email']}
                </div>

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
            key='save_allergies_button'
        ):

            save_user_allergies(
                user['id'],
                selected
            )


            st.success(
                t['saved'] + ' ✓'
            )


            st.rerun()


    # =====================================================
    # FAMILY PAGE
    # =====================================================

    elif st.session_state.page == 'family':

        st.html(
            f"""
            <div class="page-head">

                <div class="page-title">
                    {t['family_title']}
                </div>

                <div class="page-desc">
                    {t['family_subtitle']}
                </div>

            </div>
            """
        )


        family = get_family_members(
            user['id']
        )


        if family:

            columns = st.columns(
                2
            )


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

                            <div class="person-relation">
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
                            in member[
                                'allergies'
                            ]
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
                            key=(
                                'delete_'
                                + str(
                                    member['id']
                                )
                            ),
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
            f"""
            <div style="
                height:28px;
            ">
            </div>

            <div class="content-card">

                <div class="card-title">
                    ＋ {t['add_member']}
                </div>

            </div>
            """
        )


        col1, col2 = st.columns(
            2
        )


        with col1:

            member_name = st.text_input(
                t['member_name'],
                key='member_name'
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
            key='add_member_button'
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
                    f'✓ {member_name}'
                )


                st.rerun()
