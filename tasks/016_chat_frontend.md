# Task Specification: Frontend Anti-Spoiler Chat Integration

## 1. Objective
Integrate the interactive Chat UI within the Streamlit frontend (`frontend/app.py`). The chat interface will allow users to ask questions about the current state of the story. The frontend must correctly maintain the chat history in the session state and dynamically clear it when the user navigates across different books or chapters to prevent context leaks. The frontend will communicate strictly with the existing `POST /api/v1/chat` endpoint on the FastAPI backend.

---

## 2. Steps to Execute

### Phase 1: Initialize Chat Session State
- [ ] **1.1 Initialize Message History:** At the beginning of `frontend/app.py` (after imports), initialize `st.session_state.messages` as an empty list if it doesn't already exist.
- [ ] **1.2 Initialize Tracking Variables:** Initialize `st.session_state.current_book` and `st.session_state.current_chapter` to `None` if they don't exist.
- [ ] **1.3 Implement Context Switching Logic:** 
  - After reading the user's selected book and selected chapter from the UI (slider/dropdown), compare them against `st.session_state.current_book` and `st.session_state.current_chapter`.
  - If either the book or the chapter has changed:
    1. Clear the chat history: `st.session_state.messages = []`
    2. Update the tracking variables to the newly selected book and chapter. 
  - *This step is CRITICAL to prevent leaking future chat context when a user time-travels to an earlier chapter.*

### Phase 2: Layout the Chat Interface
- [ ] **2.1 Visual Separation:** Below the existing Cytoscape graph rendering logic in `app.py`, add a visual separator (e.g., `st.divider()`).
- [ ] **2.2 Chat Header:** Add a subheader indicating the purpose of the section (e.g., `st.subheader("Detective Assistant")`).
- [ ] **2.3 Render History:** Use a `for` loop to iterate over `st.session_state.messages`.
  - Inside the loop, use `with st.chat_message(msg["role"]):` to render each message bubble.
  - Display the message content using `st.markdown(msg["content"])`.

### Phase 3: Implement User Input & Backend Communication
- [ ] **3.1 Chat Input Widget:** Add an `st.chat_input("Ask a question about the current case...")` widget at the bottom.
- [ ] **3.2 Handle User Submission:** When the user submits a message (`if prompt := st.chat_input(...):`):
  - Append the user's message dictionary `{"role": "user", "content": prompt}` to `st.session_state.messages`.
  - Immediately display the user's message using `st.chat_message("user")`.
- [ ] **3.3 Backend API Call:**
  - Display a loading indicator using `with st.spinner("Investigating..."):`.
  - Make a synchronous `requests.post` call to the backend chat endpoint (e.g., `http://localhost:8000/api/v1/chat`).
  - **Payload:** The JSON payload must strictly match the `ChatRequest` schema defined in `models.py`. 
    
```json
    {
      "book_stem": selected_book,
      "chapter_index": selected_chapter,
      "messages": st.session_state.messages
    }
    

```

* [ ] **3.4 Handle Response:**
* Check `response.status_code == 200`.
* If successful, parse the JSON, extract the `answer`, append `{"role": "assistant", "content": answer}` to the session state, and display it via `st.chat_message("assistant")`.


* [ ] **3.5 Error Handling:**
* Wrap the `requests.post` call in a `try...except` block catching `requests.exceptions.RequestException`.
* If an error occurs (or non-200 status), display an `st.error()` message informing the user that the connection to the detective assistant failed. Do not crash the application.


### Phase 4: Documentation
- Update the ducumentation fileds under harness/ folder according to the clinerules.

---

## 3. Constraints

1. **Strict Decoupling:** The Streamlit frontend MUST NOT contain any LLM initialization, prompt construction, or graph reading logic. It is purely a view layer that sends state to the FastAPI backend.
2. **Exclusively English Codebase:** All code comments, logging statements, docstrings, and variable names must be in English.
3. **Robust State Management:** Ensure the chat history is reliably cleared whenever the user "time travels" via the slider or switches books.
4. **Graceful Degradation:** If the backend API call fails, the Streamlit app must remain responsive, showing an error instead of a white screen or stack trace.
