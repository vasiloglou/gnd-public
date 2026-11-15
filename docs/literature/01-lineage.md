# Trace a method's lineage

A literature note can say a method was fine-tuned from a predecessor,
evaluated as a baseline, or merely cited. Those statements support
different queries. This example keeps the method's name, the source
passage and the meaning of the relation together.

## Start with the passage

Ask an extraction agent to record the work version, exact passage,
predicate, participants and conditions for each assertion. Ask it to
include the experiment, whether the author asserts or negates the
claim, and whether the passage attributes the claim to someone else.
A statement can be an accurate extraction of someone else's assertion
and still supply no positive finding by the document's authors.

Two passages may use similar names for different things. In the worked
example, VampNet makes music and VAMPnet models molecular kinetics.
WhAM generates whale vocalizations and WHAM reconstructs human pose.
Keep the evidence for these decisions with the original spellings.

## Review the statements before querying

Ask a reviewer to decide whether each cited passage supports the
specific predicate and its conditions. Retain declined, abstained,
and missing reviews in the audit record. Keep a supported evaluation
of the Boltz-1 family as an evaluation.

| Query | Result in the example |
|---|---|
| How does transformer-based music generation connect to whale vocalization? | Two documented steps supported by distinct sources |
| How does motion reconstruction connect to a biomechanics method? | Two documented steps with the human-pose sense of WHAM |
| Does the molecular-kinetics VAMPnet give a path through whale WhAM to biomechanics? | The directed path lacks supported steps |
| Does PoseX descend from the Boltz-1 family? | The source describes an evaluation |

The flat two-document whale fixture demonstrates the false path that
joining spellings without resolution can create. The context-qualified
run uses the saved reviews and source identity decisions to exclude it.

## Ask a separate transfer question

Ask what assumptions and interface evidence justify carrying a result
from one method to another. The example gives transfer its own proof.
Each step needs both kinds of evidence. When a step lacks its interface
condition, the same documented relation can support lineage while the
transfer query remains missing.

A successful witness identifies the assertion facts and their source
coordinates. The composition record identifies the decisions behind
the composed facts, so the source review can be checked again.
