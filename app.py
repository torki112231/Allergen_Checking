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
    add_family_member,
    get_family_members
)


st.set_page_config(
    page_title='mosabb',
    page_icon='🛡️',
    layout='centered'
)

create_tables()


if 'user' not in st.session_state:
    st.session_state.user = None


ALLERGEN_KEYWORDS = {
    'Milk / Dairy': [
        'milk',
        'dairy',
        'whey',
        'casein',
        'caseinate',
        'lactose',
        'cream',
        'butter',
        'cheese',
        'yogurt',
        'حليب',
        'لبن',
        'مصل الحليب',
        'كازين',
        'لاكتوز',
        'زبدة',
        'جبن',
        'قشطة'
    ],

    'Peanuts': [
        'peanut',
        'peanuts',
        'groundnut',
        'فول سوداني',
        'فول السوداني'
    ],

    'Sesame': [
        'sesame',
        'tahini',
        'sesame seed',
        'سمسم',
        'طحينة'
    ],

    'Eggs': [
        'egg',
        'eggs',
        'albumin',
        'ovalbumin',
        'بيض',
        'البيض'
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


@st.cache_resource
def load_model():
    return YOLO('models/ingredient_label_model.pt')


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
        conf=0.25,
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

    x1, y1, x2, y2 = best_box.xyxy[0].cpu().numpy()

    x1 = max(int(x1), 0)
    y1 = max(int(y1), 0)
    x2 = min(int(x2), image.width)
    y2 = min(int(y2), image.height)

    cropped = image.crop(
        (x1, y1, x2, y2)
    )

    return cropped


def run_ocr(image, reader):
    image_array = np.array(image)

    results = reader.readtext(
        image_array,
        detail=0,
        paragraph=True
    )

    text = ' '.join(results)

    return text


def find_allergen_matches(text, allergy):
    text_lower = text.lower()

    found = []

    keywords = ALLERGEN_KEYWORDS.get(
        allergy,
        []
    )

    for keyword in keywords:

        keyword_lower = keyword.lower()

        if keyword_lower in text_lower:

            found.append(keyword)

        else:

            words = text_lower.split()

            for word in words:

                score = fuzz.ratio(
                    word,
                    keyword_lower
                )

                if score >= 85:

                    found.append(keyword)
                    break

    return list(set(found))


def check_family(text, family):
    results = []

    for member in family:

        member_matches = {}

        for allergy in member['allergies']:

            matches = find_allergen_matches(
                text,
                allergy
            )

            if matches:

                member_matches[allergy] = matches

        results.append({
            'name': member['name'],
            'relation': member['relation'],
            'matches': member_matches
        })

    return results


st.title('mosabb | مسبب')

st.caption(
    'افحص المنتج واعرف إذا كان مناسب لك ولعائلتك'
)


if st.session_state.user is None:

    login_tab, register_tab = st.tabs([
        'تسجيل الدخول',
        'إنشاء حساب'
    ])

    with login_tab:

        st.subheader('تسجيل الدخول')

        email = st.text_input(
            'البريد الإلكتروني',
            key='login_email'
        )

        password = st.text_input(
            'كلمة المرور',
            type='password',
            key='login_password'
        )

        if st.button(
            'دخول',
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
                    'البريد الإلكتروني أو كلمة المرور غير صحيحة'
                )


    with register_tab:

        st.subheader(
            'إنشاء حساب عائلة'
        )

        name = st.text_input(
            'اسمك',
            key='register_name'
        )

        email = st.text_input(
            'البريد الإلكتروني',
            key='register_email'
        )

        password = st.text_input(
            'كلمة المرور',
            type='password',
            key='register_password'
        )

        if st.button(
            'إنشاء الحساب',
            use_container_width=True
        ):

            if not name or not email or not password:

                st.warning(
                    'عب البيانات كلها'
                )

            else:

                success = register_user(
                    name,
                    email,
                    password
                )

                if success:

                    st.success(
                        'تم إنشاء الحساب، سجل دخولك الآن'
                    )

                else:

                    st.error(
                        'الإيميل مستخدم من قبل'
                    )


else:

    user = st.session_state.user

    st.success(
        f'أهلاً {user["name"]} 👋'
    )

    if st.button(
        'تسجيل الخروج'
    ):

        st.session_state.user = None
        st.rerun()


    scan_tab, family_tab = st.tabs([
        '📷 فحص منتج',
        '👨‍👩‍👧‍👦 عائلتي'
    ])


    with scan_tab:

        st.header(
            'فحص منتج'
        )

        family = get_family_members(
            user['id']
        )

        if not family:

            st.warning(
                'أضف أفراد العائلة وحساسياتهم أول'
            )

        else:

            camera_image = st.camera_input(
                'صور مكونات المنتج'
            )

            uploaded_file = st.file_uploader(
                'أو ارفع صورة',
                type=[
                    'jpg',
                    'jpeg',
                    'png'
                ]
            )

            image_source = None

            if camera_image:

                image_source = camera_image

            elif uploaded_file:

                image_source = uploaded_file


            if image_source:

                image = Image.open(
                    image_source
                ).convert('RGB')

                st.image(
                    image,
                    caption='الصورة الأصلية',
                    use_container_width=True
                )

                if st.button(
                    '🔍 تحليل المنتج',
                    use_container_width=True
                ):

                    with st.spinner(
                        'mosabb يحلل المكونات...'
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
                                    'ما قدرت أحدد قائمة المكونات. حاول تصورها بشكل أوضح.'
                                )

                            else:

                                st.subheader(
                                    'منطقة المكونات المكتشفة'
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
                                        'تم تحديد المكونات لكن ما قدرت أقرأ النص.'
                                    )

                                else:

                                    st.subheader(
                                        'النص المقروء'
                                    )

                                    st.write(
                                        text
                                    )

                                    results = check_family(
                                        text,
                                        family
                                    )

                                    st.divider()

                                    st.header(
                                        'نتيجة mosabb'
                                    )

                                    any_warning = False

                                    for result in results:

                                        if result['matches']:

                                            any_warning = True

                                            st.error(
                                                f'🚨 المنتج قد لا يكون مناسباً لـ {result["name"]}'
                                            )

                                            for allergy, matches in result['matches'].items():

                                                st.write(
                                                    f'**الحساسية:** {allergy}'
                                                )

                                                st.write(
                                                    'تم العثور على: '
                                                    + ', '.join(matches)
                                                )

                                        else:

                                            st.success(
                                                f'✅ لم نجد مسببات الحساسية المسجلة لـ {result["name"]}'
                                            )


                                    if not any_warning:

                                        st.success(
                                            '✅ لم نجد أي مسبب حساسية مسجل لأفراد العائلة'
                                        )

                                    st.caption(
                                        'النتيجة تعتمد على جودة الصورة ودقة قراءة النص، وليست بديلاً عن قراءة تحذيرات العبوة أو الاستشارة الطبية.'
                                    )

                        except Exception as error:

                            st.error(
                                f'صار خطأ أثناء التحليل: {error}'
                            )


    with family_tab:

        st.header(
            'أفراد العائلة'
        )

        family = get_family_members(
            user['id']
        )

        if family:

            for member in family:

                with st.container(
                    border=True
                ):

                    st.subheader(
                        member['name']
                    )

                    st.write(
                        f'الصفة: {member["relation"]}'
                    )

                    st.write(
                        'الحساسيات: '
                        + ', '.join(
                            member['allergies']
                        )
                    )

        else:

            st.info(
                'ما أضفت أحد للعائلة للحين'
            )


        st.divider()

        st.subheader(
            'إضافة فرد للعائلة'
        )

        member_name = st.text_input(
            'الاسم'
        )

        relation = st.selectbox(
            'صلة القرابة',
            [
                'ابن',
                'ابنة',
                'أم',
                'أب',
                'أخ',
                'أخت',
                'أخرى'
            ]
        )

        allergies = st.multiselect(
            'الحساسيات',
            [
                'Milk / Dairy',
                'Peanuts',
                'Sesame',
                'Eggs',
                'Tree Nuts'
            ]
        )

        if st.button(
            'إضافة فرد',
            use_container_width=True
        ):

            if not member_name:

                st.warning(
                    'اكتب اسم الشخص'
                )

            elif not allergies:

                st.warning(
                    'اختر حساسية واحدة على الأقل'
                )

            else:

                add_family_member(
                    user['id'],
                    member_name,
                    relation,
                    allergies
                )

                st.success(
                    f'تمت إضافة {member_name}'
                )

                st.rerun()
