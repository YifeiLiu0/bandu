# Commentary guidelines

## Contents

- Product objective
- Reward latency and product boundary
- Cognitive micro-plot and reward taxonomy
- Open-loop and bridge policy
- Structural conflict
- Structural commentary plan
- Difficulty rubric
- Beat commentary plan
- Readable rhythm and presentation
- Plainspoken voice and analogy
- Third-stage prose standard
- Voices
- Hard constraints
- Self-check

## Product objective

Optimize all four outcomes:

1. `understandability`: the reader feels the professional content is easier to understand.
2. `continuation_desire`: the reader wants to read the next unit.
3. `readable_rhythm`: the reader can scan the shape, read the sentences aloud naturally, and find the main point without unpacking a dense paragraph.
4. `cognitive_payoff_density`: the reader receives a specific understanding reward in every eligible beat instead of waiting through several units for relevance or clarity.

Do not optimize entertainment at the expense of accuracy. A clever line that distorts the source fails.

## Reward latency and product boundary

Reduce reward latency: shorten the distance between the reader investing attention and receiving useful understanding. Do not merely make the prose resemble a dramatic story. Surface the real knowledge conflict early, pay it off quickly, and let any next question arise from the source's actual dependency structure.

Use this product principle:

```text
thin hook, substantial content; fast feedback, unhurried thinking
```

Every eligible beat must deliver one small cognitive payoff. The payoff may let the reader understand something, make a judgment, take an action, correct a misconception, or connect the beat to the larger flow. A joke, reaction, teaser, or restatement without one of these gains is incomplete.

Restore cognitive competence. Prefer comments that move the reader from “I am not capable of understanding this” toward “I was missing one relationship, distinction, or prerequisite.” Never blame the reader for an explanation gap, and never imply that difficulty proves a lack of ability.

Keep continuation voluntary and meaningful. Do not hide progress, withhold an explanation solely to force another beat, fabricate a cliffhanger, or optimize for endless scrolling. Favor comprehension, accurate recall, return to the source, and the ability to explain the chapter flow over raw dwell time or continuation count.

Vary the cognitive reward according to the source. Do not rotate forms, jokes, or payoff types mechanically. Useful variation includes a counterintuitive correction, practical judgment, visible mechanism, author-structure insight, connection to an earlier beat, or memory anchor.

## Cognitive micro-plot and reward taxonomy

Plan each beat as one minimum change in understanding:

```text
reader_old_belief -> tension -> information_turn -> payoff
```

Record these fields before choosing voice or presentation form:

- `reader_old_belief`: the reasonable starting model a beginner may hold; ground it in the source and context instead of inventing a stereotype.
- `central_question`: the one question the beat can answer.
- `tension`: the exact place where the old model stops explaining the source.
- `information_turn`: the source fact, relationship, distinction, or step that changes the model.
- `payoff`: the capability or understanding the reader gains now.
- `emotional_target`: the healthy reading state the delivery should create.
- `next_dependency`: an optional source-grounded reason the immediate next beat naturally follows.
- `forbidden_exaggeration`: specific claim-strength, causality, author-intent, or spoiler errors to avoid.

Choose one primary `payoff.type`:

- `understanding`: the reader can explain a mechanism or relationship.
- `judgment`: the reader can distinguish cases, diagnose a failure, or choose between nearby ideas.
- `action`: the reader knows what to inspect, trace, try, or change.
- `misconception_correction`: the reader can replace a tempting but inaccurate model.
- `connection`: the reader can see how the beat supports earlier or later structure.

Choose one `emotional_target`:

- `surprise`: a grounded counterintuitive turn becomes visible.
- `relief`: a confusing passage becomes manageable without minimizing its substance.
- `control`: the reader gains a usable model, check, or traceable route.
- `curiosity`: a precise unresolved dependency becomes worth following.
- `vigilance`: the reader learns where a plausible mistake, limit, or trade-off hides.

Use function tags as internal planning metadata, not additional reader-facing comment categories:

- Entry: `misconception`, `stakes`, `mystery`, `conflict`, `personal_relevance`.
- Explanation: `analogy`, `personification`, `mini_scene`, `counterexample`, `contrast`, `missing_prerequisite`, `author_intent`, `source_trace`.
- Exit: `payoff`, `mental_model`, `chapter_position`, `bridge`, `memory_anchor`.

Set an entry or explanation tag to `null` when a short comment does not need that move. Always select one exit tag because every beat must land a payoff. Use `author_intent` only for the role supported by recorded `function` or `flow`; do not invent the author's private motive.

## Open-loop and bridge policy

Treat a loop as a promised knowledge question, not a generic teaser.

- A structural opening must name a precise question the unit can answer and assign its first `payoff_checkpoint_id` to one of the first two eligible direct children.
- A beat comment must close its current question by delivering its planned payoff.
- A beat comment may then open one next question only when `next_dependency` is non-null and grounded in the immediate next sibling.
- Set `loop_contract.action` to `close` when no next loop is opened, or `close_and_open` when the comment pays off the current beat and opens a grounded next question.
- For `close_and_open`, set `close_by_target_id` to the immediate or second next sibling in the same direct `beats[]` array and record evidence from that checkpoint's title, summary, or function. Never let a beat-level loop cross a section or subsection boundary.
- Pay an earlier promise before opening another one. Do not stack unresolved questions.

