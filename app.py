import json
import os
import re
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_file
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity

    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "uploads"
REPORT_FOLDER = BASE_DIR / "reports"
DATASET_PATH = BASE_DIR / "data" / "tech_jobs_dataset.json"
ALLOWED_EXTENSIONS = {"pdf"}


SKILL_ALIASES = {
    "Python": [r"\bpython\b", r"\bpython3\b"],
    "Java": [r"\bjava\b"],
    "C++": [r"\bc\+\+\b", r"\bcpp\b"],
    "JavaScript": [r"\bjavascript\b", r"\bjs\b"],
    "TypeScript": [r"\btypescript\b", r"\bts\b"],
    "HTML": [r"\bhtml5?\b"],
    "CSS": [r"\bcss3?\b"],
    "React": [r"\breact(?:\.js)?\b"],
    "Node.js": [r"\bnode(?:\.js|js)?\b"],
    "Express": [r"\bexpress(?:\.js|js)?\b"],
    "Flask": [r"\bflask\b"],
    "Django": [r"\bdjango\b"],
    "FastAPI": [r"\bfastapi\b"],
    "Machine Learning": [r"\bmachine learning\b", r"\bml\b"],
    "Deep Learning": [r"\bdeep learning\b", r"\bdl\b"],
    "Pandas": [r"\bpandas\b"],
    "NumPy": [r"\bnumpy\b"],
    "Scikit-learn": [r"\bscikit[- ]learn\b", r"\bsklearn\b"],
    "TensorFlow": [r"\btensorflow\b", r"\btf\b"],
    "PyTorch": [r"\bpytorch\b"],
    "NLP": [r"\bnlp\b", r"\bnatural language processing\b"],
    "SQL": [r"\bsql\b", r"\bmysql\b", r"\bpostgresql\b", r"\bpostgres\b"],
    "MongoDB": [r"\bmongodb\b", r"\bmongo\b"],
    "REST API": [r"\brest api\b", r"\brestful api\b", r"\bapi development\b"],
    "API Testing": [r"\bapi testing\b", r"\bpostman\b", r"\bservice testing\b"],
    "Git": [r"\bgit\b", r"\bgithub\b", r"\bgitlab\b"],
    "Docker": [r"\bdocker\b", r"\bcontainerization\b"],
    "AWS": [r"\baws\b", r"\bamazon web services\b"],
    "Azure": [r"\bazure\b"],
    "GCP": [r"\bgcp\b", r"\bgoogle cloud\b"],
    "OOP": [r"\boop\b", r"\bobject oriented\b"],
    "System Design": [r"\bsystem design\b", r"\bscalable systems\b"],
    "Testing": [r"\btesting\b", r"\bunit test(?:ing)?\b", r"\bqa\b", r"\bjest\b", r"\bpytest\b"],
    "Algorithms": [r"\balgorithms?\b"],
    "Data Structures": [r"\bdata structures?\b"],
    "Data Visualization": [r"\bdata visualization\b", r"\bdashboard(s)?\b", r"\btableau\b", r"\bpower bi\b"],
    "Statistics": [r"\bstatistics\b", r"\bstatistical\b"],
    "Power BI": [r"\bpower bi\b"],
    "Tableau": [r"\btableau\b"],
    "Bootstrap": [r"\bbootstrap\b"],
    "CI/CD": [r"\bci/cd\b", r"\bcontinuous integration\b", r"\bcontinuous delivery\b", r"\bdeployment pipeline(s)?\b"],
    "ETL": [r"\betl\b", r"\bdata pipeline(s)?\b"],
    "Next.js": [r"\bnext(?:\.js|js)?\b"],
    "Tailwind CSS": [r"\btailwind(?:\s*css)?\b"],
    "Responsive Design": [r"\bresponsive design\b", r"\bresponsive ui\b"],
    "Accessibility": [r"\baccessibility\b", r"\ba11y\b"],
    "Figma": [r"\bfigma\b"],
    "Database Design": [r"\bdatabase design\b", r"\bschema design\b", r"\bdata modeling\b"],
    "Authentication": [r"\bauthentication\b", r"\boauth\b", r"\bjwt\b"],
    "Redis": [r"\bredis\b"],
    "GraphQL": [r"\bgraphql\b"],
    "Excel": [r"\bexcel\b", r"\bmicrosoft excel\b"],
    "Data Analysis": [r"\bdata analysis\b", r"\banalytics\b"],
    "A/B Testing": [r"\ba\/b testing\b", r"\bab testing\b", r"\bexperimentation\b"],
    "Feature Engineering": [r"\bfeature engineering\b"],
    "Data Warehousing": [r"\bdata warehousing\b", r"\bwarehouse\b"],
    "MLOps": [r"\bmlops\b", r"\bmodel ops\b", r"\bmachine learning operations\b"],
    "Kubernetes": [r"\bkubernetes\b", r"\bk8s\b"],
    "Airflow": [r"\bairflow\b", r"\bapache airflow\b"],
    "Terraform": [r"\bterraform\b", r"\binfrastructure as code\b"],
    "Monitoring": [r"\bmonitoring\b", r"\bobservability\b", r"\balerting\b"],
    "Bash": [r"\bbash\b", r"\bshell scripting\b"],
    "Jenkins": [r"\bjenkins\b"],
    "GitHub Actions": [r"\bgithub actions\b"],
    "Selenium": [r"\bselenium\b"],
    "Regression Testing": [r"\bregression testing\b", r"\bregression suite\b"],
    "Bug Tracking": [r"\bbug tracking\b", r"\bdefect tracking\b", r"\bjira\b"],
    "Documentation": [r"\bdocumentation\b", r"\btechnical writing\b"],
    "Performance Testing": [r"\bperformance testing\b", r"\bload testing\b"],
    "Network Security": [r"\bnetwork security\b"],
    "SIEM": [r"\bsiem\b", r"\bsecurity information and event management\b"],
    "Incident Response": [r"\bincident response\b"],
    "Risk Assessment": [r"\brisk assessment\b"],
    "Identity and Access Management": [r"\bidentity and access management\b", r"\biam\b"],
    "Security Monitoring": [r"\bsecurity monitoring\b", r"\blog analysis\b"],
    "Splunk": [r"\bsplunk\b"],
    "Cloud Security": [r"\bcloud security\b"],
    "Compliance": [r"\bcompliance\b", r"\bsoc 2\b", r"\biso 27001\b"],
    "Forensics": [r"\bforensics\b", r"\bdigital forensics\b"],
    "Linux": [r"\blinux\b"],
    "Communication": [r"\bcommunication\b", r"\bstakeholder communication\b"],
}


