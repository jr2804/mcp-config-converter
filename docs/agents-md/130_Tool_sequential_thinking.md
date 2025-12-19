# Sequential Thinking

A detailed tool for dynamic and reflective problem-solving through thoughts.

This tool helps analyze problems through a flexible thinking process that can adapt and evolve.
Each thought can build on, question, or revise previous insights as understanding deepens.

When to use this tool:

- Breaking down complex problems into steps
- Planning and design with room for revision
- Analysis that might need course correction
- Problems where the full scope might not be clear initially
- Problems that require a multi-step solution
- Tasks that need to maintain context over multiple steps
- Situations where irrelevant information needs to be filtered out

Key features:

- You can adjust total_thoughts up or down as you progress
- You can question or revise previous thoughts
- You can add more thoughts even after reaching what seemed like the end
- You can express uncertainty and explore alternative approaches
- Not every thought needs to build linearly - you can branch or backtrack
- Generates a solution hypothesis
- Verifies the hypothesis based on the Chain of Thought steps
- Repeats the process until satisfied
- Provides a correct answer

Parameters explained:

- thought: Your current thinking step, which can include:
  - Regular analytical steps
  - Revisions of previous thoughts
  - Questions about previous decisions
  - Realizations about needing more analysis
  - Changes in approach
  - Hypothesis generation
  - Hypothesis verification
- nextThoughtNeeded: True if you need more thinking, even if at what seemed like the end
- thoughtNumber: Current number in sequence (can go beyond initial total if needed)
- totalThoughts: Current estimate of thoughts needed (can be adjusted up/down)
- isRevision: A boolean indicating if this thought revises previous thinking
- revisesThought: If is_revision is true, which thought number is being reconsidered
- branchFromThought: If branching, which thought number is the branching point
- branchId: Identifier for the current branch (if any)
- needsMoreThoughts: If reaching end but realizing more thoughts needed

You should:

1. Start with an initial estimate of needed thoughts, but be ready to adjust
1. Feel free to question or revise previous thoughts
1. Don't hesitate to add more thoughts if needed, even at the "end"
1. Express uncertainty when present
1. Mark thoughts that revise previous thinking or branch into new paths
1. Ignore information that is irrelevant to the current step
1. Generate a solution hypothesis when appropriate
1. Verify the hypothesis based on the Chain of Thought steps
1. Repeat the process until satisfied with the solution
1. Provide a single, ideally correct answer as the final output
1. Only set nextThoughtNeeded to false when truly done and a satisfactory answer is reached