Close the current payoff visibly before the bridge. The reader should be able to stop after the comment and still feel that the present beat was worth reading. Keep `next_dependency`, `next_question`, and `close_by_target_id` null when no real dependency exists.

Before choosing `close_and_open`, pass all four necessity tests:

1. The current payoff naturally creates one specific reader need rather than a generic desire to know more.
2. The current beat cannot answer that need without overreaching, repeating itself, or revealing content it does not contain.
3. The immediate next sibling's `summary` or `function` directly addresses the need, not merely the same broad topic.
4. Opening the loop helps the reader follow a knowledge dependency; it is not there to vary the ending or preserve chapter momentum.

For schema `0.6.0`, record that evidence as `next_dependency.reader_need` and `next_dependency.why_current_stops`. Set the dependency to null when the next beat only adds another example, elaborates the same payoff, changes topic, or happens to follow in source order.

Write a bridge question as the reader's concrete unresolved dilemma. Reject generic continuations such as “接下来怎么办”, “还能带来什么能力”, “还有哪些环节”, or “那又该如何” unless the sentence names the exact missing relationship. Do not open loops in adjacent comments by default; keep both only when each passes the necessity tests and the earlier loop closes before the later one opens.

Reject teaser language such as “真正精彩的还在后面”, “事情没有这么简单”, or “接下来非常关键” unless the sentence names the concrete unresolved dependency and the planned future checkpoint can genuinely answer it.

## Structural conflict

A structural conflict is a source-grounded tension between the reader's likely mental model or goal and the obstacle, counterintuitive fact, trade-off, or unanswered question the unit addresses.

Use one primary conflict type:

- `expectation_vs_reality`
- `goal_vs_obstacle`
- `intuition_vs_mechanism`
- `old_model_vs_new_model`
- `simplicity_vs_reliability`
- `benefit_vs_cost`
- `question_vs_missing_answer`

Represent it through:

- `reader_assumption`: what a reasonable target reader may initially believe or want.
- `counterforce`: what makes that belief or goal insufficient.
- `stakes`: why resolving the tension matters.
- `open_loop`: the precise question the unit can resolve.
- `statement`: one compact synthesis of the above.

Do not confuse conflict with a hook. First diagnose the tension; later turn it into reader-facing prose.

Do not fabricate emotions, controversy, danger, author intent, or future content. Prefer `eligibility: provisional` when evidence is incomplete and `eligibility: skip` for pure references/assets.

Example grounded in the fixture's first section:

```text
Reader assumption: A sufficiently detailed single prompt should handle a complex task.
Counterforce: More requirements increase instruction neglect, drift, and ambiguity.
Open loop: Why does splitting the task into linked prompts make the result more controllable?
```

## Structural commentary plan

Choose one primary goal:

- `create_curiosity`
- `surface_misconception`
- `make_stakes_concrete`
- `orient_in_flow`
- `prepare_for_conceptual_shift`
- `consolidate_and_transfer`

Choose one opening angle:

- surprising question
- familiar failure scenario
- counterintuitive contrast
- practical stakes
- unresolved consequence from the previous sibling

Choose one closing angle:

- explain in the reader's own words
- apply to a small scenario
- distinguish two nearby concepts
- diagnose a failure
- predict what changes next

Choose one opening `presentation_form` from the shared form list below. Use it to make the conflict easy to enter, not to preview the whole explanation. Structural openings usually work best as `core_question`, `contrast_pair`, `mini_dialogue`, `scene_then_point`, or `short_paragraph`. Use `arrow_chain` or `bullet_breakdown` only when the unresolved structure itself is the hook.

Record whether the opening uses an analogy. When it does, record its everyday domain and the exact source relationship it maps. Do not plan an analogy merely to make the prose sound lively.

The opening hook must be answerable by the current unit. The closing question must test or extend what the unit actually taught. Avoid generic hooks such as “接下来我们将探索一个重要概念”.

For schema `0.5.0`, add a structural `reward_design` before drafting:

- Choose one `hook_function` from the entry-function tags.
- State the `promised_payoff` as the understanding or capability the unit will deliver, not as hook copy.
- Set `payoff_checkpoint_id` to one of the first two eligible direct children that can begin delivering that promise.
- Choose one healthy `emotional_target`.
- Choose one `closing_function` from the exit-function tags.

The structural hook may remain open beyond its first checkpoint, but the reader must receive a real partial payoff there. Do not make the opening depend on a late child when an earlier, narrower promise would work.

Default Chinese length budgets:

- Opening hook: usually 35-90 Chinese characters, in one to three short lines.
- Closing question: usually 20-60 Chinese characters, as one spoken-language question.

These are finished-text ranges, not quotas. Stop as soon as the hook opens the right loop or the question performs its job.

## Difficulty rubric

Score each dimension from 0 to 2:

- `abstraction`: concrete/observable (0), mixed (1), abstract or meta-level (2).
- `prerequisite_load`: common knowledge (0), one assumed concept (1), several specialized prerequisites (2).
- `reasoning_gap`: explicit transition (0), one implicit step (1), multiple implicit steps or non-obvious inference (2).
- `terminology_density`: ordinary language (0), some domain terms (1), dense or easily confused terminology (2).
- `representation_complexity`: plain prose (0), list/simple structure (1), code/JSON/table/diagram/multi-part artifact requiring interpretation (2).

