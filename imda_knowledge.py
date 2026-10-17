───────────────────────────────────────────────────────────────────────────────────────


[01:15:33] 🐍 Python dependencies were installed from /mount/src/imda-preapproval-assistant/requirements.txt using uv.

Check if streamlit is installed

Streamlit is already installed

[01:15:34] 📦 Processed dependencies!




────────────────────── Traceback (most recent call last) ───────────────────────

  /home/adminuser/venv/lib/python3.11/site-packages/streamlit/runtime/scriptru  

  nner/exec_code.py:121 in exec_func_with_error_handling                        

                                                                                

  /home/adminuser/venv/lib/python3.11/site-packages/streamlit/runtime/scriptru  

  nner/script_runner.py:591 in code_to_exec                                     

                                                                                

  /mount/src/imda-preapproval-assistant/app.py:10 in <module>                   

                                                                                

      7 from google.genai import types                                          

      8                                                                         

      9 # Import the multi-turn RAG engine                                      

  ❱  10 from imda_knowledge import query_live_guide_rag                         

     11                                                                         

     12                                                                         

     13 # =========================================================             

────────────────────────────────────────────────────────────────────────────────

────────────────────────────────────────────────────────────────────────────────

   /mount/src/imda-preapproval-assistant/imda_knowledge.py:96                   

      if not text.strip():                                                      

                          ▲                                                     

────────────────────────────────────────────────────────────────────────────────

IndentationError: expected an indented block after 'if' statement on line 96
