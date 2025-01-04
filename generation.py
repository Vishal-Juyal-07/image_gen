from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os
from datetime import datetime
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import torch
import regex as re
from huggingface_hub import InferenceClient
# from google.colab import userdata
import pandas as pd
import time
import random
import streamlit as st
from concurrent.futures import ThreadPoolExecutor, TimeoutError




HF_TOKEN = st.secrets["HF_TOKEN"]
client = InferenceClient(api_key=HF_TOKEN)



def create_banner(width=1200, height=120):
    # Create a new image with transparent background
    image = Image.new('RGBA', (width, height), (0, 0, 0, 0))

    background = Image.new('RGBA', (width, height), (242, 101, 34, 255))  # f26522 with alpha 180
    image.paste(background, (0, 0), background)  # Use background as mask

    draw = ImageDraw.Draw(image)
    # Calculate proportional font size
    # font_size = int(height * 0.2)
    font_size = 18

    try:
        font = ImageFont.truetype("Helvetica.ttc", font_size)
    except:
        default_font = ImageFont.load_default()
        font = default_font.font_variant(size=font_size)

    texts = ["Low Interest Rates",'|', "Hassle Free process",'|', "Flexible tenure"]

    # Calculate box dimensions
    box_width = int(width * 1/(len(texts)))
    box_height = int(height * 0.9)
    spacing = (width - (box_width * len(texts))) // len(texts)+1

    # Calculate proportional corner radius
    corner_radius = int(box_height * 0.15)

    # Shadow parameters
    shadow_offset = int(height * 0.03)
    shadow_blur = int(height * 0.04)

    # Draw boxes with white shadows
    for i, text in enumerate(texts):
        # Calculate box position
        x1 = spacing + (i * (box_width + spacing))
        y1 = (height - box_height) // 2
        x2 = x1 + box_width
        y2 = y1 + box_height

        # Calculate text position for centering
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        text_x = x1 + (box_width - text_width) // 2
        text_y = y1 + (box_height - text_height) // 2

        # Draw text in white
        draw.text((text_x, text_y), text, fill='white', font=font, stroke_width=0.2, stroke_fill='white') #Bold effect using stroke

    # Calculate disclaimer font size and position
    disclaimer_font_size = int(font_size * 0.6) # Smaller than main text

    # Add "Follow us on" and social media icons
    follow_text = "Follow us on:"
    follow_font_size = int(font_size * 0.8)
    try:
        follow_font = ImageFont.truetype("Helvetica.ttc", follow_font_size)
    except:
        default_font = ImageFont.load_default()
        follow_font = default_font.font_variant(size=follow_font_size)

    follow_text_bbox = draw.textbbox((0, 0), follow_text, font=follow_font)
    follow_text_width = follow_text_bbox[2] - follow_text_bbox[0]

    # Right indent (adjust this value as needed)
    right_indent = image.width // 2

    # Calculate position with right indent
    follow_text_x = width - follow_text_width - right_indent
    follow_text_y = 10 # 10 pixels padding from the top

    draw.text((follow_text_x, follow_text_y), follow_text, fill='white', font=follow_font, stroke_width=0.2, stroke_fill='white')

    # Load social media icons (replace with your actual icon paths)
    icon_paths = ["facebook.png", "twitter.png", "instagram.png"]
    icons = [Image.open(path) for path in icon_paths if os.path.exists(path)]

    # Resize and position icons
    icon_size = int(follow_font_size * 2.5)  # Slightly larger than follow text
    icons = [icon.resize((icon_size, icon_size)) for icon in icons]

    # Calculate icon position to be on the same line as "Follow us on"
    total_icon_width = sum(icon.width for icon in icons) + (len(icons) - 1) * 10  # 10px spacing
    icon_x = follow_text_x + follow_text_width + 20  # Start after follow text
    icon_y = follow_text_y + (follow_font_size - icon_size) // 2 # Vertically center-align

    for icon in icons:
        image.paste(icon, (icon_x, icon_y), icon)  # Paste icons with transparency
        icon_x += icon.width + 10


    # Add disclaimer
    disclaimer_text = "This image was generated using artificial intelligence and may not depict real people, places, or events.\
    Any resemblance to actual individuals or situations is purely coincidental."
    disclaimer_text = disclaimer_text.replace('  ', ' ')
    try:
        disclaimer_font = ImageFont.truetype("Helvetica.ttc", disclaimer_font_size)
    except:
        default_font = ImageFont.load_default()
        disclaimer_font = default_font.font_variant(size=disclaimer_font_size)

    disclaimer_text_bbox = draw.textbbox((0, 0), disclaimer_text, font=disclaimer_font)
    disclaimer_text_width = disclaimer_text_bbox[2] - disclaimer_text_bbox[0]
    disclaimer_text_x = (width - disclaimer_text_width) // 2  # Centered
    disclaimer_text_y = height - disclaimer_font_size - 5  # 5 pixels padding from bottom

    # Draw disclaimer text
    draw.text((disclaimer_text_x, disclaimer_text_y), disclaimer_text, fill='white', font=disclaimer_font, stroke_width=0.4, stroke_fill='white')

    return image

