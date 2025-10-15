# GHOSTWIRE GOALS

## The Idead

Use sqlite as a buffer and cache to save on tokens when talking to remote llm instances. 
This way only want needs to get processed is getting processed. 
It should also provide long term "memory". 

In short the goal is to save as many token as possible
 

The general idea follows this pattern:

User Input -> GHOSTWIRE -> Remote LLM

The procress inside GHOSTWIRE should look something like this:

USER INPUT -> DATABASE -> OUTPUT TO REMOTE LLM

REMOTE LLM INPUT -> DATABASE -> OUTPUT TO USER


- use sqlite as a vector database
- take user input over a fully compatiable ollama and openai endpoints
- take user input and convert to embedding, store those embedings in the sqlite vector database
- pass those embedings to a remote ollama instances
- optionally engage a summerization engine prior to embedding

- A way to store user documents eg code in the vector database
- A way to access that index via a fully compatiable qdrant endpoint
