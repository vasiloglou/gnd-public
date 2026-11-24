# Characterizing possible failure modes in physics-informed neural networks (2021)
Work arXiv:2109.01050. A synthetic paraphrase written for regression testing; it is not the text of the work.
The study shows that physics-informed neural networks, or PINNs, can fail on only slightly harder problems such as convection.
It traces the failures to the soft PDE regularization, which makes the loss landscape hard to optimize, not to a lack of expressivity.
The authors introduce curriculum regularization, which starts PINNs on a simple PDE term and makes the term harder as training goes on.
The remedy cut the error by one to two orders of magnitude compared with the regular training baseline.
Curriculum regularization is used in scientific machine learning for training PINNs on hard equations.
