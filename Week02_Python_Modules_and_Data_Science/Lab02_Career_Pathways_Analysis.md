# CE49X: Introduction to Computational Thinking and Data Science for Civil Engineers
## Lab 2: Where Do Bogazici CE Graduates End Up?
### Spring 2026 | Dr. Eyuphan Koc | Bogazici University

---

**Due Date:** Two weeks from the lab session
**Total Points:** 100
**Submission:** Upload your Jupyter notebook (.ipynb) and any collected data files to Moodle. All code cells must be executed with visible output.
**Collaboration:** You may work in teams of 2–3. Each team submits one notebook.

---

## Overview

Your department has been producing civil engineers for decades — but where do they actually end up? Do most stay in structural engineering? How many switch to finance or tech? What universities do they pursue graduate studies at? Where in the world do they go?

**Your mission:** Investigate the career pathways of Bogazici University Civil Engineering graduates using real, publicly available data. You will collect, organize, analyze, and visualize your findings using Python.

There is no pre-made dataset. **You build the dataset.**

---

## The Big Questions

Your investigation should aim to answer some (or all) of the following:

1. What industries and job titles do Bogazici CE graduates hold today?
2. What is the split between those who stayed in engineering vs. those who switched fields?
3. How many pursued graduate studies? Where (which universities, which countries)?
4. What companies and organizations employ the most Bogazici CE alumni?
5. Are there noticeable generational shifts (e.g., do recent graduates leave engineering more often than older cohorts)?
6. What is the geographic distribution — how many stayed in Turkey vs. went abroad?

You do **not** need to answer all of these. Pick the questions that interest you most and that your data can support.

---

## Part A: Data Collection (30 points)

This is the core of the lab. You need to gather real data about Bogazici CE alumni careers. Here are some approaches — use **at least two** different sources:

### Suggested Data Sources

| Source | What You Can Find | How to Access |
|---|---|---|
| **LinkedIn** | Job titles, companies, locations, education history | Manual search, browse alumni pages |
| **Bogazici University website** | Faculty listings, department pages, alumni spotlights | Web browsing, department pages |
| **Google Scholar / ResearchGate** | Academic alumni — publications, affiliations, h-index | Search by name + "Bogazici" |
| **Company websites** | Where alumni work, their roles, project portfolios | Google search for specific people |
| **News articles / interviews** | Notable alumni, career stories, entrepreneurship | Google News, Turkish media |
| **YOK (Higher Education Council)** | Academic faculty across Turkish universities | akademik.yok.gov.tr |
| **Personal knowledge** | Upperclassmen, TAs, professors you know | Ask around! |

### What to Collect

For each alumnus you find, try to record as many of the following fields as possible:

- **Name** (or anonymize as "Alumnus 1", "Alumnus 2", etc. if you prefer)
- **Approximate graduation year** (or decade, e.g., "2010s")
- **Current job title**
- **Current employer / organization**
- **Industry sector** (e.g., Structural Engineering, Construction, Finance, Academia, Tech, Government, etc.)
- **Location** (city, country)
- **Highest degree** (B.Sc., M.Sc., Ph.D.)
- **Graduate school** (if applicable — name and country)
- **Still in civil engineering?** (Yes / No / Partially)

### Requirements

**(a)** Collect data on **at least 30 alumni** (more is better). Document your sources — for each entry, note where you found the information (e.g., "LinkedIn search", "department website", "Google Scholar").

**(b)** Organize your collected data into a **pandas DataFrame**. Each row is one alumnus, each column is one attribute. Save the DataFrame to a CSV file (`bogazici_ce_alumni.csv`).

**(c)** In a markdown cell, describe your data collection process:
- Which sources did you use and why?
- What challenges did you face (e.g., incomplete profiles, privacy settings, ambiguous information)?
- How did you handle missing data?
- Roughly how long did data collection take?

---

## Part B: Data Cleaning and Exploration (20 points)

Real-world data is messy. Before analysis, you need to clean what you collected.

**(a)** Load your CSV and inspect it. Report:
- Total number of records
- Number of missing values per column
- Data types of each column

