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
st.caption("Instantly analyze Terms & Conditions and Privacy Policies using AI")

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
        # Translated error response to English
        return text if len(text) > 300 else "Error: Not enough text content found on the page."
    except Exception as e:
        return f"Error: {str(e)}"

def analyze_tos(text):
    # Professional English Prompt for Gemini 2.5 Flash
    prompt = f"""
    Command: You are an expert privacy attorney and data protection specialist. Analyze the following text using Gemini 2.5 Flash.
    Objective: Generate a concise, highly scannable, and actionable privacy report in English.

    Format the output exactly using the following structure:

    🏢 **Company / Platform**: [Name]

    ✅ **Pros & Fair Practices**:
    * (Maximum 2 short bullet points highlighting user-friendly terms)

    ⚠️ **Major Risks & Red Flags**:
    * (Maximum 3 of the most critical/dangerous points regarding data tracking, third-party sharing, hidden fees, or liability waivers. Keep them concise and direct)

    📊 **Privacy Safety Score**: [X/10]

    ⚖️ **Verdict**: [One clear, short summary sentence advising the user]

    Text: {text[:20000]}
    """
    response = model.generate_content(prompt)
    return response.text

# English Tabs interface
tab1, tab2 = st.tabs(["🔗 Analyze via Link", "📝 Paste Text Manually"])

with tab1:
    url_input = st.text_input("Paste the Terms & Conditions / Privacy Policy URL (e.g., Temu, Facebook):")
    if st.button("Analyze URL"):
        if url_input:
            with st.spinner('Scraping and analyzing website content...'):
                scraped_text = scrape_with_selenium(url_input)
                # Fixed bug: Now checking for English "Error" string properly
                if "Error" not in scraped_text:
                    st.success("Website content successfully loaded!")
                    report = analyze_tos(scraped_text)
                    st.markdown(report)
                else:
                    st.error(f"Analysis failed: {scraped_text}")

with tab2:
    manual_text = st.text_area("Paste the T&C text manually here:", height=300)
    if st.button("Analyze Text"):
        if manual_text:
            with st.spinner('AI is generating your privacy report...'):
                report = analyze_tos(manual_text)
                st.markdown(report)