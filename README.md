# Clinical NLP Intelligence Pipeline

A real-time clinical document intelligence demo built for a healthcare analytics intern assessment.

## Live Demo

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-name.streamlit.app)

## What It Does

Processes clinical notes through three AI-powered NLP stages:

| Stage | Task | Healthcare Application |
|---|---|---|
| 🔍 **Entity Extraction** | Named entity recognition — extracts diagnoses, medications, labs, vitals | Risk adjustment, audit trail |
| 📋 **Clinical Summary** | Live-streaming handoff summary | Care transitions, UR review |
| 🏷️ **ICD-10 Coding** | Code suggestion with HCC flags | Payment integrity, risk adjustment |

## Data Sources

- **MTSamples** (mtsamples.com) — Real de-identified clinical transcriptions across 6 specialties
- **MIMIC-III Demo** (PhysioNet, ODC Open Database License) — 100 real ICU patient records from Beth Israel Deaconess Medical Center

## Run Locally

```bash
git clone https://github.com/YOUR_USERNAME/clinical-nlp-pipeline
cd clinical-nlp-pipeline/poc
pip install -r requirements.txt
streamlit run app.py
```

Enter your OpenAI API key in the app when prompted.

## Deploy to Streamlit Cloud (free)

1. Fork this repo
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub repo → set **Main file path** to `poc/app.py`
4. Under **Advanced settings → Secrets**, add:
   ```toml
   OPENAI_API_KEY = "sk-..."
   ```
5. Click Deploy — your app gets a public URL instantly

## Tech Stack

- **Model:** GPT-4o-mini (OpenAI)
- **Framework:** Streamlit
- **Data:** MTSamples + MIMIC-III Demo (PhysioNet)
- **Language:** Python 3.11+

## References

- Johnson et al. MIMIC-III (2016). *Scientific Data*
- Singhal et al. Med-PaLM 2 (2023). *Nature*
- Devlin et al. BERT (2019). *NAACL*
- Shrank et al. Waste in the US Healthcare System (2019). *JAMA*