SECTION_ALIASES = {
    "education": ["education", "academic background", "academics", "qualification"],
    "experience": [
        "experience",
        "work experience",
        "employment",
        "professional experience",
        "internship",
    ],
    "projects": ["projects", "personal projects", "academic projects"],
    "skills": ["skills", "technical skills", "core competencies", "technologies"],
    "certifications": ["certifications", "certificates", "licenses"],
}


ACTION_VERBS = {
    "built",
    "created",
    "developed",
    "designed",
    "implemented",
    "improved",
    "led",
    "optimized",
    "managed",
    "delivered",
    "automated",
    "launched",
    "architected",
    "streamlined",
    "deployed",
}


def load_tech_roles() -> dict:
    with DATASET_PATH.open(encoding="utf-8") as dataset_file:
        return json.load(dataset_file)


def normalize_term(term: str) -> str:
    return re.sub(r"\s+", " ", term).strip(" ,;\n\t")


def dedupe_preserve_order(items: list[str]) -> list[str]:
    seen = set()
    results = []
    for item in items:
        compact = normalize_term(item)
        if compact and compact.lower() not in seen:
            seen.add(compact.lower())
            results.append(compact)
    return results


TECH_ROLE_DATA = load_tech_roles()


def build_general_skill_catalog(role_data: dict) -> set[str]:
    seed_skills = {
        "Python",
        "Java",
        "C++",
        "JavaScript",
        "TypeScript",
        "HTML",
        "CSS",
        "React",
        "Node.js",
        "Express",
        "Flask",
        "Django",
        "Machine Learning",
        "Deep Learning",
        "Pandas",
        "NumPy",
        "Scikit-learn",
        "TensorFlow",
        "PyTorch",
        "NLP",
        "SQL",
        "MongoDB",
        "Git",
        "Docker",
        "Kubernetes",
        "AWS",
        "Azure",
        "GCP",
        "REST API",
        "GraphQL",
        "Linux",
        "OOP",
        "System Design",
        "Testing",
        "Statistics",
        "Algorithms",
        "Data Structures",
        "Communication",
        "Leadership",
    }

    for role in role_data.values():
        for field in ("must_have_skills", "nice_to_have_skills", "keywords", "related_tools"):
            seed_skills.update(role.get(field, []))

    return seed_skills


