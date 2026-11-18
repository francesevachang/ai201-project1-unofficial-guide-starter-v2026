# The Unofficial Guide

<!-- Replace this line with your name and which corpus you picked. -->

Name: Frances Chang

Corpus picked: `campus_life`.

> **This file is your submission.** Fill it in as you go — most sections get
> written during the milestone that produces them, not at the end.
>
> How the starter works, and every command you'll need, is in `RUNNING.md`.
> Leave that file alone.
>
> **Paste everything as text.** No screenshots, no video. A typed table gets
> full credit; a picture of the same table gets none.
>
> Delete these instruction blocks as you replace them. The `<!-- -->` comments
> are notes to you and don't show up when the page renders — you can leave them
> or remove them.

---

# Unit 1

## What This Does

<!-- Three or four sentences. Which corpus you picked, and the kinds of
     questions your system answers. Write it for someone who has never seen
     this repo.

     Milestone 5. -->

This project answers questions about the `campus_life` corpus — 88 short posts about dorms, dining halls, courses, and deadlines. It handles specific questions a student would actually ask that the corpus has answers to, like when to drop a class or how long the wait is at a dining hall. It works by breaking each document into small pieces, finding the pieces closest to the question, and only answering when a piece is a close enough match — otherwise it says it doesn't know.

## Chunking Strategy

**Chunk size:**

I did not set a fixed chunk size. Instead, judging the structure of the documents in this corpus, I set each chunk to contain one sentence, preappended by one sentence before it, preappended by the first paragraph of the document, which is the title of the post. My reason for this approach is that most sentences seem to tell at least a piece of information, and the overlap of one sentence further preserves context, especially when a pronoun is used in the current sentence that refers to something mentioned in the previous sentence. I did not slice the documents based on paragraphs because I found out that some longer paragraphs contain multiple pieces of information which I fear would lead to loss of focus on the important information.

**Overlap:**

One sentence right before the current sentence. (Reason stated above.)

<!-- What about YOUR documents made you pick these numbers? Short posts and
     long sectioned guides don't want the same chunking, and "800 seemed
     reasonable" earns nothing. Point at something you noticed when you read
     the documents in Milestone 1.

     If you changed your mind partway through, say so and say why. That's worth
     more than pretending you got it right first time.

     Milestone 3. -->

## Sample Chunks

<!-- Five chunks, pasted as text. Label each one and name the file it came from
     AND the function that produced it — the grader checks your code against
     what you claim here.

     `python app.py chunks -n 5` prints all three for you. Copy them straight
     across.

     Milestone 3. -->

**Chunk 1** — source: ``admin_add_drop_deadline.txt#0 — produced by: chunker.py::split_documents``

```
On the add/drop deadline

You can add a course through the end of the second week.
```

**Chunk 2** — source: ``course_cs_340.txt#2 — produced by: chunker.py::split_documents``

```
CS 340 Databases

Format is lecture twice a week plus a project that runs the whole term. Assessment: one midterm and a final, both open-book.
```

**Chunk 3** — source: ``course_stat_150.txt#3 — produced by: chunker.py::split_documents``

```
STAT 150 Applied Statistics

Assessment: three equally weighted midterms, no final. No curve, but the lowest midterm is dropped.
```

**Chunk 4** — source: ``dining_the_ridgeway_cafe_followup.txt#3 — produced by: chunker.py::split_documents``

```
Re: The Ridgeway Café

If you're trying to eat between classes, go before 11:45 and it's a different building entirely. Also worth saying: seating is tight; about 40 seats for a building of 900.
```

**Chunk 5** — source: ``housing_morrow_house.txt#1 — produced by: chunker.py::split_documents``

```
Morrow House — what it's actually like

Just finished a year in this building. Built 1954, partially renovated 2008.
```

## Sample Answer

<!-- One complete question and answer, pasted as text, with the source line
     visible. Milestone 4. -->

**Question:**

Can I use my remaining printing quota from a past semester?

**Answer:**

```
No, you cannot use remaining printing quota from a past semester because the printing quota does not roll over (admin_printing_quota.txt).
```

**Selected relevance cutoff and reason:**