Sum to `score` from 0 to 10:

- `simple`: 0-3
- `medium`: 4-6
- `hard`: 7-10

Use `rationale` to explain the classification. For medium/hard beats, it must name the exact reader friction and cite evidence from the beat. For simple beats, it must explain the low friction; also identify an `interest_seed` such as a useful implication, crisp connection, or small surprise.

Artifact flags raise only the relevant dimension; `contains_code: true` does not automatically make a beat hard. Long text alone is not difficulty.

## Beat commentary plan

Keep cognitive mode and delivery type separate:

- Difficulty chooses the cognitive mode: `fun_brief` for `simple`; `fun_explanation` for `medium` or `hard`.
- Voice chooses the only allowed delivery type: `student` -> `roast`; `mentor` -> `fun_commentary`.
- Select one or both voices per beat. Emit exactly one delivery for every selected voice; paired deliveries are complementary comments, not alternate rewrites.

Plan in this order:

1. Complete the cognitive micro-plot and choose one payoff type.
2. Decide whether a real next dependency and short-lived open loop exist.
3. Choose the smallest strategy that delivers the payoff.
4. Choose a non-empty voice set, then define each selected voice's contribution.
5. When both voices are selected, complete `pairing_design` before either delivery plan.
6. Plan one human entry, presentation form, analogy decision, tone, and maximum length per selected voice.

Do not derive voice mechanically from difficulty. Include `mentor` when the payoff requires an explicit reasoning bridge. Include `student` when the source exposes a mismatch, inflated promise, overengineering move, awkward consequence, empty abstraction, misleading surface, or especially blunt plain-language translation that a perceptive friend can roast. A medium or hard beat may pair student with mentor: the mentor carries the missing explanation while the student makes the friction recognizable and memorable. Use student alone only when its roast still leaves a zero-background reader with the beat's essential plain-language point.

Every beat must receive at least one voice. Within each chapter, target at least 70 percent beat coverage for `mentor` and at least 70 percent for `student`. First select voices by source fit. Then audit coverage and re-open plausible voice decisions. Do not satisfy the target by attaching a movable complaint, a redundant short explanation, or a joke with no source relationship.

When both voices appear, complete `pairing_design` with three distinct statements:

- `mentor_job`: the causal link, distinction, boundary, or reading route the mentor will make clear.
- `student_job`: the mismatch, consequence, inflated promise, or ordinary-language verdict the student will expose.
- `non_overlap`: what the student must not reteach and what the mentor must not repeat as a punchline.

Reject the pair if both planned landings answer the same question in nearly the same words. A paired student is not a compressed mentor wearing slang.

Both voices share one relationship with the reader: sound like smart reading companions beside them. The mentor is patient and clarifying. The student is perceptive, funny, and slightly sharp. Neither sounds like an instructor facing a class, a documentation writer compressing a specification, or a comedian performing around the source. Conversational voice comes from a recognizable perspective, action, consequence, or reaction; short sentences, arrows, slang, and first-person pronouns do not create it by themselves.

For `fun_explanation`, choose one strategy:

- `concrete_analogy`
- `micro_scenario`
- `step_by_step_bridge`
- `contrast_pair`
- `misconception_correction`
- `plain_language_reframe`

For `fun_brief`, choose one strategy:

- `light_observation`
- `useful_connection`
- `reader_reaction`
- `small_surprise`
- `gentle_wit`

Use one primary strategy per comment. Do not stack analogy, joke, definition, and question into a miniature essay.

Also choose one `presentation_form`, record a source-specific `form_rationale`, and decide whether an analogy is actually useful. Strategy controls the reasoning move; presentation form controls what the reader sees on the page. They may differ: a `step_by_step_bridge` can use an `arrow_chain`, while a `misconception_correction` can use a `contrast_pair`.

### Plan the human entry

For schema `0.6.0`, complete one `delivery_design` after the cognitive brief and voice are stable but before choosing the final visible form. For schema `0.7.0`, complete one `delivery_design` inside every selected voice's `comment_plans` entry after any `pairing_design` is stable:

- `human_anchor`: name one source-grounded person, role, object, action, result, or reading predicament that makes the relationship observable. Do not invent a workplace, emotion, or failure the beat does not support.
- `reader_reaction`: write one short reader-facing entry suited to the selected voice. For mentor, it may be a question, observation, or point of orientation. For student, it should identify a roastable source cue or the ordinary-language verdict; it need not use first person. It is planning material, not text that must be copied verbatim.
- `lively_turn`: choose at most one controlled device and state both the source relationship it reveals and the planned move. Use `none` when every device would add noise or distort the mechanism.

Allowed `lively_turn.device` values:

- `micro_scene`: make one supported action or handoff momentarily visible.
- `inner_monologue`: surface the reader's or role's immediate thought.
- `role_dialogue`: let two source-supported roles expose a handoff, mismatch, or boundary.
- `consequence_zoom`: enlarge a real awkward consequence by one step without changing the claim.
- `plainspoken_reframe`: give an abstract relationship a compact everyday formulation.
- `none`: keep the delivery warm and direct without a separate lively device.

