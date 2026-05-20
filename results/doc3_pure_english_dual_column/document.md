## Machine Learning Operations (MLOps): Overview, Definition, and Architecture

Dominik Kreuzberger
KIT
Germany
dominik.kreuzberger@alumni.kit.edu

Niklas Kühl
KIT
Germany
kuehl@kit.edu

Sebastian Hirschl
IBM^†
Germany
sebastian.hirschl@de.ibm.com

## ABSTRACT

The final goal of all industrial machine learning (ML) projects is to
develop ML products and rapidly bring them into production.
However, it is highly challenging to automate and operationalize
ML products and thus many ML endeavors fail to deliver on their
expectations. The paradigm of Machine Learning Operations
(MLOps) addresses this issue. MLOps includes several aspects,
such as best practices, sets of concepts, and development culture.
However, MLOps is still a vague term and its consequences for
researchers and professionals are ambiguous. To address this gap,
we conduct mixed-method research, including a literature review,
a tool review, and expert interviews. As a result of these
investigations, we provide an aggregated overview of the necessary
principles, components, and roles, as well as the associated
architecture and workflows. Furthermore, we furnish a definition
of MLOps and highlight open challenges in the field. Finally, this
work provides guidance for ML researchers and practitioners who
want to automate and operate their ML products with a designated
set of technologies.

## KEYWORDS

CI/CD, DevOps, Machine Learning, MLOps, Operations,
Workflow Orchestration

## 1 Introduction

Machine Learning (ML) has become an important technique to
leverage the potential of data and allows businesses to be more
innovative [1], efficient [13], and sustainable [22]. However, the
success of many productive ML applications in real-world settings
falls short of expectations [21]. A large number of ML projects
fail—with many ML proofs of concept never progressing as far as
production [30]. From a research perspective, this does not come as
a surprise as the ML community has focused extensively on the
building of ML models, but not on (a) building production-ready
ML products and (b) providing the necessary coordination of the
resulting, often complex ML system components and infrastructure,
including the roles required to automate and operate an ML system
in a real-world setting [35]. For instance, in many industrial
applications, data scientists still manage ML workflows manually

to a great extent, resulting in many issues during the operations of
the respective ML solution [26].

To address these issues, the goal of this work is to examine how
manual ML processes can be automated and operationalized so that
more ML proofs of concept can be brought into production. In this
work, we explore the emerging ML engineering practice “Machine
Learning Operations”—MLOps for short—precisely addressing
the issue of designing and maintaining productive ML. We take a
holistic perspective to gain a common understanding of the
involved components, principles, roles, and architectures. While
existing research sheds some light on various specific aspects of
MLOps, a holistic conceptualization, generalization, and
clarification of ML systems design are still missing. Different
perspectives and conceptions of the term “MLOps” might lead to
misunderstandings and miscommunication, which, in turn, can lead
to errors in the overall setup of the entire ML system. Thus, we ask
the research question:

RQ: What is MLOps?

To answer that question, we conduct a mixed-method research
endeavor to (a) identify important principles of MLOps, (b) carve
out functional core components, (c) highlight the roles necessary to
successfully implement MLOps, and (d) derive a general
architecture for ML systems design. In combination, these insights
result in a definition of MLOps, which contributes to a common
understanding of the term and related concepts.

In so doing, we hope to positively impact academic and
practical discussions by providing clear guidelines for
professionals and researchers alike with precise responsibilities.
These insights can assist in allowing more proofs of concept to
make it into production by having fewer errors in the system’s
design and, finally, enabling more robust predictions in real-world
environments.

The remainder of this work is structured as follows. We will first
elaborate on the necessary foundations and related work in the field.
Next, we will give an overview of the utilized methodology,
consisting of a literature review, a tool review, and an interview
study. We then present the insights derived from the application of
the methodology and conceptualize these by providing a unifying
definition. We conclude the paper with a short summary,
limitations, and outlook.

[^1]: ^† This paper does not represent an official IBM
statement