Based on the results below, the numbers separating the two groups (questions with answers supported in the corpus, versus not) are 0.4679 and 0.7873, so the cutoff should sit in this gap. It seems reasonable to place the cutoff at 0.65, slightly higher than there average 0.63, for a lower risk of the system refusing questions it has answer to.

<!-- The number you set in config.py, and how you got there.

     You ran five questions your corpus covers and the five in OUT_OF_SCOPE
     that it clearly doesn't, and wrote down the best distance for each. What
     did those two groups look like? Where was the gap? Put the actual numbers
     here — the table below wants all ten rows.

     Milestone 4. -->

| Question | In corpus? | Best distance |
|---|---|---|
| When should I drop a class to avoid a W on my transcript? | campus_life/admin_add_drop_deadline.txt | 0.3643 |
| How many classes can I take as pass/fail in my degree? | campus_life/admin_pass_fail_option.txt | 0.3487 |
| What's a typical wait time to talk to a councellor at the health center for the first time? | campus_life/health_center.txt | 0.3976 |
| When does the weather turn warmer after winter? | campus_life/winter_gear.txt | 0.4679 |
| Can I use my remaining printing quota from a past semester? | campus_life/admin_printing_quota.txt | 0.3604 |
| What is the capital of Mongolia? | NOT IN CORPUS | 0.7873 |
| How do I change the oil in a diesel engine? | NOT IN CORPUS | 0.8677 |
| Who won the 1994 World Cup? | NOT IN CORPUS | 0.8270 |
| What is the recommended dosage of ibuprofen for a headache? | NOT IN CORPUS | 0.8327 |
| How do I write a for loop in Rust? | NOT IN CORPUS | 0.8312 |

## How I Used AI

<!-- Two specific moments. For each: what you asked for, what came back, and
     what you changed about it.

     "I asked Claude to write the chunking function from my notes. It ignored
     the overlap, so I added that myself" is the level of detail we're after.
     "I used AI to help me code" is not.

     Milestone 5. -->

**1.** I asked Claude to write the chunking function based on my notes and it actually ignored the overlap for the first time. However, later I changed my chunking approach, and this time it did a good job following my

**2.** I asked Claude to generate a script for retrieving the top results and their relevance for the five test questions and out-of-scope questions. I was very specific about what I was looking for as well as the format, and it did a pretty good job, so I did not change anything.

<!-- ── Stretch features ─────────────────────────────────────────────────────
     Doing one? Say so here BEFORE you start. A feature this README never
     claims earns nothing.
     ───────────────────────────────────────────────────────────────────────── -->

---

# Unit 2

<!-- These sections get ADDED to what's already above. Don't delete or rewrite
     unit 1 — the point is that someone can see what you said before you knew
     how it went. -->

## Run Log — Before

<!-- Your five criteria, three runs each. `python run_eval.py --label before`
     runs the questions, puts the OUT_OF_SCOPE ones through the gate, and
     writes it all into results/ for you. Targets come from criteria.md; the
     verdict column is your call.

     Criterion 3 is measured in one deterministic pass rather than three, so
     the same number goes in all three run columns. That's correct, not lazy.

     Milestone 1. -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 4/5 | MISSED |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Proper chunk size | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Source in generated answer contains answer | 4 of 5 | 5/5 | 5/5  | 4/5 | MET |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

The following are parts of real output from run 1 (outputs are listed in order of the questions).

- Produced by: `run_eval.py::main`
- Retrieval: `store.py::search`, chunks from `chunker.py::split_documents`
- Corpus: `campus_life` (index variant `default`)
- top-k: 4 · relevance cutoff: 0.65
- Runs per question: 3, caching off
- When: 2026-09-23 21:20

### When should I drop a class to avoid a W on my transcript? — run 1

- Best distance: 0.3643 (passed the gate)
- Sources retrieved: admin_add_drop_deadline.txt, admin_grade_appeals.txt, admin_withdrawal_deadline.txt
```
To avoid a W on your transcript, you should drop a class through the end of the second week, because a drop after week two shows as a W. 

Source: admin_add_drop_deadline.txt
```

### How many classes can I take as pass/fail in my degree? — run 1

