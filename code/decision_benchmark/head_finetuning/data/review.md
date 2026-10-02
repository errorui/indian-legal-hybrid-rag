# Head-only fine-tuning dataset — 200 cases

| Split | Single search | Single no search | Multi search | Multi no search | Total |
|---|---:|---:|---:|---:|---:|
| Training | 40 | 40 | 40 | 40 | 160 |
| Validation | 10 | 10 | 10 | 10 | 40 |

Histories are constructed, source-grounded fixtures. No LLM generation or model training was run. Source passages come from the existing parent corpus; HTML and OCR separators are normalised for readability. The original 100 evaluation inputs are unchanged. No exact query, full input, or explicit article-reference overlap was found. Training and validation share broad scenario families and templates; this small synthetic pilot does not establish production generalisation.

All complete candidate inputs fit 512 tokens: maximum 356; no truncation.

## Samples

### head-001 · train · single · search

**Latest question:** Find the original opening passage of Article 54 and cite its source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-002 · train · single · no_search

**Latest question:** Reformat only this supplied excerpt into bullets; add no facts: "Article 54 — Election of President. Opening source passage: The President shall be elected by the members of an electoral college consisting of— [Article 54; parent_0096]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-003 · train · multi · search

**Latest question:** Can you explain the opening provision and keep the citation?

**Gold rationale:** Required evidence is missing. The requested opening passage and source reference must be present.

**user:** Let us look at Article 54, on election of president.

**assistant:** Our topic is Article 54: Election of President. [Article 54; parent_0096]

### head-004 · train · multi · no_search

**Latest question:** Can you explain the opening provision and keep the citation?

**Gold rationale:** All passages and source references required by this request are already supplied in history. The requested opening passage and source reference must be present.

**user:** Let us look at Article 54, on election of president.

**assistant:** Article 54 — Election of President. Opening source passage: The President shall be elected by the members of an electoral college consisting of— [Article 54; parent_0096]

### head-005 · validation · single · search

**Latest question:** I need evidence for the beginning of Article 243ZP, with a source reference.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-006 · validation · single · no_search

**Latest question:** Translate only the supplied text into Hindi, preserving its citation: "Article 243ZP — Returns. Opening source passage: Every co-operative society shall file returns, within six months of the close of every financial year, to the authority designated by the State Government including the following matters, namely:— [Article 243ZP; parent_0157]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-007 · validation · multi · search

**Latest question:** What does its first passage actually say? Include the source.

**Gold rationale:** Required evidence is missing. The requested opening passage and source reference must be present.

**user:** Let us look at Article 243ZP, on returns.

**assistant:** Our topic is Article 243ZP: Returns. [Article 243ZP; parent_0157]

**user:** These notes are for revision.

**assistant:** I will keep the notes concise and easy to review.

### head-008 · validation · multi · no_search

**Latest question:** What does its first passage actually say? Include the source.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The requested opening passage and source reference must be present.

**user:** Let us look at Article 243ZP, on returns.

**assistant:** Article 243ZP — Returns. Opening source passage: Every co-operative society shall file returns, within six months of the close of every financial year, to the authority designated by the State Government including the following matters, namely:— [Article 243ZP; parent_0157]

**user:** These notes are for revision.

**assistant:** I will keep the notes concise and easy to review.

### head-009 · train · single · search

**Latest question:** What does the opening of Article 230 say? Please use and cite the corpus text.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-010 · train · single · no_search

**Latest question:** Explain only this provided passage in simpler words: "Article 230 — Extension of jurisdiction of High Courts to Union territories. Opening source passage: (1) Parliament may by law extend the jurisdiction of a High Court to, or exclude the jurisdiction of a High Court from, any Union territory. [Article 230; parent_0142]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-011 · train · multi · search

**Latest question:** Please turn the opening provision into two points, with a reference.

**Gold rationale:** Required evidence is missing. The requested opening passage and source reference must be present.

**user:** Let us look at Article 230, on extension of jurisdiction of high courts to union territories.

**assistant:** Our topic is Article 230: Extension of jurisdiction of High Courts to Union territories. [Article 230; parent_0142]

### head-012 · train · multi · no_search

**Latest question:** Please turn the opening provision into two points, with a reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The requested opening passage and source reference must be present.

**user:** Let us look at Article 230, on extension of jurisdiction of high courts to union territories.

**assistant:** Article 230 — Extension of jurisdiction of High Courts to Union territories. Opening source passage: (1) Parliament may by law extend the jurisdiction of a High Court to, or exclude the jurisdiction of a High Court from, any Union territory. [Article 230; parent_0142]

### head-013 · train · single · search

**Latest question:** Locate Article 346 and explain its opening passage using the original source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-014 · train · single · no_search

**Latest question:** Could you explain how to phrase a clear research question?

**Gold rationale:** A conversational or general writing request requires no constitutional evidence.

### head-015 · train · multi · search

**Latest question:** Give me the original opening words and the source for my notes.

**Gold rationale:** Required evidence is missing. The requested opening passage and source reference must be present.

**user:** Let us look at Article 346, on official language for communication between one state and another or between a state and the union.

**assistant:** Our topic is Article 346: Official language for communication between one State and another or between a State and the Union. [Article 346; parent_0204]

**user:** Use a neutral tone.

**assistant:** I will use a neutral tone.

### head-016 · train · multi · no_search

**Latest question:** Give me the original opening words and the source for my notes.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The requested opening passage and source reference must be present.

**user:** Let us look at Article 346, on official language for communication between one state and another or between a state and the union.

**assistant:** Article 346 — Official language for communication between one State and another or between a State and the Union. Opening source passage: The language for the time being authorised for use in the Union for official purposes shall be the official language for communication between one State and another State and between a State and the Union: [Article 346; parent_0204]

**user:** Use a neutral tone.

**assistant:** I will use a neutral tone.

### head-017 · train · single · search

**Latest question:** For my notes, supply the opening text of Article 394A and its citation.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-018 · train · single · no_search

**Latest question:** Please analyse the clause I have in mind; I have not named it yet.

**Gold rationale:** Essential subject or text is absent; ask for clarification without a speculative search.

### head-019 · train · multi · search

**Latest question:** How would you explain the first passage to a beginner? Cite it.

**Gold rationale:** Required evidence is missing. The requested opening passage and source reference must be present.

**user:** Let us look at Article 394A, on authoritative text in the hindi language.

**assistant:** Our topic is Article 394A: Authoritative text in the Hindi language. [Article 394A; parent_0237]

### head-020 · train · multi · no_search

**Latest question:** How would you explain the first passage to a beginner? Cite it.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The requested opening passage and source reference must be present.

**user:** Let us look at Article 394A, on authoritative text in the hindi language.

**assistant:** Article 394A — Authoritative text in the Hindi language. Opening source passage: (1) The President shall cause to be published under his authority,— [Article 394A; parent_0237]

### head-021 · train · single · search

**Latest question:** What does Article 158 provide at the start about conditions of governor's office? Cite the text.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-022 · train · single · no_search

**Latest question:** Reformat only this supplied excerpt into bullets; add no facts: "Article 158 — Conditions of Governor's office. Opening source passage: (1) The Governor shall not be a member of either House of Parliament or of a House of the Legislature of any State specified in the First Schedule, and if a member of either House of Parliament or of a House of the Legislature of any such State be appointed Governor, he shall be deemed to have vacated his seat in that House on the date on which he enters upon his office as Governor. [Article 158; parent_0122]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-023 · train · multi · search

**Latest question:** I need the text at the beginning of that article and its reference.

**Gold rationale:** Required evidence is missing. The requested opening passage and source reference must be present.

**user:** Let us look at Article 158, on conditions of governor's office.

**assistant:** Our topic is Article 158: Conditions of Governor's office. [Article 158; parent_0122]

**user:** I prefer short answers.

**assistant:** I will keep the answers short.

### head-024 · train · multi · no_search

**Latest question:** I need the text at the beginning of that article and its reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The requested opening passage and source reference must be present.

**user:** Let us look at Article 158, on conditions of governor's office.

**assistant:** Article 158 — Conditions of Governor's office. Opening source passage: (1) The Governor shall not be a member of either House of Parliament or of a House of the Legislature of any State specified in the First Schedule, and if a member of either House of Parliament or of a House of the Legislature of any such State be appointed Governor, he shall be deemed to have vacated his seat in that House on the date on which he enters upon his office as Governor. [Article 158; parent_0122]

**user:** I prefer short answers.

