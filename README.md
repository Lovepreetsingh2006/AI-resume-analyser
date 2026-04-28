# 🚀 AI Resume Analyzer  

An intelligent **full-stack web application** that analyzes resumes and provides ATS-style feedback, scoring, and improvement suggestions for technical roles.

---

## 📌 Features  

- ✨ Upload PDF resumes  
- 📊 Resume scoring out of 100  
- 🧠 Skill detection & matching  
- 📉 Missing skills & keyword gaps  
- 🎯 Role-based analysis (Software, Data, DevOps, etc.)  
- 📈 TF-IDF similarity scoring  
- 💡 Smart suggestions for improvement  
- 📝 Downloadable report  
- 🎨 Modern UI with animations & dark mode  

---

## 🛠️ Tech Stack  

### Frontend  
- HTML  
- CSS  
- JavaScript  

### Backend  
- Python  
- Flask  

### Libraries  
- PyPDF2 (PDF text extraction)  
- scikit-learn (TF-IDF similarity)  
- Werkzeug (file handling)  

---

## 📂 Project Structure  

```
AI-Resume-Analyzer/
│
├── app.py
├── requirements.txt
├── data/
│   └── tech_jobs_dataset.json
│
├── templates/
│   └── index.html
│
├── static/
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── app.js
│
└── runstop.txt
```

---

## ⚙️ Installation & Setup  

### 1. Clone the repository  
```
git clone https://github.com/Lovepreetsingh2006/AI-resume-analyser.git
cd AI-resume-analyser
```

### 2. Install dependencies  
```
pip install -r requirements.txt
```

### 3. Run the application  
```
python app.py
```

### 4. Open in browser  
```
http://127.0.0.1:5000/
```

---

## 🧠 How It Works  

1. Upload your resume (PDF)  
2. Select a target job role  
3. System extracts text using PyPDF2  
4. Skills, education & experience are detected  
5. Resume is compared with role dataset  
6. TF-IDF calculates similarity score  
7. Final score + suggestions are generated  

---

## 📊 Scoring System  

| Component            | Weight |
|---------------------|--------|
| Skills Match        | 35%    |
| Resume Completeness | 25%    |
| Keywords            | 20%    |
| Role Similarity     | 20%    |

---

## 📸 UI Preview  

(Add your screenshots here)

- Home Page  
- Upload Section  
- Score Dashboard  
- Skills Analysis  
- Suggestions Panel  

---

## 📥 Download Report  

- Generates a `.txt` report  
- Contains full analysis  
- Easy to review offline  

---

## ⚠️ Limitations  

- Works best with text-based PDFs  
- Not optimized for scanned resumes  
- Uses TF-IDF (not deep AI models)  

---

## 🔮 Future Improvements  

- Support DOCX files  
- Add advanced NLP (spaCy / Transformers)  
- Generate PDF reports  
- Add analytics dashboard  
- Recruiter bulk screening mode  
- AI resume rewriting suggestions  

---

## 👨‍💻 Author  

Lovepreet Singh  

---

## ⭐ Contribute  

Feel free to fork this repository and improve it.  
Pull requests are welcome.  

---

## 📜 License  

This project is for educational purposes.  
