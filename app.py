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


st.set_page_config(
    page_title='mosabb',
    page_icon='🛡️',
    layout='centered'
)


create_tables()


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
        'groundnuts',
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
        'pecans',
        'macadamia',
        'لوز',
        'اللوز',
        'جوز',
        'الجوز',
        'كاجو',
        'فستق',
        'الفستق',
        'بندق',
        'البندق'
    ]
}


if 'user' not in st.session_state:
    st.session_state.user = None


@st.cache_resource
def load_model():
    model = YOLO(
        'models/ingredient_label_model.pt'
    )

    return model


@st.cache_resource
def load_ocr():
    reader = easyocr.Reader(
        ['ar', 'en'],
        gpu=False
    )

    return reader


def extract_ingredient_region(
    image,
    model
):

    image_array = np.array(image)

    results = model(
        image_array,
        conf=0.20,
        verbose=False
    )

    boxes = results[0].boxes

    if boxes is None:
        return None

    if len(boxes) == 0:
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

    if best_box is None:
        return None

    coordinates = (
        best_box
        .xyxy[0]
        .cpu()
        .numpy()
    )

    x1 = int(coordinates[0])
    y1 = int(coordinates[1])
    x2 = int(coordinates[2])
    y2 = int(coordinates[3])

    x1 = max(x1, 0)
    y1 = max(y1, 0)

    x2 = min(
        x2,
        image.width
    )

    y2 = min(
        y2,
        image.height
    )

    cropped = image.crop(
        (
            x1,
            y1,
            x2,
            y2
        )
    )

    return cropped


def run_ocr(
    image,
    reader
):

    image_array = np.array(
        image
    )

    results = reader.readtext(
        image_array,
        detail=0,
        paragraph=True
    )

    text = ' '.join(
        results
    )

    return text


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

    for keyword in keywords:

        keyword_lower = (
            keyword.lower()
        )

        if keyword_lower in text_lower:

            found.append(
                keyword
            )

            continue

        if len(keyword_lower) <= 4:

            continue

        words = (
            text_lower
            .replace(',', ' ')
            .replace('.', ' ')
            .replace(':', ' ')
            .replace(';', ' ')
            .replace('(', ' ')
            .replace(')', ' ')
            .split()
        )

        for word in words:

            score = fuzz.ratio(
                word,
                keyword_lower
            )

            if score >= 88:

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

    results = []

    for person in people:

        matches = {}

        for allergy in person['allergies']:

            found = find_allergen_matches(
                text,
                allergy
            )

            if found:

                matches[allergy] = found

        results.append({
            'name': person['name'],
            'relation': person['relation'],
            'matches': matches
        })

    return results


st.title(
    'mosabb | مسبب'
)

st.caption(
    'افحص المنتج واعرف إذا كان مناسب لك ولعائلتك'
)


# =========================
# Login / Register
# =========================

if st.session_state.user is None:

    login_tab, register_tab = st.tabs([
        'تسجيل الدخول',
        'إنشاء حساب'
    ])


    with login_tab:

        st.subheader(
            'تسجيل الدخول'
        )

        login_email = st.text_input(
            'البريد الإلكتروني',
            key='login_email'
        )

        login_password = st.text_input(
            'كلمة المرور',
            type='password',
            key='login_password'
        )

        if st.button(
            'دخول',
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
                    'البريد الإلكتروني أو كلمة المرور غير صحيحة'
                )


    with register_tab:

        st.subheader(
            'إنشاء حساب'
        )

        register_name = st.text_input(
            'اسمك',
            key='register_name'
        )

        register_email = st.text_input(
            'البريد الإلكتروني',
            key='register_email'
        )

        register_password = st.text_input(
            'كلمة المرور',
            type='password',
            key='register_password'
        )

        if st.button(
            'إنشاء الحساب',
            use_container_width=True
        ):

            if (
                not register_name
                or not register_email
                or not register_password
            ):

                st.warning(
                    'عب البيانات كلها'
                )

            else:

                success = register_user(
                    register_name,
                    register_email,
                    register_password
                )

                if success:

                    st.success(
                        'تم إنشاء الحساب، سجل دخولك الآن ✅'
                    )

                else:

                    st.error(
                        'البريد الإلكتروني مستخدم من قبل'
                    )