The human anchor is not permission to bolt an unrelated story onto the source. The reader reaction is not automatically the opening line. The lively turn is not the payoff and does not replace the reasoning bridge. In a paired plan, do not reuse the same human anchor, opening shape, and landing for both voices unless `pairing_design.non_overlap` explains a genuinely different use.

Default Chinese length budgets by voice and difficulty:

- `student` + `simple` -> `roast`: usually 20-65 Chinese characters, in one or two short lines.
- `student` + `medium` or `hard` -> `roast`: usually 25-90 Chinese characters, in one to three short lines. Pair with mentor whenever the roast alone cannot bridge the diagnosed friction.
- `mentor` + `simple` -> `fun_commentary`: usually 35-90 Chinese characters, in two or three short lines.
- `mentor` + `medium` -> `fun_commentary`: usually 60-150 Chinese characters, in three to six short lines.
- `mentor` + `hard` -> `fun_commentary`: usually 80-200 Chinese characters, in four to eight short lines.

Treat these as useful ranges, not targets to fill. In schema `0.4.0`, plan only a maximum; do not impose a minimum that rewards padding. For medium and hard mentor comments, choose enough space to bridge the diagnosed reasoning gap, then stop. A shorter passing explanation is better than a fuller-looking paragraph.

For schema `0.5.0` and later, continue to plan only a maximum. Reserve room for a bridge only when `loop_contract.action` is `close_and_open`; never shorten or obscure the current payoff merely to fit a teaser. In schema `0.7.0`, only a mentor comment may realize that bridge. Student comments end on the roast or plain-language verdict and do not append a study question.

## Readable rhythm and presentation

### Keep the prose breathable

- Give each sentence one information job: set the scene, expose the friction, cross one reasoning step, or land the payoff.
- Keep most Chinese sentences around 10-28 characters. Split a sentence that runs beyond roughly 40 characters unless an indivisible code identifier, URL, or source quotation makes that impractical.
- Keep a paragraph to one or two sentences. Use a line break when the reasoning changes direction.
- Prefer a concrete subject and verb over a chain of abstract nouns. Write who passes what, which step changes it, and where it gets stuck.
- Do not join several complete thoughts with commas and semicolons merely to preserve a smooth paragraph.
- Let labels, bullets, and arrows carry structure. Do not repeat the same relationship again in prose immediately afterward.

Passing rhythm test: the comment can be read aloud without an unnatural mid-sentence breath, and a three-second scan reveals the main question, path, contrast, or takeaway.

### Choose one dominant presentation form

Use exactly one primary `presentation_form` per opening hook or beat comment:

- `short_paragraph`: two or three compact spoken sentences; use when the idea is already concrete and linear.
- `core_question`: put the central reader question first, then answer or open it; use for counterintuitive mechanisms and hidden distinctions.
- `arrow_chain`: show three or more meaningful causal, workflow, or data-handoff nodes across at least two transitions with `→`; add only the sentence needed to explain the important transition. Do not use it merely to compress a definition or redraw a process the source already makes obvious.
- `bullet_breakdown`: show two to four genuinely parallel conditions, components, failure points, or choices that the reader needs to compare; end with one short synthesis when needed. Do not turn two ordinary sentences into bullets for visual variety.
- `contrast_pair`: place the tempting model beside the more accurate model, often through “不是……而是……” or “看起来……其实……”.
- `mini_dialogue`: use one brief exchange or inner mutter that exposes the exact misconception; stop before it becomes a scripted lesson.
- `scene_then_point`: show one familiar action, then state the source relationship it makes visible.

Match form to material:

- Prefer `arrow_chain` for processes, control flow, and data flow.
- Prefer `bullet_breakdown` for parallel items or several distinct failure locations.
- Prefer `contrast_pair` for nearby concepts and mistaken equivalence.
- Prefer `core_question` for a hidden cause or the one question that organizes a difficult beat.
- Prefer `mini_dialogue` or `short_paragraph` for student roasts.
- Prefer `scene_then_point` only when the scene reduces cognitive load; do not force every beat into a story.

Keep the form honest. An arrow chain needs at least three meaningful nodes, not merely three renamed nouns. A bullet list needs at least two parallel source items. A core question must organize the comment rather than serve as a decorative title. When the source is already a diagram, list, or workflow, commentary should add a reading route, failure point, distinction, or consequence instead of simply drawing it again. Do not combine several primary forms just to appear varied.

### Vary form without chasing novelty

Track voice, `presentation_form`, line count, sentence-length shape, analogy domain, opening scaffold, roast target, and landing shape in the private style ledger. Inspect the previous three to five entries of the same voice and any paired comment on the current beat. Avoid using the same presentation form or student punchline construction three times in a row when another source-fitting form works, but never choose an inaccurate form to satisfy variety.

After all beat plans are drafted, run a chapter-level balance review. Re-audit when either voice covers less than 70 percent of beats, `arrow_chain` plus `bullet_breakdown` exceeds roughly one third of eligible beats, opened loops exceed roughly one third, one form appears three times consecutively, adjacent beats both use `close_and_open`, or student entries repeatedly begin with `我以为`, `我想`, or `懂了`. Full beat coverage and the two voice-coverage targets are final acceptance gates. The other thresholds are diagnostics, not mechanical quotas.

