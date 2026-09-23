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
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

<!-- Underneath, paste the REAL output for each criterion from one of your
     runs — the actual text your system produced, not a description of it.
     Name the file and function that produced it. -->

## Verdicts

<!-- MET or MISSED for each of the five, against the target you wrote last
     unit — not a new one. Plus a sentence on how you decided. That sentence
     matters most where it was close.

     If your target said 4 of 5 and your runs came out 4, 3, 4, that's a MISS.
     The target has to hold, not show up occasionally.

     Milestone 2. -->

| # | Criterion | Verdict | How I decided |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |
| 4 |  |  |  |
| 5 |  |  |  |

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

## The Improvement

**What I changed:**

**Why I picked it:**

<!-- Connect it to a specific diagnosis above in one sentence. If you can't,
     you picked a fix because it sounded impressive. -->

### Run Log — After

<!-- Same format, same five criteria, three runs each.
     `python run_eval.py --label after` -->

| Criterion | Target | Run 1 | Run 2 | Run 3 | Verdict |
|---|---|---|---|---|---|
| 1. Retrieved chunk contains the answer | 4 of 5 |  |  |  |  |
| 2. Every answer names a source | 5 of 5 |  |  |  |  |
| 3. Gate stops out-of-corpus questions | 4 of 5 |  |  |  |  |
| 4. | | | | | |
| 5. | | | | | |

**Did it help?**

<!-- Say plainly whether it did, and how you know. If it made things worse,
     say that — a change that backfired, honestly reported, earns full credit
     and is more interesting than one that worked. What matters is that you can
     tell.

     Milestone 4. -->

## What's Still Broken

<!-- For each criterion still missed after your fix: what you'd do about it,
     and why you stopped where you did.

     "I ran out of time" is fine if it's true. Pretending nothing is left is
     not.

     Milestone 5. -->

## What I'd Do Differently

<!-- Knowing what you know now — which of your five criteria would you write
     differently, and why?

     Milestone 5. -->