def save_genimage(product, age, location, gender, profession):
    """Create and save the banner"""
    # product = input('\nEnter your product details: ')
    # age = input('\nEnter your age details: ')
    # location = input('\nEnter your location details: ')
    # income = input('\nEnter your income details: ')
    # gender = input('\nEnter your gender details: ')
    # profession = input('\nEnter your profession details: ')

    if product == 'jewel':
        product = 'jewellery'
    elif product == 'personal':
        product = 'vacation'

    user_prompt = f'{product} pitched to {age} year old Indian customer'
    #tagline = generate_tagline(user_prompt)
    #tagline = "Your Perfect Choice"
    tagline = ["Dreams Within Reach"
              ,"Empowering Your Goals"
              ,"Finance Your Future"
              ,"Simplify Your Tomorrow"
              ,"Loans Made Easy"
              ,"Borrow With Confidence"
              ,"Unlock New Possibilities"
              ,"Invest In You"
              ,"Quick, Easy Loans"
              ,"Grow Your Potential"
              ,"Solutions That Empower"
              ,"Seamless Loan Experience"
              ,"Secure Your Dreams"
              ,"Freedom Through Finance"
              ,"Achieve More Today"]
    tagline = random.choice(tagline)

    system_prompt = f"A photo taken with an iPhone 16 Pro Max showcasing a loan marketing ad featuring a {age}-year-old {gender} {profession} professional in {location}, India.\
    The {product} (Without brand logo to prevent copyright infringement) is positioned in the foreground, fully in focus, and beside the person.\
    The EXACT English text '{tagline}' is prominently displayed in a stylish Helvetica font, with a font size not exceeding 24 points, and no other text visible in the image."
    system_prompt = system_prompt.replace('  ', ' ')
    system_prompt = system_prompt.replace('  ', ' ')
    print(system_prompt)

    # output is a PIL.Image object
    client = InferenceClient("black-forest-labs/FLUX.1-dev", token=HF_TOKEN)

    image = client.text_to_image(system_prompt)

    return image

def generate_image_with_timeout(*args, timeout=240):
    with ThreadPoolExecutor() as executor:
        future = executor.submit(save_genimage, *args)
        try:
            return future.result(timeout=timeout)
        except TimeoutError:
            return None

def apply_tagline_and_logo(image, banner_output_path, logo_path, logo_position="top_left"):
    """Applies tagline and logo to the image."""

    # Load and resize logo
    logo = Image.open(logo_path)
    logo_width = int(image.width * 0.2)  # 20% of image width
    logo_height = int(logo.height * (logo_width / logo.width))
    logo = logo.resize((logo_width, logo_height))

    # Calculate logo position
    if logo_position == "top_left":
        logo_x = 10
        logo_y = 10
    elif logo_position == "top_right":
        logo_x = image.width - logo_width - 10
        logo_y = 10
    else:
        raise ValueError("Invalid logo_position. Choose 'top_left' or 'top_right'.")


    # Paste banner onto image
    image.paste(logo, (logo_x, logo_y), logo) # Use mask for transparency if logo has it

    # Load and resize banner
    banner = Image.open(banner_output_path)
    banner_width = int(image.width)  # 100% of image width
    banner_height = int(banner.height * (banner_width / banner.width))
    banner = banner.resize((banner_width, banner_height))

    # Calculate banner position

    # Create a new blank image with the calculated dimensions
    new_image = Image.new('RGB', (image.width, image.height + banner_height), color=(255, 255, 255))

    # Paste the first image at the top
    new_image.paste(image, (0, 0))

    # Paste the second image at the bottom
    new_image.paste(banner, (0, image.height))

    return new_image