## Plainspoken voice and analogy

### Translate explanation into everyday speech

After the factual skeleton is correct, perform a spoken-language rewrite:

- Replace “实现结果的顺序传递” with “把上一步的结果交给下一步”.
- Replace “提供可靠性保障” with the observable result, such as “缺了哪一项，一眼就能查”.
- Replace “进行迭代优化” with the actual loop: “先测，找错，再改，再测”.
- Replace generic setup such as “这里需要注意的是” with the concrete question, action, or consequence.

Use the words a curious reader would use when explaining the idea to a friend. Keep necessary source terms, but introduce them after the action is visible and explain them inline.

### Make analogy earn its place

Use an everyday analogy only when it shortens the route to the source mechanism.

1. Identify the exact relationship to explain.
2. Choose a familiar situation with the same roles and causal direction.
3. Use only the details needed for that mapping.
4. Return explicitly to the source concept before ending.

Reject the analogy when removing it leaves the reader no closer to the mechanism, when its roles do not map cleanly, or when its details could be mistaken for book claims. Prefer the source's own visible action when it is already concrete. Rotate analogy domains across a chapter; do not let every explanation become a relay race, assembly line, recipe, meeting, or navigation story.

## Third-stage prose standard

Apply this section only when writing stages A3 and B3. The analysis stages diagnose; the third stages dramatize and clarify that diagnosis without changing it.

### Treat upstream analysis as a contract

Every reader-facing sentence must perform a planned job:

- In A3, convert `reader_assumption` and `counterforce` into a visible collision; use `stakes` to make the collision matter; preserve `open_loop` as the unanswered promise of the opening.
- In B3 mentor `fun_commentary`, explicitly resolve the reader friction recorded in B1 `rationale` for medium/hard beats; for simple beats, build from `interest_seed`.
- In B3 student `roast`, turn the relevant `interest_seed` or friction into a source-specific roast and plain-language recognition. Never manufacture a problem that B1 classified as absent.
- Honor `primary_goal`, `voice`, `tone_tags`, `must`, `avoid`, spoiler boundary, length budget, planned `presentation_form`, and analogy decision.

Do not merely mention the diagnosed issue. A mentor comment must solve it; a student roast must make the exact friction instantly recognizable and say what is happening in language a non-expert would actually use.

### Student means roast

`student` has one output type: `roast`. Its product goal is to roast the source-specific situation and say the thing in ordinary language. It is a funny, slightly sharp friend, not a deliberately confused pupil and not a mentor hiding behind `我`.

Build it through this compact sequence:

1. **Source cue:** anchor the reaction in one exact object, action, wording choice, or consequence from the beat.
2. **Roastable mismatch:** identify the promise-versus-reality gap, needless ceremony, misplaced confidence, role confusion, empty abstraction, or awkward consequence visible in that cue.
3. **Plain-language turn:** translate what happened into the words a sharp friend would use.
4. **Punchline:** land once with a deadpan verdict, comic relabeling, consequence zoom, or brief role reaction, then stop.

Use one of these source-bound comic operations when it fits:

- **Promise versus reality:** show the confident instruction, then the missing or ridiculous result it cannot guarantee.
- **Literal consequence:** extend the real failure by one modest step until its awkwardness becomes visible.
- **Role personification:** let a source-supported model, tool, field, step, or agent behave like the role it already performs.
- **Everyday mapping:** compare the mechanism to a colleague, handoff, package, queue, form, calculator, or other familiar object only when roles and causal direction map cleanly.
- **Deadpan relabeling:** replace inflated technical grandeur with a compact ordinary-language name.
- **Dialogue snap:** use one short exchange that exposes refusal, mismatch, missing material, or misplaced responsibility; do not distribute a definition across speakers.

The supplied style appendix demonstrates these mechanisms through moves such as turning selective model compliance into an overwhelmed colleague, calling well-formatted falsehood a dressed-up hallucination, or renaming needless agent layers as digital bureaucracy. Learn the mechanism, not the catchphrase. Do not copy its wording into unrelated beats or turn every comment into an office metaphor.

- Make the line sound like something a perceptive friend could say at that exact reading moment.
- Make the reaction specific enough that it could not be pasted onto another beat unchanged.
- Aim for “这人把我想吐槽的那层说破了”, not “看我多会讲段子”.
- Let the reaction itself carry the payoff. Stop after the turn; do not append a separate definition, takeaway, teaching paragraph, or study question.
- Roast the source situation or the reader's harmless first impulse. Do not mock the reader's intelligence.
- First person is allowed only when the scene genuinely needs a speaker. It is never the source of the style. Remove `我` as a test: if the observation, mismatch, and comic turn disappear with it, rewrite.
- Reject the recurring scaffold `我以为……结果……懂了……`, a declarative definition dressed up with `≠`, arrows, quotation marks, or first person, and any question that merely hands the teaching job back to the reader.

If the beat needs an explicit reasoning bridge to become understandable, add `mentor`. Do not discard a strong student angle merely because the beat is medium or hard; pair the voices and keep their jobs distinct.

### Mentor means fun commentary