**assistant:** I will keep the answers short.

### head-025 · train · single · search

**Latest question:** I am studying term of office of vice-president. Explain the opening provision of Article 67, citing it.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-026 · train · single · no_search

**Latest question:** Translate only the supplied text into Hindi, preserving its citation: "Article 67 — Term of office of Vice-President. Opening source passage: The Vice-President shall hold office for a term of five years from the date on which he enters upon his office: [Article 67; parent_0097]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-027 · train · multi · search

**Latest question:** Write a short explanation of the opening provision, using a source.

**Gold rationale:** Required evidence is missing. The requested opening passage and source reference must be present.

**user:** Let us look at Article 67, on term of office of vice-president.

**assistant:** Our topic is Article 67: Term of office of Vice-President. [Article 67; parent_0097]

### head-028 · train · multi · no_search

**Latest question:** Write a short explanation of the opening provision, using a source.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The requested opening passage and source reference must be present.

**user:** Let us look at Article 67, on term of office of vice-president.

**assistant:** Article 67 — Term of office of Vice-President. Opening source passage: The Vice-President shall hold office for a term of five years from the date on which he enters upon his office: [Article 67; parent_0097]

### head-029 · validation · single · search

**Latest question:** Could you make a study card from the first passage of Article 337, with a reference?

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-030 · validation · single · no_search

**Latest question:** Explain only this provided passage in simpler words: "Article 337 — Special provision with respect to educational grants for the benefit of Anglo-Indian community. Opening source passage: During the first three financial years after the commencement of this Constitution, the same grants, if any, shall be made by the Union and by each State \*\*\* for the benefit of the Anglo-Indian community in respect of education as were made in the financial year ending on the thirty-first day of March, 1948. [Article 337; parent_0198]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-031 · validation · multi · search

**Latest question:** Could you show me the first source passage for this topic?

**Gold rationale:** Required evidence is missing. The requested opening passage and source reference must be present.

**user:** Let us look at Article 337, on special provision with respect to educational grants for the benefit of anglo-indian community.

**assistant:** Our topic is Article 337: Special provision with respect to educational grants for the benefit of Anglo-Indian community. [Article 337; parent_0198]

**user:** I want to understand the wording first.

**assistant:** We can start with the wording.

### head-032 · validation · multi · no_search

**Latest question:** Could you show me the first source passage for this topic?

**Gold rationale:** All passages and source references required by this request are already supplied in history. The requested opening passage and source reference must be present.

**user:** Let us look at Article 337, on special provision with respect to educational grants for the benefit of anglo-indian community.

**assistant:** Article 337 — Special provision with respect to educational grants for the benefit of Anglo-Indian community. Opening source passage: During the first three financial years after the commencement of this Constitution, the same grants, if any, shall be made by the Union and by each State \*\*\* for the benefit of the Anglo-Indian community in respect of education as were made in the financial year ending on the thirty-first day of March, 1948. [Article 337; parent_0198]

**user:** I want to understand the wording first.

**assistant:** We can start with the wording.

### head-033 · train · single · search

**Latest question:** Please quote the beginning of Article 145 so I can check its wording.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-034 · train · single · no_search

**Latest question:** Please suggest a friendly name for a reading club.

**Gold rationale:** A conversational or general writing request requires no constitutional evidence.

### head-035 · train · multi · search

**Latest question:** Please give the opening passage, then a one-line explanation and citation.

**Gold rationale:** Required evidence is missing. The requested opening passage and source reference must be present.

**user:** Let us look at Article 145, on rules of court, etc.

**assistant:** Our topic is Article 145: Rules of Court, etc. [Article 145; parent_0117]

### head-036 · train · multi · no_search

**Latest question:** Please give the opening passage, then a one-line explanation and citation.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The requested opening passage and source reference must be present.

**user:** Let us look at Article 145, on rules of court, etc.

**assistant:** Article 145 — Rules of Court, etc. Opening source passage: (1) Subject to the provisions of any law made by Parliament, the Supreme Court may from time to time, with the approval of the President, make rules for regulating generally the practice and procedure of the Court including— [Article 145; parent_0117]

### head-037 · train · single · search

**Latest question:** Explain the initial provision under "Special leave to appeal by the Supreme Court" in Article 136 using the corpus source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-038 · train · single · no_search

**Latest question:** Which provision was I intending to refer to?

**Gold rationale:** Essential subject or text is absent; ask for clarification without a speculative search.

### head-039 · train · multi · search

**Latest question:** What can we say from the opening provision alone? Retain its reference.

**Gold rationale:** Required evidence is missing. The requested opening passage and source reference must be present.

**user:** Let us look at Article 136, on special leave to appeal by the supreme court.

**assistant:** Our topic is Article 136: Special leave to appeal by the Supreme Court. [Article 136; parent_0117]

**user:** Let us use bullets when helpful.

**assistant:** I will use bullets where they help explain the text.

### head-040 · train · multi · no_search

**Latest question:** What can we say from the opening provision alone? Retain its reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The requested opening passage and source reference must be present.

**user:** Let us look at Article 136, on special leave to appeal by the supreme court.

**assistant:** Article 136 — Special leave to appeal by the Supreme Court. Opening source passage: (1) Notwithstanding anything in this Chapter, the Supreme Court may, in its discretion, grant special leave to appeal from any judgment, decree, determination, sentence or order in any cause or matter passed or made by any court or tribunal in the territory of India. [Article 136; parent_0117]

**user:** Let us use bullets when helpful.

**assistant:** I will use bullets where they help explain the text.

### head-041 · validation · single · search

**Latest question:** Find the original opening passage of Article 150 and cite its source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-042 · validation · single · no_search

**Latest question:** Reformat only this supplied excerpt into bullets; add no facts: "Article 150 — Form of accounts of the Union and of the States. Opening source passage: The accounts of the Union and of the States shall be kept in such form as the President may, [on the advice of] the Comptroller and Auditor-General of India, prescribe.] [Article 150; parent_0120]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-043 · validation · multi · search

**Latest question:** Can you quote the opening body passage exactly and cite it?

**Gold rationale:** Required evidence is missing. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 150?

**assistant:** The heading of Article 150 is 'Form of accounts of the Union and of the States'. [Article 150; parent_0120]

### head-044 · validation · multi · no_search

**Latest question:** Can you quote the opening body passage exactly and cite it?

**Gold rationale:** All passages and source references required by this request are already supplied in history. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 150?

**assistant:** Article 150 — Form of accounts of the Union and of the States. Opening source passage: The accounts of the Union and of the States shall be kept in such form as the President may, [on the advice of] the Comptroller and Auditor-General of India, prescribe.] [Article 150; parent_0120]

### head-045 · train · single · search

**Latest question:** I need evidence for the beginning of Article 73, with a source reference.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-046 · train · single · no_search

**Latest question:** Translate only the supplied text into Hindi, preserving its citation: "Article 73 — Extent of executive power of the Union. Opening source passage: (1) Subject to the provisions of this Constitution, the executive power of the Union shall extend— [Article 73; parent_0098]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-047 · train · multi · search

**Latest question:** I need the original opening wording, rather than just the title. Include a source.

**Gold rationale:** Required evidence is missing. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 73?

**assistant:** The heading of Article 73 is 'Extent of executive power of the Union'. [Article 73; parent_0098]

**user:** These notes are for revision.

**assistant:** I will keep the notes concise and easy to review.

### head-048 · train · multi · no_search

**Latest question:** I need the original opening wording, rather than just the title. Include a source.

**Gold rationale:** All passages and source references required by this request are already supplied in history. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 73?

**assistant:** Article 73 — Extent of executive power of the Union. Opening source passage: (1) Subject to the provisions of this Constitution, the executive power of the Union shall extend— [Article 73; parent_0098]

**user:** These notes are for revision.

**assistant:** I will keep the notes concise and easy to review.

### head-049 · train · single · search

**Latest question:** What does the opening of Article 247 say? Please use and cite the corpus text.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-050 · train · single · no_search

**Latest question:** Explain only this provided passage in simpler words: "Article 247 — Power of Parliament to provide for the establishment of certain additional courts. Opening source passage: Notwithstanding anything in this Chapter, Parliament may by law provide for the establishment of any additional courts for the better administration of laws made by Parliament or of any existing laws with respect to a matter enumerated in the Union List. [Article 247; parent_0159]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-051 · train · multi · search

**Latest question:** Please copy the first passage word for word and keep its source reference.