- Best distance: 0.3487 (passed the gate)
- Sources retrieved: admin_graduation_requirements.txt, admin_pass_fail_option.txt
```
You can take a maximum of eight classes as pass/fail across your degree (with a limit of two per year). 

Source: `admin_pass_fail_option.txt`

```

### What's a typical wait time to talk to a councellor at the health center for the first time? — run 1

- Best distance: 0.3976 (passed the gate)
- Sources retrieved: dining_the_ridgeway_cafe.txt, dining_the_ridgeway_cafe_followup.txt, health_center.txt
```
The typical wait time for a first counselling session is usually three or four days. 

Source: health_center.txt

```

### When does the weather turn warmer after winter? — run 1

- Best distance: 0.4679 (passed the gate)
- Sources retrieved: transit_walking.txt, winter_gear.txt
```
I do not have enough information to answer this question.

Source: winter_gear.txt and transit_walking.txt

```

### Can I use my remaining printing quota from a past semester? — run 1

- Best distance: 0.3604 (passed the gate)
- Sources retrieved: admin_add_drop_deadline.txt, admin_printing_quota.txt
```
No, you cannot use your remaining printing quota from a past semester because it does not roll over. 

Source: `admin_printing_quota.txt`

```


## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 | Retrieved chunk contains the answer | MET | all 5 questions consistently retrieved a chunk containing the answer across all three runs, exceeding the 4/5 bar |
| 2 | Every answer names a source | MISSED | The target allowed zero tolerance (5/5), and Run 3's answer produced no source line at all, failing the threshold |
| 3 | Gate stops out-of-corpus questions | MET | All 5 out-of-scope questions were refused in the single deterministic pass, passing the 4/5 threshold |
| 4 | Proper chunk size | MET | 5 of 5 sampled chunks each carried a clear, checkable fact within the stated bounds |
| 5 | Source in generated answer contains answer | MET | In all but one run, the source named in a generated answer genuinely supported that answer, and the last run only has one question failing to provide a source, thus keeping the result at the 4/5 threshold. |

## Diagnoses

<!-- For each miss: which stage caused it, and how. The stage alone isn't
     enough — you need the mechanism.

     Not a diagnosis: "Question 3 didn't work."
     A diagnosis:     "Question 3 asks about laundry costs. The answer is in
                       one sentence that got split across two chunks, so
                       neither chunk on its own contains it."

     The five stages: loading → chunking → embedding → retrieval → generation.

     Look for a pattern. If three misses all ask about numbers, that's one
     problem, not three.

     Missed nothing? Say so, then say honestly whether your targets were set
     low, and which one you'd tighten and to what.

     Milestone 3. -->


The only criterion missed is the second one, "Every answer the system produces names at least one source document." Run 3 of the fourth question that asks "When does the weather turn warmer after winter?" yields the following:

```
Best distance: 0.4679 (passed the gate)

Sources retrieved: transit_walking.txt, winter_gear.txt

I do not have enough information to answer this question from the provided documents.
```

We can see that the best distance is well under the gate, so the generation stage is what is causing the problem out of the five stages (loading, chunking, embedding, retrieval, generation).

A potential mechanism causing this could be that the model is over-cautious from the strict instruction. Note that in `generate.py`, we specify:

```
GROUNDING_INSTRUCTION = """You answer questions using only the documents provided to you.

Rules:
- Use only the information in the documents below. Do not use anything you know from elsewhere.
- If the documents don't cover the question, say you don't have enough information. Do not guess.
- Name the document your answer came from, using the filename given in each excerpt.
- Be brief. Two or three sentences is usually enough."""
```

However, the document only says "Cold from mid-November to early March" — never "turns warmer" as worded in the question, so the answer "early March" requires one small inference (cold ending implies warmer starting), unlike the other four questions, which are near-exact substring lookups. It's answerable with high confidence, but sits right at the edge of what "do not guess" was meant to prevent, so a strictly-instructed model can reasonably refuse rather than take that one step. This is why this question does not pass criterion 2 and 5, leading to our verdict of a missed criterion (criterion #2).




## The Improvement