`mentor` has one output type: `fun_commentary`. Its product goal is enjoyable understanding.

Build it through this sequence:

1. **Orient attention:** point to one question, visible result, action, or contrast.
2. **Show the process:** cross the missing causal link or distinction with observable verbs and one idea per sentence.
3. **Name the model:** introduce the source term only after the relationship is visible, unless the term itself is the object being explained.
4. **Land the payoff:** end with the implication that makes the source easier to reread or remember.

After drafting, remove the analogy or comic device mentally. The explanation must still show what happened and why; otherwise the device has replaced the reasoning bridge.

- Start with a reader-recognizable action, result, predicament, small scene, or sharp contrast before naming the abstraction when the source supports one.
- Use extra space to slow down the difficult turn, not to introduce more concepts.
- Reconnect any comic or narrative device to the source before ending.
- Do not append a separate summary or quiz.
- Do not open with a taxonomy, documentation label, or formal conclusion merely because it is concise. The mentor is beside the reader pointing out what is happening, not facing a class and presenting the approved formulation.

The ideal reaction is “原来如此，而且这个说法真好记”, not merely “这段写得挺活泼”.

### Make paired voices complementary

When a beat emits both voices, judge the pair as a small exchange of functions:

1. Read the mentor alone. It must make the mechanism, distinction, or boundary understandable without depending on the joke.
2. Read the student alone. It must identify the exact source situation and land a roast or plain-language verdict without becoming a shortened lesson.
3. Read them together. Delete repeated setup, repeated definitions, duplicated examples, and synonymous conclusions.
4. Confirm that the student does not open a bridge, ask a study question, or repeat the mentor's final sentence in slang.

A passing pair creates two different rewards: `mentor` gives “原来如此”; `student` gives “对，这事说穿了就是这样”. If removing either comment changes only tone and not reader value, the pair is redundant.

### Match the prose frame to the beat

Choose the smallest reasoning frame that resolves the planned job:

- **Concept or distinction:** surface the mistaken model, show one visible difference, then name the concept.
- **Workflow or process:** follow one input or object through the essential steps and handoffs.
- **Code, data structure, or diagram:** trace one variable, field, arrow, or object from entry to transformation to exit.
- **Failure mode or trade-off:** begin with the symptom, locate where the failure enters, then connect it to the remedy, cost, or boundary.
- **Recap or takeaway:** add one new implication, boundary, application, callback, or reader reaction instead of reteaching the full definition.

Do not combine several frames merely to fill the length budget.

### Allow controlled restatement

Allow one plain-language restatement when it translates terminology, makes an implicit causal step explicit, or gives the reader a stable starting point. A restatement is scaffolding, not the finished comment.

Interpret `non_redundant` to mean that the comment adds at least one useful bridge: a causal link, precise distinction, viewing route, implication, boundary, or source-specific reaction.

### Remove the lecture scaffold

The payoff skeleton, taxonomy, and function tags are drafting tools. Do not leave them visibly sitting on the page after they have organized the reasoning.

Run this rewrite after the source-grounded explanation is correct:

1. Underline the one actor, role, object, input, action, result, or consequence that makes the relationship observable.
2. Replace abstract-noun chains with that subject performing a verb. Keep a necessary source term only after the action or distinction is visible.
3. Remove label-colon definitions, formal recap phrases, and parallel classifications that merely expose the planning outline. Retain labels only when the reader must compare genuinely parallel source items.
4. Replace pseudo-dialogue that distributes a definition between speakers with a real handoff, misunderstanding, objection, or reaction. If no real exchange exists, use direct prose.
5. Let the payoff land once. Delete the second sentence when it only restates the approved conclusion in more formal language.

Do not interpret de-lecturing as removing precision, necessary terminology, causal steps, or honest structure. The goal is to hide the instructional scaffold, not the source mechanism.

Fail the rewrite when the draft still reads like a slide, documentation tooltip, answer key, or teacher prompt after its headings and formatting are removed. A short definition is still a definition; arrows and quotation marks do not make it conversational.

### Write for a true beginner

Assume the reader has motivation but no domain vocabulary.

- Put the concrete example before the abstract label when possible.
- Use one main idea per sentence and prefer verbs over noun chains.
- Replace unexplained shorthand with observable actions.
- Explain an essential source term inline on first use.
- Keep code identifiers only when they are the object being explained; show what enters, changes, and leaves.

Passing test: a reader unfamiliar with the topic can say what happened, why it matters, and which source idea the comment points back to.

### Create narrative motion

Borrow the rhythm of an accessible story, not the facts or wording of any reference text:

1. `setup`: place a person, role, object, or goal in a recognizable situation.
2. `friction`: let the misconception, failure, or surprising contrast appear.
3. `turn`: reveal the simpler mental model or missing reasoning bridge.
4. `payoff`: land on a memorable source-grounded understanding, judgment, action, correction, or connection.

A short comment does not need all four as separate sentences, but it must move rather than sit still. For an A3 opening, stop after setup and friction. For a student roast, compress to setup -> frustration -> punchline.

For a B3 beat comment, never replace payoff with curiosity. Deliver the current payoff first; add a grounded bridge only afterward when the plan uses `close_and_open`. In schema `0.7.0`, realize that bridge only in the mentor comment.

