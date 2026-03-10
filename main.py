import streamlit as st
import google.generativeai as genai
import os
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time


load_dotenv()
api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-2.5-flash')

st.set_page_config(page_title="PrivacyGuard AI", page_icon="🛡️")
st.title("🛡️ PrivacyGuard AI")


def scrape_with_selenium(url):
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    try:

        if os.path.exists("/usr/bin/chromium-browser"):
            chrome_options.binary_location = "/usr/bin/chromium-browser"


        driver = webdriver.Chrome(options=chrome_options)

        driver.get(url)
        time.sleep(5)

        page_source = driver.page_source
        driver.quit()

        soup = BeautifulSoup(page_source, 'html.parser')
        for script in soup(["script", "style"]):
            script.extract()

        text = soup.get_text(separator=' ', strip=True)
        return text if len(text) > 300 else "Error: ტექსტი ვერ მოიძებნა."
    except Exception as e:
        return f"Error: {str(e)}"


def analyze_tos(text):
    prompt = f"""
    Command: შენ ხარ პრივატულობის ექსპერტი. გააანალიზე ტექსტი Gemini 2.5 Flash-ის გამოყენებით.
    მიზანი: შექმენი ძალიან მოკლე, სკანირებადი და ეფექტური რეპორტი ქართულად.

    გამოიყენე შემდეგი ფორმატი:

    🏢 **კომპანია**: [სახელი]

    ✅ **დადებითი მხარეები**:
    * (მაქსიმუმ 2 მოკლე პუნქტი)

    ⚠️ **მთავარი საფრთხეები (Red Flags)**:
    * (მაქსიმუმ 3 ყველაზე საშიში პუნქტი - დაწერე მოკლედ და კონკრეტულად)

    📊 **უსაფრთხოების ქულა**: [X/10]

    ⚖️ **დასკვნა**: [ერთი მოკლე წინადადება]

    ტექსტი: {text[:20000]}
    """
    response = model.generate_content(prompt)
    return response.text


tab1, tab2 = st.tabs(["🔗 ლინკით ანალიზი", "📝 ტექსტის ჩაკოპირება"])

with tab1:
    url_input = st.text_input("ჩასვით საიტის Terms & Conditions ლინკი (მაგ: Temu, Facebook):")
    if st.button("გაანალიზე ლინკი"):
        if url_input:
            with st.spinner('მიმდინარეობს ანალიზი...'):
                scraped_text = scrape_with_selenium(url_input)
                if "Error" not in scraped_text:
                    st.success("საიტი წარმატებით ჩაიტვირთა!")
                    report = analyze_tos(scraped_text)
                    st.markdown(report)
                else:
                    st.error(f"ვერ მოხერხდა: {scraped_text}")

with tab2:
    manual_text = st.text_area("ჩააკოპირეთ ტექსტი ხელით:", height=300)
    if st.button("გაანალიზე ტექსტი"):
        if manual_text:
            with st.spinner('AI აანალიზებს...'):
                report = analyze_tos(manual_text)
                st.markdown(report)