If we would like questions similar to the fourth test question to be answered correctly, we would need to edit the grounding instruction to be slightly looser.

**What I changed:**

Added a clause to `GROUNDING_INSTRUCTION` in `generate.py` allowing direct, text-supported inference: "You may state something the documents directly imply — for example, if a document gives a date range for one condition, you may state when that condition ends or begins — as long as you don't bring in facts from outside the documents."

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

The diagnosis showed the model refused question 4 not for lack of evidence but because answering "early March" required one inferential step beyond a direct lookup, which "do not guess" discouraged too broadly — this clause narrows that instruction to still block outside knowledge while permitting inferences the text already supports.

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 2. Every answer names a source | 5 of 5 | 5/5 | 5/5 | 5/5 | MET  |
| 3. Gate stops out-of-corpus questions | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 4. Proper chunk size | 4 of 5 | 5/5 | 5/5 | 5/5 | MET |
| 5. Source in generated answer contains answer | 4 of 5 | 4/5 | 5/5 | 4/5 | MET |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

From the above, we can see that criterion #2 is not met, so it's reasonable to say that the change helps. Although from the running log we can see the generated answer to the same question still does not directly tell the expected answer consistently, but now the model is giving more information for the user to judge on their own whether to make the inference, instead of just saying there is not enough information, which is how we want it to behave.

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

We can see from the running log and the table above that all criteria are met. However, for future improvements, I would consider trying a different chunking approach that yields larger chunks and potentially less overlap, to improve storage and embedding time while retaining retrieval correctness.

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->

I might rewrite criterion #2 for better clarity. As worded — "every answer names at least one source document," target 5/5 — it assumes the only way this criterion fails is a citation-formatting slip (the system found the right chunk, answered, but forgot to write the filename). But what actually happened in Run 3 was different: the generation stage refused to answer at all over an inference gap, so there was no source to name in the first place. A refusal and a missing-citation-on-a-real-answer are two different failure modes with two different fixes, but the criterion as written can't tell them apart — it just says MISSED either way, which obscures which stage actually broke. Given common practice usually exempts refusals from citation requirements, I would rewrite to something like: "Every answer the gate allows through must name at least one source document (5/5), except when the model still refuses to answer after the gate."

