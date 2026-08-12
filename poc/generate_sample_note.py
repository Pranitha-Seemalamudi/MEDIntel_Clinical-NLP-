from reportlab.lib.pagesizes import LETTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER

OUTPUT = "sample_clinical_note.pdf"

doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=LETTER,
    leftMargin=0.85*inch,
    rightMargin=0.85*inch,
    topMargin=0.8*inch,
    bottomMargin=0.8*inch,
)

styles = getSampleStyleSheet()

# Custom styles
header_style = ParagraphStyle(
    "header", fontSize=9, textColor=colors.HexColor("#555555"),
    fontName="Helvetica", leading=13,
)
title_style = ParagraphStyle(
    "title", fontSize=15, fontName="Helvetica-Bold",
    textColor=colors.HexColor("#1a0a3d"), spaceAfter=2,
)
section_style = ParagraphStyle(
    "section", fontSize=9, fontName="Helvetica-Bold",
    textColor=colors.HexColor("#d4007a"), spaceBefore=10, spaceAfter=3,
    letterSpacing=1,
)
body_style = ParagraphStyle(
    "body", fontSize=9.5, fontName="Helvetica",
    textColor=colors.HexColor("#1a1a2e"), leading=15, spaceAfter=4,
)
small_style = ParagraphStyle(
    "small", fontSize=8.5, fontName="Helvetica",
    textColor=colors.HexColor("#555555"), leading=13,
)

story = []

# ── Hospital header ──
story.append(Paragraph("BETH ISRAEL GENERAL HOSPITAL", ParagraphStyle(
    "hosp", fontSize=13, fontName="Helvetica-Bold",
    textColor=colors.HexColor("#1a0a3d"), alignment=TA_CENTER,
)))
story.append(Paragraph("Department of Internal Medicine · 330 Brookline Ave, Boston, MA 02215", ParagraphStyle(
    "hosp2", fontSize=8.5, fontName="Helvetica",
    textColor=colors.HexColor("#666666"), alignment=TA_CENTER, spaceAfter=6,
)))
story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor("#1a0a3d")))
story.append(Spacer(1, 6))

# ── Patient info table ──
patient_data = [
    ["PATIENT", "Margaret Sullivan", "MRN", "MRN-0094821"],
    ["DOB", "September 12, 1958 (Age 67)", "SEX", "Female"],
    ["ADMIT DATE", "August 5, 2026", "DISCHARGE DATE", "August 9, 2026"],
    ["ATTENDING", "Dr. Priya Nair, MD", "INSURANCE", "Medicare Part A/B"],
]
pt_table = Table(patient_data, colWidths=[1.1*inch, 2.5*inch, 1.1*inch, 2.1*inch])
pt_table.setStyle(TableStyle([
    ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
    ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8.5),
    ("TEXTCOLOR", (0,0), (0,-1), colors.HexColor("#1a0a3d")),
    ("TEXTCOLOR", (2,0), (2,-1), colors.HexColor("#1a0a3d")),
    ("TEXTCOLOR", (1,0), (1,-1), colors.HexColor("#1a1a2e")),
    ("TEXTCOLOR", (3,0), (3,-1), colors.HexColor("#1a1a2e")),
    ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#f8f5ff"), colors.white]),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
]))
story.append(pt_table)
story.append(Spacer(1, 4))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#ddccee")))

# ── Title ──
story.append(Spacer(1, 8))
story.append(Paragraph("DISCHARGE SUMMARY", title_style))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#d4007a")))
story.append(Spacer(1, 8))

# ── Chief Complaint ──
story.append(Paragraph("CHIEF COMPLAINT", section_style))
story.append(Paragraph(
    "Acute onset chest pain radiating to left arm, diaphoresis, and shortness of breath "
    "for approximately 3 hours prior to presentation.",
    body_style,
))

# ── HPI ──
story.append(Paragraph("HISTORY OF PRESENT ILLNESS", section_style))
story.append(Paragraph(
    "Margaret Sullivan is a 67-year-old female with a past medical history significant for "
    "type 2 diabetes mellitus (A1C 9.1%), hypertension, hyperlipidemia, and a 30-pack-year "
    "smoking history (quit 2018) who presented to the emergency department via EMS with acute "
    "onset substernal chest pain 8/10 in severity, radiating to the left arm and jaw, associated "
    "with diaphoresis and dyspnea. Initial 12-lead ECG demonstrated ST-elevation in leads II, III, "
    "and aVF, consistent with inferior STEMI. Patient was taken emergently to the cardiac "
    "catheterization laboratory.",
    body_style,
))

# ── Vitals ──
story.append(Paragraph("VITAL SIGNS ON ADMISSION", section_style))
vitals = [
    ["BP", "162/98 mmHg", "HR", "104 bpm", "RR", "22/min"],
    ["SpO2", "91% (room air)", "Temp", "98.9°F", "Weight", "84 kg"],
]
vt = Table(vitals, colWidths=[0.5*inch, 1.3*inch, 0.5*inch, 1.1*inch, 0.5*inch, 0.9*inch])
vt.setStyle(TableStyle([
    ("FONTNAME", (0,0), (-1,-1), "Helvetica"),
    ("FONTNAME", (0,0), (0,-1), "Helvetica-Bold"),
    ("FONTNAME", (2,0), (2,-1), "Helvetica-Bold"),
    ("FONTNAME", (4,0), (4,-1), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8.5),
    ("TEXTCOLOR", (0,0), (-1,-1), colors.HexColor("#1a1a2e")),
    ("BACKGROUND", (0,0), (-1,-1), colors.HexColor("#f8f5ff")),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#ddccee")),
]))
story.append(vt)