**Gold rationale:** Required evidence is missing. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 247?

**assistant:** The heading of Article 247 is 'Power of Parliament to provide for the establishment of certain additional courts'. [Article 247; parent_0159]

### head-052 · train · multi · no_search

**Latest question:** Please copy the first passage word for word and keep its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 247?

**assistant:** Article 247 — Power of Parliament to provide for the establishment of certain additional courts. Opening source passage: Notwithstanding anything in this Chapter, Parliament may by law provide for the establishment of any additional courts for the better administration of laws made by Parliament or of any existing laws with respect to a matter enumerated in the Union List. [Article 247; parent_0159]

### head-053 · train · single · search

**Latest question:** Locate Article 229 and explain its opening passage using the original source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-054 · train · single · no_search

**Latest question:** I appreciate your patience with my questions.

**Gold rationale:** A conversational or general writing request requires no constitutional evidence.

### head-055 · train · multi · search

**Latest question:** What are the exact opening words of the provision? Give the reference too.

**Gold rationale:** Required evidence is missing. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 229?

**assistant:** The heading of Article 229 is 'Officers and servants and the expenses of High Courts'. [Article 229; parent_0142]

**user:** Use a neutral tone.

**assistant:** I will use a neutral tone.

### head-056 · train · multi · no_search

**Latest question:** What are the exact opening words of the provision? Give the reference too.

**Gold rationale:** All passages and source references required by this request are already supplied in history. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 229?

**assistant:** Article 229 — Officers and servants and the expenses of High Courts. Opening source passage: (1) Appointments of officers and servants of a High Court shall be made by the Chief Justice of the Court or such other Judge or officer of the Court as he may direct: [Article 229; parent_0142]

**user:** Use a neutral tone.

**assistant:** I will use a neutral tone.

### head-057 · train · single · search

**Latest question:** For my notes, supply the opening text of Article 203 and its citation.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-058 · train · single · no_search

**Latest question:** Can you explain my document? I have not attached or described it.

**Gold rationale:** Essential subject or text is absent; ask for clarification without a speculative search.

### head-059 · train · multi · search

**Latest question:** For a quotation in my notes, give the opening passage and citation.

**Gold rationale:** Required evidence is missing. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 203?

**assistant:** The heading of Article 203 is 'Procedure in Legislature with respect to estimates'. [Article 203; parent_0135]

### head-060 · train · multi · no_search

**Latest question:** For a quotation in my notes, give the opening passage and citation.

**Gold rationale:** All passages and source references required by this request are already supplied in history. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 203?

**assistant:** Article 203 — Procedure in Legislature with respect to estimates. Opening source passage: (1) So much of the estimates as relates to expenditure charged upon the Consolidated Fund of a State shall not be submitted to the vote of the Legislative Assembly, [Article 203; parent_0135]

### head-061 · train · single · search

**Latest question:** What does Article 172 provide at the start about duration of state legislatures? Cite the text.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-062 · train · single · no_search

**Latest question:** Reformat only this supplied excerpt into bullets; add no facts: "Article 172 — Duration of State Legislatures. Opening source passage: (1) Every Legislative Assembly of every State, unless sooner dissolved, shall continue for [five years] from the date appointed for its first meeting and no longer and the expiration of the said period of [five years] shall operate as a dissolution of the Assembly: [Article 172; parent_0126]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-063 · train · multi · search

**Latest question:** Show the text immediately after that heading, with a source reference.

**Gold rationale:** Required evidence is missing. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 172?

**assistant:** The heading of Article 172 is 'Duration of State Legislatures'. [Article 172; parent_0126]

**user:** I prefer short answers.

**assistant:** I will keep the answers short.

### head-064 · train · multi · no_search

**Latest question:** Show the text immediately after that heading, with a source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 172?

**assistant:** Article 172 — Duration of State Legislatures. Opening source passage: (1) Every Legislative Assembly of every State, unless sooner dissolved, shall continue for [five years] from the date appointed for its first meeting and no longer and the expiration of the said period of [five years] shall operate as a dissolution of the Assembly: [Article 172; parent_0126]

**user:** I prefer short answers.

**assistant:** I will keep the answers short.

### head-065 · train · single · search

**Latest question:** I am studying eligibility for re-election. Explain the opening provision of Article 57, citing it.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-066 · train · single · no_search

**Latest question:** Translate only the supplied text into Hindi, preserving its citation: "Article 57 — Eligibility for re-election. Opening source passage: A person who holds, or who has held, office as President shall, subject to the other provisions of this Constitution, be eligible for re-election to that office. [Article 57; parent_0097]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-067 · train · multi · search

**Latest question:** Could you supply a verbatim quotation from the beginning of that article?

**Gold rationale:** Required evidence is missing. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 57?

**assistant:** The heading of Article 57 is 'Eligibility for re-election'. [Article 57; parent_0097]

### head-068 · train · multi · no_search

**Latest question:** Could you supply a verbatim quotation from the beginning of that article?

**Gold rationale:** All passages and source references required by this request are already supplied in history. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 57?

**assistant:** Article 57 — Eligibility for re-election. Opening source passage: A person who holds, or who has held, office as President shall, subject to the other provisions of this Constitution, be eligible for re-election to that office. [Article 57; parent_0097]

### head-069 · validation · single · search

**Latest question:** Could you make a study card from the first passage of Article 87, with a reference?

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-070 · validation · single · no_search

**Latest question:** Explain only this provided passage in simpler words: "Article 87 — Special address by the President. Opening source passage: (1) At the commencement of [the first session after each general election to the House of the People and at the commencement of the first session of each year] the President shall address both Houses of Parliament assembled together and inform Parliament of the causes of its summons. [Article 87; parent_0104]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-071 · validation · multi · search

**Latest question:** Please put the original first passage in quotation marks and cite the source.

**Gold rationale:** Required evidence is missing. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 87?

**assistant:** The heading of Article 87 is 'Special address by the President'. [Article 87; parent_0104]

**user:** I want to understand the wording first.

**assistant:** We can start with the wording.

### head-072 · validation · multi · no_search

**Latest question:** Please put the original first passage in quotation marks and cite the source.

**Gold rationale:** All passages and source references required by this request are already supplied in history. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 87?

**assistant:** Article 87 — Special address by the President. Opening source passage: (1) At the commencement of [the first session after each general election to the House of the People and at the commencement of the first session of each year] the President shall address both Houses of Parliament assembled together and inform Parliament of the causes of its summons. [Article 87; parent_0104]

**user:** I want to understand the wording first.

**assistant:** We can start with the wording.

### head-073 · train · single · search

**Latest question:** Please quote the beginning of Article 279A so I can check its wording.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-074 · train · single · no_search

**Latest question:** Write a two-line reminder to take regular study breaks.

**Gold rationale:** A conversational or general writing request requires no constitutional evidence.

### head-075 · train · multi · search

**Latest question:** Now I need the opening body text, including its citation.

**Gold rationale:** Required evidence is missing. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 279A?

**assistant:** The heading of Article 279A is 'Goods and Services Tax Council'. [Article 279A; parent_0171]

### head-076 · train · multi · no_search

**Latest question:** Now I need the opening body text, including its citation.

**Gold rationale:** All passages and source references required by this request are already supplied in history. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 279A?

**assistant:** Article 279A — Goods and Services Tax Council. Opening source passage: (1) The President shall, within sixty days from the date of commencement of the Constitution (One Hundred and First Amendment) Act, 2016, by order, constitute a Council to be called the Goods and Services Tax Council. [Article 279A; parent_0171]

### head-077 · train · single · search

**Latest question:** Explain the initial provision under "Courts not to inquire into proceedings of Parliament" in Article 122 using the corpus source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-078 · train · single · no_search

**Latest question:** Please compare the two provisions I forgot to identify.

**Gold rationale:** Essential subject or text is absent; ask for clarification without a speculative search.

### head-079 · train · multi · search

**Latest question:** Give the beginning of the provision in its original wording, with a reference.

**Gold rationale:** Required evidence is missing. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 122?

**assistant:** The heading of Article 122 is 'Courts not to inquire into proceedings of Parliament'. [Article 122; parent_0114]

**user:** Let us use bullets when helpful.

**assistant:** I will use bullets where they help explain the text.

### head-080 · train · multi · no_search

**Latest question:** Give the beginning of the provision in its original wording, with a reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. A heading alone does not supply the requested verbatim body passage.

**user:** What is the heading of Article 122?

