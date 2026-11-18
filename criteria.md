# Acceptance criteria — The Unofficial Guide

Five criteria that say what "working" means for this system, written in unit 1
**before** any results existed.

An acceptance criterion names a target: a number, a count, a rate, or something
a person could plainly observe. *"Retrieval works"* is an opinion. *"For at
least 4 of my 5 test questions, the top results include a chunk containing the
answer"* is a criterion.

Under each one, write a sentence or two on **why that target** and not a
stricter or looser one. A reason that says something about your corpus or your
pipeline earns credit; *"80% seemed reasonable"* does not.

> Missing your own targets next unit costs you nothing. Setting a target so
> easy you can't miss it does.

---

## 1. Retrieved chunks contain the answer

For at least 4 of my 5 test questions, the retrieved chunks include one that contains the answer.

**Why this target:**
<!-- e.g. "One of my questions is about a topic only two documents mention, so
     I expect that one to be hard." -->

While all the current test questions have a definite answer retrievable from the corpus, most of them are topics that are only mentioned in just one document. Requiring 5/5 would need perfect retrieval and does not tolerate any occasional miss, while having a lower standard seems to allow too many misses to judge the system as a well functioning retrieval system.

---

## 2. Every answer names a source

Every answer the system produces names at least one source document.

**Why this target:**
<!-- Why all five and not four? What about your setup makes that achievable —
     or what would have to go wrong for it not to be? -->

Naming the source document should be required for each answer as a source document should be an observable proof that the answer is coming from an actual document in the corpus. The  expected answers of the five test questions are also made sure to come from at least one documents from the corpus.

---

## 3. The relevance gate stops out-of-corpus questions

When I ask a question my documents clearly don't cover, the relevance gate
stops it and the system returns "I don't have enough information about that" —
in at least 4 of 5 tries.

<!-- The five questions are the ones in `OUT_OF_SCOPE` at the bottom of
     `questions.py`, and `run_eval.py` puts them through the gate and writes
     what happened into your run log. Swap them for your own if you'd rather —
     just keep five of them, or the "4 of 5" above has nothing to be 4 of. -->

**Why this target:**
<!-- What did your distances look like when you set the cutoff in Milestone 4?
     Was there a clean gap, or did the two groups overlap? -->

Requiring 4/5 allows for classification errors of whether a question is supported, which might happen occasionally. Having a higher threshold means no tolerance at all and having a lower threshold seems to allow out-of-scope questions too frequently for the system to be judged as well-functioning. 

---

## 4. Something about your chunks

<!-- YOU WRITE THIS ONE.

     How would you know if your chunks were the right size? Name something
     countable or observable.

     Examples of the right shape — don't copy these, they should come from
     what you actually saw in Milestone 3:
       - "At least 4 of 5 sampled chunks read as a complete thought, with no
          sentence cut in half at either end."
       - "No chunk is shorter than 200 characters, since anything below that
          in my corpus turned out to be a heading with no content under it." -->

At least 4 of 5 sample chunks contains a piece of factual information which a person can tell the same information using a complete sentence with a subjective and a verb (and an objective if it only makes sense with its presence), and no more than 7 pieces of factual information.


**Why this target:**

This threshold allows for most of the chunks to have at least one useful content and not too much information such that that importance of each piece gets diluted. Requiring more than that would not allow any tolerance, while allowing less than that would allows too many chunks with low amount of information or too much information.

---

## 5. Your choice

<!-- YOU WRITE THIS ONE TOO.

     Pick something you actually care about getting right. It could be about
     speed, about refusals, about a particular kind of question your corpus
     handles badly, about source attribution being correct rather than merely
     present — anything, as long as it names a number or an observable
     outcome. -->

For at least 4 of 5 test questions, every source named in the generated answer actually contains answer to the question (source not only present, but correct).


**Why this target:**

Requiring 4/5 allows for errors when a document appears to be highly relevant but actually does not contain the answer to the question, which might happen sometimes. Having a higher threshold means no tolerance at all and having a lower threshold seems to allow too many answers to cite wrong sources for the system to be judged as well-functioning.

---

---

# Capstone criteria

## 1. Every request leaves one complete log line

Send 20 mixed requests (answered, gate-refused, empty question). The log gets exactly 20 new lines, each valid JSON with all the fields its `status` should have.

**Why this target:** The log is my only view of what the service did, so one bad line makes it hard to trust. 20 of 20 because logging is plain code, so a miss is a bug.

## 2. Answered requests are fast

Out of 20 uncached answered requests, at most 1 has `latency_ms` over 3000.

**Why this target:** My mean is 1158 ms and the slowest I saw was 2307 ms, so 3000 leaves room for Gemini being slow. 2000 would fail on a question I already know is slow. Past 3 seconds, a student would think it's broken. I allow one miss for a random slow call.

## 3. Answers stay cheap

Mean `input_tokens + output_tokens` over 10 uncached answered requests is at most 600.

**Why this target:** I measured 428. Most of that is the 4 retrieved chunks, so it jumps if `TOP_K` or the prompt grows. 600 is about 40% above now, enough to ignore normal swings (input was 366–442) but still catch a real change. 450 would trip on noise. 1000 would let the cost double without me noticing.

## 4. Bad input gets a clean rejection (bad path)

Send `{"question": ""}`, `{}`, and `{"question": "   "}`. Each returns HTTP 400 (not 500), logs `bad_request` with an `error` message and no answer, and uses 0 tokens. A normal question right after still works.

**Why this target:** I've only tried the empty string. A missing key or all spaces could slip through and get sent to Gemini. 3 of 3 because this is simple input checking. A typo from a student shouldn't look like the server crashed.

## 5. A broken pipeline fails loudly and recovers (bad path)

With a bad API key, 3 requests each return HTTP 500, log `status: "error"` with the message and a `latency_ms`, and show no stack trace in the response. After I put the key back, the next request is answered without a restart.

**Why this target:** The Gemini call is the part most likely to fail for real (key, quota, network). If errors aren't logged I won't know why answers stopped, and if one failure kills the server, a bad minute becomes an outage. I've only seen it log once, so 3 of 3 shows it isn't luck.

---

<!-- ─────────────────────────────────────────────────────────────────────────
     UNIT 2 — read this before you change anything above.

     If a criterion turns out to be BROKEN rather than merely unmet, you can
     revise it, and that earns credit. But never delete or edit the original
     line. Add the revision underneath it, like this:

         ## 1. Retrieved chunks contain the answer

         For at least 4 of my 5 test questions, the retrieved chunks include
         one that contains the answer.

         **Why this target:** ...

         > **Revised in unit 2:** For at least 4 of 5 questions, the top three
         > results contain the answer.
         >
         > **Why revised:** I couldn't judge "the chunks include one that
         > contains the answer" the same way twice — I scored two questions
         > differently on Monday than on Wednesday. The new version is
         > something I can actually check.

     That's a revision because the criterion couldn't be MEASURED.

     Lowering a target because you missed it is not a revision, and it costs
     you the point:

         ✗ "I said 4 of 5 but got 2 of 5, so 2 of 5 is more realistic."

     A number you missed stays where it is, gets diagnosed, and gets a fix
     attempted. That's where the points are.

     The whole reason the originals stay visible is so someone can see what you
     said before you knew the answer.
     ───────────────────────────────────────────────────────────────────────── -->