if __name__ == "__main__":


    # Streamlit App
    st.title("Personalized Ad Generation App")

    # Landing Page
    st.header("Choose an Option")
    option = st.radio(
        "Select how you want to generate images:",
        ("Ad-generation by Manually Entering Data", "Ad-generation by Uploading CSV File")
    )

    if option == "Manually Enter Data":
        st.subheader("Manual Data Entry")
        age = st.text_input("Age")
        gender = st.text_input("Gender")
        profession = st.text_input("Profession")
        location = st.text_input("Location")
        product = st.text_input("Product")
        income=0

        if st.button("Generate Image"):
            if age and gender and profession and location and product:
                with st.spinner("Processing... Please wait while the image is being generated."):                            
                    img = generate_image_with_timeout(product,age,location,gender,profession,timeout=240)
                if img:
                    # st.image(img, caption="Generated Image", use_container_width=True)
                    banner_output_path = "banner.png"
                    banner = create_banner(height = int(img.height * 0.08), width = int(img.width))
                    # banner = create_banner()
                    banner.save(banner_output_path)
                    print(f"Banner saved as {banner_output_path}")

                    image = apply_tagline_and_logo(img, banner_output_path, "logo.png", logo_position="top_right")
                    output_path = f"output_image_data{datetime.now().strftime('%Y%m%d%H%M%S')}.png"

                    image.save(output_path)
                    print(f"Image saved as {output_path}")
                    st.image(image, caption="Generated Image", use_container_width=True)
                else:
                    st.error("Model too busy, unable to get response in less than 240 second(s).")
                # st.image(img, caption="Generated Image", use_container_width=True)
                
            else:
                st.error("Please fill all fields to generate an image.")

    elif option == "Upload CSV File":
        st.subheader("Personalized Ad generation from CSV")
        uploaded_file = st.file_uploader("Upload a CSV file", type=["csv"])

        if uploaded_file:
            try:
                data = pd.read_csv(uploaded_file)
                st.write("Uploaded CSV Data Preview:")
                st.write(data.head())

                if st.button("Generate Images from CSV"):
                    # Ensure required columns are present
                    required_columns = ['Age', 'Gender', 'Profession', 'Location', 'Product']
                    if all(col in data.columns for col in required_columns):
                        # Pick 5 random rows
                        sampled_data = data.sample(5)
                        for idx, row in sampled_data.iterrows():
                            with st.spinner("Processing... Please wait while the image is being generated."):                    
                                img = generate_image_with_timeout(row['Product'],row['Age'], row['Location'], row['Gender'],row['Profession'], timeout=240)
                            if img:
                    # st.image(img, caption="Generated Image", use_container_width=True)
                                banner_output_path = "banner.png"
                                banner = create_banner(height = int(img.height * 0.08), width = int(img.width))
                                # banner = create_banner()
                                banner.save(banner_output_path)
                                print(f"Banner saved as {banner_output_path}")

                                image = apply_tagline_and_logo(img, banner_output_path, "logo.png", logo_position="top_right")
                                output_path = f"output_image_data{datetime.now().strftime('%Y%m%d%H%M%S')}.png"

                                image.save(output_path)
                                print(f"Image saved as {output_path}")
                                st.image(image, caption="Generated Image", use_container_width=True)
                            else:
                                st.error("Model too busy, unable to get response in less than 240 second(s).")
                            # st.image(img, caption="Generated Image", use_container_width=True)
                    else:
                        st.error(f"CSV must contain columns: {', '.join(required_columns)}")
            except Exception as e:
                st.error(f"Error reading CSV file: {e}")


    
    
    

    
    # CSV Upload Section
    
    # Load data from dataframe
    # df = pd.read_csv('output.csv')

    # # Get 5 random row indices
    # random_indices = random.sample(range(len(df)), 5)

    # # Process the selected random rows
    # for index in random_indices:
    #     row = df.iloc[index]  # Get the row using the index
    #     product = row['Product']
    #     age = row['age']
    #     location = row['location']
    #     income = row['balance']
    #     gender = row['gender']
    #     profession = row['job']

    #     # Generate image based on prompt
    #     image = save_genimage(product, age, location, income, gender, profession)
    #     # image = Image.open("input_image1.jpg")

        







