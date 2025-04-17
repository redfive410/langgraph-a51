https://langchain-ai.github.io/langgraph/tutorials/introduction/

https://app.tavily.com/home

## 17APR2025
The first graph (with the central router node) actually helps solve the recursion limit issue you were experiencing, despite looking more complex visually. Here's why:
Why the Router Pattern (Image 1) Helps with Recursion Limits:

Stack Depth Control: In the first graph, each node always returns to the central router node before proceeding to the next step. This creates a "hub-and-spoke" pattern where the call stack effectively resets at each step.
Flattened Call Chain: Instead of building a deep chain of function calls (A → B → C → D → A → B...), which increases the recursion depth with each iteration, the router pattern keeps the chain shallow (A → Router, B → Router, C → Router).
Centralized Decision Making: The router examines the state and decides what to do next, rather than having each node determine the next node, which can lead to complex recursive patterns.

Why the Linear Pattern (Image 2) Has Recursion Issues:
The second graph shows a linear flow with a feedback loop. When you have 10 questions:

The call stack builds up as you go from ask_question → answer_question → make_guess → check_game_over
When check_game_over routes back to ask_question, you're creating a deep recursive chain
After several iterations, you exceed Python's recursion limit

The router pattern in the first image breaks this deep recursion by flattening the call structure. After each operation completes, control returns to a central point (the router) before proceeding, preventing the call stack from growing too deep.
So while the second graph looks simpler and more intuitive (and is closer to how we'd think about the game flow), the first graph is actually computationally more efficient for preventing recursion issues in LangGraph.

## 08MAR2025
Experiments with LangGraph

## 23MAR2025
Experiment to create a langgaph 20 questions game.