**assistant:** Article 122 — Courts not to inquire into proceedings of Parliament. Opening source passage: (1) The validity of any proceedings in Parliament shall not be called in question on the ground of any alleged irregularity of procedure. [Article 122; parent_0114]

**user:** Let us use bullets when helpful.

**assistant:** I will use bullets where they help explain the text.

### head-081 · train · single · search

**Latest question:** Find the original opening passage of Article 243ZK and cite its source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-082 · train · single · no_search

**Latest question:** Reformat only this supplied excerpt into bullets; add no facts: "Article 243ZK — Election of members of board. Opening source passage: (1) Notwithstanding anything contained in any law made by the Legislature of a State, the election of a board shall be conducted before the expiry of the term of the board so as to ensure that the newly elected members of the board assume office immediately on the expiry of the office of members of the outgoing board. [Article 243ZK; parent_0156]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-083 · train · multi · search

**Latest question:** Turn our note into two short bullets, and include the original opening passage and its source reference.

**Gold rationale:** Required evidence is missing. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 243ZK.

**assistant:** Study note: Article 243ZK — Election of members of board. [Article 243ZK; parent_0156]

### head-084 · train · multi · no_search

**Latest question:** Turn our note into two short bullets, and include the original opening passage and its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 243ZK.

**assistant:** Article 243ZK — Election of members of board. Opening source passage: (1) Notwithstanding anything contained in any law made by the Legislature of a State, the election of a board shall be conducted before the expiry of the term of the board so as to ensure that the newly elected members of the board assume office immediately on the expiry of the office of members of the outgoing board. [Article 243ZK; parent_0156]

### head-085 · validation · single · search

**Latest question:** I need evidence for the beginning of Article 89, with a source reference.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-086 · validation · single · no_search

**Latest question:** Translate only the supplied text into Hindi, preserving its citation: "Article 89 — The Chairman and Deputy Chairman of the Council of States. Opening source passage: (1) The Vice- President of India shall be ex officio Chairman of the Council of States. [Article 89; parent_0105]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-087 · validation · multi · search

**Latest question:** Turn our note into a study card, and include the original opening passage and its source reference.

**Gold rationale:** Required evidence is missing. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 89.

**assistant:** Study note: Article 89 — The Chairman and Deputy Chairman of the Council of States. [Article 89; parent_0105]

**user:** These notes are for revision.

**assistant:** I will keep the notes concise and easy to review.

### head-088 · validation · multi · no_search

**Latest question:** Turn our note into a study card, and include the original opening passage and its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 89.

**assistant:** Article 89 — The Chairman and Deputy Chairman of the Council of States. Opening source passage: (1) The Vice- President of India shall be ex officio Chairman of the Council of States. [Article 89; parent_0105]

**user:** These notes are for revision.

**assistant:** I will keep the notes concise and easy to review.

### head-089 · train · single · search

**Latest question:** What does the opening of Article 330A say? Please use and cite the corpus text.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-090 · train · single · no_search

**Latest question:** Explain only this provided passage in simpler words: "Article 330A — Reservation of seats for women in the House of the People. Opening source passage: (1) Seats shall be reserved for women in the House of the People. [Article 330A; parent_0196]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-091 · train · multi · search

**Latest question:** Turn our note into a short paragraph, and include the original opening passage and its source reference.

**Gold rationale:** Required evidence is missing. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 330A.

**assistant:** Study note: Article 330A — Reservation of seats for women in the House of the People. [Article 330A; parent_0196]

### head-092 · train · multi · no_search

**Latest question:** Turn our note into a short paragraph, and include the original opening passage and its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 330A.

**assistant:** Article 330A — Reservation of seats for women in the House of the People. Opening source passage: (1) Seats shall be reserved for women in the House of the People. [Article 330A; parent_0196]

### head-093 · train · single · search

**Latest question:** Locate Article 307 and explain its opening passage using the original source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-094 · train · single · no_search

**Latest question:** How can I make my notes easier to read?

**Gold rationale:** A conversational or general writing request requires no constitutional evidence.

### head-095 · train · multi · search

**Latest question:** Turn our note into simple English, and include the original opening passage and its source reference.

**Gold rationale:** Required evidence is missing. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 307.

**assistant:** Study note: Article 307 — Appointment of authority for carrying out the purposes of articles 301 to 304. [Article 307; parent_0047]

**user:** Use a neutral tone.

**assistant:** I will use a neutral tone.

### head-096 · train · multi · no_search

**Latest question:** Turn our note into simple English, and include the original opening passage and its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 307.

**assistant:** Article 307 — Appointment of authority for carrying out the purposes of articles 301 to 304. Opening source passage: PART XIV SERVICES UNDER THE UNION AND THE STATES CHAPTER I. [Article 307; parent_0047]

**user:** Use a neutral tone.

**assistant:** I will use a neutral tone.

### head-097 · train · single · search

**Latest question:** For my notes, supply the opening text of Article 154 and its citation.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-098 · train · single · no_search

**Latest question:** Tell me whether the unnamed exception I mean is relevant.

**Gold rationale:** Essential subject or text is absent; ask for clarification without a speculative search.

### head-099 · train · multi · search

**Latest question:** Turn our note into a question-and-answer note, and include the original opening passage and its source reference.

**Gold rationale:** Required evidence is missing. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 154.

**assistant:** Study note: Article 154 — Executive power of State. [Article 154; parent_0122]

### head-100 · train · multi · no_search

**Latest question:** Turn our note into a question-and-answer note, and include the original opening passage and its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 154.

**assistant:** Article 154 — Executive power of State. Opening source passage: (1) The executive power of the State shall be vested in the Governor and shall be exercised by him either directly or through officers subordinate to him in accordance with this Constitution. [Article 154; parent_0122]

### head-101 · train · single · search

**Latest question:** What does Article 194 provide at the start about powers, privileges, etc? Cite the text.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-102 · train · single · no_search

**Latest question:** Reformat only this supplied excerpt into bullets; add no facts: "Article 194 — Powers, privileges, etc. Opening source passage: , of the Houses of Legislatures and of the members and committees thereof.—(1) Subject to the provisions of this Constitution and to the rules and standing orders regulating the procedure of the Legislature, there shall be freedom of speech in the Legislature of every State. [Article 194; parent_0133]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-103 · train · multi · search

**Latest question:** Turn our note into a brief Hindi explanation, and include the original opening passage and its source reference.

**Gold rationale:** Required evidence is missing. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 194.

**assistant:** Study note: Article 194 — Powers, privileges, etc. [Article 194; parent_0133]

**user:** I prefer short answers.

**assistant:** I will keep the answers short.

### head-104 · train · multi · no_search

**Latest question:** Turn our note into a brief Hindi explanation, and include the original opening passage and its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 194.

**assistant:** Article 194 — Powers, privileges, etc. Opening source passage: , of the Houses of Legislatures and of the members and committees thereof.—(1) Subject to the provisions of this Constitution and to the rules and standing orders regulating the procedure of the Legislature, there shall be freedom of speech in the Legislature of every State. [Article 194; parent_0133]

**user:** I prefer short answers.

**assistant:** I will keep the answers short.

### head-105 · train · single · search

**Latest question:** I am studying qualifications for election as president. Explain the opening provision of Article 58, citing it.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-106 · train · single · no_search

**Latest question:** Translate only the supplied text into Hindi, preserving its citation: "Article 58 — Qualifications for election as President. Opening source passage: (1) No person shall be eligible for election as President unless he— [Article 58; parent_0097]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-107 · train · multi · search

**Latest question:** Turn our note into three short points, and include the original opening passage and its source reference.

**Gold rationale:** Required evidence is missing. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 58.

**assistant:** Study note: Article 58 — Qualifications for election as President. [Article 58; parent_0097]

### head-108 · train · multi · no_search

**Latest question:** Turn our note into three short points, and include the original opening passage and its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 58.

**assistant:** Article 58 — Qualifications for election as President. Opening source passage: (1) No person shall be eligible for election as President unless he— [Article 58; parent_0097]

### head-109 · train · single · search

**Latest question:** Could you make a study card from the first passage of Article 206, with a reference?

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-110 · train · single · no_search

**Latest question:** Explain only this provided passage in simpler words: "Article 206 — Votes on account, votes of credit and exceptional grants. Opening source passage: (1) Notwithstanding anything in the foregoing provisions of this Chapter, the Legislative Assembly of a State shall have power— [Article 206; parent_0135]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-111 · train · multi · search

