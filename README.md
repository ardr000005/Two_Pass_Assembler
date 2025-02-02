# 🚀 Two Pass Assembler

## 📌 Overview

The **Two Pass Assembler** is a web-based tool built with **Django** that simulates the **first and second passes** of an assembler. It allows users to upload input files and an **operation table (OPTAB)** to generate **intermediate** and **object code** based on assembly language instructions. The application features a **user-friendly interface** for running passes and viewing results, including **symbol tables** and **program lengths**.

## ✨ Features

- 📂 **File Upload**: Upload assembly language files and an OPTAB file.
- 🔄 **Pass 1 Logic**: Generates intermediate file content and a symbol table.
- 🖥️ **Pass 2 Logic**: Uses intermediate data to produce the final object code.
- ❌ **Clear Functionality**: Resets all session data with one click.
- ⚠️ **Error Handling**: Prevents running Pass 2 without completing Pass 1.

## 🛠 Installation

To set up the **Two Pass Assembler**, follow these steps:

### ✅ Prerequisites

- 🐍 **Python 3.x**
- 🌐 **Django**

### 🚀 Steps

1. **Create a Virtual Environment**:
   ```bash
   python -m venv env
   ```
   Activate the virtual environment:
   ```bash
   source env/bin/activate  # On Windows use `env\Scripts\activate`
   ```

2. **Install Required Packages**:
   ```bash
   pip install django
   ```

3. **Run Database Migrations**:
   ```bash
   python manage.py migrate
   ```

4. **Run the Development Server**:
   ```bash
   python manage.py runserver
   ```

5. **Access the Application**:
   Open your browser and go to **`http://127.0.0.1:8000/`**.

## 📌 Usage

1. **Upload Files** 📂
   - Upload your **assembly language file** and **OPTAB file**.

2. **Run Pass 1** ▶️
   - Click **"Run Pass 1"** to process the files.
   - View the **intermediate file** and **symbol table**.

3. **Run Pass 2** 🔄
   - Click **"Run Pass 2"** to generate the **object code**.

4. **Clear Data** ❌
   - Click **"Clear"** to reset the application.

5. **Error Handling** ⚠️
   - If you try to run Pass 2 without Pass 1, an **error message** appears.

## 📝 Code Explanation

### 📌 Views (`views.py`)

- **Pass 1 Logic**
  - Reads **input and OPTAB files**.
  - Generates **intermediate content** and a **symbol table**.
  - Stores results in the **session**.

- **Pass 2 Logic**
  - Retrieves **intermediate data** and **symbol table**.
  - Generates **object code**.

- **Clear Functionality**
  - Clears all **session data**.

### 🎨 HTML Template (`single_page.html`)

- **File Input Fields** 📂 for **uploading files**.
- **Buttons** 🔘 to **run passes** and **clear data**.
- **Conditional Rendering** 👁️ shows results **only if passes are completed**.

### 🔄 Session Management

- Uses **Django sessions** to store:
  - **Intermediate content**
  - **Symbol tables**
  - **Program lengths**
  - **Object code**

## 📜 License
This project is open-source and available under the **MIT License**.

---
💡 **Happy Coding!** 🚀