**(b)** Standardize your data:
- Make sure industry/sector labels are consistent (e.g., don't have both "Structural Eng." and "Structural Engineering")
- Standardize location names (e.g., decide on "Istanbul" vs. "İstanbul", "USA" vs. "United States")
- Handle missing values — decide on a strategy and explain your choice

**(c)** Create at least two **derived columns** that don't exist in the raw data but are useful for analysis. Examples:
- `abroad` (True/False — is the person outside Turkey?)
- `career_switch` (True/False — did they leave civil engineering?)
- `decade` (graduation decade: "2000s", "2010s", "2020s")
- `has_graduate_degree` (True/False)

---

## Part C: Analysis and Visualization (35 points)

Now answer the questions you set out to investigate. Create **at least four visualizations** and support each with a brief written interpretation (2–3 sentences).

### Required Analyses (pick at least four)

1. **Career sector breakdown**: What proportion of graduates are in each sector? (bar chart or pie chart)

2. **Engineering vs. non-engineering**: What fraction stayed in engineering-related careers vs. switched to other fields? Does this vary by graduation decade?

3. **Geographic distribution**: Where are Bogazici CE alumni located? (bar chart of top cities/countries, or a simple map if you're ambitious)

4. **Graduate studies pipeline**: What fraction pursued M.Sc. or Ph.D.? Which universities appear most frequently? Which countries?

5. **Top employers**: Which companies or organizations employ the most alumni? (horizontal bar chart)

6. **Generational trends**: Has the career distribution shifted over time? Compare older graduates (pre-2010) vs. recent ones (2015+) if your data allows.

7. **Any other question** that your data can answer and that you find interesting.

### Visualization Guidelines

- Use matplotlib (or seaborn/plotly if you prefer)
- Every plot needs a title, axis labels, and should be readable
- After each plot, include a markdown cell with your interpretation: what does this plot tell us?

---

## Part D: Findings Report (15 points)

Write a summary (300–500 words) in markdown cells at the end of your notebook. Address the following:

**(a) Key Findings** — What are the 3–4 most interesting or surprising things you discovered about Bogazici CE career pathways? Support each finding with a specific number or visualization from your analysis.

**(b) Data Limitations** — What are the biggest limitations of your dataset? Consider:
- Selection bias (who is visible on LinkedIn vs. who isn't?)
- Sample size and representativeness
- Missing data and its potential impact
- Any assumptions you had to make

**(c) Recommendations** — Based on your findings, what is one piece of advice you would give to a first-year CE student at Bogazici about planning their career? What would you tell the department about how they might better prepare students?

**(d) Methodology Reflection** — If you had more time and resources, how would you improve this study? What additional data would you collect, and what tools would you use?

---

## Bonus Challenges (up to +15 points)

These are optional. Attempt them only after completing the main lab.

- **[+5] Web scraping**: Write a Python script that programmatically collects data from a public web page (e.g., a faculty listing or company team page). Use `requests` and `BeautifulSoup` or similar tools.

- **[+5] Interactive visualization**: Create an interactive plot using `plotly` (e.g., a hover-enabled bar chart or an interactive map showing alumni locations).

- **[+5] Comparison study**: Find similar data about graduates from another Turkish university's CE department (e.g., METU, ITU) and compare the career distributions to Bogazici's. Are there meaningful differences?

---

## Tips for Success

- **Start data collection early.** This is the most time-consuming part. Don't leave it to the last day.
- **Divide the work** if working in a team — one person can search LinkedIn, another can search academic databases, etc.
- **30 entries is the minimum.** Teams that collect 50+ and find interesting patterns will score higher.
- **Quality matters more than quantity.** 30 well-documented entries with consistent fields are better than 80 sloppy ones.
- **Document everything.** Your notebook should tell the story of your investigation from start to finish.
- **Be ethical.** Use only publicly available information. Do not scrape private profiles or share personal data without consent. You may anonymize names if you wish.

---

## Grading Rubric

| Component | Points | What We're Looking For |
|---|---|---|
| **Data Collection** | 30 | At least 30 entries, at least 2 sources, well-documented process |
| **Data Cleaning** | 20 | Consistent formatting, handled missing values, useful derived columns |
| **Analysis & Visualization** | 35 | At least 4 informative plots, correct use of pandas/numpy, written interpretations |
| **Findings Report** | 15 | Thoughtful analysis of findings, honest about limitations, actionable recommendations |
| **Bonus** | +15 | Web scraping, interactive plots, or comparison study |

---

### Questions?
**Dr. Eyuphan Koc**
eyuphan.koc@bogazici.edu.tr