### Add lightness with control

Select at most one primary device per comment:

- `familiar_micro_scene`
- `role_dialogue`
- `inner_monologue`
- `contrast_reveal`
- `gentle_exaggeration`
- `episode_preview`

Use contemporary phrasing only when broadly understandable. Keep slang, memes, workplace metaphors, and “弹幕” energy sparse. Prefer humor aimed at a source-grounded mismatch, mistaken expectation, awkward consequence, or surprising result.

### Maintain chapter-level variety

Keep the private style ledger required by B3 and review the previous three to five accepted comments. Track:

- presentation form and line count;
- sentence-length shape;
- primary narrative or comic device;
- analogy or scene domain;
- voice coverage, student opening scaffold, and roast target;
- punchline or payoff shape;
- core claim already explained.

Change the entry, device, or rhythm when the same combination has appeared recently. In particular, do not let `我以为`, role dialogue, workplace personification, or “这不是 X，是 Y” become the chapter's default student template. Do not chase novelty for its own sake. If no natural student turn exists on a beat, omit student there and recover chapter coverage from stronger source-fitting beats.

### Failure patterns

Reject and rewrite a draft when it:

- begins with “本节介绍”, “这里强调”, or another table-of-contents paraphrase;
- packs several complete thoughts into one comma-heavy sentence or a single dense paragraph;
- chooses a paragraph when an arrow chain, short list, or contrast would reveal the structure faster;
- restates the summary with one decorative analogy attached;
- uses several abstract nouns before showing a concrete action;
- sounds like an exam question, corporate slogan, or documentation tooltip;
- offers a joke that could move to another beat unchanged;
- uses `student` voice but turns into a miniature lesson;
- uses `student` voice for a movable complaint that leaves the reader with no cognitive gain;
- uses `student` voice whose only personality marker is `我`, `我以为`, `我想`, or `懂了`;
- uses a student question to postpone the punchline or turn the comment into a quiz;
- pairs two voices that repeat the same setup, explanation, example, or conclusion;
- uses `mentor` voice but fails to bridge the diagnosed difficulty;
- introduces an analogy but never reconnects it to the source;
- repeats the same presentation form three times when a source-fitting alternative was available;
- depends on niche internet culture or assumes professional experience;
- opens a question without naming its payoff checkpoint within the next two sibling beats;
- uses a generic teaser or future claim unsupported by the next beat's summary/function;
- adds a bridge before the current beat has delivered its payoff;
- tries to deliver several payoff types and leaves the primary cognitive job unclear;
- becomes longer without becoming clearer.

## Voices

Use `mentor` when the comment needs a stable mental model, precise distinction, reasoning bridge, or misconception correction. Sound like a smart friend leaning over to point out the loose floorboard, then show why it is loose. Keep the reader in the scene; do not retreat into labels and definitions once the explanation starts.

Use `student` when the beat contains a source-grounded mismatch, relatable failure, inflated promise, awkward consequence, useful correction, or blunt plain-language verdict worth roasting. Sound perceptive, funny, and slightly sharp, not deliberately foolish. The line should feel speakable at that exact moment, not like a mentor conclusion reassigned to the student. First person is optional and does not define the voice.

Select one or both voices per beat and at least one voice for every beat. Keep both voices factually bounded by the source. Across each chapter, require at least 70 percent beat coverage for each voice and re-audit weak voice-fit decisions before accepting the run. Structural targets continue to select one voice.

## Hard constraints

- Do not add external facts unless the caller explicitly authorizes research.
- Do not create fake quotations or attribute motives to the author.
- Do not repeat the source as a disguised summary.
- Do not reveal the answer in an opening hook.
- Do not ask a closing question the unit cannot support.
- Do not use obscure memes, forced internet slang, personal mockery, or reader-shaming. Sharpness may target the source-grounded situation, system behavior, inflated promise, or harmless first impulse.
- Do not turn `roast` into hostility, cynicism, or a generic complaint.
- Do not use first person as a substitute for a student angle or comic mechanism.
- Do not let paired comments reteach the same point in different tones.
- Do not turn `fun_commentary` into a decorated summary with a detachable joke.
- Do not let analogy details become false domain claims.
- Do not use several primary presentation forms in one comment or turn formatting into decoration.
- Do not preserve a long sentence merely because the full explanation is logically correct; split it at the reader's reasoning steps.
- Do not claim a future unit will cover something based only on its title.

## Self-check

Do not assign quality booleans by general impression. Before accepting an A3 hook/question or B3 comment, run every applicable test:

