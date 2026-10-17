    scored = []
    for chunk in chunks:
        title = chunk["title"].lower()
        body = chunk["content"].lower()
        url = chunk["url"].lower()
        title_words = set(_tokens(title))
        body_words = set(_tokens(body))
        score = 5 * len(words & title_words) + len(words & body_words)
        if eligibility:
            if "/eligibility-criteria" in url:
                score += 16
            if "eligib" in title:
                score += 8
            if any(t in q for t in ("month", "incorporat")) and "18 month" in body:
                score += 12
            if "customer" in q and ("customer" in body or "reference" in body):
                score += 8
            if "preparing-submission" in url:
                score -= 6
        if score > 0:
            scored.append((score, chunk))
    scored.sort(key=lambda item: item[0], reverse=True)
    selected = []
    seen = set()
    for _, chunk in scored:
        signature = (chunk["url"], chunk["content"][:100])
        if signature not in seen:
            selected.append(chunk)
            seen.add(signature)
        if len(selected) >= top_k:
            break
    return selected


def _build_prompt(user_query, matches, history):
    context = "\n\n---\n\n".join(
        f"SOURCE: {m['url']}\nSECTION: {m['title']}\nTEXT:\n{m['content']}"
        for m in matches
    )
    recent = "\n".join(
        f"{m.get('role', 'user')}: {str(m.get('content', ''))[:350]}"
        for m in (history or [])[-4:]
    )
    return (
        f"<official_reference_material>\n{context}\n</official_reference_material>\n"
        f"<recent_conversation>\n{recent}\n</recent_conversation>\n"
        f"<vendor_question>\n{user_query}\n</vendor_question>\n"
        "Use only the official reference material. Answer the vendor question succinctly."
    )


def query_live_guide_rag(client, user_query, chat_history=None, model_name=MODEL_NAME):
    """Stream grounded text; compatible with st.write_stream().

    IMPORTANT: This function is a generator, not a string-returning function.
    In app.py call: answer = st.write_stream(query_live_guide_rag(client, question, history))
    """
    if not user_query or not user_query.strip():
        yield "Please enter a question."
        return
    t0 = time.perf_counter()
    matches = search_knowledge(user_query, top_k=5)
    print(f"IMDA retrieval: {time.perf_counter() - t0:.2f}s", flush=True)
    if not matches:
        yield ("I could not locate enough information in the available official guide index. "
               f"Please refer to {BASE_URL}/ or https://go.gov.sg/pareginterest.")
        return
    source_urls = list(dict.fromkeys(m["url"] for m in matches))
    prompt = _build_prompt(user_query, matches, chat_history)
    first_text = True
    completed = False
    finish_reason = None
    try:
        stream = client.models.generate_content_stream(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                temperature=0.1,
                max_output_tokens=1024,
            ),
        )
        for chunk in stream:
            if chunk.candidates:
                reason = getattr(chunk.candidates[0], "finish_reason", None)
                if reason is not None:
                    finish_reason = str(reason)
            text = getattr(chunk, "text", None)
            if text:
                if first_text:
                    print(f"IMDA Gemini first text: {time.perf_counter() - t0:.2f}s", flush=True)
                    first_text = False
                yield text
        completed = True
    except Exception as exc:
        LOGGER.warning("Gemini request failed: %s", type(exc).__name__)
        if first_text:
            yield "The AI service is temporarily unavailable. Please try again shortly."
        else:
            yield "\n\n*The response was interrupted. Please retry the question.*"
    if completed and finish_reason and "MAX_TOKENS" in finish_reason.upper():
        yield "\n\n*The response reached the model's output limit. Please ask a narrower question.*"
    # Cite only retrieved source URLs, not invented links.
    if source_urls:
        url = source_urls[0]
        yield f"\n\n🔗 **Official Reference:** [{url}]({url})"


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    refresh_knowledge()
