# backend/main.py
import json, os, re
from difflib import SequenceMatcher
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

# ---- Load environment ----
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---- Load JSON data ----
BASE_DIR = os.path.dirname(__file__)

TEXTS_PATH = os.path.join(BASE_DIR, "psutext.json")
PROGRAMS_PATH = os.path.join(BASE_DIR, "programs.json")
COURSES_PATH = os.path.join(BASE_DIR, "courses.json")

TEXTS, PROGRAMS, COURSES = [], [], []

if os.path.exists(TEXTS_PATH):
    with open(TEXTS_PATH, "r") as f:
        TEXTS = json.load(f)
if os.path.exists(PROGRAMS_PATH):
    with open(PROGRAMS_PATH, "r") as f:
        PROGRAMS = json.load(f)
if os.path.exists(COURSES_PATH):
    with open(COURSES_PATH, "r") as f:
        COURSES = json.load(f)

# ---- FastAPI setup ----
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---- Pydantic Model ----
class Message(BaseModel):
    user_input: str

# ---- Utility Functions ----
def normalize(text: str):
    text = text.lower()
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\b(bs|ba|bfa|bnurs|bmus|bphil|mba|program|major)\b", "", text)
    return " ".join(text.split())

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

# ---- Find Program ----
def find_program_in_text(query: str):
    q = normalize(query)
    best_match = None
    best_score = 0

    for p in PROGRAMS:
        name = normalize(p["name"].split(",")[0])
        if re.search(rf"\b{name}\b", q):
            return p
        score = similarity(q, name)
        if score > best_score:
            best_score = score
            best_match = p
    if best_score > 0.65:
        return best_match
    return None

# ---- Find Course ----
def find_course_in_text(query):
    """Detect course codes like IST 210 or CHEM110 and return match."""
    match = re.search(r"\b([A-Z]{2,4})\s?(\d{2,3})\b", query.upper())
    if not match:
        return None
    code = f"{match.group(1)} {match.group(2)}".strip()
    for c in COURSES:
        if code.replace(" ", "") in c["code"].replace(" ", ""):
            return c
    return None

# ---- Tuition Helpers ----
TUITION_LINK = "https://tuition.psu.edu/calculator"

def is_tuition_question(q: str):
    q = q.lower()
    return any(w in q for w in ["tuition", "cost", "fee", "in-state", "out-of-state", "afford"])

# ---- Main Chat Endpoint ----
@app.post("/chat")
async def chat(message: Message):
    user_q = message.user_input.strip()

    # 0️⃣ Course lookup
    course_match = find_course_in_text(user_q)
    if course_match:
        prereq = course_match.get("prerequisite", "")
        desc = course_match.get("description", "")
        msg = (
            f"{course_match['code']} — {course_match['title']}\n\n"
            f"{desc}\n\n{prereq or 'No specific prerequisites listed.'}\n"
            f"Source: {course_match['link']}"
        )
        return {"response": msg, "follow_ups": ["Related Majors", "Full Course List"]}

    # 1️⃣ Tuition logic
    if is_tuition_question(user_q):
        tuition_prompt = (
            f"The user asked: '{user_q}'. "
            "Explain briefly how Penn State tuition works — clarify in-state vs. out-of-state costs, "
            "and that rates vary by campus and program. "
            f"End the response with: 'Use the official Tuition Calculator here: {TUITION_LINK}'."
        )
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a factual Penn State advisor."},
                {"role": "user", "content": tuition_prompt},
            ],
            temperature=0.6,
        )
        return {
            "response": completion.choices[0].message.content,
            "follow_ups": ["Scholarships", "Financial Aid"],
        }

    # 2️⃣ Program logic
    match = find_program_in_text(user_q)
    if match:
        text = next((t["text"] for t in TEXTS if match["name"].lower() in t["name"].lower()), "")
        if text:
            prompt = (
                f"The user asked: '{user_q}'. "
                f"Here is official PSU Bulletin info for {match['name']}:\n\n{text}\n\n"
                "Summarize what this major focuses on and what students study or prepare for. "
                f"Keep it factual, concise (2–4 sentences), and end with: 'Source: {match['link']}'."
            )
        else:
            prompt = (
                f"The user asked about {match['name']}. "
                "Provide a concise, factual overview of what this Penn State major covers. "
                f"Include the Bulletin link: {match['link']}."
            )
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a Penn State academic advisor."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.6,
        )
        return {
            "response": completion.choices[0].message.content,
            "follow_ups": ["Core Courses", "Career Options", "Campuses Offered"],
        }

    # 3️⃣ General fallback
    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful Penn State advisor."},
            {"role": "user", "content": user_q},
        ],
        temperature=0.7,
    )
    return {
        "response": completion.choices[0].message.content,
        "follow_ups": ["Majors", "Admissions", "Tuition"],
    }