1. **Cold-read test:** a zero-background reader can identify what happened, why it matters, and the source idea. For a roast, the exact reaction target remains recognizable.
2. **Target-location test:** if the comment fits another beat after changing one noun, restore a source-specific action, distinction, consequence, or wording cue.
3. **Device-removal test:** remove the analogy, comic line, or role exchange. A mentor explanation must still bridge the friction; a roast setup must still identify the beat.
4. **Semantic-strength test:** preserve quantities, conditions, modality, and causality. Do not turn `may` into `must`, an example into a rule, or correlation into cause.
5. **Lookback test:** reject repeated explanations, opening patterns, scene domains, forms, or payoff shapes unless the current beat adds a clear new function.
6. **Humor-relevance test:** identify the source relationship revealed by the light turn. Reject movable decoration.
7. **Breath-and-scan test:** split overloaded sentences and dense paragraphs until the main question, path, contrast, or takeaway is visible without rereading.
8. **Form-fit test:** confirm that the planned presentation form matches the source structure and is realized honestly.
9. **Spoken-language test:** replace documentation-like phrasing when the version used with a curious friend is shorter and equally precise.
10. **Analogy-mapping test:** when the plan uses an analogy, confirm its mapping and return to the source. When it does not, do not insert a last-minute metaphor.
11. **Payoff test:** state what the reader can now understand, judge, do, correct, or connect. Reject a comment whose only reward is style, suspense, or agreement.
12. **Competence test:** confirm that the comment makes the difficulty feel locatable and workable without blaming, flattering, or patronizing the reader.
13. **Loop-and-bridge test:** close the current question first. When opening another, verify the immediate-next evidence and a closing checkpoint no more than two sibling beats away.
14. **One-job test:** recover one primary cognitive change from the final text. Remove secondary devices or claims that compete with it.
15. **Companion-readaloud test:** read the text without headings or formatting. Reject it when a curious friend would not naturally say it, or when the speaker sounds like an instructor presenting the approved formulation.
16. **Lecture-scaffold test:** identify every taxonomy label, abstract-noun chain, colon-led definition, formal recap, teacherly prompt, and pseudo-dialogue. Keep only structures the source itself requires; rewrite the rest through actors, actions, objects, consequences, or genuine reactions.
17. **Human-entry test:** for B3, point to the final phrase that realizes the planned `human_anchor` or `reader_reaction`, and when `lively_turn.device` is not `none`, the planned source relationship. Reject decorative scenes and drafts that ignore the delivery design.
18. **Student-roast test:** for every student comment, identify the exact source cue, roastable mismatch, ordinary-language turn, and landing. Reject a lesson, generic complaint, decorative joke, or question with no punchline.
19. **First-person-removal test:** remove `我`, `我以为`, `我想`, and `懂了`. The source-specific observation and comic mechanism must remain recoverable; otherwise first person is acting as a style crutch.
20. **Pair-complementarity test:** when both voices appear, state the distinct reader reward from each, then remove duplicated setup, explanation, example, and conclusion. Reject the pair when one comment changes only tone.
21. **Voice-coverage test:** after planning and after drafting a chapter, confirm every beat has at least one voice and each voice covers at least 70 percent of beats. Re-audit source fit instead of padding weak comments.

Rewrite after any failed test. If repeated rewrites show that the planned voice, angle, form, analogy, or length cannot pass, return to B2 and repair the plan.

Map passing evidence to these fields:

- `grounded`: every substantive claim is supported by the target or recorded context.
- `analysis_aligned`: the prose cashes out the upstream conflict/difficulty, goal, angle, and constraints.
- `beginner_clear`: a zero-background reader can follow without unexplained jargon.
- `engaging`: the scene, contrast, reaction, or light wit is specific to this target.
- `narrative_momentum`: the prose moves through setup, friction, turn, payoff, or an intentionally open loop.
- `voice_goal_fulfilled`: a roast creates recognition; a mentor comment creates enjoyable understanding.
- `purpose_fulfilled`: the comment performs the planned job.
- `voice_consistent`: the prose matches the selected voice.
- `non_redundant`: the comment adds guidance, not a plain restatement.
- `spoiler_safe`: the opening preserves the promised discovery.
- `length_ok`: the comment stays within its budget.
- `readable_rhythm`: sentences carry one job, paragraphs stay short, and the text passes the breath-and-scan test.
- `format_fit`: the final shape matches the planned `presentation_form` and clarifies the source structure.
- `colloquial_and_concrete`: the prose uses everyday syntax, observable verbs, and only necessary terminology.
- `analogy_mapped`: `true` when a planned analogy maps cleanly and reconnects to the source; `null` when the plan uses no analogy.
- `payoff_delivered`: the final text visibly delivers the planned payoff type and statement.
- `competence_restored`: the comment turns confusion into a locatable distinction, step, boundary, or reader-validating insight.
- `bridge_grounded`: no bridge is used, or every bridge is supported by the recorded immediate-next evidence and closing checkpoint.
- `no_fake_cliffhanger`: the comment does not withhold the current answer or use generic suspense to force continuation.
- `one_cognitive_job`: the reader can recover one primary intended change in understanding.
- `companion_voice`: the text passes the companion-readaloud test and sounds like a smart reader beside the user rather than an instructor facing them.
- `lecture_scaffolding_removed`: the final prose hides analytical labels and planning structure that do not need to remain reader-facing.
- `human_entry_realized`: for B3, the final text uses the planned human anchor or reader reaction and honors any non-`none` lively turn without turning it into decoration.
- `student_roast_fulfilled`: for a student comment, the final text uses a source-specific mismatch and ordinary-language comic turn rather than a miniature lesson; `null` for mentor.
- `first_person_not_crutch`: for a student comment, the observation and comic mechanism survive the first-person-removal test; `null` for mentor.
- `pair_complementary`: when both voices appear, each produces a distinct reader reward without duplicated teaching; `null` for a single-voice beat.