# ── Diagnostic Results ──
story.append(Paragraph("DIAGNOSTIC RESULTS", section_style))
story.append(Paragraph(
    "<b>ECG:</b> ST-elevation leads II, III, aVF — inferior STEMI confirmed.<br/>"
    "<b>Troponin I (peak):</b> 18.4 ng/mL (HIGH — normal &lt;0.04)<br/>"
    "<b>BNP:</b> 620 pg/mL (HIGH)<br/>"
    "<b>HbA1c:</b> 9.1% (HIGH — uncontrolled diabetes)<br/>"
    "<b>LDL:</b> 148 mg/dL (HIGH)<br/>"
    "<b>Creatinine:</b> 1.2 mg/dL (within normal limits)<br/>"
    "<b>Echocardiogram:</b> EF 40%, inferior wall hypokinesis, mild mitral regurgitation.",
    body_style,
))

# ── Diagnoses ──
story.append(Paragraph("DIAGNOSES", section_style))
diagnoses = [
    "1.  ST-Elevation Myocardial Infarction (STEMI) — inferior wall",
    "2.  Coronary artery disease — right coronary artery 95% occlusion",
    "3.  Acute systolic heart failure (EF 40%)",
    "4.  Type 2 diabetes mellitus, poorly controlled (HbA1c 9.1%)",
    "5.  Hypertension",
    "6.  Hyperlipidemia",
    "7.  Mild mitral regurgitation",
]
for dx in diagnoses:
    story.append(Paragraph(dx, body_style))

# ── Hospital Course ──
story.append(Paragraph("HOSPITAL COURSE", section_style))
story.append(Paragraph(
    "Patient underwent emergent percutaneous coronary intervention (PCI) with placement of "
    "a drug-eluting stent to the right coronary artery with TIMI 3 flow restored. "
    "Post-procedure, patient was monitored in the cardiac ICU for 48 hours. "
    "Aspirin 325 mg and ticagrelor 90 mg BID initiated for dual antiplatelet therapy. "
    "IV metoprolol transitioned to oral. Lisinopril initiated for ACE inhibition post-MI. "
    "Atorvastatin increased to 80 mg. Endocrinology consulted — insulin glargine 12 units "
    "at bedtime initiated for glycemic control. Patient remained hemodynamically stable "
    "and was transferred to the step-down unit on day 3.",
    body_style,
))

# ── Discharge Medications ──
story.append(Paragraph("DISCHARGE MEDICATIONS", section_style))
meds = [
    ("Aspirin", "81 mg", "oral", "daily"),
    ("Ticagrelor (Brilinta)", "90 mg", "oral", "twice daily"),
    ("Metoprolol succinate", "50 mg", "oral", "daily"),
    ("Lisinopril", "5 mg", "oral", "daily"),
    ("Atorvastatin", "80 mg", "oral", "at bedtime"),
    ("Insulin glargine", "12 units", "subcutaneous", "at bedtime"),
    ("Nitroglycerin SL", "0.4 mg", "sublingual", "PRN chest pain"),
]
med_data = [["Medication", "Dose", "Route", "Frequency"]] + [list(m) for m in meds]
mt = Table(med_data, colWidths=[2.0*inch, 0.9*inch, 1.3*inch, 1.6*inch])
mt.setStyle(TableStyle([
    ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#1a0a3d")),
    ("TEXTCOLOR", (0,0), (-1,0), colors.white),
    ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
    ("FONTSIZE", (0,0), (-1,-1), 8.5),
    ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.HexColor("#f8f5ff"), colors.white]),
    ("TOPPADDING", (0,0), (-1,-1), 4),
    ("BOTTOMPADDING", (0,0), (-1,-1), 4),
    ("LEFTPADDING", (0,0), (-1,-1), 6),
    ("GRID", (0,0), (-1,-1), 0.5, colors.HexColor("#ddccee")),
]))
story.append(mt)

# ── Follow-up ──
story.append(Paragraph("FOLLOW-UP INSTRUCTIONS", section_style))
followups = [
    "• Cardiology clinic in 5 days — repeat echocardiogram, titrate lisinopril",
    "• Primary care in 2 weeks — recheck BMP, lipid panel, HbA1c",
    "• Cardiac rehabilitation program — referral placed",
    "• DO NOT stop ticagrelor or aspirin without cardiology approval (stent thrombosis risk)",
    "• Return to ED immediately for: chest pain, shortness of breath, palpitations, syncope",
]
for f in followups:
    story.append(Paragraph(f, body_style))

# ── Signature ──
story.append(Spacer(1, 12))
story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#ddccee")))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "Electronically signed by: <b>Dr. Priya Nair, MD</b> — Board Certified Internal Medicine &amp; Cardiology<br/>"
    "Date: August 9, 2026 · Beth Israel General Hospital",
    small_style,
))

doc.build(story)
print(f"PDF saved: {OUTPUT}")
