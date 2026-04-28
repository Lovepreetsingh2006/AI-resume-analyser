const form = document.getElementById("resumeForm");
const resumeInput = document.getElementById("resumeInput");
const fileName = document.getElementById("fileName");
const roleSelect = document.getElementById("roleSelect");
const customSkills = document.getElementById("customSkills");
const customKeywords = document.getElementById("customKeywords");
const results = document.getElementById("results");
const formMessage = document.getElementById("formMessage");
const analyzeBtn = document.getElementById("analyzeBtn");
const btnText = analyzeBtn.querySelector(".btn-text");
const btnLoader = analyzeBtn.querySelector(".btn-loader");
const dropzone = document.getElementById("dropzone");
const themeToggle = document.getElementById("themeToggle");

const scoreValue = document.getElementById("scoreValue");
const scoreBar = document.getElementById("scoreBar");
const scoreGauge = document.getElementById("scoreGauge");
const scoreSummary = document.getElementById("scoreSummary");
const resultTitle = document.getElementById("resultTitle");
const skillsBreakdown = document.getElementById("skillsBreakdown");
const completenessBreakdown = document.getElementById("completenessBreakdown");
const keywordsBreakdown = document.getElementById("keywordsBreakdown");
const similarityBreakdown = document.getElementById("similarityBreakdown");
const matchingSkills = document.getElementById("matchingSkills");
const missingSkills = document.getElementById("missingSkills");
const keywordGap = document.getElementById("keywordGap");
const educationList = document.getElementById("educationList");
const experienceList = document.getElementById("experienceList");
const suggestionsList = document.getElementById("suggestionsList");
const missingSectionsList = document.getElementById("missingSectionsList");
const skillsFoundCount = document.getElementById("skillsFoundCount");
const missingSectionsCount = document.getElementById("missingSectionsCount");
const keywordCoverage = document.getElementById("keywordCoverage");
const similarityScore = document.getElementById("similarityScore");
const similarityMethod = document.getElementById("similarityMethod");
const customTargeting = document.getElementById("customTargeting");
const roleCategory = document.getElementById("roleCategory");
const roleMarketSignal = document.getElementById("roleMarketSignal");
const roleOutlookScore = document.getElementById("roleOutlookScore");
const relatedTools = document.getElementById("relatedTools");
const downloadReport = document.getElementById("downloadReport");


function setTheme(theme) {
    document.body.dataset.theme = theme;
    localStorage.setItem("resume-analyzer-theme", theme);
    themeToggle.innerHTML =
        theme === "dark"
            ? '<i class="bi bi-sun"></i><span>Light mode</span>'
            : '<i class="bi bi-moon-stars"></i><span>Dark mode</span>';
}


function initTheme() {
    const storedTheme = localStorage.getItem("resume-analyzer-theme");
    const preferredDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    setTheme(storedTheme || (preferredDark ? "dark" : "light"));
}


function showMessage(message, type = "error") {
    formMessage.textContent = message;
    formMessage.className = `message ${type}`;
    formMessage.classList.remove("hidden");
}


function hideMessage() {
    formMessage.className = "message hidden";
    formMessage.textContent = "";
}


function updateFileName() {
    const file = resumeInput.files[0];
    fileName.textContent = file ? file.name : "No file selected";
}


function setLoading(isLoading) {
    analyzeBtn.disabled = isLoading;
    btnText.textContent = isLoading ? "Analyzing..." : "Analyze Resume";
    btnLoader.classList.toggle("hidden", !isLoading);
}


function renderTagList(container, items, variant, fallbackText) {
    container.innerHTML = "";

    if (!items || items.length === 0) {
        const tag = document.createElement("span");
        tag.className = `tag ${variant || "neutral"}`;
        tag.textContent = fallbackText;
        container.appendChild(tag);
        return;
    }

    items.forEach((item) => {
        const tag = document.createElement("span");
        tag.className = `tag ${variant}`;
        tag.textContent = item;
        container.appendChild(tag);
    });
}


function renderDetailList(container, items, fallbackText) {
    container.innerHTML = "";

    if (!items || items.length === 0) {
        const li = document.createElement("li");
        li.className = "empty-item";
        li.textContent = fallbackText;
        container.appendChild(li);
        return;
    }

    items.forEach((item) => {
        const li = document.createElement("li");
        li.textContent = item;
        container.appendChild(li);
    });
}


