# DS-BizCardX-Extracting-Business-Card-Data-with-OCR

## What is EasyOCR?

   EasyOCR, as the name suggests, is a Python package that allows computer vision developers to effortlessly perform Optical Character Recognition.It is a Python library for Optical Character Recognition (OCR) that allows you to easily extract text from images and scanned documents. In my project I am using easyOCR to extract text from **business cards.**
   
   When it comes to OCR, EasyOCR is by far the most straightforward way to apply Optical Character Recognition:

   - The EasyOCR package can be installed with a single pip command.
   - The dependencies on the EasyOCR package are minimal, making it easy to configure your OCR development environment.
   - Once EasyOCR is installed, only one import statement is required to import the package into your project.
   - From there, all you need is two lines of code to perform OCR — one to initialize the Reader class and then another to OCR the image via the readtext function.

## Overview

This project aims to develop a Streamlit application that streamlines the extraction of relevant information from business cards uploaded by users. Leveraging the power of easyOCR, the application will intelligently extract details such as company name, cardholder name, designation, contact information, address, and more. The extracted data will be neatly displayed in a graphical user interface (GUI) for user convenience.

## Libraries/Modules used for the project!

   - Pandas - (To Create a DataFrame with the scraped data)
   - mysql.connector - (To store and retrieve the data)
   - Streamlit - (To Create Graphical user Interface)
   - EasyOCR - (To extract text from images)

## Features
### User-Friendly Interface: 
The application boasts a simple and intuitive UI that guides users seamlessly through the process of uploading a business card image and extracting information.

### Data Extraction: 
Utilizing the easyOCR library, the application extracts key details including company name, cardholder name, designation, mobile number, email address, website URL, area, city, state, and pin code.

### Database Integration: 
Users can save the extracted information into a database along with the uploaded business card image. The database, powered by SQLite or MySQL, is designed to store multiple entries, each associated with its respective business card image and extracted information.

### CRUD Operations: 
The application supports essential CRUD (Create, Read, Update, Delete) operations. Users can easily add, view, update, and delete entries through the Streamlit UI.
