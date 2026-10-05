# Rendered review

CUA in-app browser, local built site, 2026-10-03 America/New_York.
Desktop 1440x980 and mobile 390x844. Viewport override restored afterward.

- Home: product purpose, calls to action, SVG check/repair diagram and application cards reviewed.
- Mobile: home heading/buttons fit; drawer opened and exposed six BookRec chapters; chapter 3 navigated correctly. Document scroll width equaled viewport width (390px). Code blocks scroll internally.
- Expense chapter 3: all 14 code blocks rendered as code, with copy controls. Visible theme toggle changed to dark and back to light.
- Search for currency returned 17 results; first result opened expense chapter 3 with highlighted terms and usable section anchors.
- Desktop content width was 1440px with no document overflow. Diagram loaded with its explanatory alt text.
- Initial custom runnable fence suffixes leaked as visible text. Corrected to HTML comments; automated rendered-fence check retains this failure class.
- Default Zensical 404 linked to missing #__skip. Added a small content override with the correct focus target; link check passes without exceptions.
- Diagram review shortened a crowded label and corrected split-path arrow endings.

This was a sampled rendered review, not a complete accessibility audit or physical-device compatibility matrix. The retained desktop image is the overview; its bytes are recorded in the evidence manifest.