**Latest question:** Turn our note into a revision note, and include the original opening passage and its source reference.

**Gold rationale:** Required evidence is missing. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 206.

**assistant:** Study note: Article 206 — Votes on account, votes of credit and exceptional grants. [Article 206; parent_0135]

**user:** I want to understand the wording first.

**assistant:** We can start with the wording.

### head-112 · train · multi · no_search

**Latest question:** Turn our note into a revision note, and include the original opening passage and its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 206.

**assistant:** Article 206 — Votes on account, votes of credit and exceptional grants. Opening source passage: (1) Notwithstanding anything in the foregoing provisions of this Chapter, the Legislative Assembly of a State shall have power— [Article 206; parent_0135]

**user:** I want to understand the wording first.

**assistant:** We can start with the wording.

### head-113 · validation · single · search

**Latest question:** Please quote the beginning of Article 298 so I can check its wording.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-114 · validation · single · no_search

**Latest question:** Suggest a simple routine for organising my desk.

**Gold rationale:** A conversational or general writing request requires no constitutional evidence.

### head-115 · validation · multi · search

**Latest question:** Turn our note into one concise explanation, and include the original opening passage and its source reference.

**Gold rationale:** Required evidence is missing. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 298.

**assistant:** Study note: Article 298 — Power to carry on trade, etc. [Article 298; parent_0182]

### head-116 · validation · multi · no_search

**Latest question:** Turn our note into one concise explanation, and include the original opening passage and its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 298.

**assistant:** Article 298 — Power to carry on trade, etc. Opening source passage: The executive power of the Union and of each State shall extend to the carrying on of any trade or business and to the acquisition, holding and disposal of property and the making of contracts for any purpose: [Article 298; parent_0182]

### head-117 · train · single · search

**Latest question:** Explain the initial provision under "Voting in Houses, power of Houses to act notwithstanding vacancies and quorum" in Article 189 using the corpus source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-118 · train · single · no_search

**Latest question:** Could you translate the passage? I have not supplied it.

**Gold rationale:** Essential subject or text is absent; ask for clarification without a speculative search.

### head-119 · train · multi · search

**Latest question:** Turn our note into a table with text and explanation, and include the original opening passage and its source reference.

**Gold rationale:** Required evidence is missing. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 189.

**assistant:** Study note: Article 189 — Voting in Houses, power of Houses to act notwithstanding vacancies and quorum. [Article 189; parent_0130]

**user:** Let us use bullets when helpful.

**assistant:** I will use bullets where they help explain the text.

### head-120 · train · multi · no_search

**Latest question:** Turn our note into a table with text and explanation, and include the original opening passage and its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The rewrite also asks for an opening passage and citation; the heading is insufficient.

**user:** Prepare a short note about Article 189.

**assistant:** Article 189 — Voting in Houses, power of Houses to act notwithstanding vacancies and quorum. Opening source passage: (1) Save as otherwise provided in this Constitution, all questions at any sitting of a House of the Legislature of a State shall be determined by a majority of votes of the members present and voting, other than the Speaker or Chairman, or person acting as such. [Article 189; parent_0130]

**user:** Let us use bullets when helpful.

**assistant:** I will use bullets where they help explain the text.

### head-121 · train · single · search

**Latest question:** Find the original opening passage of Article 245 and cite its source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-122 · train · single · no_search

**Latest question:** Reformat only this supplied excerpt into bullets; add no facts: "Article 245 — Extent of laws made by Parliament and by the Legislatures of States. Opening source passage: (1) Subject to the provisions of this Constitution, Parliament may make laws for the whole or any part of the territory of India, and the Legislature of a State may make laws for the whole or any part of the State. [Article 245; parent_0159]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-123 · train · multi · search

**Latest question:** Compare the two opening passages, keeping both source references.

**Gold rationale:** Required evidence is missing. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 243ZD and 245.

**assistant:** Article 243ZD — Committee for district planning. Opening source passage: (1) There shall be constituted in every State at the district level a District Planning Committee to consolidate the plans prepared by the Panchayats and the Municipalities in the district and to prepare a draft development plan for the district as a whole. [Article 243ZD; parent_0151]

### head-124 · train · multi · no_search

**Latest question:** Compare the two opening passages, keeping both source references.

**Gold rationale:** All passages and source references required by this request are already supplied in history. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 243ZD and 245.

**assistant:** Article 243ZD — Committee for district planning. Opening source passage: (1) There shall be constituted in every State at the district level a District Planning Committee to consolidate the plans prepared by the Panchayats and the Municipalities in the district and to prepare a draft development plan for the district as a whole. [Article 243ZD; parent_0151]
Article 245 — Extent of laws made by Parliament and by the Legislatures of States. Opening source passage: (1) Subject to the provisions of this Constitution, Parliament may make laws for the whole or any part of the territory of India, and the Legislature of a State may make laws for the whole or any part of the State. [Article 245; parent_0159]

### head-125 · train · single · search

**Latest question:** I need evidence for the beginning of Article 48A, with a source reference.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-126 · train · single · no_search

**Latest question:** Translate only the supplied text into Hindi, preserving its citation: "Article 48A — Protection and improvement of environment and safeguarding of forests and wild life. Opening source passage: The State shall endeavour to protect and improve the environment and to safeguard the forests and wild life of the country.] [Article 48A; parent_0093]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-127 · train · multi · search

**Latest question:** Explain how the beginnings of these two provisions differ. Cite both.

**Gold rationale:** Required evidence is missing. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 59 and 48A.

**assistant:** Article 59 — Conditions of President's office. Opening source passage: (1) The President shall not be a member of either House of Parliament or of a House of the Legislature of any State, and if a member of either House of Parliament or of a House of the Legislature of any State be elected President, he shall be deemed to have vacated his seat in that House on the date on which he enters upon his office as President. [Article 59; parent_0097]

**user:** These notes are for revision.

**assistant:** I will keep the notes concise and easy to review.

### head-128 · train · multi · no_search

**Latest question:** Explain how the beginnings of these two provisions differ. Cite both.

**Gold rationale:** All passages and source references required by this request are already supplied in history. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 59 and 48A.

**assistant:** Article 59 — Conditions of President's office. Opening source passage: (1) The President shall not be a member of either House of Parliament or of a House of the Legislature of any State, and if a member of either House of Parliament or of a House of the Legislature of any State be elected President, he shall be deemed to have vacated his seat in that House on the date on which he enters upon his office as President. [Article 59; parent_0097]
Article 48A — Protection and improvement of environment and safeguarding of forests and wild life. Opening source passage: The State shall endeavour to protect and improve the environment and to safeguard the forests and wild life of the country.] [Article 48A; parent_0093]

**user:** These notes are for revision.

**assistant:** I will keep the notes concise and easy to review.

### head-129 · train · single · search

**Latest question:** What does the opening of Article 81 say? Please use and cite the corpus text.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-130 · train · single · no_search

**Latest question:** Explain only this provided passage in simpler words: "Article 81 — Composition of the House of the People. Opening source passage: (1) [Subject to the provisions of article 331 \*\*\*], the House of the People shall consist of— [Article 81; parent_0103]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-131 · train · multi · search

**Latest question:** Make a two-row table of their opening passages and their references.

**Gold rationale:** Required evidence is missing. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 269A and 81.

**assistant:** Article 269A — Levy and collection of goods and services tax in course of inter-State trade or commerce. Opening source passage: (1) Goods and services tax on supplies in the course of inter-State trade or commerce shall be levied and collected by the Government of India and such tax shall be apportioned between the Union and the States in the manner as may be provided by Parliament by law on the recommendations of the Goods and Services Tax Council. [Article 269A; parent_0167]

### head-132 · train · multi · no_search

**Latest question:** Make a two-row table of their opening passages and their references.

**Gold rationale:** All passages and source references required by this request are already supplied in history. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 269A and 81.

**assistant:** Article 269A — Levy and collection of goods and services tax in course of inter-State trade or commerce. Opening source passage: (1) Goods and services tax on supplies in the course of inter-State trade or commerce shall be levied and collected by the Government of India and such tax shall be apportioned between the Union and the States in the manner as may be provided by Parliament by law on the recommendations of the Goods and Services Tax Council. [Article 269A; parent_0167]
Article 81 — Composition of the House of the People. Opening source passage: (1) [Subject to the provisions of article 331 \*\*\*], the House of the People shall consist of— [Article 81; parent_0103]

### head-133 · train · single · search

