#Importing 

import easyocr
import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu
import psycopg2
from PIL import Image
import cv2
import os
import matplotlib.pyplot as plt
import re

# SETTING PAGE CONFIGURATIONS
icon = Image.open("icon.png")
st.set_page_config(page_title= "BizCardX: Extracting Business Card Data with OCR",
                   page_icon= icon,
                   layout= "wide",
                   initial_sidebar_state= "expanded")
st.markdown("<h1 style='text-align: center; color: white;'>BizCardX: Extracting Business Card Data with OCR</h1>", unsafe_allow_html=True)

# SETTING-UP BACKGROUND IMAGE
def setting_bg():
    st.markdown(f""" <style>.stApp {{
                        background:url("https://cutewallpaper.org/21/background/Digital-Background-by-Digitexx-VideoHive.jpg");
                        background-size: cover}}
                     </style>""",unsafe_allow_html=True) 
setting_bg()

SELECT = option_menu(
        menu_title = None,
        options = ["About","Upload","Modify","Deletion"],
        icons =["database","cloud-upload","pencil","trash"],
        default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "35px", "text-align": "centre", "margin": "0px", "--hover-color": "#6495ED"},
                               "icon": {"font-size": "35px"},
                               "container" : {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#6495ED"}})

# INITIALIZING THE EasyOCR READER
reader = easyocr.Reader(['en'])

#SQL connection

mydb=psycopg2.connect(host="localhost",
                        user="postgres",
                        password="priya1",
                        database="bizcardx",
                        port="5432")
mycursor=mydb.cursor()

#creating table in Database

mycursor.execute('''CREATE TABLE IF NOT EXISTS image_files
                        (Company_Name TEXT,
                         Card_Holder_Name TEXT,
                         Designation TEXT, 
                         Mobile_No VARCHAR(50),
                         Email_Address TEXT,
                         Website TEXT,
                         Address_Area TEXT,
                         City TEXT,
                         State TEXT,
                         Pincode VARCHAR(10),
                         Image BYTEA
                         )''')

mydb.commit()

if SELECT=="About":
    st.subheader("About the Application")
    st.write(" Users can save the information extracted from the card image using easy OCR. The information can be uploaded into a database (MySQL) after alterations that supports multiple entries. ")
    st.subheader("What is Easy OCR?")
    st.write("EasyOCR is a python module for extracting text from image and it is user-friendly Optical Character Recognition (OCR) technology, converting documents like scanned paper, PDFs, or digital camera images into editable and searchable data. A variety of OCR solutions, including open-source libraries, commercial software, and cloud-based services, are available. These tools are versatile recognizing printed or handwritten text, and making scanned documents editable.")
    st.subheader("Existing Data in Database")
    mycursor.execute('''Select Company_Name,Card_Holder_Name,Designation,
                         Mobile_No,Email_Address,Website,Address_Area,City,State,Pincode from image_files''')
    updated_df = pd.DataFrame(mycursor.fetchall(),columns=["Company Name","Card_Holder_Name","Designation",
                "Mobile No", "Email Address ","Website", "Address Area", "City", "State", "Pincode"])
    st.write(updated_df)

#Uploading

if SELECT=="Upload": 
    st.subheader(":black[Business Card]")
    image_files = st.file_uploader("Upload the Business Card below:", type=["png","jpg","jpeg"])
    
    def save_card(image_files):
            os.makedirs("bizcard", exist_ok=True)
            filename = os.path.join("bizcard",image_files.name)
            with open(filename, "wb") as f:
                f.write(image_files.getbuffer()
                        )
    if image_files is not None:
        col1, col2 = st.columns(2, gap="large")
        with col1:
            img = image_files.read()
            st.markdown("### Business Card has been uploaded")
            st.image(img, caption='The image has been uploaded successfully',width=500)
            save_card(image_files)
            
        with col2:
            saved_img = os.path.join(os.getcwd(), "bizcard", image_files.name)
            image = cv2.imread(saved_img)
            res = reader.readtext(saved_img)
            st.markdown("Data has been extracted from images")
    
            def image_preview(image, res):
                for (bbox, text, prob) in res:
                    # unpack the bounding box
                    (tl, tr, br, bl) = bbox
                    tl = (int(tl[0]), int(tl[1]))
                    tr = (int(tr[0]), int(tr[1]))
                    br = (int(br[0]), int(br[1]))
                    bl = (int(bl[0]), int(bl[1]))
                    cv2.rectangle(image, tl, br, (0, 255, 0), 2)
                    cv2.putText(image, text, (tl[0], tl[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                plt.rcParams['figure.figsize'] = (15, 15)
                plt.axis('off')
                plt.imshow(image)
            b=image_preview(image,res)
            st.set_option('deprecation.showPyplotGlobalUse', False)
            st.pyplot(b)
        
        # easy OCR
        saved_img = os.path.join(os.getcwd(), "bizcard", image_files.name)
        result = reader.readtext(saved_img, detail=0, paragraph=False)
    
        # CONVERTING IMAGE TO BINARY TO UPLOAD TO SQL DATABASE
        def img_to_binary(file):
            # Convert image data to binary format
            with open(file, 'rb') as file:
                binaryData = file.read()
            return binaryData
                
        data = {
                "Company_Name": [],
                "Card_Holder_Name": [],
                "Designation": [],
                "Mobile_No": [],
                "Email_Address": [],
                "Website": [],
                "Address_Area": [],
                "City": [],
                "State": [],
                "Pincode": [],
                "image": img_to_binary(saved_img)
        }

        
        def get_data(res):
                for ind, i in enumerate(res):
                    
                    # To get WEBSITE_URL
                    if "www " in i.lower() or "www." in i.lower():
                        data["Website"].append(i)
                    elif "WWW" in i:
                        data["Website"] = res[4] + "." + res[5]

                    # To get EMAIL ID
                    elif "@" in i:
                        data["Email_Address"].append(i)
                        
                    # To get MOBILE NUMBER
                    elif "-" in i:
                        data["Mobile_No"].append(i)
                        if len(data["Mobile_No"]) == 2:
                            data["Mobile_No"] = " & ".join(data["Mobile_No"])
                    # To get COMPANY NAME
                    elif ind == len(res) - 1:
                        data["Company_Name"].append(i)

                    # To get CARD HOLDER NAME
                    elif ind == 0:
                        data["Card_Holder_Name"].append(i)
                        
                    # To get DESIGNATION
                    elif ind == 1:
                        data["Designation"].append(i)
                        
                    # To get Address Area
                    if re.findall('^[0-9].+, [a-zA-Z]+', i):
                        data["Address_Area"].append(i.split(',')[0])
                    elif re.findall('[0-9] [a-zA-Z]+', i):
                        data["Address_Area"].append(i)
                
                    # To get CITY NAME
                    match1 = re.findall('.+St , ([a-zA-Z]+).+', i)
                    match2 = re.findall('.+St,, ([a-zA-Z]+).+', i)
                    match3 = re.findall('^[E].*', i)
                    if match1:
                        data["City"].append(match1[0])
                    elif match2:
                        data["City"].append(match2[0])
                    elif match3:
                        data["City"].append(match3[0])
                    
                    # To get STATE
                    state_match = re.findall('[a-zA-Z]{9} +[0-9]', i)
                    if state_match:
                        data["State"].append(i[:9])
                    elif re.findall('^[0-9].+, ([a-zA-Z]+);', i):
                        data["State"].append(i.split()[-1])
                    if len(data["State"]) == 2:
                        data["State"].pop(0)

                    # To get PINCODE
                    if len(i) >= 6 and i.isdigit():
                        data["Pincode"].append(i)
                    elif re.findall('[a-zA-Z]{9} +[0-9]', i):
                        data["Pincode"].append(i[10:])
        get_data(result)

        
        df = pd.DataFrame(data)
        st.success("### Data Extracted!")
        st.write(df)

        if st.button("Upload to Database"):
            try:
                for i, row in df.iterrows():
                    query1='''insert into image_files(Company_Name,Card_Holder_Name,Designation,
                                Mobile_No,Email_Address,Website,Address_Area,City,State,Pincode,Image)
                                values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'''
                    mycursor.execute(query1, tuple(row.values))
                    mydb.commit()

                    mycursor.execute('''SELECT Company_Name,Card_Holder_Name,Designation,
                                    Mobile_No,Email_Address,Website,Address_Area,City,State,Pincode from image_files''')
                    updated_data=mycursor.fetchall()

                    updated_df = pd.DataFrame(updated_data, columns=["Company Name","Card_Holder_Name","Designation",
                                                                "Mobile_No", "Email_Address","Website", "Address_Area", "City", "State", "Pincode"])
                    st.success("#### Uploaded to database successfully!")
                    st.write(updated_df)

            except Exception as e:
                    st.error(f"Error: {e}")
        
elif SELECT=="Modify":
    st.markdown(":black[Alter the data here]")
    try:
            mycursor.execute("SELECT Card_Holder_Name FROM image_files")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            options = ["Select Card"] + list(business_cards.keys())
            selected_card = st.selectbox("**Select a card**", options)
            if selected_card == "Select Card":
                st.write("Card not selected")
            else:
                st.markdown("#### Update or modify the data below")
                mycursor.execute('''Select Company_Name,Card_Holder_Name,Designation,
                    Mobile_No,Email_Address,Website,Address_Area,City,State,Pincode 
                    from image_files WHERE Card_Holder_Name=%s''', (selected_card,))
                result = mycursor.fetchone()

                # DISPLAYING ALL THE INFORMATIONS
                company_name = st.text_input("Company_Name", result[0])
                card_holder = st.text_input("Card_Holder_Name", result[1])
                designation = st.text_input("Designation", result[2]) 
                mobile_no = st.text_input("Mobile_No", result[3])
                email_address = st.text_input("Email_Address", result[4])
                website = st.text_input("Website", result[5])
                address_area = st.text_input("Address_Area", result[6])
                city = st.text_input("City", result[7])
                state = st.text_input("State", result[8])
                pincode = st.text_input("Pincode", result[9])



                if st.button(":black[Commit changes to DB]"):
                    
                    # Update the information for the selected business card in the database
                    mycursor.execute("""UPDATE image_files SET Company_Name=%s,Card_Holder_Name=%s,Designation=%s,Mobile_No=%s,Email_Address=%s,Website=%s,
                                    Address_Area=%s,City=%s,State=%s,Pincode=%s where Card_Holder_Name=%s""",
                                    (company_name,card_holder,designation, mobile_no, email_address, website, address_area, city, state, pincode,
                    selected_card))

                    mydb.commit()
                    st.success("Information updated successfully.")

            if st.button(":black[View data]"):
                mycursor.execute('''Select Company_Name,Card_Holder_Name,Designation,
                    Mobile_No,Email_Address,Website,Address_Area,City,State,Pincode 
                    from image_files WHERE Card_Holder_Name=%s''', (selected_card,))
                mydb.commit()
                updated_df2 = pd.DataFrame(mycursor.fetchall(),
                                        columns=["Company Name","Card_Holder_Name","Designation",
                "Mobile_No", "Email_Address","Website", "Address_Area", "City", "State", "Pincode"])
                st.write(updated_df2)
    except:
                st.warning("No data available")

               
if SELECT == "Deletion":
        st.subheader(":black[Delete the data]")
        try:
            mycursor.execute("SELECT Card_Holder_Name FROM image_files")
            result = mycursor.fetchall()
            business_cards = {}
            for row in result:
                business_cards[row[0]] = row[0]
            options = ["None"] + list(business_cards.keys())
            selected_card = st.selectbox("**Select a card**", options)
            if selected_card == "None":
                st.write("No card selected")
            else:
                st.write(f"### You have selected :green[**{selected_card}'s**] card to delete")
                st.write("#### Process to delete the card?")
                if st.button("Confirm deletion"):
                    mycursor.execute(f"DELETE FROM image_files WHERE Card_Holder_Name='{selected_card}'")
                    mydb.commit()
                    st.success("Business card information has been deleted from database")
            
            if st.button(":black[View data]"):
                mycursor.execute('''Select Company_Name,Card_Holder_Name,Designation,
                    Mobile_No,Email_Address,Website,Address_Area,City,State,Pincode 
                    from image_files WHERE Card_Holder_Name=%s''', (selected_card,))
                updated_df3 = pd.DataFrame(mycursor.fetchall(),
                                            columns=["Company Name","Card_Holder_Name","Designation",
                "Mobile_No", "Email_Address","Website", "Address_Area", "City", "State", "Pincode"])
                st.write(updated_df3)
        except:
            st.warning("No data available")
            mydb.commit()

