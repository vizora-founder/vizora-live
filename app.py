import base64
import io
import os
import streamlit as st
from PIL import Image, ImageDraw
from openai import OpenAI

st.set_page_config(page_title='VIZORA LIVE', page_icon='👁️')
st.title('👁️ VIZORA LIVE')
st.caption('Suratga ol • Tushun • Xavfsiz o‘rgan')
st.info('Sinov versiyasi: AI xato qilishi mumkin. Elektr, gaz va xavfli uskunalarni ta’mirlash uchun mutaxassisga murojaat qiling.')

photo = st.camera_input('Buyumni suratga oling')
upload = st.file_uploader('Yoki surat yuklang', type=['jpg','jpeg','png'])
source = photo if photo is not None else upload
question = st.text_input('Nimani bilmoqchisiz?', 'Bu buyum nima va undan qanday xavfsiz foydalaniladi?')

if source is not None:
    raw = source.getvalue()
    try:
        img = Image.open(io.BytesIO(raw)).convert('RGB')
        img.thumbnail((1024, 1024))
        buf = io.BytesIO()
        img.save(buf, format='JPEG', quality=80)
        jpeg = buf.getvalue()
    except Exception:
        st.error('Suratni ochib bo‘lmadi.')
        st.stop()
    st.image(img, caption='Tahlil qilinadigan surat', use_container_width=True)
    if st.button('🔍 Tahlil qilish', type='primary'):
        key = st.secrets.get('OPENAI_API_KEY', os.getenv('OPENAI_API_KEY', ''))
        if not key:
            st.error('OPENAI_API_KEY sozlanmagan. Streamlit Secrets ga qo‘shing.')
            st.stop()
        try:
            client = OpenAI(api_key=key)
            b64 = base64.b64encode(jpeg).decode('ascii')
            result = client.responses.create(
                model='gpt-4.1-mini',
                store=False,
                max_output_tokens=550,
                input=[{'role':'user','content':[
                    {'type':'input_text','text':(
                        'O‘zbek tilida javob ber. Rasmdagi maishiy buyumni taxminan aniqlang. '
                        'Aniq bo‘lmasa noaniqlikni ayting. Faqat xavfsiz, oddiy foydalanish '
                        'yoki tashqi tekshiruv bo‘yicha 3 qadam bering. '
                        'Elektr, gaz, kimyoviy modda yoki mexanik xavfli ta’mirlash amallarini '
                        'tavsiya qilmang. Suratdagi aniq qismlarni bilmasangiz uydirmang. '
                        'Format: BUYUM: ...\nISHONCH: ...\nQADAM 1: ...\nQADAM 2: ...\nQADAM 3: ...\nOGOHLANTIRISH: ...\n'
                        f'Foydalanuvchi savoli: {question}'
                    )},
                    {'type':'input_image','image_url':f'data:image/jpeg;base64,{b64}','detail':'low'}
                ]}]
            )
            st.subheader('AI javobi')
            st.write(result.output_text)
            st.caption('Keyingi versiyada surat ustiga aniq joylashgan belgilar qo‘shiladi.')
        except Exception:
            st.error('AI so‘rovi bajarilmadi. API kaliti, balans va modelga ruxsatni tekshiring.')
