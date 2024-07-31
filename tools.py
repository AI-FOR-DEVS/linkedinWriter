from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from typing_extensions import Annotated
from openai import OpenAI
import os
import time
import base64


def analyze_profile(profile_name: Annotated[str, "The name of the profile to scrape"]) -> Annotated[None, "A detailed description of the linkedIn profile"]:
    filename = create_screenshot(profile_name)
    analysis = analyze_screenshot(filename)
    return analysis


def create_screenshot(profile_name):
    driver = webdriver.Chrome()
    username = os.environ.get("LINKEDIN_EMAIL")
    password = os.environ.get("LINKEDIN_PASSWORD")

    if not (username and password):
        raise Exception('Username or password not given')

    driver.get("https://www.linkedin.com/login")
    username_input = driver.find_element("id", "username")
    password_input = driver.find_element("id", "password")
    username_input.send_keys(username)
    password_input.send_keys(password)
    password_input.send_keys(Keys.RETURN)
    driver.get(
        f"https://www.linkedin.com/in/{profile_name}/recent-activity/all/")
    time.sleep(3)

    screenshot_path = f"{profile_name}_linkedin.png"
    driver.save_screenshot(screenshot_path)
    return screenshot_path


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_screenshot(image_path):
    client = OpenAI()
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "user",
             "content": [
                 {
                     "type": "text",
                     "text": "Describe the interests of this user as detailed as possible."
                 },
                 {
                     "type": "image_url",
                     "image_url": {
                         "url": f"data:image/jpeg;base64,{base64_image}"
                     }
                 },
             ],
             }
        ],
        max_tokens=300,
    )

    return response.choices[0].message.content