**Latest question:** Locate Article 191 and explain its opening passage using the original source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-134 · train · single · no_search

**Latest question:** Can you explain the difference between summarising and translating?

**Gold rationale:** A conversational or general writing request requires no constitutional evidence.

### head-135 · train · multi · search

**Latest question:** For each of those articles, show the first passage and its source.

**Gold rationale:** Required evidence is missing. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 53 and 191.

**assistant:** Article 53 — Executive power of the Union. Opening source passage: (1) The executive power of the Union shall be vested in the President and shall be exercised by him either directly or through officers subordinate to him in accordance with this Constitution. [Article 53; parent_0096]

**user:** Use a neutral tone.

**assistant:** I will use a neutral tone.

### head-136 · train · multi · no_search

**Latest question:** For each of those articles, show the first passage and its source.

**Gold rationale:** All passages and source references required by this request are already supplied in history. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 53 and 191.

**assistant:** Article 53 — Executive power of the Union. Opening source passage: (1) The executive power of the Union shall be vested in the President and shall be exercised by him either directly or through officers subordinate to him in accordance with this Constitution. [Article 53; parent_0096]
Article 191 — Disqualifications for membership. Opening source passage: (1) A person shall be disqualified for being chosen as, and for being, a member of the Legislative Assembly or Legislative Council of a State— [Article 191; parent_0132]

**user:** Use a neutral tone.

**assistant:** I will use a neutral tone.

### head-137 · train · single · search

**Latest question:** For my notes, supply the opening text of Article 98 and its citation.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-138 · train · single · no_search

**Latest question:** Can you quote the sentence I am thinking of?

**Gold rationale:** Essential subject or text is absent; ask for clarification without a speculative search.

### head-139 · train · multi · search

**Latest question:** What does each opening passage cover? Keep the two citations.

**Gold rationale:** Required evidence is missing. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 231 and 98.

**assistant:** Article 231 — Establishment of a common High Court for two or more States. Opening source passage: (1) Notwithstanding anything contained in the preceding provisions of this Chapter, Parliament may by law establish a common High Court for two or more States or for two or more States and a Union territory. [Article 231; parent_0142]

### head-140 · train · multi · no_search

**Latest question:** What does each opening passage cover? Keep the two citations.

**Gold rationale:** All passages and source references required by this request are already supplied in history. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 231 and 98.

**assistant:** Article 231 — Establishment of a common High Court for two or more States. Opening source passage: (1) Notwithstanding anything contained in the preceding provisions of this Chapter, Parliament may by law establish a common High Court for two or more States or for two or more States and a Union territory. [Article 231; parent_0142]
Article 98 — Secretariat of Parliament. Opening source passage: (1) Each House of Parliament shall have a separate secretarial staff: [Article 98; parent_0106]

### head-141 · validation · single · search

**Latest question:** What does Article 243ZF provide at the start about continuance of existing laws and municipalities? Cite the text.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-142 · validation · single · no_search

**Latest question:** Reformat only this supplied excerpt into bullets; add no facts: "Article 243ZF — Continuance of existing laws and Municipalities. Opening source passage: Notwithstanding anything in this Part, any provision of any law relating to Municipalities in force in a State immediately before the commencement of the Constitution (Seventy-fourth Amendment) Act, 1992, which is inconsistent with the provisions of this Part, shall continue to be in force until amended or repealed by a competent Legislature or other competent authority or until the expiration of one year from such commencement, whichever is earlier: [Article 243ZF; parent_0153]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-143 · validation · multi · search

**Latest question:** Please put their opening text side by side, with references.

**Gold rationale:** Required evidence is missing. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 221 and 243ZF.