And then, score refusal behavior separately under another metric, potentially on whether it states the specific gap (naming what's missing rather than generic "not enough information") and points to what it did find (referencing the closes relevant document/chunk), and those would be new criteria to be written.

## How I Used AI 
I asked Claude to argue the opposite verdict as strongly as it can to see if I did not catch anything. I also used it to confirm my thought on why criterion #2 cannot be met and suggest ways of improvement.

## Capstone

**The System**

The Unofficial Guide, my RAG system over the `campus_life` corpus from units 1 and 2.

**The Shape**

Shape A, deploy and instrument. `serve.py` has no logging right now. I'm adding a structured log so every `/ask` request writes one JSON line (fields listed below). It runs locally (Path B) with `python serve.py`, since the embedding model and Chroma index won't fit well in a 512 MB free tier.

**Log Fields**

One JSON line per `/ask` request, in `logs/requests.jsonl`.

- `timestamp`: when the request came in, UTC.
- `label`: an optional tag I send with the request to find it later, like `before-c1-t2`. `null` if I didn't send one.
- `corpus`: which corpus answered. Always `campus_life` for me.
- `model`: which Gemini model was used.
- `question`: what was asked.
- `status`: what happened. One of:
  - `answered`: the gate passed and the model answered
  - `refused_by_gate`: the question was too far from the corpus, so the model was never called
  - `refused_by_model`: the gate passed, but the model said it didn't have enough information
  - `bad_request`: no question in the request (HTTP 400)
  - `error`: something broke inside the pipeline (HTTP 500)
- `error`: the error message when `status` is `error` or `bad_request`, otherwise `null`.
- `answer`: what came back. `null` on `error` and `bad_request`.
- `sources`: the files the retrieved chunks came from. Empty when the gate refused.
- `num_chunks`: how many chunks retrieval pulled back. Always 4, from `TOP_K`.
- `best_distance`: distance of the closest chunk. Lower is closer. Above 0.65 the gate refuses.
- `cached`: `true` if the answer came from the local cache instead of a real model call.
- `input_tokens`: tokens sent to the model. 0 when cached or refused by the gate.
- `output_tokens`: tokens the model wrote back. Same zeros as above.
- `retrieval_ms`: search plus the gate decision, in milliseconds.
- `generation_ms`: the model call, in milliseconds. 0 when the gate refused.
- `latency_ms`: the whole request, start to finish, in milliseconds. A bit more than `retrieval_ms` + `generation_ms`, since it also covers parsing, imports and prompt building.

Lines with `status` of `error` or `bad_request` stop early, so they leave out the fields that never got filled in (`sources`, `best_distance`, `num_chunks`, `retrieval_ms`, `generation_ms`, `cached` and the token counts). `latency_ms` is always there.

**Out of Scope**

- No changes to chunking, retrieval, the gate, or the prompt.
- No new endpoints or UI.

**Instrumentation**

Every `/ask` request adds a line to `logs/requests.jsonl`, which is committed. The first 10 lines below are my cost run: the 5 test questions twice, cache off, after one warm-up request I left out. The last line is a request with no question in it.

I also tested the error path with a bad API key. It returned a 500 and logged `"status": "error"`. I cleared that log, so it isn't pasted.

```json
{"timestamp": "2026-11-18T20:48:45.795+00:00", "label": "cost-1795034922-1", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "When should I drop a class to avoid a W on my transcript?", "status": "answered", "error": null, "answer": "You should drop a class through the end of the second week to avoid a W on your transcript, because a drop after week two shows as a W. \n\nSource: `admin_add_drop_deadline.txt`", "sources": ["admin_add_drop_deadline.txt", "admin_grade_appeals.txt", "admin_withdrawal_deadline.txt"], "best_distance": 0.3643, "num_chunks": 4, "retrieval_ms": 99, "generation_ms": 806, "cached": false, "input_tokens": 403, "output_tokens": 46, "latency_ms": 905}
{"timestamp": "2026-11-18T20:48:46.704+00:00", "label": "cost-1795034922-2", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "How many classes can I take as pass/fail in my degree?", "status": "answered", "error": null, "answer": "You can take a maximum of two pass/fail courses per year, with a maximum of eight across your entire degree (admin_pass_fail_option.txt).", "sources": ["admin_graduation_requirements.txt", "admin_pass_fail_option.txt"], "best_distance": 0.3487, "num_chunks": 4, "retrieval_ms": 83, "generation_ms": 733, "cached": false, "input_tokens": 400, "output_tokens": 34, "latency_ms": 816}
{"timestamp": "2026-11-18T20:48:47.525+00:00", "label": "cost-1795034922-3", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "What's a typical wait time to talk to a councellor at the health center for the first time?", "status": "answered", "error": null, "answer": "The typical wait time for a first counselling session is usually three or four days (health_center.txt).", "sources": ["dining_the_ridgeway_cafe.txt", "dining_the_ridgeway_cafe_followup.txt", "health_center.txt"], "best_distance": 0.3976, "num_chunks": 4, "retrieval_ms": 89, "generation_ms": 1592, "cached": false, "input_tokens": 442, "output_tokens": 22, "latency_ms": 1681}
{"timestamp": "2026-11-18T20:48:49.210+00:00", "label": "cost-1795034922-4", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "When does the weather turn warmer after winter?", "status": "answered", "error": null, "answer": "Based on the provided documents, the cold period lasts until early March (winter_gear.txt). However, the documents do not state when the weather actually turns warmer.", "sources": ["transit_walking.txt", "winter_gear.txt"], "best_distance": 0.4679, "num_chunks": 4, "retrieval_ms": 81, "generation_ms": 2226, "cached": false, "input_tokens": 366, "output_tokens": 34, "latency_ms": 2307}
{"timestamp": "2026-11-18T20:48:51.520+00:00", "label": "cost-1795034922-5", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "Can I use my remaining printing quota from a past semester?", "status": "answered", "error": null, "answer": "No, you cannot. The printing quota does not roll over from past semesters (admin_printing_quota.txt).", "sources": ["admin_add_drop_deadline.txt", "admin_printing_quota.txt"], "best_distance": 0.3604, "num_chunks": 4, "retrieval_ms": 147, "generation_ms": 557, "cached": false, "input_tokens": 368, "output_tokens": 24, "latency_ms": 704}
{"timestamp": "2026-11-18T20:48:52.228+00:00", "label": "cost-1795034922-6", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "When should I drop a class to avoid a W on my transcript?", "status": "answered", "error": null, "answer": "To avoid a W on your transcript, you should drop a class through the end of the second week, because drops after week two show as a W. \n\nSource: `admin_add_drop_deadline.txt`", "sources": ["admin_add_drop_deadline.txt", "admin_grade_appeals.txt", "admin_withdrawal_deadline.txt"], "best_distance": 0.3643, "num_chunks": 4, "retrieval_ms": 84, "generation_ms": 636, "cached": false, "input_tokens": 403, "output_tokens": 46, "latency_ms": 720}
{"timestamp": "2026-11-18T20:48:52.952+00:00", "label": "cost-1795034922-7", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "How many classes can I take as pass/fail in my degree?", "status": "answered", "error": null, "answer": "You can take a maximum of eight courses pass/fail across a degree, with a limit of two per year (admin_pass_fail_option.txt).", "sources": ["admin_graduation_requirements.txt", "admin_pass_fail_option.txt"], "best_distance": 0.3487, "num_chunks": 4, "retrieval_ms": 80, "generation_ms": 1347, "cached": false, "input_tokens": 400, "output_tokens": 33, "latency_ms": 1427}
{"timestamp": "2026-11-18T20:48:54.384+00:00", "label": "cost-1795034922-8", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "What's a typical wait time to talk to a councellor at the health center for the first time?", "status": "answered", "error": null, "answer": "The typical wait time for a first counselling session is usually three or four days (from health_center.txt).", "sources": ["dining_the_ridgeway_cafe.txt", "dining_the_ridgeway_cafe_followup.txt", "health_center.txt"], "best_distance": 0.3976, "num_chunks": 4, "retrieval_ms": 88, "generation_ms": 833, "cached": false, "input_tokens": 442, "output_tokens": 23, "latency_ms": 921}
{"timestamp": "2026-11-18T20:48:55.308+00:00", "label": "cost-1795034922-9", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "When does the weather turn warmer after winter?", "status": "answered", "error": null, "answer": "Based on the provided documents, the cold period lasts until early March (winter_gear.txt). However, the documents do not specifically state when the weather turns warmer after winter.", "sources": ["transit_walking.txt", "winter_gear.txt"], "best_distance": 0.4679, "num_chunks": 4, "retrieval_ms": 83, "generation_ms": 869, "cached": false, "input_tokens": 366, "output_tokens": 36, "latency_ms": 953}
{"timestamp": "2026-11-18T20:48:56.265+00:00", "label": "cost-1795034922-10", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "Can I use my remaining printing quota from a past semester?", "status": "answered", "error": null, "answer": "No, you cannot. The printing quota does not roll over from one semester to the next (admin_printing_quota.txt).", "sources": ["admin_add_drop_deadline.txt", "admin_printing_quota.txt"], "best_distance": 0.3604, "num_chunks": 4, "retrieval_ms": 85, "generation_ms": 1062, "cached": false, "input_tokens": 368, "output_tokens": 27, "latency_ms": 1147}
{"timestamp": "2026-11-18T20:49:18.746+00:00", "label": "fail-empty-question", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "", "status": "bad_request", "error": "Send JSON with a question in it, like {\"question\": \"is the housing lottery random?\"}", "answer": null, "latency_ms": 0}
```

**What It Costs**

One answered question costs about 430 tokens (396 in, 33 out) and about 1.2 seconds.

I measured it with `tools/measure_cost.py` and `AI201_CACHE=0`. It sends one warm-up request, then 10 more, and averages the logged tokens and latency for those 10.

| Average over 10 warm requests | |
|---|---|
| input tokens | 395.8 |
| output tokens | 32.5 |
| total tokens | 428.3 |
| `latency_ms` | 1158 |
| `retrieval_ms` | 92 |s
| `generation_ms` | 1066 |

I skip the first request because it's slower. On a cold start, retrieval took 1173 ms against about 90 ms after.

A question the gate refuses costs 0 tokens and about 0.1 seconds. A cached repeat also costs 0 tokens.

## Capstone Run Log

Three runs of all five criteria from `criteria.md` (capstone section). Each run starts fresh servers with the cache off and sends one warm-up request that isn't counted. Full output, including every log line, is in `results/capstone_run_2026-11-18_1658.md`. The raw server logs are in `results/capstone_logs/`.

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Every request leaves one complete log line | 20 of 20 | 20/20 | 20/20 | 20/20 | MET |
| 2. Answered requests are fast | at most 1 of 20 over 3000 ms | 8/20 over | 6/20 over | 1/20 over | MISSED |
| 3. Answers stay cheap | mean tokens at most 600 | 430 | 429 | 431 | MET |
| 4. Bad input gets a clean rejection | 3 of 3, then a normal question works | 3/3 | 3/3 | 3/3 | MET |
| 5. A broken pipeline fails loudly and recovers | 3 of 3, then recovers without restart | 3/3, no recovery | 3/3, no recovery | 3/3, no recovery | MISSED |

Notes:
- Criterion 2, run 2: one request failed after 15.5 s on a Gemini rate limit (429). I counted it as a miss. A student waiting on it got an error after 15 seconds.
- Criterion 5: in all three runs the 3 bad-key requests returned a clean 500 and were logged. After the real key was put back into the running server's environment, the next request still failed with the old key error.

All lines below are from run 1, produced by `serve.py::ask` (the `/ask` route) and driven by `tools/run_capstone_eval.py`.

**1. Log lines** (`run_capstone_eval.py::crit1`): one of each status, out of 20.

```json
{"timestamp": "2026-11-18T21:55:08.652+00:00", "label": "c1-r1-1", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "When should I drop a class to avoid a W on my transcript?", "status": "answered", "error": null, "answer": "To avoid a \"W\" on your transcript, you must drop a class by the end of week two, because drops after week two show as a \"W\". \n\nSource: *admin_add_drop_deadline.txt*", "sources": ["admin_add_drop_deadline.txt", "admin_grade_appeals.txt", "admin_withdrawal_deadline.txt"], "best_distance": 0.3643, "num_chunks": 4, "retrieval_ms": 83, "generation_ms": 2327, "cached": false, "input_tokens": 403, "output_tokens": 48, "latency_ms": 2410}
{"timestamp": "2026-11-18T21:55:11.065+00:00", "label": "c1-r1-2", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "What is the capital of Mongolia?", "status": "refused_by_gate", "error": null, "answer": "I don't have enough information about that.", "sources": [], "best_distance": 0.7873, "num_chunks": 4, "retrieval_ms": 85, "generation_ms": 0, "cached": false, "input_tokens": 0, "output_tokens": 0, "latency_ms": 85}
{"timestamp": "2026-11-18T21:55:11.152+00:00", "label": "c1-r1-3", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "", "status": "bad_request", "error": "Send JSON with a question in it, like {\"question\": \"is the housing lottery random?\"}", "answer": null, "latency_ms": 0}
```

**2. Latency** (`run_capstone_eval.py::crit2_and_3`): the slowest request and a fast one. Retrieval stays near 90 ms. The time is in `generation_ms`.

```json
{"timestamp": "2026-11-18T21:54:14.810+00:00", "label": "c23-r1-01", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "When should I drop a class to avoid a W on my transcript?", "status": "answered", "error": null, "answer": "To avoid a W on your transcript, you should drop a class by the end of the second week, as drops after week two result in a W. \n\nSource: admin_add_drop_deadline.txt", "sources": ["admin_add_drop_deadline.txt", "admin_grade_appeals.txt", "admin_withdrawal_deadline.txt"], "best_distance": 0.3643, "num_chunks": 4, "retrieval_ms": 110, "generation_ms": 5761, "cached": false, "input_tokens": 403, "output_tokens": 44, "latency_ms": 5871}
{"timestamp": "2026-11-18T21:54:31.409+00:00", "label": "c23-r1-04", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "When does the weather turn warmer after winter?", "status": "answered", "error": null, "answer": "Based on the provided documents, it states that the winter is cold from mid-November to early March, but the documents do not specifically state when the weather turns warmer after winter. (Source: winter_gear.txt)", "sources": ["transit_walking.txt", "winter_gear.txt"], "best_distance": 0.4679, "num_chunks": 4, "retrieval_ms": 78, "generation_ms": 601, "cached": false, "input_tokens": 366, "output_tokens": 45, "latency_ms": 679}
```

**3. Tokens** (`run_capstone_eval.py::crit2_and_3`): same requests as above. 403 + 44 and 366 + 45. The 10-request mean was 429.6.

**4. Bad input** (`run_capstone_eval.py::crit4`): empty string, missing key, spaces only, then a normal question.

```json
{"timestamp": "2026-11-18T21:55:17.847+00:00", "label": "c4-r1-empty", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "", "status": "bad_request", "error": "Send JSON with a question in it, like {\"question\": \"is the housing lottery random?\"}", "answer": null, "latency_ms": 0}
{"timestamp": "2026-11-18T21:55:17.848+00:00", "label": "c4-r1-missing", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "", "status": "bad_request", "error": "Send JSON with a question in it, like {\"question\": \"is the housing lottery random?\"}", "answer": null, "latency_ms": 0}
{"timestamp": "2026-11-18T21:55:17.849+00:00", "label": "c4-r1-space", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "", "status": "bad_request", "error": "Send JSON with a question in it, like {\"question\": \"is the housing lottery random?\"}", "answer": null, "latency_ms": 0}
{"timestamp": "2026-11-18T21:55:17.850+00:00", "label": "c4-r1-after", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "When should I drop a class to avoid a W on my transcript?", "status": "answered", "error": null, "answer": "To avoid a W on your transcript, you should drop a class by the end of the second week, as drops after week two result in a W. \n\nSource: `admin_add_drop_deadline.txt`", "sources": ["admin_add_drop_deadline.txt", "admin_grade_appeals.txt", "admin_withdrawal_deadline.txt"], "best_distance": 0.3643, "num_chunks": 4, "retrieval_ms": 96, "generation_ms": 624, "cached": false, "input_tokens": 403, "output_tokens": 46, "latency_ms": 720}
```

**5. Bad key** (`run_capstone_eval.py::crit5`): the first error, then the request sent after the real key was put back.

```json
{"timestamp": "2026-11-18T21:55:18.579+00:00", "label": "c5-r1-1", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "When should I drop a class to avoid a W on my transcript?", "status": "error", "error": "ClientError: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'API key not valid. Please pass a valid API key.', 'status': 'INVALID_ARGUMENT', 'details': [{'@type': 'type.googleapis.com/google.rpc.ErrorInfo', 'reason': 'API_KEY_INVALID', 'domain': 'googleapis.com', 'metadata': {'service': 'generativelanguage.googleapis.com'}}, {'@type': 'type.googleapis.com/google.rpc.LocalizedMessage', 'locale': 'en-US', 'message': 'API key not valid. Please pass a valid API key.'}]}}", "answer": null, "latency_ms": 1951}
{"timestamp": "2026-11-18T21:55:21.337+00:00", "label": "c5-r1-recover", "corpus": "campus_life", "model": "gemini-3.5-flash-lite", "question": "When should I drop a class to avoid a W on my transcript?", "status": "error", "error": "ClientError: 400 INVALID_ARGUMENT. {'error': {'code': 400, 'message': 'API key not valid. Please pass a valid API key.', 'status': 'INVALID_ARGUMENT', 'details': [{'@type': 'type.googleapis.com/google.rpc.ErrorInfo', 'reason': 'API_KEY_INVALID', 'domain': 'googleapis.com', 'metadata': {'service': 'generativelanguage.googleapis.com'}}, {'@type': 'type.googleapis.com/google.rpc.LocalizedMessage', 'locale': 'en-US', 'message': 'API key not valid. Please pass a valid API key.'}]}}", "answer": null, "latency_ms": 121}
```