function animateScore(score) {
    const safeScore = Math.max(0, Math.min(Number(score) || 0, 100));
    const targetAngle = `${(safeScore / 100) * 360}deg`;
    let current = 0;

    scoreGauge.style.setProperty("--score-angle", "0deg");
    scoreBar.style.width = "0%";

    const step = () => {
        current += Math.max(1, Math.ceil((safeScore - current) / 8));
        if (current > safeScore) {
            current = safeScore;
        }

        scoreValue.textContent = current;
        scoreGauge.style.setProperty("--score-angle", `${(current / 100) * 360}deg`);
        scoreBar.style.width = `${current}%`;

        if (current < safeScore) {
            requestAnimationFrame(step);
        } else {
            scoreGauge.style.setProperty("--score-angle", targetAngle);
        }
    };

    requestAnimationFrame(step);
}


function renderResults(payload) {
    const { analysis, filename, report_url: reportUrl } = payload;

    resultTitle.textContent = `${filename} analyzed for ${analysis.role}`;
    scoreSummary.textContent = analysis.summary;
    skillsBreakdown.textContent = `${analysis.score_breakdown.skills}/35`;
    completenessBreakdown.textContent = `${analysis.score_breakdown.completeness}/25`;
    keywordsBreakdown.textContent = `${analysis.score_breakdown.keywords}/20`;
    similarityBreakdown.textContent = `${analysis.score_breakdown.similarity}/20`;
    skillsFoundCount.textContent = analysis.skills_found.length;
    missingSectionsCount.textContent = analysis.missing_sections.length;
    keywordCoverage.textContent = `${analysis.keyword_coverage}%`;
    similarityScore.textContent = `${analysis.role_similarity.score}%`;
    similarityMethod.textContent = analysis.role_similarity.method;
    roleCategory.textContent = analysis.role_overview.category;
    roleMarketSignal.textContent = analysis.role_overview.market_signal;
    roleOutlookScore.textContent = analysis.role_overview.outlook_score;

    renderTagList(matchingSkills, analysis.matching_skills, "match", "No matching skills detected yet");
    renderTagList(missingSkills, analysis.missing_skills, "missing", "No missing skills");
    renderTagList(keywordGap, analysis.keyword_gap, "neutral", "No major keyword gaps");
    renderTagList(
        customTargeting,
        [...(analysis.custom_skills || []), ...(analysis.custom_keywords || [])],
        "neutral",
        "Using built-in role requirements only"
    );
    renderTagList(
        relatedTools,
        analysis.role_overview.related_tools || [],
        "neutral",
        "No dataset tools available"
    );

    renderDetailList(educationList, analysis.education, "No education details detected");
    renderDetailList(experienceList, analysis.experience, "No experience details detected");
    renderDetailList(suggestionsList, analysis.suggestions, "No suggestions generated");
    renderDetailList(missingSectionsList, analysis.missing_sections, "No missing key sections");

    if (reportUrl) {
        downloadReport.href = reportUrl;
        downloadReport.hidden = false;
    } else {
        downloadReport.hidden = true;
    }

    results.classList.remove("hidden");
    animateScore(analysis.score);
    results.scrollIntoView({ behavior: "smooth", block: "start" });
}


async function submitResume(event) {
    event.preventDefault();
    hideMessage();

    const file = resumeInput.files[0];
    if (!file) {
        showMessage("Please choose a PDF resume before analyzing.");
        return;
    }

    if (!roleSelect.value) {
        showMessage("Please select a target job role.");
        return;
    }

    const formData = new FormData();
    formData.append("resume", file);
    formData.append("role", roleSelect.value);
    formData.append("custom_skills", customSkills.value);
    formData.append("custom_keywords", customKeywords.value);

    try {
        setLoading(true);

        const response = await fetch("/analyze", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Something went wrong while analyzing the resume.");
        }

        showMessage(data.message, "success");
        renderResults(data);
    } catch (error) {
        showMessage(error.message || "Unable to analyze the resume.");
        results.classList.add("hidden");
    } finally {
        setLoading(false);
    }
}


["dragenter", "dragover"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropzone.classList.add("drag-over");
    });
});

["dragleave", "drop"].forEach((eventName) => {
    dropzone.addEventListener(eventName, (event) => {
        event.preventDefault();
        dropzone.classList.remove("drag-over");
    });
});

dropzone.addEventListener("drop", (event) => {
    const files = event.dataTransfer.files;
    if (files.length) {
        resumeInput.files = files;
        updateFileName();
    }
});

resumeInput.addEventListener("change", updateFileName);
form.addEventListener("submit", submitResume);
themeToggle.addEventListener("click", () => {
    const nextTheme = document.body.dataset.theme === "dark" ? "light" : "dark";
    setTheme(nextTheme);
});

initTheme();