GENERAL_SKILLS = build_general_skill_catalog(TECH_ROLE_DATA)


app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
app.config["MAX_CONTENT_LENGTH"] = 10 * 1024 * 1024


UPLOAD_FOLDER.mkdir(exist_ok=True)
REPORT_FOLDER.mkdir(exist_ok=True)


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def extract_text_from_pdf(file_path: Path) -> str:
    reader = PdfReader(str(file_path))
    pages = []

    for page in reader.pages:
        pages.append(page.extract_text() or "")

    return normalize_text("\n".join(pages))


def normalize_text(text: str) -> str:
    cleaned = text.replace("\x00", " ")
    cleaned = re.sub(r"\r", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def parse_custom_terms(raw_value: str) -> list[str]:
    if not raw_value:
        return []
    parts = re.split(r"[\n,;|]+", raw_value)
    return dedupe_preserve_order([part for part in parts if normalize_term(part)])


def contains_section(text: str, aliases: list[str]) -> bool:
    lowered = text.lower()
    return any(re.search(rf"(^|\n)\s*{re.escape(alias)}\s*($|\n)", lowered) or alias in lowered for alias in aliases)


def extract_section_block(text: str, section_name: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    aliases = [name.lower() for name in SECTION_ALIASES[section_name]]
    all_heading_aliases = {
        alias
        for alias_group in SECTION_ALIASES.values()
        for alias in alias_group
    }

    start_index = None
    for index, line in enumerate(lines):
        normalized = re.sub(r"[^a-z ]", "", line.lower()).strip()
        if normalized in aliases:
            start_index = index + 1
            break

    if start_index is None:
        return ""

    section_lines = []
    for line in lines[start_index:]:
        normalized = re.sub(r"[^a-z ]", "", line.lower()).strip()
        if normalized in all_heading_aliases:
            break
        section_lines.append(line)

    return "\n".join(section_lines[:10]).strip()


def build_skill_patterns(skill: str) -> list[str]:
    canonical = normalize_term(skill)
    patterns = SKILL_ALIASES.get(canonical)
    if patterns:
        return patterns

    escaped = re.escape(canonical.lower()).replace(r"\ ", r"\s+")
    return [rf"\b{escaped}\b"]


def term_in_text(text: str, term: str) -> bool:
    lowered = text.lower()
    return any(re.search(pattern, lowered, re.IGNORECASE) for pattern in build_skill_patterns(term))


def find_matching_terms(text: str, terms: list[str]) -> tuple[list[str], list[str]]:
    matches = []
    missing = []

    for term in dedupe_preserve_order(terms):
        if term_in_text(text, term):
            matches.append(term)
        else:
            missing.append(term)

    return matches, missing


def find_skills(text: str, custom_skills: list[str] | None = None) -> list[str]:
    skill_catalog = sorted(GENERAL_SKILLS.union(set(custom_skills or [])))
    return [skill for skill in skill_catalog if term_in_text(text, skill)]


def extract_education(text: str) -> list[str]:
    block = extract_section_block(text, "education")
    entries = []

    if block:
        entries.extend([line for line in block.splitlines() if len(line) > 3])
    else:
        education_patterns = [
            r"\b(b\.?tech|bachelor|master|m\.?tech|mba|phd|bsc|msc|be|me)\b.*",
            r".*\b(university|college|institute|school)\b.*",
        ]
        for line in text.splitlines():
            stripped = line.strip()
            if any(re.search(pattern, stripped, re.IGNORECASE) for pattern in education_patterns):
                entries.append(stripped)

    return dedupe_preserve_order(entries)[:5]


def extract_experience(text: str) -> list[str]:
    block = extract_section_block(text, "experience")
    entries = []

    if block:
        entries.extend([line for line in block.splitlines() if len(line) > 3])
    else:
        experience_patterns = [
            r".*\b(years?|yrs?)\b.*\b(experience)\b.*",
            r".*\b(intern|engineer|developer|analyst|scientist|manager)\b.*",
            r".*\b(implemented|developed|built|led|designed|automated|deployed)\b.*",
        ]
        for line in text.splitlines():
            stripped = line.strip()
            if any(re.search(pattern, stripped, re.IGNORECASE) for pattern in experience_patterns):
                entries.append(stripped)

    return dedupe_preserve_order(entries)[:6]


def compute_keyword_density(text: str, keywords: list[str]) -> dict:
    matches, missing = find_matching_terms(text, keywords)
    return {
        "matched": matches,
        "missing": missing,
        "coverage": round((len(matches) / max(len(keywords), 1)) * 100),
        "mentions": len(matches),
        "total_words": max(len(text.split()), 1),
    }


def build_similarity_target(role_data: dict, custom_keywords: list[str], custom_skills: list[str]) -> str:
    parts = [
        role_data.get("profile", ""),
        " ".join(role_data.get("must_have_skills", [])),
        " ".join(role_data.get("nice_to_have_skills", [])),
        " ".join(role_data.get("keywords", [])),
        " ".join(role_data.get("related_tools", [])),
        " ".join(custom_keywords),
        " ".join(custom_skills),
    ]
    return " ".join(part for part in parts if part).strip()


def compute_role_similarity(text: str, role_data: dict, custom_keywords: list[str], custom_skills: list[str]) -> dict:
    target_text = build_similarity_target(role_data, custom_keywords, custom_skills)

    if SKLEARN_AVAILABLE and target_text:
        vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
        matrix = vectorizer.fit_transform([text, target_text])
        similarity = float(cosine_similarity(matrix[0:1], matrix[1:2])[0][0])
        method = "TF-IDF semantic similarity"
    else:
        resume_tokens = set(re.findall(r"[a-zA-Z][a-zA-Z\+\#\./-]+", text.lower()))
        target_tokens = set(re.findall(r"[a-zA-Z][a-zA-Z\+\#\./-]+", target_text.lower()))
        similarity = len(resume_tokens & target_tokens) / max(len(target_tokens), 1)
        method = "Token overlap fallback"

    return {
        "score": max(0, min(round(similarity * 100), 100)),
        "method": method,
    }


def calculate_score(
    text: str,
    required_skills: list[str],
    optional_skills: list[str],
    matched_required: list[str],
    matched_optional: list[str],
    keyword_terms: list[str],
    present_sections: dict,
    missing_sections: list[str],
    keyword_gap: list[str],
    role_similarity: int,
) -> dict:
    required_score = round((len(matched_required) / max(len(required_skills), 1)) * 25)
    optional_score = round((len(matched_optional) / max(len(optional_skills), 1)) * 10)
    skill_score = required_score + optional_score

    completeness_items = [
        present_sections["education"],
        present_sections["experience"],
        present_sections["projects"],
        present_sections["skills"],
        present_sections["certifications"],
    ]
    completeness_score = round((sum(completeness_items) / len(completeness_items)) * 25)

    lowered = text.lower()
    keyword_hits = sum(1 for term in keyword_terms if term_in_text(lowered, term))
    action_verb_bonus = 2 if any(verb in lowered for verb in ACTION_VERBS) else 0
    keyword_score = min(round((keyword_hits / max(len(keyword_terms), 1)) * 18) + action_verb_bonus, 20)

    similarity_score = round((role_similarity / 100) * 20)

    penalty = 0
    if len(text.split()) < 180:
        penalty += 4
    if missing_sections:
        penalty += min(len(missing_sections) * 2, 6)
    if len(keyword_gap) >= max(4, len(keyword_terms) // 3):
        penalty += 3

    total = max(0, min(skill_score + completeness_score + keyword_score + similarity_score - penalty, 100))

    return {
        "skills": skill_score,
        "completeness": completeness_score,
        "keywords": keyword_score,
        "similarity": similarity_score,
        "penalty": penalty,
        "total": total,
    }


def build_suggestions(
    text: str,
    missing_required: list[str],
    missing_optional: list[str],
    missing_sections: list[str],
    keyword_gap: list[str],
    score: int,
    role_similarity: int,
    custom_keywords: list[str],
) -> list[str]:
    suggestions = []
    lowered = text.lower()

    if missing_required:
        suggestions.append(
            f"Strengthen role fit by adding experience tied to core skills like {', '.join(missing_required[:4])}."
        )
    if missing_optional:
        suggestions.append(
            f"Consider adding adjacent tools or technologies such as {', '.join(missing_optional[:3])} if you have used them."
        )
    if "Projects" in missing_sections:
        suggestions.append("Include a projects section to show practical impact and problem-solving.")
    if "Skills" in missing_sections:
        suggestions.append("Add a dedicated skills section so recruiters can scan your strengths quickly.")
    if "Certifications" in missing_sections:
        suggestions.append("Mention relevant certifications if you have them to strengthen credibility.")
    if not any(verb in lowered for verb in ACTION_VERBS):
        suggestions.append("Use stronger action verbs like built, developed, optimized, or implemented.")
    if len(text.split()) < 180:
        suggestions.append("Add more measurable achievements and context to make the resume feel complete.")
    if role_similarity < 55:
        suggestions.append("Tailor your summary and project bullets more closely to the target tech role language.")
    if keyword_gap:
        suggestions.append(
            f"Mirror important role keywords such as {', '.join(keyword_gap[:4])} where they genuinely match your experience."
        )
    if custom_keywords and any(keyword not in lowered for keyword in [item.lower() for item in custom_keywords[:3]]):
        suggestions.append("You added custom keywords. Reuse those exact phrases in results-driven bullet points when relevant.")
    if score >= 85:
        suggestions.append("Your resume is already strong. Focus on tailoring achievements to the specific company or stack.")

    return suggestions[:7]


def build_summary(role: str, score: int, matched_required: list[str], missing_sections: list[str], role_similarity: int) -> str:
    section_note = "all key sections are present" if not missing_sections else f"missing {', '.join(missing_sections).lower()}"
    return (
        f"This resume scores {score}/100 for the {role} role, matches {len(matched_required)} core dataset skills, "
        f"{section_note}, and shows a role-fit similarity of {role_similarity}%."
    )


def analyze_resume_text(text: str, role: str, custom_skills: list[str], custom_keywords: list[str]) -> dict:
    role_data = TECH_ROLE_DATA[role]

    required_skills = dedupe_preserve_order(role_data.get("must_have_skills", []) + custom_skills)
    optional_skills = role_data.get("nice_to_have_skills", [])
    role_keywords = dedupe_preserve_order(role_data.get("keywords", []) + role_data.get("related_tools", []) + custom_keywords)

    found_skills = find_skills(text, custom_skills)
    matched_required, missing_required = find_matching_terms(text, required_skills)
    matched_optional, missing_optional = find_matching_terms(text, optional_skills)
    keyword_metrics = compute_keyword_density(text, role_keywords)
    role_similarity = compute_role_similarity(text, role_data, custom_keywords, custom_skills)
    related_tools_found, _ = find_matching_terms(text, role_data.get("related_tools", []))

    matching_skills = dedupe_preserve_order(matched_required + matched_optional)
    missing_skills = dedupe_preserve_order(missing_required + missing_optional)

    education = extract_education(text)
    experience = extract_experience(text)

    present_sections = {
        section: contains_section(text, aliases)
        for section, aliases in SECTION_ALIASES.items()
    }
    missing_sections = [
        "Projects" if not present_sections["projects"] else None,
        "Skills" if not present_sections["skills"] else None,
        "Certifications" if not present_sections["certifications"] else None,
    ]
    missing_sections = [section for section in missing_sections if section]

    score_breakdown = calculate_score(
        text=text,
        required_skills=required_skills,
        optional_skills=optional_skills,
        matched_required=matched_required,
        matched_optional=matched_optional,
        keyword_terms=role_keywords,
        present_sections=present_sections,
        missing_sections=missing_sections,
        keyword_gap=keyword_metrics["missing"],
        role_similarity=role_similarity["score"],
    )

    suggestions = build_suggestions(
        text=text,
        missing_required=missing_required,
        missing_optional=missing_optional,
        missing_sections=missing_sections,
        keyword_gap=keyword_metrics["missing"],
        score=score_breakdown["total"],
        role_similarity=role_similarity["score"],
        custom_keywords=custom_keywords,
    )

    role_overview = {
        "category": role_data.get("category", "Tech"),
        "market_signal": role_data.get("market_signal", "Strong demand"),
        "outlook_score": role_data.get("outlook_score", 80),
        "related_tools": role_data.get("related_tools", []),
        "required_skill_count": len(required_skills),
        "optional_skill_count": len(optional_skills),
    }

    return {
        "role": role,
        "role_overview": role_overview,
        "score": score_breakdown["total"],
        "score_breakdown": score_breakdown,
        "skills_found": found_skills,
        "matching_skills": matching_skills,
        "missing_skills": missing_skills,
        "matched_required_skills": matched_required,
        "missing_required_skills": missing_required,
        "matched_optional_skills": matched_optional,
        "missing_optional_skills": missing_optional,
        "education": education,
        "experience": experience,
        "missing_sections": missing_sections,
        "keyword_gap": keyword_metrics["missing"][:10],
        "keyword_coverage": keyword_metrics["coverage"],
        "keyword_matches": keyword_metrics["matched"],
        "role_similarity": role_similarity,
        "custom_skills": custom_skills,
        "custom_keywords": custom_keywords,
        "related_tools_found": related_tools_found,
        "suggestions": suggestions,
        "summary": build_summary(
            role=role,
            score=score_breakdown["total"],
            matched_required=matched_required,
            missing_sections=missing_sections,
            role_similarity=role_similarity["score"],
        ),
    }


def create_report(analysis: dict, original_filename: str) -> tuple[str, Path]:
    report_id = uuid.uuid4().hex
    report_path = REPORT_FOLDER / f"resume_report_{report_id}.txt"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    report_text = f"""AI Resume Analyzer Report
Generated: {timestamp}
Source File: {original_filename}
Target Role: {analysis['role']}
Category: {analysis['role_overview']['category']}
Market Signal: {analysis['role_overview']['market_signal']}
Outlook Score: {analysis['role_overview']['outlook_score']}/100

Overall Score: {analysis['score']}/100
Score Breakdown:
- Skills Match: {analysis['score_breakdown']['skills']}/35
- Completeness: {analysis['score_breakdown']['completeness']}/25
- Keywords: {analysis['score_breakdown']['keywords']}/20
- Role Similarity: {analysis['score_breakdown']['similarity']}/20
- Penalty: -{analysis['score_breakdown']['penalty']}

Role Similarity Model:
- Method: {analysis['role_similarity']['method']}
- Similarity: {analysis['role_similarity']['score']}%

Custom Skills:
{format_list_for_report(analysis['custom_skills'])}

Custom Keywords:
{format_list_for_report(analysis['custom_keywords'])}

Matched Core Skills:
{format_list_for_report(analysis['matched_required_skills'])}

Missing Core Skills:
{format_list_for_report(analysis['missing_required_skills'])}

Matched Optional Skills:
{format_list_for_report(analysis['matched_optional_skills'])}

Missing Optional Skills:
{format_list_for_report(analysis['missing_optional_skills'])}

Keyword Matches:
{format_list_for_report(analysis['keyword_matches'])}

Missing Keywords:
{format_list_for_report(analysis['keyword_gap'])}

Related Tools Found:
{format_list_for_report(analysis['related_tools_found'])}

Summary:
{analysis['summary']}

Education:
{format_list_for_report(analysis['education'])}

Experience:
{format_list_for_report(analysis['experience'])}

Missing Sections:
{format_list_for_report(analysis['missing_sections'])}

Suggestions:
{format_list_for_report(analysis['suggestions'])}
"""

    report_path.write_text(report_text, encoding="utf-8")
    return report_id, report_path


def format_list_for_report(items: list[str]) -> str:
    if not items:
        return "- None"
    return "\n".join(f"- {item}" for item in items)


@app.route("/")
def home():
    roles = list(TECH_ROLE_DATA.keys())
    return render_template("index.html", roles=roles, role_count=len(roles))


@app.route("/analyze", methods=["POST"])
def analyze():
    if "resume" not in request.files:
        return jsonify({"error": "Please upload a PDF resume."}), 400

    resume_file = request.files["resume"]
    role = request.form.get("role", "").strip()
    custom_skills = parse_custom_terms(request.form.get("custom_skills", ""))
    custom_keywords = parse_custom_terms(request.form.get("custom_keywords", ""))

    if not resume_file or not resume_file.filename:
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(resume_file.filename):
        return jsonify({"error": "Invalid file type. Please upload a PDF."}), 400

    if role not in TECH_ROLE_DATA:
        return jsonify({"error": "Please select a valid tech job role."}), 400

    safe_name = secure_filename(resume_file.filename)
    file_id = uuid.uuid4().hex
    stored_file = UPLOAD_FOLDER / f"{file_id}_{safe_name}"
    resume_file.save(stored_file)

    try:
        extracted_text = extract_text_from_pdf(stored_file)
        if not extracted_text.strip():
            return jsonify({"error": "The uploaded PDF appears to be empty or unreadable."}), 400

        analysis = analyze_resume_text(extracted_text, role, custom_skills, custom_keywords)
        report_id, _ = create_report(analysis, safe_name)

        return jsonify(
            {
                "message": "Resume analyzed successfully.",
                "filename": safe_name,
                "analysis": analysis,
                "report_url": f"/download-report/{report_id}",
            }
        )
    except Exception as exc:
        return jsonify({"error": f"Unable to process resume: {exc}"}), 500
    finally:
        if stored_file.exists():
            stored_file.unlink()


@app.route("/download-report/<report_id>")
def download_report(report_id: str):
    report_name = f"resume_report_{report_id}.txt"
    report_path = REPORT_FOLDER / report_name

    if not report_path.exists():
        return jsonify({"error": "Report not found."}), 404

    return send_file(report_path, as_attachment=True, download_name=report_name)


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "true").lower() == "true"
    host = os.getenv("FLASK_HOST", "127.0.0.1")
    port = int(os.getenv("FLASK_PORT", "5000"))
    app.run(host=host, port=port, debug=debug_mode)