# =========================
# Logged in
# =========================

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


    scan_tab, profile_tab = st.tabs([
        '📷 فحص منتج',
        '👤 ملفي وعائلتي'
    ])


    # =========================
    # Scan tab
    # =========================

    with scan_tab:

        st.header(
            'فحص منتج'
        )

        my_allergies = get_user_allergies(
            user['id']
        )

        family = get_family_members(
            user['id']
        )

        people_to_check = []


        # صاحب الحساب
        if my_allergies:

            people_to_check.append({
                'name': user['name'],
                'relation': 'أنا',
                'allergies': my_allergies
            })


        # أفراد العائلة
        for member in family:

            people_to_check.append({
                'name': member['name'],
                'relation': member['relation'],
                'allergies': member['allergies']
            })


        if not people_to_check:

            st.warning(
                'سجل حساسيتك أول من تبويب ملفي وعائلتي'
            )

        else:

            st.write(
                'mosabb بيفحص المنتج للأشخاص التاليين:'
            )

            for person in people_to_check:

                allergies_text = ', '.join(
                    person['allergies']
                )

                st.write(
                    f'• {person["name"]}: {allergies_text}'
                )


            st.divider()


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
                    caption='الصورة الأصلية',
                    use_container_width=True
                )


                if st.button(
                    '🔍 تحليل المنتج',
                    use_container_width=True
                ):

                    with st.spinner(
                        'mosabb يحلل المنتج...'
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
                                    'ما قدرت أحدد قائمة المكونات. صور المكونات بشكل أوضح وقريب.'
                                )

                            else:

                                st.subheader(
                                    'المكونات المكتشفة'
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
                                        'حددت مكان المكونات لكن ما قدرت أقرأ النص.'
                                    )

                                else:

                                    st.subheader(
                                        'النص المقروء'
                                    )

                                    st.write(
                                        text
                                    )


                                    results = check_people(
                                        text,
                                        people_to_check
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
                                                f'🚨 المنتج قد يسبب حساسية لـ {result["name"]}'
                                            )


                                            for allergy, matches in result['matches'].items():

                                                st.write(
                                                    f'**نوع الحساسية:** {allergy}'
                                                )

                                                st.write(
                                                    '**تم العثور على:** '
                                                    + ', '.join(matches)
                                                )

                                        else:

                                            st.success(
                                                f'✅ لم نجد مسبب الحساسية المسجل لـ {result["name"]}'
                                            )


                                    if not any_warning:

                                        st.success(
                                            '✅ لم نجد أي مسبب حساسية مسجل'
                                        )


                                    st.warning(
                                        'mosabb أداة مساعدة فقط. تأكد دائماً من تحذيرات الحساسية المكتوبة على المنتج.'
                                    )


                        except Exception as error:

                            st.error(
                                'صار خطأ أثناء التحليل'
                            )

                            st.write(
                                error
                            )


    # =========================
    # Profile tab
    # =========================

    with profile_tab:

        st.header(
            'ملفي'
        )


        st.subheader(
            f'{user["name"]}'
        )

        st.caption(
            'حدد الأشياء اللي تسبب لك حساسية'
        )


        current_allergies = get_user_allergies(
            user['id']
        )


        selected_allergies = st.multiselect(
            'حساسيتي',
            ALLERGIES,
            default=current_allergies,
            key='my_allergies'
        )


        if st.button(
            'حفظ حساسيتي',
            use_container_width=True
        ):

            save_user_allergies(
                user['id'],
                selected_allergies
            )

            st.success(
                'تم حفظ حساسيتك ✅'
            )

            st.rerun()


        st.divider()


        st.header(
            'عائلتي'
        )

        st.caption(
            'إضافة أفراد العائلة اختيارية'
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

                    if member['allergies']:

                        st.write(
                            'الحساسيات: '
                            + ', '.join(
                                member['allergies']
                            )
                        )

                    if st.button(
                        f'حذف {member["name"]}',
                        key=f'delete_{member["id"]}'
                    ):

                        delete_family_member(
                            member['id']
                        )

                        st.rerun()

        else:

            st.info(
                'ما أضفت أفراد للعائلة، وتقدر تستخدم mosabb لنفسك عادي.'
            )


        st.divider()


        st.subheader(
            'إضافة فرد للعائلة'
        )


        member_name = st.text_input(
            'الاسم',
            key='member_name'
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
            ],
            key='relation'
        )


        member_allergies = st.multiselect(
            'حساسياته',
            ALLERGIES,
            key='member_allergies'
        )


        if st.button(
            'إضافة فرد',
            use_container_width=True
        ):

            if not member_name:

                st.warning(
                    'اكتب اسم الشخص'
                )

            elif not member_allergies:

                st.warning(
                    'اختر حساسية واحدة على الأقل'
                )

            else:

                add_family_member(
                    user['id'],
                    member_name,
                    relation,
                    member_allergies
                )

                st.success(
                    f'تمت إضافة {member_name} ✅'
                )

                st.rerun()