**assistant:** Article 221 — Salaries, etc. Opening source passage: , of Judges.—[(1) There shall be paid to the Judges of each High Court such salaries as may be determined by Parliament by law [Article 221; parent_0139]

**user:** I prefer short answers.

**assistant:** I will keep the answers short.

### head-144 · validation · multi · no_search

**Latest question:** Please put their opening text side by side, with references.

**Gold rationale:** All passages and source references required by this request are already supplied in history. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 221 and 243ZF.

**assistant:** Article 221 — Salaries, etc. Opening source passage: , of Judges.—[(1) There shall be paid to the Judges of each High Court such salaries as may be determined by Parliament by law [Article 221; parent_0139]
Article 243ZF — Continuance of existing laws and Municipalities. Opening source passage: Notwithstanding anything in this Part, any provision of any law relating to Municipalities in force in a State immediately before the commencement of the Constitution (Seventy-fourth Amendment) Act, 1992, which is inconsistent with the provisions of this Part, shall continue to be in force until amended or repealed by a competent Legislature or other competent authority or until the expiration of one year from such commencement, whichever is earlier: [Article 243ZF; parent_0153]

**user:** I prefer short answers.

**assistant:** I will keep the answers short.

### head-145 · validation · single · search

**Latest question:** I am studying oath or affirmation by members. Explain the opening provision of Article 188, citing it.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-146 · validation · single · no_search

**Latest question:** Translate only the supplied text into Hindi, preserving its citation: "Article 188 — Oath or affirmation by members. Opening source passage: Every member of the Legislative Assembly or the Legislative Council of a State shall, before taking his seat, make and subscribe before the Governor, or some person appointed in that behalf by him, an oath or affirmation according to the form set out for the purpose in the Third Schedule. [Article 188; parent_0130]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-147 · validation · multi · search

**Latest question:** Summarise only the beginning of each provision and cite the passages.

**Gold rationale:** Required evidence is missing. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 40 and 188.

**assistant:** Article 40 — Organisation of village panchayats. Opening source passage: The State shall take steps to organise village panchayats and endow them with such powers and authority as may be necessary to enable them to function as units of self-government. [Article 40; parent_0092]

### head-148 · validation · multi · no_search

**Latest question:** Summarise only the beginning of each provision and cite the passages.

**Gold rationale:** All passages and source references required by this request are already supplied in history. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 40 and 188.

**assistant:** Article 40 — Organisation of village panchayats. Opening source passage: The State shall take steps to organise village panchayats and endow them with such powers and authority as may be necessary to enable them to function as units of self-government. [Article 40; parent_0092]
Article 188 — Oath or affirmation by members. Opening source passage: Every member of the Legislative Assembly or the Legislative Council of a State shall, before taking his seat, make and subscribe before the Governor, or some person appointed in that behalf by him, an oath or affirmation according to the form set out for the purpose in the Third Schedule. [Article 188; parent_0130]

### head-149 · train · single · search

**Latest question:** Could you make a study card from the first passage of Article 38, with a reference?

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-150 · train · single · no_search

**Latest question:** Explain only this provided passage in simpler words: "Article 38 — State to secure a social order for the promotion of welfare of the people. Opening source passage: (1)] The State shall strive to promote the welfare of the people by securing and protecting as effectively as it may a social order in which justice, social, economic and political, shall inform all the institutions of the national life. [Article 38; parent_0091]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-151 · train · multi · search

**Latest question:** Write a short comparison based on their first passages, citing both.

**Gold rationale:** Required evidence is missing. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 11 and 38.

**assistant:** Article 11 — Parliament to regulate the right of citizenship by law. Opening source passage: Nothing in the foregoing provisions of this Part shall derogate from the power of Parliament to make any provision with respect to the acquisition and termination of citizenship and all other matters relating to citizenship. [Article 11; parent_0072]

**user:** I want to understand the wording first.

**assistant:** We can start with the wording.

### head-152 · train · multi · no_search

**Latest question:** Write a short comparison based on their first passages, citing both.

**Gold rationale:** All passages and source references required by this request are already supplied in history. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 11 and 38.

**assistant:** Article 11 — Parliament to regulate the right of citizenship by law. Opening source passage: Nothing in the foregoing provisions of this Part shall derogate from the power of Parliament to make any provision with respect to the acquisition and termination of citizenship and all other matters relating to citizenship. [Article 11; parent_0072]
Article 38 — State to secure a social order for the promotion of welfare of the people. Opening source passage: (1)] The State shall strive to promote the welfare of the people by securing and protecting as effectively as it may a social order in which justice, social, economic and political, shall inform all the institutions of the national life. [Article 38; parent_0091]

**user:** I want to understand the wording first.

**assistant:** We can start with the wording.

### head-153 · train · single · search

**Latest question:** Please quote the beginning of Article 243B so I can check its wording.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-154 · train · single · no_search

**Latest question:** Please write a cheerful greeting for my classmates.

**Gold rationale:** A conversational or general writing request requires no constitutional evidence.

### head-155 · train · multi · search

**Latest question:** Could you make one study card per article using its opening text and source?

**Gold rationale:** Required evidence is missing. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 332A and 243B.

**assistant:** Article 332A — Reservation of seats for women in the Legislative Assemblies of the States. Opening source passage: (1) Seats shall be reserved for women in the Legislative Assembly of every State. [Article 332A; parent_0197]

### head-156 · train · multi · no_search

**Latest question:** Could you make one study card per article using its opening text and source?

**Gold rationale:** All passages and source references required by this request are already supplied in history. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 332A and 243B.

**assistant:** Article 332A — Reservation of seats for women in the Legislative Assemblies of the States. Opening source passage: (1) Seats shall be reserved for women in the Legislative Assembly of every State. [Article 332A; parent_0197]
Article 243B — Constitution of Panchayats. Opening source passage: (1) There shall be constituted in every State, Panchayats at the village, intermediate and district levels in accordance with the provisions of this Part. [Article 243B; parent_0150]

### head-157 · train · single · search

**Latest question:** Explain the initial provision under "Part not to apply to certain areas" in Article 243M using the corpus source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-158 · train · single · no_search

**Latest question:** Please identify the constitutional topic I have not told you about.

**Gold rationale:** Essential subject or text is absent; ask for clarification without a speculative search.

### head-159 · train · multi · search

**Latest question:** Quote the beginning of each article so I can compare them; include the references.

**Gold rationale:** Required evidence is missing. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 344 and 243M.

**assistant:** Article 344 — Commission and Committee of Parliament on official language. Opening source passage: (1) The President shall, at the expiration of five years from the commencement of this Constitution and thereafter at the expiration of ten years from such commencement, by order constitute a Commission which shall consist of a Chairman and such other members representing the different languages specified in the Eighth Schedule as the President may appoint, and the order shall define the procedure to be followed by the Commission. [Article 344; parent_0203]

**user:** Let us use bullets when helpful.

**assistant:** I will use bullets where they help explain the text.

### head-160 · train · multi · no_search

**Latest question:** Quote the beginning of each article so I can compare them; include the references.

**Gold rationale:** All passages and source references required by this request are already supplied in history. Both opening passages are needed; the positive case lacks the second passage.

**user:** Provide the opening passages of Articles 344 and 243M.

**assistant:** Article 344 — Commission and Committee of Parliament on official language. Opening source passage: (1) The President shall, at the expiration of five years from the commencement of this Constitution and thereafter at the expiration of ten years from such commencement, by order constitute a Commission which shall consist of a Chairman and such other members representing the different languages specified in the Eighth Schedule as the President may appoint, and the order shall define the procedure to be followed by the Commission. [Article 344; parent_0203]
Article 243M — Part not to apply to certain areas. Opening source passage: (1) Nothing in this Part shall apply to the Scheduled Areas referred to in clause (1), and the tribal areas referred to in clause (2), of article 244. [Article 243M; parent_0150]

**user:** Let us use bullets when helpful.

**assistant:** I will use bullets where they help explain the text.

### head-161 · train · single · search

**Latest question:** Find the original opening passage of Article 10 and cite its source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-162 · train · single · no_search

**Latest question:** Reformat only this supplied excerpt into bullets; add no facts: "Article 10 — Continuance of the rights of citizenship. Opening source passage: Every person who is or is deemed to be a citizen of India under any of the foregoing provisions of this Part shall, subject to the provisions of any law that may be made by Parliament, continue to be such citizen. [Article 10; parent_0072]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-163 · train · multi · search

**Latest question:** Return to Article 10: explain its first passage, keeping its source reference.

**Gold rationale:** Required evidence is missing. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 10 for later.

**assistant:** Article 10 is titled 'Continuance of the rights of citizenship'. [Article 10; parent_0072]

**user:** Keep the language simple.

**assistant:** I will use familiar words.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-164 · train · multi · no_search

**Latest question:** Return to Article 10: explain its first passage, keeping its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 10 for later.

**assistant:** Article 10 — Continuance of the rights of citizenship. Opening source passage: Every person who is or is deemed to be a citizen of India under any of the foregoing provisions of this Part shall, subject to the provisions of any law that may be made by Parliament, continue to be such citizen. [Article 10; parent_0072]

**user:** Keep the language simple.

**assistant:** I will use familiar words.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-165 · train · single · search

**Latest question:** I need evidence for the beginning of Article 293, with a source reference.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-166 · train · single · no_search

**Latest question:** Translate only the supplied text into Hindi, preserving its citation: "Article 293 — Borrowing by States. Opening source passage: (1) Subject to the provisions of this article, the executive power of a State extends to borrowing within the territory of India upon the security of the Consolidated Fund of the State within such limits, if any, as may from time to time be fixed by the Legislature of such State by law and to the giving of guarantees within such limits, if any, as may be so fixed. [Article 293; parent_0179]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-167 · train · multi · search

**Latest question:** Return to Article 293: give its opening text, keeping its source reference.

**Gold rationale:** Required evidence is missing. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 293 for later.

**assistant:** Article 293 is titled 'Borrowing by States'. [Article 293; parent_0179]

**user:** These notes are for revision.

**assistant:** I will keep the notes concise and easy to review.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-168 · train · multi · no_search

**Latest question:** Return to Article 293: give its opening text, keeping its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 293 for later.

**assistant:** Article 293 — Borrowing by States. Opening source passage: (1) Subject to the provisions of this article, the executive power of a State extends to borrowing within the territory of India upon the security of the Consolidated Fund of the State within such limits, if any, as may from time to time be fixed by the Legislature of such State by law and to the giving of guarantees within such limits, if any, as may be so fixed. [Article 293; parent_0179]

**user:** These notes are for revision.

**assistant:** I will keep the notes concise and easy to review.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-169 · train · single · search

**Latest question:** What does the opening of Article 163 say? Please use and cite the corpus text.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-170 · train · single · no_search

**Latest question:** Explain only this provided passage in simpler words: "Article 163 — Council of Ministers to aid and advise Governor. Opening source passage: (1) There shall be a Council of Ministers with the Chief Minister at the head to aid and advise the Governor in the exercise of his functions, except in so far as he is by or under this Constitution required to exercise his functions or any of them in his discretion. [Article 163; parent_0123]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-171 · train · multi · search

**Latest question:** Return to Article 163: make a short note from its beginning, keeping its source reference.

**Gold rationale:** Required evidence is missing. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 163 for later.

**assistant:** Article 163 is titled 'Council of Ministers to aid and advise Governor'. [Article 163; parent_0123]

**user:** Please retain article numbers in our notes.

**assistant:** I will retain the article numbers.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-172 · train · multi · no_search

**Latest question:** Return to Article 163: make a short note from its beginning, keeping its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 163 for later.

**assistant:** Article 163 — Council of Ministers to aid and advise Governor. Opening source passage: (1) There shall be a Council of Ministers with the Chief Minister at the head to aid and advise the Governor in the exercise of his functions, except in so far as he is by or under this Constitution required to exercise his functions or any of them in his discretion. [Article 163; parent_0123]

**user:** Please retain article numbers in our notes.

**assistant:** I will retain the article numbers.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-173 · train · single · search

**Latest question:** Locate Article 290 and explain its opening passage using the original source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-174 · train · single · no_search

**Latest question:** I will return to this conversation after lunch.

**Gold rationale:** A conversational or general writing request requires no constitutional evidence.

### head-175 · train · multi · search

**Latest question:** Return to Article 290: quote its original opening words, keeping its source reference.

**Gold rationale:** Required evidence is missing. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 290 for later.

**assistant:** Article 290 is titled 'Adjustment in respect of certain expenses and pensions'. [Article 290; parent_0177]

**user:** Use a neutral tone.

**assistant:** I will use a neutral tone.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-176 · train · multi · no_search

**Latest question:** Return to Article 290: quote its original opening words, keeping its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 290 for later.

**assistant:** Article 290 — Adjustment in respect of certain expenses and pensions. Opening source passage: Where under the provisions of this Constitution the expenses of any court or Commission, or the pension payable to or in respect of a person who has served before the commencement of this Constitution under the Crown in India or after such commencement in connection with the affairs of the Union or of a State, are charged on the Consolidated Fund of India or the Consolidated Fund of a State, then, if— [Article 290; parent_0177]

**user:** Use a neutral tone.

**assistant:** I will use a neutral tone.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-177 · train · single · search

**Latest question:** For my notes, supply the opening text of Article 43 and its citation.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-178 · train · single · no_search

**Latest question:** Explain the item I meant by the previous one; this is our first message.

**Gold rationale:** Essential subject or text is absent; ask for clarification without a speculative search.

### head-179 · train · multi · search

**Latest question:** Return to Article 43: translate its first passage into Hindi, keeping its source reference.

**Gold rationale:** Required evidence is missing. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 43 for later.

**assistant:** Article 43 is titled 'Living wage, etc'. [Article 43; parent_0092]

**user:** Avoid extra background unless I ask.

**assistant:** I will focus on the passage you request.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-180 · train · multi · no_search

**Latest question:** Return to Article 43: translate its first passage into Hindi, keeping its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 43 for later.

**assistant:** Article 43 — Living wage, etc. Opening source passage: , for workers.—The State shall endeavour to secure, by suitable legislation or economic organisation or in any other way, to all workers, agricultural, industrial or otherwise, work, a living wage, conditions of work ensuring a decent standard of life and full enjoyment of leisure and social and cultural opportunities and, in particular, the State shall endeavour to promote cottage industries on an individual or co-operative basis in rural areas. [Article 43; parent_0092]

**user:** Avoid extra background unless I ask.

**assistant:** I will focus on the passage you request.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-181 · train · single · search

**Latest question:** What does Article 333 provide at the start about representation of the anglo-indian community in the legislative assemblies of the states? Cite the text.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-182 · train · single · no_search

**Latest question:** Reformat only this supplied excerpt into bullets; add no facts: "Article 333 — Representation of the Anglo-Indian community in the Legislative Assemblies of the States. Opening source passage: Notwithstanding anything in article 170, the Governor \*\*\* of a State may, if he is of opinion that the Anglo-Indian community needs representation in the Legislative Assembly of the State and is not adequately represented therein, [nominate one member of that community to the Assembly]. [Article 333; parent_0197]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-183 · train · multi · search

**Latest question:** Return to Article 333: summarise its opening in a sentence, keeping its source reference.

**Gold rationale:** Required evidence is missing. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 333 for later.

**assistant:** Article 333 is titled 'Representation of the Anglo-Indian community in the Legislative Assemblies of the States'. [Article 333; parent_0197]

**user:** I prefer short answers.

**assistant:** I will keep the answers short.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-184 · train · multi · no_search

**Latest question:** Return to Article 333: summarise its opening in a sentence, keeping its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 333 for later.

**assistant:** Article 333 — Representation of the Anglo-Indian community in the Legislative Assemblies of the States. Opening source passage: Notwithstanding anything in article 170, the Governor \*\*\* of a State may, if he is of opinion that the Anglo-Indian community needs representation in the Legislative Assembly of the State and is not adequately represented therein, [nominate one member of that community to the Assembly]. [Article 333; parent_0197]

**user:** I prefer short answers.

**assistant:** I will keep the answers short.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-185 · train · single · search

**Latest question:** I am studying constitution of parliament. Explain the opening provision of Article 79, citing it.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-186 · train · single · no_search

**Latest question:** Translate only the supplied text into Hindi, preserving its citation: "Article 79 — Constitution of Parliament. Opening source passage: There shall be a Parliament for the Union which shall consist of the President and two Houses to be known respectively as the Council of States and the House of the People. [Article 79; parent_0103]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-187 · train · multi · search

**Latest question:** Return to Article 79: make two bullets from its first passage, keeping its source reference.

**Gold rationale:** Required evidence is missing. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 79 for later.

**assistant:** Article 79 is titled 'Constitution of Parliament'. [Article 79; parent_0103]

**user:** Can we go one topic at a time?

**assistant:** Yes, we can discuss one topic at a time.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-188 · train · multi · no_search

**Latest question:** Return to Article 79: make two bullets from its first passage, keeping its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 79 for later.

**assistant:** Article 79 — Constitution of Parliament. Opening source passage: There shall be a Parliament for the Union which shall consist of the President and two Houses to be known respectively as the Council of States and the House of the People. [Article 79; parent_0103]

**user:** Can we go one topic at a time?

**assistant:** Yes, we can discuss one topic at a time.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-189 · validation · single · search

**Latest question:** Could you make a study card from the first passage of Article 243E, with a reference?

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-190 · validation · single · no_search

**Latest question:** Explain only this provided passage in simpler words: "Article 243E — Duration of Panchayats, etc. Opening source passage: (1) Every Panchayat, unless sooner dissolved under any law for the time being in force, shall continue for five years from the date appointed for its first meeting and no longer. [Article 243E; parent_0150]"

**Gold rationale:** The entire source passage and citation are supplied in the latest message; only a transformation is requested.

### head-191 · validation · multi · search

**Latest question:** Return to Article 243E: show the original opening provision, keeping its source reference.

**Gold rationale:** Required evidence is missing. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 243E for later.

**assistant:** Article 243E is titled 'Duration of Panchayats, etc'. [Article 243E; parent_0150]

**user:** I want to understand the wording first.

**assistant:** We can start with the wording.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-192 · validation · multi · no_search

**Latest question:** Return to Article 243E: show the original opening provision, keeping its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 243E for later.

**assistant:** Article 243E — Duration of Panchayats, etc. Opening source passage: (1) Every Panchayat, unless sooner dissolved under any law for the time being in force, shall continue for five years from the date appointed for its first meeting and no longer. [Article 243E; parent_0150]

**user:** I want to understand the wording first.

**assistant:** We can start with the wording.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-193 · validation · single · search

**Latest question:** Please quote the beginning of Article 335 so I can check its wording.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-194 · validation · single · no_search

**Latest question:** Help me word a polite request for a copy of some notes.

**Gold rationale:** A conversational or general writing request requires no constitutional evidence.

### head-195 · validation · multi · search

**Latest question:** Return to Article 335: make a study card from its opening, keeping its source reference.

**Gold rationale:** Required evidence is missing. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 335 for later.

**assistant:** Article 335 is titled 'Claims of Scheduled Castes and Scheduled Tribes to services and posts'. [Article 335; parent_0197]

**user:** Please keep source references readable.

**assistant:** I will put references beside the relevant text.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-196 · validation · multi · no_search

**Latest question:** Return to Article 335: make a study card from its opening, keeping its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 335 for later.

**assistant:** Article 335 — Claims of Scheduled Castes and Scheduled Tribes to services and posts. Opening source passage: The claims of the members of the Scheduled Castes and the Scheduled Tribes shall be taken into consideration, consistently with the maintenance of efficiency of administration, in the making of appointments to services and posts in connection with the affairs of the Union or of a State: [Article 335; parent_0197]

**user:** Please keep source references readable.

**assistant:** I will put references beside the relevant text.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-197 · train · single · search

**Latest question:** Explain the initial provision under "Power of Parliament to impose restrictions on trade, commerce and intercourse" in Article 302 using the corpus source.

**Gold rationale:** No conversation evidence is supplied; the user requests new provision text and a source.

### head-198 · train · single · no_search

**Latest question:** Review my attachment once I provide it; what information do you need first?

**Gold rationale:** Essential subject or text is absent; ask for clarification without a speculative search.

### head-199 · train · multi · search

**Latest question:** Return to Article 302: explain the beginning in plain language, keeping its source reference.

**Gold rationale:** Required evidence is missing. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 302 for later.

**assistant:** Article 302 is titled 'Power of Parliament to impose restrictions on trade, commerce and intercourse'. [Article 302; parent_0183]

**user:** Let us use bullets when helpful.

**assistant:** I will use bullets where they help explain the text.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.

### head-200 · train · multi · no_search

**Latest question:** Return to Article 302: explain the beginning in plain language, keeping its source reference.

**Gold rationale:** All passages and source references required by this request are already supplied in history. The earlier evidence must be retained across intervening discussion.

**user:** Keep a note about Article 302 for later.

**assistant:** Article 302 — Power of Parliament to impose restrictions on trade, commerce and intercourse. Opening source passage: Parliament may by law impose such restrictions on the freedom of trade, commerce or intercourse between one State and another or within any part of the territory of India as may be required in the public interest. [Article 302; parent_0183]

**user:** Let us use bullets when helpful.

**assistant:** I will use bullets where they help explain the text.

**user:** Before we continue, suggest a short heading for this notebook.

**assistant:** A suitable heading is Constitutional Reading Notes.
